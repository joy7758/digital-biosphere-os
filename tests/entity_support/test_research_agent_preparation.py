"""Tests for the non-instantiating Research Agent preparation template."""

from __future__ import annotations

import unittest

from entity_support.research_agent_preparation import (
    RESEARCH_AGENT_CAPABILITY_NAMES,
    build_research_agent_preparation_template,
    validate_research_agent_preparation_template,
)


class ResearchAgentPreparationTests(unittest.TestCase):
    def test_template_uses_operational_entity_role(self) -> None:
        template = build_research_agent_preparation_template()
        self.assertEqual(template["entity_classification"], "OPERATIONAL_ENTITY")
        self.assertEqual(template["research_role"], "RESEARCH_AGENT")

    def test_template_has_no_identity_or_instance_ids(self) -> None:
        template = build_research_agent_preparation_template()
        serialized = repr(template)
        for key in ("entity_id", "agent_id", "runtime_id", "capability_id"):
            self.assertNotIn(key, serialized)

    def test_template_remains_preparation_only(self) -> None:
        template = build_research_agent_preparation_template()
        self.assertEqual(template["template_status"], "PREPARATION_ONLY")
        self.assertEqual(template["identity_status"], "NOT_ASSIGNED")
        self.assertEqual(template["instance_effect"], "NONE")

    def test_reference_capability_names_match_architecture(self) -> None:
        template = build_research_agent_preparation_template()
        names = tuple(
            item["capability_name"] for item in template["capability_profile_template"]
        )
        self.assertEqual(names, RESEARCH_AGENT_CAPABILITY_NAMES)

    def test_capabilities_are_templates_without_permission(self) -> None:
        template = build_research_agent_preparation_template()
        for item in template["capability_profile_template"]:
            self.assertEqual(item["template_status"], "DECLARATION_TEMPLATE")
            self.assertEqual(item["permission_effect"], "NONE")

    def test_human_oversight_is_mandatory(self) -> None:
        template = build_research_agent_preparation_template()
        metadata = template["research_role_metadata"]
        self.assertTrue(metadata["human_oversight_required"])
        self.assertEqual(metadata["publication_authority"], "NONE")

    def test_injected_entity_id_is_rejected(self) -> None:
        template = build_research_agent_preparation_template()
        template["entity_id"] = "forbidden-instance"
        errors = validate_research_agent_preparation_template(template)
        self.assertTrue(any("prohibited instance key" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
