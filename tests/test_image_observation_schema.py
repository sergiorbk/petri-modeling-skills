import copy
import unittest

from petri_modeling_skills import read_schema

try:
    from jsonschema import Draft202012Validator, ValidationError
except ImportError:
    Draft202012Validator = None


@unittest.skipIf(Draft202012Validator is None, "Install the optional test extra for schema validation")
class ImageObservationSchemaTests(unittest.TestCase):
    def setUp(self):
        self.schema = read_schema("petri-image-observation")
        self.validator = Draft202012Validator(self.schema)
        self.example = {
            "schema_version": "1.0",
            "source_image": {"width": 1200, "height": 900},
            "analysis_image": {"width": 800, "height": 600, "preprocessing": ["crop", "resize"], "source_to_analysis": None},
            "nodes": [
                {"id": "n1", "type": "place", "label": "Queue", "marking": None,
                 "bounds": {"x": 20, "y": 40, "width": 30, "height": 30},
                 "provenance": [{"field": "marking", "basis": "unknown", "evidence": "The interior is blurred"}]},
                {"id": "n2", "type": "transition", "label": "Service", "marking": None, "bounds": None,
                 "provenance": [{"field": "type", "basis": "observed", "evidence": "A clear vertical bar"}]}
            ],
            "arcs": [{"id": "a1", "source": "n1", "target": None, "direction": "unknown", "kind": "ordinary", "weight": None,
                      "points": [], "provenance": [{"field": "target", "basis": "unknown", "evidence": "The far endpoint is cropped"}]}],
            "assumptions": [],
            "uncertainties": [{"element_id": "a1", "field": "target", "description": "Need an uncropped endpoint to connect the arc", "blocking": True}],
            "canvas_transform": None,
        }

    def test_schema_allows_explicitly_unreadable_values_without_invented_semantics(self):
        Draft202012Validator.check_schema(self.schema)
        self.validator.validate(self.example)
        self.assertIsNone(self.example["nodes"][0]["marking"])
        self.assertIsNone(self.example["arcs"][0]["target"])

    def test_invalid_markings_weights_or_transition_markings_are_rejected(self):
        invalid_examples = []
        invalid = copy.deepcopy(self.example)
        invalid["nodes"][0]["marking"] = -1
        invalid_examples.append(invalid)
        invalid = copy.deepcopy(self.example)
        invalid["arcs"][0]["weight"] = 0
        invalid_examples.append(invalid)
        invalid = copy.deepcopy(self.example)
        invalid["nodes"][1]["marking"] = 1
        invalid_examples.append(invalid)
        for invalid in invalid_examples:
            with self.assertRaises(ValidationError):
                self.validator.validate(invalid)

    def test_visual_judgments_cannot_be_stored_as_calibrated_confidence_fields(self):
        invalid = copy.deepcopy(self.example)
        invalid["nodes"][0]["confidence"] = 0.99
        with self.assertRaises(ValidationError):
            self.validator.validate(invalid)

    def test_known_coordinate_transforms_and_explicit_parameters_are_supported(self):
        value = copy.deepcopy(self.example)
        value["analysis_image"]["source_to_analysis"] = [[1, 0, -100], [0, 1, -50], [0, 0, 1]]
        value["canvas_transform"] = {"scale": 1.5, "offset_x": 40, "offset_y": 60}
        value["nodes"][1]["parameters"] = [{"name": "delay", "value": 5, "unit": "s",
                                            "provenance": {"field": "delay", "basis": "observed", "evidence": "The image explicitly says 5 s"}}]
        self.validator.validate(value)
        value["canvas_transform"]["scale"] = 0
        with self.assertRaises(ValidationError):
            self.validator.validate(value)

    def test_visual_frame_semantics_are_kept_separate_from_net_nodes(self):
        value = copy.deepcopy(self.example)
        value["frames"] = [{"id": "f1", "label": "Section A", "bounds": None, "member_ids": ["n1", "n2"],
                            "semantics": "visual-group", "provenance": [{"field": "semantics", "basis": "observed", "evidence": "Only a grouping box is visible"}]}]
        self.validator.validate(value)


if __name__ == "__main__":
    unittest.main()
