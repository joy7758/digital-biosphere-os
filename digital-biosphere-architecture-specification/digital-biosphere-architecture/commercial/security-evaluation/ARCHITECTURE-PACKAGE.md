# Security Evaluation Architecture Package

## System boundary

```text
Customer Agent/Application
  -> Adapter
  -> Gate API
  -> Customer Action System
  -> Receipt
  -> Audit / Health
```

Customer Data Plane retains raw customer content by default. TITMAS Private Platform receives approved minimum metadata; Management Plane handles manual provisioning, configuration and support. Public discovery/proof is not the private implementation.

## Authority boundary

- Gate outcome does not prove result correctness;
- Receipt does not prove Truth, legality, safety or certification;
- Monitor has no enforcement effect;
- Enforce requires customer-specific written scope, Human approval and rollback;
- Verification cannot create authorization;
- the evaluator cannot grant production, commercial, certification or release authority.

## Canonical dependencies

Identity, execution evidence, policy references, Receipt semantics and Audit semantics remain owned by their canonical repositories. This kit creates no alternate source of truth.
