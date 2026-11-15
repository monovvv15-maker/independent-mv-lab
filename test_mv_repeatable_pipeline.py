import copy
import json
import tempfile
import unittest
from pathlib import Path
from mv_repeatable_pipeline import (
    SCRIPT_VERSION,STAGES,cache_valid,record,stage_key,
    execute,load_recipe,check_private_assets,receipt_path,file_sha
)

class RepeatablePipelineTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.root=Path(self.tmp.name)
        self.recipe_path=Path("catalog/mv_repeatable_recipe_v1.json")
        self.recipe=load_recipe(self.recipe_path)
    def tearDown(self):self.tmp.cleanup()
    def test_recipe_and_five_stages(self):
        self.assertEqual(len(STAGES),5)
        self.assertEqual(self.recipe["engine"],"drawing-v42")
    def test_dry_run_never_creates_video(self):
        result=execute(self.recipe_path,self.root/"run",dry_run=True)
        self.assertTrue(result["dry_run"])
        self.assertFalse(result["video_generated"])
        self.assertFalse((self.root/"run"/"products").exists())
    def test_no_approval_rejects_build(self):
        with self.assertRaises(PermissionError):
            execute(self.recipe_path,self.root/"run")
    def test_private_asset_sha_required(self):
        image=self.root/"image.jpg"
        audio=self.root/"audio.mp3"
        image.write_bytes(b"fake")
        audio.write_bytes(b"fake")
        with self.assertRaises(ValueError):
            check_private_assets(self.recipe,image,audio)
    def test_receipt_reuse_only_for_sha_matching(self):
        work=self.root/"work";work.mkdir()
        output=work/"test.out";output.write_bytes(b"valid output")
        key=stage_key("render",self.recipe,source_hashes={"a":"123"})
        record(work,"render",key,[output])
        self.assertTrue(cache_valid(work,"render",key))
        self.assertFalse(cache_valid(work,"render","changed"))
        output.write_bytes(b"tampered")
        self.assertFalse(cache_valid(work,"render",key))
    def test_digest_changes_on_script_change(self):
        a=stage_key("render",self.recipe,source_hashes={"code":"a"})
        b=stage_key("render",self.recipe,source_hashes={"code":"b"})
        self.assertNotEqual(a,b)
    def test_receipt_rejects_output_outside_workspace(self):
        work=self.root/"workspace";work.mkdir()
        external=self.root/"external.txt";external.write_bytes(b"data")
        with self.assertRaises(ValueError):
            record(work,"render","key",[external])
    def test_blank_receipt_does_not_validate(self):
        work=self.root/"workspace";work.mkdir()
        receipt_path(work,"render").parent.mkdir(parents=True)
        receipt_path(work,"render").write_text(json.dumps({"state":"complete","key":"x","outputs":{}}))
        self.assertFalse(cache_valid(work,"render","x"))
    def test_renderer_dependencies_all_exist(self):
        for p in self.recipe["renderer_sources"]:
            self.assertTrue(Path(p).is_file(),p)
    def test_missing_media_no_fallback(self):
        with self.assertRaises(FileNotFoundError):
            check_private_assets(self.recipe,self.root/"missing.jpg",self.root/"missing.mp3")
if __name__=="__main__":unittest.main()
