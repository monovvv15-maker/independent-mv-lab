import unittest
from unittest.mock import patch
from mv_private_connection_check import check_environment,check_sources
class PrivateConnectionChecks(unittest.TestCase):
 def test_flags_do_not_echo_values(self):
  env={"DROPBOX_REFRESH_TOKEN":"testsecret"}
  flags=check_environment(env)
  self.assertIs(flags["DROPBOX_REFRESH_TOKEN"],True)
  self.assertNotIn("testsecret",str(flags))
 def test_empty_config_safe(self):
  with patch.dict("os.environ",{},clear=True):
   r=check_sources()
   self.assertFalse(r["ready"])
   self.assertTrue(r["no_video_generated"])
   self.assertTrue(r["no_private_bytes_downloaded"])
 def test_missing_cache_path(self):
  env={name:"ok" for name in
       ("DROPBOX_REFRESH_TOKEN","DROPBOX_APP_KEY","DROPBOX_APP_SECRET",
       "MV_JACKET_DROPBOX_PATH","MV_AUDIO_DROPBOX_PATH")}
  flags=check_environment(env)
  self.assertFalse(flags["MV_PRIVATE_CACHE_PATH"])
if __name__=="__main__":unittest.main()
