import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch
from mv_private_dropbox import safe_dropbox_path,backup_workspace,restore_workspace,access_token

class PrivateBridgeTests(unittest.TestCase):
    def test_path_must_be_absolute(self):
        with self.assertRaises(ValueError):safe_dropbox_path("relative/file")
        with self.assertRaises(ValueError):safe_dropbox_path("/private/../public/file")
        self.assertEqual(safe_dropbox_path("/Suilemo/MV/private.zip"),"/Suilemo/MV/private.zip")
    def test_secret_absence_fails_closed(self):
        with patch.dict("os.environ",{},clear=True):
            with self.assertRaises(RuntimeError):access_token()
    def test_archive_includes_receipts_not_raw_media(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/"work";root.mkdir()
            (root/"receipts").mkdir()
            (root/"receipts"/"render.json").write_text('{"state":"complete"}')
            (root/"products").mkdir()
            (root/"products"/"test.mp4").write_bytes(b"render-only")
            (root/"source.jpg").write_bytes(b"private original")
            archive=Path(d)/"store.zip"
            backup_workspace(root,archive)
            with zipfile.ZipFile(archive) as z:
                files=set(z.namelist())
                self.assertIn("receipts/render.json",files)
                self.assertIn("products/test.mp4",files)
                self.assertNotIn("source.jpg",files)
            out=Path(d)/"restore"
            restore_workspace(archive,out)
            self.assertEqual((out/"products"/"test.mp4").read_bytes(),b"render-only")
    def test_archive_traversal_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            f=root/"bad.zip"
            with zipfile.ZipFile(f,"w") as z:z.writestr("../escape.txt","no")
            with self.assertRaises(ValueError):
                restore_workspace(f,root/"restored")
            self.assertFalse((root/"escape.txt").exists())
if __name__=="__main__":unittest.main()
