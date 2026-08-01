import unittest
from validation.environment_qualification_validator import verifier_covers_qualification, QUALIFICATION_REGISTRY_PATH

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

if __name__ == '__main__':
    unittest.main()
