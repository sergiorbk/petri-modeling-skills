import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

import petri_modeling_skills as skills


class ResourceTests(unittest.TestCase):
    def test_catalog_entries_resolve_to_real_documents(self):
        entries = skills.catalog()
        self.assertEqual(7, len(entries))
        self.assertEqual(len(entries), len({entry["id"] for entry in entries}))
        for entry in entries:
            self.assertTrue(entry["name"])
            self.assertTrue(entry["description"])
            body = skills.read_resource(entry["uri"])
            self.assertEqual(body, skills.read_skill(entry["id"]))
            self.assertTrue(body.startswith("# "))
            self.assertNotIn("\nname:", body)

    def test_catalog_does_not_expose_mutable_shared_state(self):
        first = skills.catalog()
        first[0]["id"] = "changed"
        first.clear()
        self.assertEqual("petri-modeling", skills.catalog()[0]["id"])

    def test_unknown_ids_and_filesystem_paths_are_rejected(self):
        for identifier in ["unknown", "../LICENSE", "petri-modeling?query", "petri-modeling#fragment", ""]:
            with self.assertRaises(KeyError):
                skills.read_skill(identifier)
        for uri in ["file:///LICENSE", "petri://skills/../LICENSE", "https://example.org", "petri://skills/petri-modeling/", "petri://skills/petri-modeling?query"]:
            with self.assertRaises(KeyError):
                skills.read_resource(uri)

    def test_assembled_guidance_includes_each_manifest_resource_once(self):
        combined = skills.modeling_guidance()
        for entry in skills.catalog():
            self.assertEqual(1, combined.count(skills.read_skill(entry["id"])))

    def test_relative_reference_links_resolve_inside_package(self):
        import re

        package = Path(skills.__file__).parent
        manifest = json.loads((package / "manifest.json").read_text(encoding="utf-8"))
        for entry in manifest["resources"]:
            document = package / entry["path"]
            for link in re.findall(r"\]\(([^)]+)\)", document.read_text(encoding="utf-8")):
                if "://" not in link:
                    target = (document.parent / link.split("#")[0]).resolve()
                    self.assertTrue(target.is_relative_to(package.resolve()))
                    self.assertTrue(target.is_file(), str(target))

    def test_resources_load_without_a_source_directory(self):
        package = Path(skills.__file__).parent
        with tempfile.TemporaryDirectory() as temporary:
            archive = Path(temporary) / "skills.zip"
            with zipfile.ZipFile(archive, "w") as output:
                for source in package.rglob("*"):
                    if source.is_file() and "__pycache__" not in source.parts:
                        output.write(source, source.relative_to(package.parent).as_posix())
            script = (
                "import json,sys; sys.path.insert(0,sys.argv[1]); "
                "import petri_modeling_skills as s; "
                "print(json.dumps([s.__version__,len(s.catalog()),len(s.modeling_guidance())]))"
            )
            result = subprocess.run([sys.executable, "-I", "-c", script, str(archive)],
                                    cwd=temporary, check=True, capture_output=True, text=True)
            version, count, length = json.loads(result.stdout)
            self.assertEqual("0.3.0", version)
            self.assertEqual(7, count)
            self.assertGreater(length, 1000)

    def test_json_schemas_use_a_separate_allowlist_and_are_not_prompt_text(self):
        schema = skills.read_schema("training-bundle")
        self.assertIn("1.1", schema["properties"]["schema_version"]["enum"])
        schema["properties"].clear()
        self.assertIn("schema_version", skills.read_schema("training-bundle")["properties"])
        self.assertNotIn('"$schema"', skills.modeling_guidance())
        for identifier in ["unknown", "../LICENSE", "training-bundle.schema.json"]:
            with self.assertRaises(KeyError):
                skills.read_schema(identifier)


if __name__ == "__main__":
    unittest.main()
