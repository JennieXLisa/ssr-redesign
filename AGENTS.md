# Instructions for the SSR redesign documentation repository

This repository contains a design and implementation guidance, not the harness runtime. Work only in the authorized documentation scope; never change source-review-harness or ssr-control, live state, installed packages, provider budgets or repository visibility implicitly.

Read README.md, CONTRACT_HARDENING.md, DECISION_REGISTER.md, ENGINEERING_DECISIONS.md and BASELINE.md. The H0 gate is OPEN: do not interpret earlier DRAFT COMPLETE labels or structural-validation results as implementation readiness. Corrected contracts identify which old prescriptions they supersede; keep unrelated hardening items explicitly open until their own proofs exist. Preserve previously approved behavior. The user delegated completion of remaining design detail; new choices must be clearly attributed as delegated engineering selections, not fabricated individual approvals. Keep implemented facts, reference-code observations, proposed behavior and actual test results distinct.

Use main roadmap → phase specification/implementation plan → feature guide. Keep shared contracts in contracts/ and refer to their owner instead of copying inconsistent fields. Avoid a giant chronological specification and avoid one file per trivial helper. Preserve historical checkpoints and requirement/test IDs. Never revive an earlier requirement for consultation as a reason to leave delegated authoring unfinished.

Provide concrete implementation mechanisms, ownership, transactions, error/recovery cases, source-sensitive boundaries, negative tests, compatibility and delivery gates. Do not add unnecessary services, managers, new stores or frameworks. Current module paths must be verified against the refactor; historical references are not proof of installed behavior.

Run tools/validate_docs.py after changes. Report what it actually checks. Schema/Markdown checks are not application tests. GitHub writes require available authenticated tooling and an authorized target; never claim a push without verifying the remote commit. Preserve unrelated remote changes.
