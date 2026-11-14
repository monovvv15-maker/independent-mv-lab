import tempfile,unittest
from pathlib import Path
from v28_sources import selected,inspect
class V28Tests(unittest.TestCase):
 def test_list(self):
  catalog=[{'id':1,'duration':15,'license_page':'Free','url':'https://www.pexels.com/video/x-1/','download_url':'https://www.pexels.com/download/video/1/','tags':['rain','morning','people','city','walking','train','street','memory','flower','wind','stillness','ending','sunset']}]
  chosen,shots=selected(catalog)
  self.assertEqual(len(shots),34)
  self.assertEqual(len(chosen),1)
 def test_failure_is_reported(self):
  catalog=[{'id':1,'duration':15,'license_page':'Free','url':'https://www.pexels.com/video/x-1/','download_url':'https://www.pexels.com/download/video/1/','tags':['rain','morning','people','city','walking','train','street','memory','flower','wind','stillness','ending','sunset']}]
  def fail(item,dest):raise ValueError('blocked')
  with tempfile.TemporaryDirectory() as d:
   result=inspect(catalog,Path(d),fetch=fail)
   self.assertEqual(result['preview_ready'],0)
   self.assertEqual(result['unavailable'],[1])
   self.assertFalse(result['video_rendered'])
if __name__=='__main__':unittest.main()
