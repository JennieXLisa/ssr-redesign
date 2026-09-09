# Phase 7 — specifications and detailed implementation plans

These plans translate cross-feature requirements into concrete record constraints, migration checks, public methods, child protocol, frontend behavior and release gates. They do not authorize a competing controller-side implementation of harness rules.

| Feature | Specification | Detailed build plan |
|---|---|---|
| P7-F01 Contracts and persistence | [Specification](P7-F01-contracts-and-persistence.md) | [Implementation](P7-F01/IMPLEMENTATION_PLAN.md) |
| P7-F02 Public SDK and controller | [Specification](P7-F02-public-sdk-and-controller.md) | [Implementation](P7-F02/IMPLEMENTATION_PLAN.md) |
| P7-F03 Configuration, versioning and rollout | [Specification](P7-F03-configuration-versioning-and-rollout.md) | [Implementation](P7-F03/IMPLEMENTATION_PLAN.md) |

[Phase integration plan](../IMPLEMENTATION_PLAN.md) · [All feature plans](../../FEATURE_IMPLEMENTATION_INDEX.md) · [Delivery order](../../DELIVERY.md).

Allocate migrations from the actual schema horizon, preserve historical contracts, and negotiate complete capabilities. The controller remains a public-SDK consumer with authenticated child-only engine dispatch where required. Clean installed-artifact and all four compatibility-pair tests are required; these documents are not reports that those application tests ran.
