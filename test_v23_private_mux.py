import unittest,tempfile
from pathlib import Path
from v23_private_mux import sha256,command
class PrivateMuxTests(unittest.TestCase):
 def test_checksum(self):
  with tempfile.TemporaryDirectory() as d:
   f=Path(d)/'x';f.write_bytes(b'abc')
   self.assertEqual(sha256(f),'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad')
 def test_no_network(self):
  cmd=command('ffmpeg','silent.mp4','private.mp3','out.mp4')
  self.assertIn('copy',cmd)
  self.assertNotIn('https://',' '.join(cmd))
if __name__=='__main__':unittest.main()
