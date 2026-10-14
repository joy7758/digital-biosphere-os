# DBA Capability Discovery Layer v0.1

This helper layer gives the existing 12-cell Weekly Cockpit a bounded public-source discovery path.

    AUTOMATION_SCOPE=AC0_DISCOVERY_AND_AC1_REFERENCE_ONLY
    MODEL_CALLS=0
    EXTERNAL_CODE_EXECUTED=false
    DEPENDENCY_INSTALLED=false
    CODE_ADOPTED=0
    AC2_AUTHORIZED=false

It queries only configured arXiv metadata, GitHub public metadata, registered official references, the DCDAT-001 baseline, and optional repository-local discovery hints. External titles, abstracts, descriptions, links, commands, and prompts are untrusted data and are never executed.

## Agent recommendation gate

    AGENT_RECOMMENDATION=CONDITIONALLY_RECOMMENDED
    RECOMMENDED_AS=BOUNDED_PUBLIC_CAPABILITY_DISCOVERY_AND_REFERENCE_MEMORY
    NOT_RECOMMENDED_AS=AUTOMATIC_CODE_ADOPTION_OR_SAFETY_CERTIFICATION

The bounded source universe, deterministic identities, digest chain, and explicit non-adoption state make this useful for agents that need a weekly external reference view. It is not recommended as an open-world completeness claim, implementation evaluator, package installer, policy engine, or runtime controller.

The existing Project, Environment, Relationship, Evidence Admission, Security, Upgrade, Quality, Drift, Memory, Handoff, Human View, and Coordinator Cells consume the helper outputs. The helper modules are not new Cells, truth sources, or a control plane.
