import copy
import unittest

from jsonschema import Draft202012Validator, FormatChecker, ValidationError
from petri_modeling_skills import read_schema


class TrainingHistoryTests(unittest.TestCase):
    def setUp(self):
        self.schema = read_schema("training-history")
        self.validator = Draft202012Validator(self.schema, format_checker=FormatChecker())

    def test_index_and_review_keep_reviewed_and_result_revisions_distinct(self):
        self.validator.validate({"schema_version": "1.0", "bundle_id": "bundle-a", "head_revision_id": "b" * 64,
                                 "revisions": [{"id": "a" * 64, "parent_revision_id": "", "model_sha256": "c" * 64},
                                               {"id": "b" * 64, "parent_revision_id": "a" * 64, "model_sha256": "d" * 64}],
                                 "reviews": [{"id": "e" * 64}]})
        schema = dict(self.schema, **{"$ref": "#/$defs/reviewRecord"})
        for key in ("required", "properties", "additionalProperties", "type"):
            schema.pop(key, None)
        validator = Draft202012Validator(schema, format_checker=FormatChecker())
        review = {"reviewer": "Declared reviewer", "reviewer_kind": "human", "decision": "changes_requested", "comment": "Capacity is incorrect",
                  "findings": [{"severity": "error", "message": "Use capacity two", "view_id": "main", "element_id": "GraphPetriPlace:2"}],
                  "revision_id": "a" * 64, "result_revision_id": "b" * 64, "created_at": "2026-10-30T12:00:00Z",
                  "previous_review_id": "", "verification_status": "unknown"}
        validator.validate(review)
        review["findings"][0]["region"] = {"coordinate_system": "image-pixels", "image_sha256": "f" * 64, "x": 10, "y": 20, "width": 40, "height": 30}
        validator.validate(review)
        invalid_region = copy.deepcopy(review)
        invalid_region["findings"][0]["region"]["width"] = -1
        with self.assertRaises(ValidationError):
            validator.validate(invalid_region)
        for field, value in [("reviewer_kind", "inferred-human"), ("verification_status", "passed"), ("revision_id", "r001"), ("decision", "probably")]:
            invalid = copy.deepcopy(review)
            invalid[field] = value
            with self.assertRaises(ValidationError):
                validator.validate(invalid)

    def test_bundle_allows_bounded_revision_artifacts_and_rejects_unsafe_paths(self):
        schema = read_schema("training-bundle")
        artifact_schema = {"$defs": schema["$defs"], "$ref": "#/$defs/artifact"}
        validator = Draft202012Validator(artifact_schema)
        record = {"name": "history/revisions/" + "a" * 64 + "/networks/object-0001.png",
                  "media_type": "image/png", "sha256": "b" * 64, "purpose": "Historical object image"}
        validator.validate(record)
        for path in ["../model.pnml", "history/revisions/../model.pnml", "networks/../../model.pnml", "C:/model.pnml", "history/revisions/not-a-hash/model.pnml"]:
            with self.assertRaises(ValidationError):
                validator.validate(dict(record, name=path))
