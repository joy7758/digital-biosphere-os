# TITMAS Product Reuse Gate v0.1

Status: `FAIL_CLOSED_MANAGEMENT_GATE`

## Entry criteria

A proposed product or solution must identify its customer problem, the exact
existing private domains it reuses, its public Product mapping, truth owners,
differences, unsupported fields and known limitations.

## Evaluation

```text
SHARED_CORE_REUSE_TARGET=70_PERCENT
ADAPTER_APPROXIMATE_BUDGET=10_PERCENT
POLICY_CONFIGURATION_APPROXIMATE_BUDGET=10_PERCENT
UI_AND_REPORT_APPROXIMATE_BUDGET=10_PERCENT
```

These percentages are portfolio estimates. They are not a protocol invariant,
standard requirement, scientific claim or externally guaranteed metric.

The gate fails if a proposal creates a second identity, evidence, policy, Gate,
Receipt, Audit, tenant or issuance core; copies a private engine into an
industry repository; or makes an Adapter a truth or verification owner.

## Results

- `PASS_PORTFOLIO_EXTENSION`: the shared-core estimate is at least 70% and no
  duplicate core is introduced.
- `REVIEW_REQUIRED`: evidence is incomplete or estimates are uncertain.
- `NOT_A_TITMAS_PORTFOLIO_EXTENSION`: the proposal requires an independent
  platform or duplicate core.

No result grants implementation, merge, release, access or production
authority.
