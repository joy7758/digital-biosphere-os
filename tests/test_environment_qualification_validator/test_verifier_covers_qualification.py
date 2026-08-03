from validation.environment_qualification_validator import (
    QUALIFICATION_REGISTRY_PATH,
    verifier_covers_qualification,
)


def test_happy_path() -> None:
    verifier = {
        "scope": {
            "registry_authority": [
                "some/other/path.yaml",
                QUALIFICATION_REGISTRY_PATH,
            ]
        }
    }
    assert verifier_covers_qualification(verifier) is True


def test_missing_scope() -> None:
    verifier = {}
    assert verifier_covers_qualification(verifier) is False


def test_scope_not_dict() -> None:
    verifier = {"scope": "not-a-dict"}
    assert verifier_covers_qualification(verifier) is False


def test_missing_registry_authority() -> None:
    verifier = {"scope": {}}
    assert verifier_covers_qualification(verifier) is False


def test_registry_authority_not_list() -> None:
    verifier = {"scope": {"registry_authority": "not-a-list"}}
    assert verifier_covers_qualification(verifier) is False


def test_missing_qualification_registry_path() -> None:
    verifier = {
        "scope": {
            "registry_authority": [
                "some/other/path.yaml",
            ]
        }
    }
    assert verifier_covers_qualification(verifier) is False
