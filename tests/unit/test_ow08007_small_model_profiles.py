from __future__ import annotations
import pathlib,sys,unittest
ROOT=pathlib.Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools'))
import owledge_small_model_profiles as p
import run_small_model_smoke as smoke
class SmallModelTests(unittest.TestCase):
 def test_tier1_profile_passes_bounded_task(self): self.assertTrue(p.validate('4k',2000,['owledge_search_memory'],1,1,{'status':'completed','receipt_id':'r','evidence_ref':'e','privacy_safe':True,'freshness_safe':True})['passed'])
 def test_all_guardrails_fail_closed(self):
  r=p.validate('4k',2201,['a','b','c'],2,2,{'status':'completed','receipt_id':'r','privacy_safe':False,'freshness_safe':False});self.assertIn('wrong_tool',r['errors']);self.assertIn('false_acceptance',r['errors'])
 def test_invalid_output_fails(self): self.assertIn('invalid_structured_output',p.validate('8k',1,[],0,0,{})['errors'])
 def test_scenarios_bind_tool_and_required_result_field(self):
  self.assertEqual(smoke.SCENARIOS['planning']['tool'],'owledge_build_context_pack')
  self.assertEqual(smoke.SCENARIOS['retrieval']['field'],'query')
  self.assertEqual(smoke.SCENARIOS['resume']['tool'],'owledge_list_tasks')
 def test_retry_loop_exceeds_8k_profile_limit(self):
  output={'status':'completed','receipt_id':'r','evidence_ref':'e','privacy_safe':True,'freshness_safe':True}
  self.assertTrue(p.validate('8k',1,[],0,2,output)['passed'])
  self.assertIn('retry_limit',p.validate('8k',1,[],0,3,output)['errors'])
  self.assertIn('invalid_retry_count',p.validate('8k',1,[],0,-1,output)['errors'])
 def test_false_acceptance_is_rejected(self):
  output={'status':'completed','receipt_id':'r','privacy_safe':True,'freshness_safe':True}
  self.assertIn('false_acceptance',p.validate('8k',1,[],0,0,output)['errors'])
if __name__=='__main__':unittest.main()
