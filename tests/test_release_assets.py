import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("release_assets", ROOT / "scripts/build_release_assets.py")
assets = importlib.util.module_from_spec(spec)
spec.loader.exec_module(assets)


class ReleaseAssetTests(unittest.TestCase):
    def test_resources_include_all_manifest_documents_and_license(self):
        entries = assets.resource_entries(ROOT)
        prefix = "petri-modeling-skills/"
        manifest = json.loads(entries[prefix + "manifest.json"])
        for entry in manifest["resources"] + manifest["schemas"]:
            self.assertIn(prefix + entry["path"], entries)
        self.assertIn(prefix + "LICENSE", entries)
        self.assertIn(prefix + "NOTICE", entries)
        self.assertTrue(all(name.startswith(prefix) and ".." not in name.split("/") for name in entries))

    def test_resource_archives_are_repeatable_and_normalize_line_endings(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "LICENSE").write_bytes(b"license\r\n")
            (root / "NOTICE").write_bytes(b"notice\r\n")
            package = root / "petri_modeling_skills"
            package.mkdir()
            (package / "manifest.json").write_bytes(b"{}\r\n")
            first, second = root / "first.zip", root / "second.zip"
            assets.write_zip(first, assets.resource_entries(root))
            (root / "LICENSE").write_bytes(b"license\n")
            assets.write_zip(second, assets.resource_entries(root))
            self.assertEqual(first.read_bytes(), second.read_bytes())
            with zipfile.ZipFile(first) as archive:
                self.assertIsNone(archive.testzip())
                self.assertEqual(b"license\n", archive.read("petri-modeling-skills/LICENSE"))
