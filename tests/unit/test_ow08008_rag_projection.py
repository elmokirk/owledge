from __future__ import annotations
import pathlib,sys,unittest
ROOT=pathlib.Path(__file__).resolve().parents[2]; sys.path.insert(0,str(ROOT/'tools'))
import owledge_rag_projection as projection
import owledge_core as core
class ProjectionTests(unittest.TestCase):
 def test_clean_heading_chunks_keep_governance_out_of_embedding(self):
  r={"metadata":{"memory_id":"mem:x","semantic_title":"Title","summary":"Summary","data_class":"internal","edges":[{"type":"supports"}],"document_version":2},"source_hash":"a"*64,"body":"# Heading\n\nUseful body."}
  row=projection.project(r)[0]
  self.assertIn("Title",row["embedding_text"]); self.assertNotIn("memory_id",row["embedding_text"]); self.assertEqual(row["metadata"]["source_hash"],"a"*64)
 def test_private_or_stale_records_do_not_project(self):
  r={"metadata":{"memory_id":"mem:x","data_class":"personal"},"source_hash":"x","body":"secret"}; self.assertEqual(projection.project(r),[])
  r["metadata"]={"memory_id":"mem:x","data_class":"internal","source_freshness":"stale"}; self.assertEqual(projection.project(r),[])
 def test_frontmatter_and_unqualified_research_never_enter_embedding(self):
  r={"metadata":{"memory_id":"mem:x","data_class":"internal","doc_type":"research"},"source_hash":"x","body":"---\nmemory_id: leak\n---\n# Body\nprivate"}
  self.assertEqual(projection.project(r),[])
  r["metadata"].update({"research_reason":"why","context":"allowed"})
  self.assertNotIn("memory_id",projection.project(r)[0]["embedding_text"])
 def test_secret_and_crlf_frontmatter_are_never_embedded(self):
  r={"metadata":{"memory_id":"mem:x","data_class":"secret"},"source_hash":"x","body":"secret"}; self.assertEqual(projection.project(r),[])
  r={"metadata":{"memory_id":"mem:x","data_class":"internal"},"source_hash":"x","body":"---\r\nmemory_id: leak\r\n---\r\n# Body\r\nUseful"}
  self.assertNotIn("memory_id",projection.project(r)[0]["embedding_text"])
 def test_core_projection_is_deterministic(self):
  self.assertEqual(core.export_rag_projection_v1(ROOT)["digest"],core.export_rag_projection_v1(ROOT)["digest"])
if __name__=='__main__': unittest.main()
