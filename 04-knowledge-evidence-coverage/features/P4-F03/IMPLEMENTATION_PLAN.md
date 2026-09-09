# P4-F03 — Knowledge reuse and corrections: implementation plan

Updated: 2026-09-09. Documentation only. Read the [feature](../P4-F03-knowledge-reuse-and-corrections.md), [STATE.md](../../../contracts/STATE.md), P2-F03 summaries and P5-F03 reassessment.

## 1. Preserve claim type and scope

Extend existing structured knowledge/results with exact subject/facet identity, source/evidence refs, assumptions, applicability conditions and limitations. FACT means a bounded source observation asserted by its producer, not a host-certified theorem. HYPOTHESIS and QUESTION remain separate; schema acceptance cannot promote them to proved findings.

Use immutable accepted artifacts as the referenceable bodies. Keep existing document/knowledge storage and query owners. Do not create a second cache containing synthesized consensus prose. Query results expose exact record IDs, original producers and recorded relations; they do not choose whichever statement sounds most confident.

## 2. Immutable revision relations

Represent SUPERSEDES, CONTRADICTS and APPLIES_UNDER as typed associations between exact artifact/claim/facet revisions. Validate source/target ownership, snapshot/policy compatibility and supporting references. The producer proposing contradiction supplies the challenged facet and explanation; the host does not infer contradiction from opposite words in two summaries.

Accept a successor body and relation in one domain transaction, preserving the previous body's hash and original publication. A duplicate operation returns the same relation/receipt. A changed payload under an old artifact ID is an integrity conflict. A correction is not permission to delete earlier counterevidence or rewrite historical exports.

A supersession relation describes recorded evolution; current validity still comes from the owning acceptance/candidate policy. Two conditional analyses may coexist without either superseding the other.

## 3. Material dependencies versus incidental context

When a result/candidate uses another artifact, record whether the selected reference is material and which argument facet depends on it. Keep exact artifact/evidence revision, subject domain, assumption digest and consumer revision. Do not make every navigation read a mandatory dependency of every finding.

Add inverse indexes from material subject/artifact/facet to consumer revisions. Availability/correction handling queries those indexes in bounded batches rather than scanning all prose. This keeps unrelated subsystem updates from invalidating every candidate.

Host validation checks reference integrity and required dependency declarations. The analyst still decides/explains semantic relevance. A missing material declaration is a result-contract gap to detect during investigation/falsification, not a reason for the host to guess a complete taint graph.

## 4. Represent negative assumptions explicitly

For claims such as 'no applicable authorization guard was found', record the checked source/registration domain, query or traversal definition, snapshot/index generation, applicable configuration assumptions and completeness limitations. A no-match result from an interrupted scan cannot support an exhaustive absence claim.

The domain may include registered middleware/caller sets, not only positively cited code ranges. A later accepted registration or caller observation can then identify affected negative facets even when the old referenced function bytes are unchanged. Do not store source-sensitive query text indiscriminately; use safe structured filters/digests and explicit omitted-query limitations under the shared content policy.

A new domain-associated observation triggers applicability evaluation. It is not automatically proof that the previous negative claim is false. P5-F03 applies conservative validity holds only under its source-grounded material challenge contract.

## 5. Correction publication and propagation

Prepare the corrected artifact/relation and accepted producer evidence. In the short publication transaction expose the successor/contradiction, update availability generation and record material-effect intents for exact affected consumers. Required current-finding holds must be atomic with acceptance of the material challenge, not delayed behind optional notices.

Optional freshness notices advertise newer information. They do not replace mandatory stale-input checks, and an analyst ignoring a notice cannot authorize accepting obsolete material. Late challenges target the exact historical revision; applicability to a current successor requires an explicit identical/reused facet or a separate assessment, not blanket refutation.

Use existing coordinator reconciliation to process propagation intents idempotently. Record which consumer/facet was examined and the outcome. Do not repeatedly create reassessment tasks for the same challenge/revision pair.

## 6. Repeated-review reuse

Extend the existing reuse/lineage owner with collaborative result/policy/model and assumption compatibility, not a new universal cache. Reuse requires exact source/symbol lineage proof plus all relevant dependency/configuration contracts. Same name or same function body with changed imported security control is not sufficient.

Create an explicit new-review adoption/import record mapping old contribution identity to verified current subjects/content. Preserve original producer and historical epoch. New review availability gets its own sequence; old review cursors and notices cannot be rebound. Source/evidence mappings must be verified against the new snapshot, not copied by path alone.

An older partial summary lacking new required facets stays readable with limitations but cannot be treated as a complete new-contract unit result. Changed source and materially affected neighbors receive required new work. Unknown dependency coverage remains explicit; do not claim complete invalidation precision where the index cannot establish it.

## 7. Concurrency and failure

Two corrections racing on one predecessor create distinct immutable artifacts and explicit relations; only a permitted compare-and-swap current pointer can choose the current revision. The loser is not silently discarded. Candidate-family authority determines current finding state separately.

Crash after corrected payload but before availability/propagation leaves pending accepted state with a recoverable intent. Crash after validity hold before task materialization leaves the hold active and the required work intent visible. Recovery cannot clear the hold merely because no reassessment worker is running.

A newly inaccessible referenced artifact stays protected during propagation/retrieval. Restore/withdraw availability uses new generations so old H-bounded listings cannot resurrect obsolete permission.

## 8. Tests

Create two conditional analyses for one helper with different caller assumptions: both remain distinguishable. Publish a source-backed correction and verify old content hashes and exact retrieval remain intact with current status. Retry the correction and ensure one transition/propagation intent.

Create a candidate whose negative authorization facet depends on a middleware registration domain. Add an accepted registration elsewhere: only relevant consumers receive applicability work; unrelated candidates do not. An interrupted initial search must not have been accepted as exhaustive absence.

Run reuse fixtures for unchanged full dependency/policy state, changed contract, changed imported control, renamed same-content symbol with verified lineage and same-name different-content symbol. Assert explicit adoption/requeue and preserved producer IDs. New review cursors must reject old review tokens.

## 9. Delivery sequence

Add structured claim/facet/assumption schemas; implement immutable relations; add material dependency indexes and bounded propagation; extend existing reuse compatibility; integrate current-finding holds and availability notices. Completion evidence is exact before/after artifact identities, targeted propagation counts and reuse-negative tests. No automatic consensus model, free-text semantic cache, broad global invalidation or invented all-callers safety proof belongs here.
