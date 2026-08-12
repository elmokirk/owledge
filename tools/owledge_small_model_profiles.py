"""Deterministic guards for small-model task capsules."""
from __future__ import annotations
from typing import Any
PROFILES={"4k":{"context":2200,"tools":2,"hops":1,"retries":1},"8k":{"context":4800,"tools":3,"hops":2,"retries":2},"16k":{"context":10000,"tools":5,"hops":3,"retries":2},"standard":{"context":24000,"tools":8,"hops":4,"retries":3}}
ALLOWED_TOOLS={"owledge_read_entrypoint","owledge_doctor","owledge_search_memory","owledge_context_synopsis","owledge_build_context_pack","owledge_list_tasks","owledge_list_reviews"}
def validate(profile:str, capsule_chars:int, tools:list[str], hops:int, attempts:int, output:dict[str,Any])->dict[str,Any]:
 if profile not in PROFILES: raise ValueError("small_model.unknown_profile")
 p=PROFILES[profile]; errors=[]
 if capsule_chars>p["context"]: errors.append("oversized_context")
 if len(tools)>p["tools"]: errors.append("tool_limit")
 if any(tool not in ALLOWED_TOOLS for tool in tools): errors.append("wrong_tool")
 if hops>p["hops"]: errors.append("multi_hop_limit")
 if attempts>p["retries"]: errors.append("retry_limit")
 if not isinstance(output,dict) or output.get("status") not in {"completed","needs_review","refused"} or not isinstance(output.get("receipt_id"),str): errors.append("invalid_structured_output")
 if output.get("status") == "completed" and not str(output.get("evidence_ref", "")).strip(): errors.append("false_acceptance")
 if output.get("privacy_safe") is not True or output.get("freshness_safe") is not True: errors.append("unsafe_output")
 return {"passed":not errors,"profile":profile,"limits":p,"errors":errors}
