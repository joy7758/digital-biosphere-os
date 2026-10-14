# TITMAS Console Information Architecture Research

Status: `PRIVATE_RESEARCH_BASELINE`

## Observed reusable patterns

- LangSmith uses organization/workspace separation, workspace-scoped usage and
  retention, project views, and explicit billing surfaces.
- AgentLoop exposes data, Trace, evaluation, experiments, registered services
  and system management as distinct assets.
- Permit exposes identity, tenant, environment, policy, decision logs and
  quota as first-class concepts.
- Cisco, WitnessAI and HiddenLayer use progressive navigation from inventory
  or visibility to policy, event, investigation and enforcement.
- Chinese cloud consoles favor persistent left navigation, dense tables,
  explicit filters, access-key management, billing, audit logs and support.

## Original TITMAS navigation

```text
Overview / Agents / Activity / Health / Gate / Approvals / Receipts / Audit /
Integrations / Usage / Deployments / Settings / Support
```

This navigation is an original composition around TITMAS objects. It must not
copy a vendor's naming sequence, visual tokens, component code or page layout.

The first screen is `Agent Overview`（智能体总览）. `Activity` is the Human
projection of the Observer entry layer; it is not a fifth product or a new
Trace platform. Policy and Gate configuration are not the first customer task.

## First-login architecture

1. choose a zero-customer-data synthetic Demo;
2. import a public or authorized redacted sample; or
3. connect one read-only test Agent;
4. view Agent Overview, activity and risk;
5. inspect shadow Gate results, a bounded Receipt and Audit timeline;
6. decide whether to request a Monitor Pilot.

The first login must not require complex Policy creation, Enforce configuration,
a payment card, an annual contract or complete production data upload.

## Mode communication

`MONITOR MODE — NO ACTIONS ARE BLOCKED` and `ENFORCE MODE — ACTIONS MAY BE
BLOCKED` must remain visible in the page header and event detail. Status is
expressed through text and icons as well as color.

Mode changes, Enforce, key creation/revocation, deletion and high-impact
approval require explicit confirmation. Monitor has authority and enforcement
effect `NONE`; Enforce remains subject to separate Human authorization.

## Data minimization

The default table stores and displays digests, references, reason codes,
timestamps, policy revision, authorization status and limitations. It does not
store or render chain of thought or raw customer payloads.

## Implementation boundary

```text
CONSOLE_INFORMATION_ARCHITECTURE_DEFINED=true
CONSOLE_IMPLEMENTED=false
OBSERVER_RUNTIME_IMPLEMENTED=false
TRACE_BACKEND_CREATED=false
POLICY_ENGINE_CREATED=false
```
