import unittest
import json
from unittest.mock import patch
from pathlib import Path
from validation.environment_qualification_validator import verifier_covers_qualification, QUALIFICATION_REGISTRY_PATH, load_json_yaml

class TestEnvironmentQualificationValidator(unittest.TestCase):
    def test_verifier_covers_qualification_valid(self):
        verifier = {
            "scope": {
                "registry_authority": [QUALIFICATION_REGISTRY_PATH]
            }
        }
        self.assertTrue(verifier_covers_qualification(verifier))

    def test_verifier_covers_qualification_missing_scope(self):
        verifier = {}
        self.assertFalse(verifier_covers_qualification(verifier))

    def test_verifier_covers_qualification_scope_not_dict(self):
        verifier = {"scope": "not a dict"}
        self.assertFalse(verifier_covers_qualification(verifier))

    def test_verifier_covers_qualification_missing_registry_authority(self):
        verifier = {"scope": {}}
        self.assertFalse(verifier_covers_qualification(verifier))

    def test_verifier_covers_qualification_registry_authority_not_list(self):
        verifier = {"scope": {"registry_authority": "not a list"}}
        self.assertFalse(verifier_covers_qualification(verifier))

    def test_verifier_covers_qualification_missing_path(self):
        verifier = {"scope": {"registry_authority": ["some/other/path"]}}
        self.assertFalse(verifier_covers_qualification(verifier))


class TestLoadJsonYaml(unittest.TestCase):
    def test_load_json_yaml_oserror(self):
        with patch("pathlib.Path.read_text", side_effect=OSError("mock os error")):
            with self.assertRaises(ValueError) as ctx:
                load_json_yaml(Path("mock_path.json"))
            self.assertIn("cannot load mock_path.json", str(ctx.exception))

    def test_load_json_yaml_json_decode_error(self):
        with patch("pathlib.Path.read_text", side_effect=json.JSONDecodeError("mock decode error", "doc", 0)):
            with self.assertRaises(ValueError) as ctx:
                load_json_yaml(Path("mock_path.json"))
            self.assertIn("cannot load mock_path.json", str(ctx.exception))

    def test_load_json_yaml_not_dict(self):
        with patch("pathlib.Path.read_text", return_value="[]"):
            with self.assertRaises(ValueError) as ctx:
                load_json_yaml(Path("mock_path.json"))
            self.assertIn("must contain one mapping", str(ctx.exception))


if __name__ == '__main__':
    unittest.main()
