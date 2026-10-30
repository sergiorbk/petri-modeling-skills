import copy
import unittest

from petri_modeling_skills import read_schema

try:
    from jsonschema import Draft202012Validator, FormatChecker, ValidationError
except ImportError:
    Draft202012Validator = None


@unittest.skipIf(Draft202012Validator is None, "Install the optional test extra for schema validation")
class TrainingBundleSchemaTests(unittest.TestCase):
    def setUp(self):
        self.schema = read_schema("training-bundle")
        self.validator = Draft202012Validator(self.schema, format_checker=FormatChecker())
        self.example = {
            "schema_version": "1.0",
            "title": "Parallel machines",
            "created_at": "2026-10-30T12:00:00Z",
            "app": {"name": "Example desktop", "version": "1.0"},
            "shared_skills": {"version": "0.2.0", "revision": None},
            "status": "unreviewed",
            "capture_scope": {"conversation": "unavailable", "tool_calls": "unavailable"},
            "files": [{"name": name, "media_type": "application/json", "sha256": "0" * 64, "purpose": name}
                      for name in ["task.json", "model.pnml", "conversation.jsonl", "tool-calls.jsonl", "verification.json"]],
            "missing_data": [{"artifact": "conversation.jsonl", "reason": "External client did not supply its conversation"},
                             {"artifact": "tool-calls.jsonl", "reason": "No trace was recorded"}],
        }

    def artifact_validator(self, name):
        return Draft202012Validator({"$ref": f"#/$defs/{name}", "$defs": self.schema["$defs"]}, format_checker=FormatChecker())

    def test_schema_is_valid_and_allows_explicit_missing_observations(self):
        Draft202012Validator.check_schema(self.schema)
        self.validator.validate(self.example)
        self.artifact_validator("task").validate({"task": None, "clarifications": [], "assumptions": [], "acceptance": []})
        self.artifact_validator("verification").validate({"status": "unknown", "checks": [], "simulation": None})

    def test_manifest_rejects_missing_artifacts_unsafe_paths_duplicate_entries_and_invalid_provenance(self):
        examples = []
        missing = copy.deepcopy(self.example)
        missing["files"].pop()
        examples.append(missing)
        unsafe = copy.deepcopy(self.example)
        unsafe["files"][0]["name"] = "../task.json"
        examples.append(unsafe)
        duplicate = copy.deepcopy(self.example)
        duplicate["files"].append(copy.deepcopy(duplicate["files"][0]))
        examples.append(duplicate)
        invalid_hash = copy.deepcopy(self.example)
        invalid_hash["files"][0]["sha256"] = "not-a-hash"
        examples.append(invalid_hash)
        invalid_time = copy.deepcopy(self.example)
        invalid_time["created_at"] = "2026-10-30T12:00:00+02:00"
        examples.append(invalid_time)
        for value in examples:
            with self.assertRaises(ValidationError):
                self.validator.validate(value)

    def test_conversation_records_cannot_mislabel_system_or_tool_text_as_dialogue(self):
        validator = self.artifact_validator("conversationRecord")
        validator.validate({"role": "user", "content": "Build two parallel machines"})
        validator.validate({"role": "assistant", "content": "The model is ready", "timestamp": "2026-10-30T12:00:00+00:00"})
        for role in ["system", "tool"]:
            with self.assertRaises(ValidationError):
                validator.validate({"role": role, "content": "Instructions or tool output"})

    def test_verification_does_not_accept_a_pass_without_actual_passed_checks(self):
        validator = self.artifact_validator("verification")
        with self.assertRaises(ValidationError):
            validator.validate({"status": "passed", "checks": [], "simulation": None})
        validator.validate({"status": "passed", "checks": [{"name": "PNML grammar", "status": "passed", "details": "Validated by the application's grammar validator"}], "simulation": None})
        with self.assertRaises(ValidationError):
            validator.validate({"status": "failed", "checks": [], "simulation": None})

    def test_tool_calls_preserve_their_capture_origin_and_allow_an_unobserved_outcome(self):
        validator = self.artifact_validator("toolCallRecord")
        validator.validate({"tool": "inspect_ui", "arguments": {}, "timestamp": "2026-10-30T12:00:00Z", "origin": "application"})
        with self.assertRaises(ValidationError):
            validator.validate({"tool": "inspect_ui", "arguments": {}, "timestamp": "2026-10-30T12:00:00Z", "origin": "invented"})

    def test_geometry_requires_its_matching_image_and_a_positive_render_scale(self):
        manifest = copy.deepcopy(self.example)
        descriptor = {"name": "model-geometry.json", "media_type": "application/json", "sha256": "0" * 64, "purpose": "Geometry for the actual rendered net"}
        manifest["files"].append(descriptor)
        with self.assertRaises(ValidationError):
            self.validator.validate(manifest)
        manifest["files"].append({"name": "network.png", "media_type": "image/png", "sha256": "0" * 64, "purpose": "Final net image"})
        self.validator.validate(manifest)
        geometry = {"coordinate_system": "image-pixels", "image": {"file": "network.png", "width": 800, "height": 600},
                    "transform": {"origin_x": 10, "origin_y": 20, "scale": 1.5}, "label_status": "renderer-derived",
                    "elements": [{"id": "p1", "kind": "place", "bounds": {"x": 20, "y": 30, "width": 40, "height": 40}, "clipped": False}]}
        validator = self.artifact_validator("modelGeometry")
        validator.validate(geometry)
        geometry["transform"]["scale"] = 0
        with self.assertRaises(ValidationError):
            validator.validate(geometry)


if __name__ == "__main__":
    unittest.main()
