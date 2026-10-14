# Cerbos

- Source URLs: https://docs.cerbos.dev/cerbos-hub/decision-points.html
- Source access time: 2026-08-03
- Page title: Service Policy Decision Points
- Product status: maintained public product documentation.
- Pricing status: not assessed in this pass.
- Architecture summary: Cerbos Hub acts as control plane while PDP instances run in customer infrastructure and serve authorization decisions to application PEPs.
- Console navigation: deployments and connected decision points are verified; full console navigation is not assessed.
- UI patterns: fleet connectivity, policy build/test/distribution and deployment state.
- Commercial funnel: documentation and enterprise Hub path; exact funnel not assessed.
- Deployment modes: customer infrastructure PDP with centralized management.
- Strengths: clean PAP/PDP/PEP and control/data-plane separation.
- Weaknesses: authorization semantics do not provide TITMAS execution-evidence semantics.
- Applicable lessons: compile/test before distribution, versioned policy bundles and local decision points.
- Non-applicable lessons: policy language, general authorization system and open-source strategy.
- Uncertainties: current pricing and China-specific support.
