"""Create one synthetic DBOS Entity Object representation and print JSON.

The example creates only an in-memory representation. It does not register,
activate, verify, persist, or grant permission to any real entity.
"""

from __future__ import annotations

from pathlib import Path
import sys


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from sdk import object_to_json  # noqa: E402
from sdk.objects import EntityObject  # noqa: E402


SYNTHETIC_ENTITY_ID = "dbio://repository/quickstart-synthetic-example/v0.1"
SYNTHETIC_SOURCE_ID = "examples/basic_object/create_entity_object.py"


def _reference(reference_id: str) -> dict[str, str]:
    return {
        "reference_id": reference_id,
        "reference_type": "ENTITY",
        "namespace": "dbio",
        "version": "v0.1",
        "source": SYNTHETIC_SOURCE_ID,
        "status": "DECLARED",
    }


def build_synthetic_entity_object() -> EntityObject:
    """Return an inert, explicitly limited Entity Object test representation."""

    return EntityObject(
        object_id=SYNTHETIC_ENTITY_ID,
        entity_id=SYNTHETIC_ENTITY_ID,
        entity_type="repository",
        owner_reference=_reference(
            "dbio://entity/quickstart-synthetic-owner/v0.1"
        ),
        lifecycle_state="PROPOSED",
        source_reference=_reference(SYNTHETIC_ENTITY_ID),
        source={
            "namespace": "dbio",
            "source_id": SYNTHETIC_SOURCE_ID,
            "version": "v0.1",
            "status": "DECLARED",
        },
        status="DECLARED",
        created_at=None,
        updated_at=None,
        limitations=(
            "Synthetic quick-start representation only.",
            "No real entity, identity verification, activation, or permission is created.",
        ),
    )


def main() -> int:
    print(object_to_json(build_synthetic_entity_object()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
