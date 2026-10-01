# Detailed Research Framework

## 1. Motivation

Safety and security arguments for cyber-physical systems are rarely static. New software versions, new sensor evidence, changed uncertainty bounds, updated verification results, runtime interventions, and operational anomalies can all alter whether an earlier assurance claim remains well supported.

This repository treats an assurance case as a **living evidence graph** rather than a fixed document. The graph makes explicit which claims depend on which evidence, assumptions, contexts, and defeaters, and it supports automated checks for structural weaknesses and changing evidence quality.

The project is designed for research on traceability and assurance maintenance. It does not turn a graph into a certification decision.

## 2. Research Questions

The initial research program is organized around the following questions.

### RQ1 — Traceability

Can a machine-readable assurance graph make it easier to trace a high-level safety or security claim back to the evidence and assumptions on which it depends?

### RQ2 — Evidence freshness

Can explicit validity windows and observation times identify claims whose support has become stale before a human reviewer notices the problem?

### RQ3 — Change impact

When one assumption, context, or evidence artifact changes, can graph traversal correctly identify the downstream claims that require reassessment?

### RQ4 — Contradiction handling

Can explicit defeaters and contradiction edges prevent positive evidence from masking newly observed counter-evidence?

### RQ5 — Argument quality

Can graph-quality metrics identify weak assurance cases, including unsupported claims, orphan evidence, cyclic dependencies, and undocumented assumption status?

### RQ6 — Cross-tool evidence integration

Can evidence from formal verification, runtime assurance, digital twins, tests, and operational monitoring be normalized into a common assurance representation without erasing source-specific semantics?

## 3. Assurance Graph Model

The graph currently defines five node types.

| Node type | Role |
|---|---|
| `claim` | A proposition that the assurance case seeks to support. |
| `evidence` | An observation, result, test artifact, verification output, or monitoring artifact used to support or challenge a claim. |
| `assumption` | A condition that must hold for a claim or evidence interpretation to remain valid. |
| `context` | Scope, system configuration, environment, version, or interpretation information. |
| `defeater` | A reason that a claim may fail despite supporting evidence. |

The current edge types are:

| Edge type | Meaning |
|---|---|
| `supports` | Source contributes positive support to the target claim. |
| `depends_on` | Target validity depends on the source condition or subclaim. |
| `contradicts` | Source provides counter-evidence against the target. |
| `qualifies` | Source constrains the scope or interpretation of the target. |

## 4. Claim Assessment Semantics

A claim is currently considered supported when all of the following hold:

1. at least one incoming support edge exists;
2. at least one supporting node remains usable after freshness checks;
3. no incoming contradiction edge is present;
4. no directly required assumption is marked `violated` or `unvalidated`.

This is intentionally conservative and transparent. It is a research baseline, not a complete assurance logic.

If usable support nodes contain confidence values, the current experimental propagation rule uses the minimum confidence among those support nodes. This is deliberately simple so its behavior can be inspected. It must not be interpreted as a probability that the physical system is safe.

## 5. Evidence Freshness

Evidence nodes may record:

- `observed_at`: when the evidence was produced or observed;
- `valid_until`: when the evidence should be considered expired;
- source-specific metadata.

A support node is treated as stale when `valid_until` is earlier than the assessment time. A claim may therefore transition from supported to unsupported even when the graph topology has not changed.

Future extensions should distinguish:

- expiry because evidence was never refreshed;
- invalidation because the software/configuration changed;
- supersession by newer evidence;
- model-assumption drift;
- source trust degradation.

## 6. Assumption Lifecycle

Assumptions should record an explicit status in node metadata. Recommended statuses are:

- `validated` — supported by current evidence;
- `explicit` — stated but not independently validated;
- `unvalidated` — known to require validation;
- `violated` — known not to hold in the current context.

The current claim analyzer treats `unvalidated` and `violated` dependencies as unmet.

A future assumption lifecycle should additionally track:

- validation method;
- validating artifact identifier;
- last validation time;
- validity scope;
- expected revalidation trigger;
- responsible reviewer or process.

## 7. Structural Validation

The repository now contains a graph validator that checks for research-relevant integrity problems.

### Errors

The current validator treats the following as structural errors:

- direct self-loops;
- cycles in support/dependency/qualification paths.

Cycles matter because they can create circular assurance arguments in which claims ultimately support themselves.

### Warnings

The validator currently surfaces:

- claims with no incoming assurance relationships;
- evidence that is not linked to any assurance element;
- assumptions without a recorded status;
- unusual support relationships that do not target claims;
- context nodes used directly as contradictory evidence.

Warnings do not imply the system is unsafe. They indicate places where the assurance argument deserves review.

## 8. Assurance Health Metrics

The graph-health summarizer reports descriptive measures including:

- total nodes and edges;
- counts of claims, evidence nodes, assumptions, contexts, and defeaters;
- number of currently supported claims;
- number of contradicted claims;
- number of claims relying on stale evidence;
- number of claims with unmet assumptions;
- support coverage;
- stale-claim rate.

