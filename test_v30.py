import unittest
from v30_preflight import inspect
class V30Tests(unittest.TestCase):
 def test_script_7(self):self.assertEqual(inspect()["chapters"],7)
 def test_no_render(self):self.assertFalse(inspect()["video_generated"])
 def test_style_and_gates(self):self.assertEqual(inspect()["errors"],[])
if __name__=="__main__":unittest.main()
