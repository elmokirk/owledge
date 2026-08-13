#!/usr/bin/env python3
"""Fail-closed real local-model Tier-1 matrix for OW-080-07 evidence."""
from __future__ import annotations
import argparse, hashlib, json, urllib.request
from datetime import datetime, timezone
from typing import Any
from owledge_small_model_profiles import validate

SCENARIOS = {
 "planning": {"task":"Create one bounded MVP step; defer nonessential work.","tools":["owledge_build_context_pack"],"hops":1,"tool":"owledge_build_context_pack","field":"mvp_step","required_keys":["deliverable","deferred_to_roadmap"]},
 "retrieval": {"task":"Select the approved scoped search tool; do not request private data.","tools":["owledge_search_memory"],"hops":1,"tool":"owledge_search_memory","field":"query","required_keys":[]},
 "resume": {"task":"A bounded handoff is already loaded. List the open work item to state its next safe action; do not invent completion.","tools":["owledge_context_synopsis","owledge_list_tasks"],"hops":2,"tool":"owledge_list_tasks","field":"next_action","required_keys":[]},
}

def invoke(base: str, model: str, scenario: str, spec: dict[str, Any], timeout: int, retry_count: int) -> dict[str, Any]:
 prompt=(f"You are completing a bounded {scenario} task: {spec['task']} "
 "Available tools: owledge_build_context_pack (build bounded task context), "
 "owledge_search_memory (search approved scoped memory), "
 "owledge_list_tasks (list bounded work items), owledge_context_synopsis (read a non-canonical synopsis). "
 "Return only JSON with status completed, privacy_safe true, freshness_safe true, "
 f"receipt_id local-smoke, evidence_ref local-model-response, selected_tool, "
 f"and a concise nonempty {spec['field']} field. " + ("For mvp_step use an object with nonempty deliverable and deferred_to_roadmap fields." if spec["required_keys"] else ""))
 request=urllib.request.Request(base+"/api/generate",data=json.dumps({"model":model,"prompt":prompt,"stream":False}).encode(),headers={"Content-Type":"application/json"})
 with urllib.request.urlopen(request,timeout=timeout) as response: raw=json.load(response)
 text=str(raw.get("response","")).strip()
 if not text: return {"passed":False,"scenario":scenario,"reason":"empty_local_model_response"}
 digest=hashlib.sha256(text.encode()).hexdigest()
 try: output=json.loads(text)
 except ValueError: return {"passed":False,"scenario":scenario,"reason":"invalid_local_model_json","response_sha256":digest}
 result=validate("8k",2000,spec["tools"],spec["hops"],retry_count,output)
 result.update({"scenario":scenario,"response_sha256":digest,"selected_tool":output.get("selected_tool"),"expected_tool":spec["tool"],"required_field":spec["field"]})
 if output.get("selected_tool") != spec["tool"]: result["passed"]=False;result["errors"].append("wrong_selected_tool")
 value=output.get(spec["field"])
 if not str(value or "").strip(): result["passed"]=False;result["errors"].append("missing_scenario_output")
 if spec["required_keys"] and (not isinstance(value,dict) or any(not str(value.get(key,"")).strip() for key in spec["required_keys"])): result["passed"]=False;result["errors"].append("scenario_quality_mismatch")
 return result

def main() -> int:
 p=argparse.ArgumentParser();p.add_argument("--model",required=True);p.add_argument("--scenario",choices=[*SCENARIOS,"all"],default="all");p.add_argument("--url",default="http://127.0.0.1:11434/api/tags");p.add_argument("--output");p.add_argument("--timeout",type=int,default=180);p.add_argument("--attempt",type=int,default=1);p.add_argument("--retry-count",type=int,default=0);a=p.parse_args()
 try:
  with urllib.request.urlopen(a.url,timeout=5) as response: available={x.get("name") for x in json.load(response).get("models",[])}
 except Exception as exc: print(json.dumps({"passed":False,"reason":"local_model_service_unavailable","detail":str(exc)}));return 1
 if a.model not in available: print(json.dumps({"passed":False,"reason":"requested_model_unavailable","model":a.model,"available":sorted(x for x in available if x)}));return 1
 base=a.url.rsplit("/api/",1)[0]; names=list(SCENARIOS) if a.scenario=="all" else [a.scenario]
 rows=[]
 started=datetime.now(timezone.utc).isoformat()
 for name in names:
  try: rows.append(invoke(base,a.model,name,SCENARIOS[name],a.timeout,a.retry_count))
  except Exception as exc: rows.append({"passed":False,"scenario":name,"reason":"local_model_invocation_failed","detail":str(exc)})
  if a.output:
   checkpoint={"passed":all(row["passed"] for row in rows),"complete":False,"model":a.model,"model_service":"local","profile":"8k","attempt":a.attempt,"retry_count":a.retry_count,"timeout_seconds":a.timeout,"started_at":started,"results":rows}
   with open(a.output,"w",encoding="utf-8",newline="\n") as handle: json.dump(checkpoint,handle,sort_keys=True,indent=2);handle.write("\n")
 passed=all(row["passed"] for row in rows)
 payload={"passed":passed,"complete":True,"model":a.model,"model_service":"local","profile":"8k","attempt":a.attempt,"retry_count":a.retry_count,"timeout_seconds":a.timeout,"started_at":started,"finished_at":datetime.now(timezone.utc).isoformat(),"command":"run_small_model_smoke.py --model "+a.model+" --scenario "+a.scenario+" --attempt "+str(a.attempt)+" --retry-count "+str(a.retry_count)+" --timeout "+str(a.timeout),"results":rows}
 if a.output:
  with open(a.output,"w",encoding="utf-8",newline="\n") as handle: json.dump(payload,handle,sort_keys=True,indent=2);handle.write("\n")
 print(json.dumps(payload,sort_keys=True));return 0 if passed else 1
if __name__=="__main__":raise SystemExit(main())
