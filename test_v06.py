import unittest
from v06 import SCENES,relevant,discover
class V06Tests(unittest.TestCase):
 def test_scene_count(self):self.assertEqual(len(SCENES),6)
 def test_block_bear(self):self.assertFalse(relevant("Bear walking at Zoo","04_walking"))
 def test_block_cloud(self):self.assertFalse(relevant("Morning cloud streets","01_morning"))
 def test_walk(self):self.assertTrue(relevant("Walking along a rural riverside path","04_walking"))
 def test_not_licensed(self):
  scenes,errors=discover(search_fn=lambda q,limit: [{"id":"a","title":"Sunny street","license_ok":False}])
  self.assertEqual(sum(len(s) for s in scenes.values()),0)
 def test_empty(self):
  scenes,errors=discover(search_fn=lambda q,limit:[])
  self.assertEqual(sum(bool(s) for s in scenes.values()),0)
if __name__=="__main__":unittest.main()