These are **argument-quality metrics**, not safety probabilities.

A useful experimental question is whether these metrics correlate with human reviewer effort or with defects in manually maintained assurance cases.

## 9. Change-Impact Analysis

The project includes transitive impact analysis. When a node changes, downstream claims reachable through support, dependency, and qualification relationships can be identified for reassessment.

Example:

```text
Sensor calibration assumption
        ↓ depends_on
State-estimation claim
        ↓ supports
Runtime shield trust claim
        ↓ supports
System-level safety claim
```

If the calibration assumption changes, the impact analysis should identify all downstream claims, not only the immediate dependency.

This enables research on **incremental assurance maintenance** rather than complete manual review after every system change.

## 10. Evidence Integration Architecture

A target integration architecture is:

```text
Formal Verification Manifest ─┐
Runtime Shield Audit Trace ───┤
Digital Twin State Record ────┤
Test / CI Results ────────────┼─> Evidence Normalizers
Monitoring / Incident Data ───┤          │
Human Review Decisions ───────┘          ↓
                                  Assurance Evidence Graph
                                            │
                              ┌─────────────┼─────────────┐
                              ↓             ↓             ↓
                         Validation     Claim Review   Impact Analysis
                              │             │             │
                              └─────────────┴─────────────┘
                                            ↓
                                   Human Assurance Review
```

Source adapters should preserve provenance. A normalized evidence node should not discard whether a result came from formal proof, simulation, testing, or runtime monitoring.

## 11. Experimental Evaluation Plan

The repository should be evaluated using controlled assurance-case scenarios rather than only unit tests.

### Experiment A — Freshness degradation

Start with a fully supported assurance case, expire selected evidence, and measure whether affected claims are correctly identified.

### Experiment B — Assumption violation

Change one assumption from `validated` to `violated` and compare automated downstream impact results with a hand-labeled reference set.

### Experiment C — Contradictory runtime evidence

Inject a defeater or contradiction after a prior verification result and verify that the claim is no longer reported as supported.

### Experiment D — Graph defects

Introduce orphan evidence, isolated claims, cycles, and undocumented assumptions and measure validator precision/recall against known defects.

### Experiment E — Cross-tool integration

Ingest evidence from formal-verification and runtime-assurance repositories and test whether provenance and scope remain traceable after normalization.

## 12. Candidate Evaluation Metrics

Potential empirical metrics include:

- unsupported-claim detection precision and recall;
- stale-evidence detection accuracy;
- affected-claim identification precision and recall;
- contradiction detection rate;
- mean graph defect count;
- evidence-to-claim trace length;
- proportion of claims with explicit assumptions;
- proportion of assumptions with validation status;
- reviewer time to identify invalidated claims;
- reviewer agreement before and after automated graph analysis;
- number of unnecessary full-case reviews avoided by change-impact analysis.

## 13. Threats to Validity

Important threats include:

- assurance cases may be manually constructed to match the analysis logic;
- synthetic examples may be too clean compared with real engineering evidence;
- confidence values may create a false sense of quantitative rigor;
- edge semantics may be insufficiently expressive for complex structured arguments;
- reviewer judgments may differ even when graph structure is identical;
- stale evidence does not always mean invalid evidence;
- external artifacts may change semantics when normalized into a common schema.

## 14. Reproducibility Requirements

Experiments should record:

- graph schema version;
- repository commit;
- node and edge counts;
- evidence timestamps and validity windows;
- assumption status changes;
- exact analysis time;
- validator version;
- metrics configuration;
- source artifact identifiers;
- expected affected claims;
- observed affected claims;
- random seed for generated cases;
- benchmark scenario identifier.

## 15. Roadmap

### Phase 1 — Core graph mechanics

- typed graph model;
- serialization;
- claim assessment;
- freshness analysis;
- contradiction handling;
- impact analysis;
- structural validation;
- health metrics.

### Phase 2 — Evidence ingestion

- formal verification manifest adapter;
- runtime assurance trace adapter;
- digital-twin state adapter;
- test/CI evidence adapter;
- provenance-preserving source metadata.

### Phase 3 — Dynamic assurance

- evidence supersession;
- version-aware graph snapshots;
- assumption history;
- diff-based assurance review;
- incremental claim re-evaluation.

### Phase 4 — Human-centered evaluation

- reviewer studies;
- review-effort measurement;
- explanation usefulness;
- graph visualization;
- assurance decision traceability.

## 16. Scientific Integrity Boundary

The repository must maintain the following distinctions:

- graph support is not physical-system safety;
- confidence is not a calibrated probability of safety;
- formal verification evidence is conditional on its model and assumptions;
- runtime observations do not automatically generalize beyond their operating context;
- absence of detected contradiction is not proof that no contradiction exists;
- automated impact analysis supports review but does not replace accountable human assurance decisions.
