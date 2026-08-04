import unittest
from validation.environment_qualification_validator import (
    QUALIFICATION_REGISTRY_PATH,
    verifier_covers_qualification,
)

class VerifierCoversQualificationTests(unittest.TestCase):
    def test_happy_path(self) -> None:
        verifier = {
            "scope": {
                "registry_authority": [
                    "some/other/path.yaml",
                    QUALIFICATION_REGISTRY_PATH,
                ]
            }
        }
        self.assertTrue(verifier_covers_qualification(verifier))

    def test_missing_scope(self) -> None:
        verifier = {}
        self.assertFalse(verifier_covers_qualification(verifier))

    def test_scope_not_dict(self) -> None:
        verifier = {"scope": "not-a-dict"}
        self.assertFalse(verifier_covers_qualification(verifier))

    def test_missing_registry_authority(self) -> None:
        verifier = {"scope": {}}
        self.assertFalse(verifier_covers_qualification(verifier))

    def test_registry_authority_not_list(self) -> None:
        verifier = {"scope": {"registry_authority": "not-a-list"}}
        self.assertFalse(verifier_covers_qualification(verifier))

    def test_missing_qualification_registry_path(self) -> None:
        verifier = {
            "scope": {
                "registry_authority": [
                    "some/other/path.yaml",
                ]
            }
        }
        self.assertFalse(verifier_covers_qualification(verifier))

if __name__ == "__main__":
    unittest.main()
