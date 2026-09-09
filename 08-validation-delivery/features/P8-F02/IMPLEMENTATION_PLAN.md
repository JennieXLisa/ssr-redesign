# P8-F02 — Quality and cost evaluation: implementation plan

Updated: 2026-09-09. This is an experiment implementation protocol, not measured evidence of improvement. Read the [feature](../P8-F02-quality-and-cost-evaluation.md), [configuration](../../../contracts/CONFIGURATION.md), P8-F01 deterministic acceptance and the controller's existing evaluation-isolation contracts.

## 1. Benchmark manifest and separation

Create an immutable BenchmarkCase manifest with permitted source provenance/license, snapshot digest, supported language/index/model capabilities, case identity, known label coverage and withheld scoring artifacts. Include cross-file positive cases, effective-control negatives, business/state/lifetime concerns without classic sinks, unsupported constructs and untagged/no-hit files.

Gold labels, expected paths, hidden hints and scorer metadata must not enter the reviewed snapshot, model dossier, tools, normal knowledge database, filenames that reveal the answer, or discovery scores. Reuse the controller's separate evaluation store and scorer interfaces. The harness receives only authorized review inputs and a run identity; the scorer reads exact output families/revisions through permitted evaluation projections.

Do not assume unlabeled code is vulnerability-free. Mark whether ground truth is exhaustive, partial or synthetic by construction. Report missed known cases separately from unknown undiscovered defects. A benchmark with incomplete labels cannot establish absolute recall across all source.

## 2. Predeclare variants and controls

Use matched variants that isolate architecture changes: baseline canonical ordering; canonical priority ordering with the same review contract; continuous candidate/context collaboration; and the same with optional focused discovery. Where a factor cannot be isolated without another feature, state the coupled change rather than calling it a pure ablation.

Pin source/index/tool/config/role-prompt identities, model/provider route and capability fingerprint, worker/provider capacity, token/currency/wall limits, optional analyzer/rule digests and budget estimator version. Record actual values, not only a friendly profile name. Vary one intended architectural factor at a time.

Use repeated runs where model stochasticity matters, with paired seeds only where the provider actually supports them. Randomize/interleave variant order to reduce time-of-day/provider-pressure confounding. A changed model revision or gateway route invalidates a naïve paired comparison unless explicitly analyzed as a separate cohort.

## 3. Measure real readiness and delivery boundaries

Record monotonic durations within each process plus correlated durable event identities for cross-process aggregation. Use wall timestamps for correlation, not unchecked subtraction across unsynchronized hosts. Distinguish source snapshot/index time, queue delay, provider execution, tool/host analysis, dependency wait, receipt finalization, falsification and host promotion.

Define time-to-first-current-upheld-finding as the first successful current gate/promotion relative to the chosen review-start boundary. Preserve whether that finding was later held/refuted. Also measure time-to-known-valid-finding confirmed by the external scorer; internal UPHELD alone is not a quality label.

Readiness delay starts when the candidate's recorded inputs and required receipts first satisfy the relevant predicate, not when an old phase controller finally emitted FALSIFICATION_PENDING. Compute an offline read-only readiness oracle from accepted history when necessary. The oracle must not mutate live workflow, read withheld gold labels, or pretend missing historical evidence proves earlier readiness.

## 4. Primary and secondary metrics

For every run record: current upheld findings; scorer-supported true positives; refuted and inconclusive cases; known missed cases; time-to-first and time-to-each known finding; canonical unit/file completion fraction and completion time; required unresolved/limitation outcomes; total and per-root model calls/tokens/cost; host analyzer/search work; queue/wait/receipt delays; and duplicate analysis effort.

Count candidate families, not repeated revisions or duplicate exports, when reporting unique findings. Preserve severity/impact categories only when grounded in the evaluation policy; do not reward a model for inflating labels. Distinguish partially supported claims from fully established expected findings.

