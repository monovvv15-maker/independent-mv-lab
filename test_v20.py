import unittest
from v20_sync import validate_marks
class V20Tests(unittest.TestCase):
 def test_pending_blocks(self):self.assertTrue(validate_marks({"status":"unverified","marks":{}}))
 def test_listener_verified(self):
  self.assertEqual(validate_marks({"status":"listener_review","marks":{"first_vocal":12.4,"shoes_word":16.1,"rain_word":24.5}}),[])
 def test_wrong_order(self):
  self.assertTrue(validate_marks({"status":"listener_review","marks":{"first_vocal":12,"shoes_word":25,"rain_word":15}}))
 def test_non_number(self):
  self.assertTrue(validate_marks({"status":"listener_review","marks":{"first_vocal":"12","shoes_word":15,"rain_word":20}}))
if __name__=="__main__":unittest.main()