Unknown provider usage remains unknown/estimated. Include failed/abandoned attempts, repair calls, reruns, falsification and uncertainty holds in cost. A recovered host tool ACK with no model call is not a new inference cost; a real repeated provider request is. Do not omit the expensive final validation stage from 'cost per finding'.

Duplicate effort measures can include repeated complete-unit analyses, overlapping source reads, repeated semantic requests and accepted coverage adoption. Reading source twice is not automatically waste: independent falsification may require it. Report operational duplicate work separately from intentional independent checking.

## 5. Handle unfinished and failed runs

Use the same hard stopping conditions across variants. When a run times out, exhausts budget or fails operationally, retain its partial observations and reason. Do not drop failed runs from aggregate cost/latency or count missing findings as zero-second latency.

Report completion rate and censored time-to-event observations alongside latency among successful runs. Early success with stalled canonical coverage is a tradeoff, not an unconditional win. A variant finding one easy issue quickly while missing difficult known cases must show that degradation.

Unsupported source/model/analyzer capability is a recorded limitation. Separate infrastructure errors from analytical misses, but keep their consumed resources in overall run cost. Repeating only a favorable variant after failure creates selection bias; follow the predeclared rerun policy equally.

## 6. Scoring procedure and auditability

Have the isolated scorer match output family/revision and source-backed claim to known case labels under an explicit rubric. Require correct affected subject/path, prerequisites and impact—not only a matching vulnerability category. Preserve raw scoring decisions and evidence references for human audit of disputed matches.

For incomplete gold labels, mark novel plausible findings for separate review instead of automatically false-positive labeling. The independent checker cannot use the candidate's self-reported confidence as truth. Conversely, a correct class name with a false reachability path is not a true positive.

Calculate paired differences in time/cost/coverage where runs are truly comparable. Report sample count, spread and uncertainty intervals using an explicitly recorded method and random seed. With too few repeated runs, present descriptive results rather than an unsupported significance claim. Do not convert scheduler simulation results into model-quality evidence.

## 7. Implementation and storage

Add read-only metric extraction at existing accepted transition/event/usage owners. Prefer durable IDs and recorded fields to parsing human log messages. Write evaluation records in the isolated evaluation store, referencing actual source/config/provider artifacts and run IDs; do not alter review rankings based on hidden scores during the same experiment.

Use a reproducible evaluation script that accepts a manifest of completed run identities and outputs per-run tables, aggregate comparisons and missing-data diagnostics. It must fail clearly on mismatched snapshots/configured controls or mark the comparison noncomparable. No silently inferred zero values.

Version protocol/scorer/metric code and include them in the experiment manifest. Proposed tuning changes become a new configuration/policy version and a separate experiment; never rewrite the baseline results under changed defaults.

## 8. Tests before any paid experiment

Feed the metric extractor synthetic traces with known event ordering and costs. Delay the old stage event after all prerequisites were usable and verify the readiness oracle measures the real delay. Create a current finding that is later held and verify both first-promotion timing and final validity are reported.

Inject missing usage, duplicate revisions/exports, abandoned roots, controlled budget differences and an incomplete run. Assert no zero-cost substitution, duplicate finding count or dropped failed run. Put a hidden label sentinel in scorer storage and inspect all model-bound inputs/tool responses; it must never appear.

Create two paired manifests with one changed model/source digest and verify separation/noncomparability. Run the aggregation twice with the same seeded synthetic inputs and compare outputs. Test partial ground-truth labels and a novel finding requiring external review rather than automatic FP.

## 9. Authorization and delivery gate

Implement manifest/scorer isolation and metric fixtures first, then instrument durable boundaries, then execute deterministic ablation harnesses. Live provider/gateway runs require an explicit operator-approved workload, route, spend and stop policy. This documentation does not supply that authorization.

A parameter recommendation must cite the actual run cohort, full quality/coverage/cost tradeoffs and remaining uncertainty. A faster first finding does not by itself approve a default change or deployment. Completion of this feature means the measurement pipeline is reproducible and honest; a positive improvement claim requires separately executed evidence.
