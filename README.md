# Assurance Case Evidence Graph CPS

**Machine-readable, continuously evolving assurance cases for traceable CPS safety and security evidence.**

This repository studies how cyber-physical-system assurance arguments can remain inspectable as software versions, verification results, runtime observations, assumptions, uncertainty bounds, and operating conditions change over time.

The project treats an assurance case as a **living evidence graph** rather than a static document. Claims remain connected to the evidence, assumptions, contexts, and defeaters on which they depend. The current v0.3 research layer adds provenance-preserving evidence adapters and versioned graph snapshots so assurance evolution can be measured rather than described informally.

## Core research question

> **Can continuously updated evidence graphs improve the traceability, consistency, maintainability, and reviewability of CPS assurance as heterogeneous evidence and assumptions evolve?**

## Why this matters

A safety argument can become outdated even when none of its sentences change. A verification result may rely on an assumption that no longer holds. A runtime shield may begin falling back more often. A digital-twin model may be refreshed. A software release may invalidate a test artifact. Traditional assurance documents make these dependencies difficult to track systematically.

This repository explores whether a machine-readable graph can make those changes explicit.

## Architecture

```text
Formal Verification Manifest ─┐
Runtime Safety-Shield Trace ──┤
Digital Twin State ───────────┤
Test / CI Evidence ───────────┼──> Provenance-Preserving Adapters
Operational Monitoring ───────┤                 │
Human Review Decisions ───────┘                 ↓
                                     Assurance Evidence Graph
                                                │
                     ┌──────────────────────────┼──────────────────────────┐
                     ↓                          ↓                          ↓
              Claim Assessment          Structural Validation      Graph Snapshots
                     │                          │                          │
                     ├─ stale support           ├─ cycles                 ├─ digest
                     ├─ contradictions          ├─ orphan evidence        ├─ diff
                     ├─ unmet assumptions       ├─ isolated claims        └─ changed nodes
                     └─ experimental            └─ missing status
                        confidence
                                                │
                                                ↓
                                      Change-Impact Analysis
                                                │
                                                ↓
                                      Focused Human Review
```

## Graph model

The research model uses five node types:

| Node | Purpose |
|---|---|
| `claim` | A proposition that requires assurance support. |
| `evidence` | A result, observation, test artifact, verification output, or monitoring artifact. |
| `assumption` | A condition required for a claim or evidence interpretation to remain valid. |
| `context` | Scope, configuration, system version, environment, or interpretation information. |
| `defeater` | Evidence or reasoning that challenges a claim. |

Relationships are represented with four edge types:

| Edge | Meaning |
|---|---|
| `supports` | Source contributes positive support to a target claim. |
| `depends_on` | Target validity depends on the source. |
| `contradicts` | Source provides counter-evidence against the target. |
| `qualifies` | Source constrains the scope or interpretation of the target. |

## Implemented capabilities

### 1. Claim assessment

For a selected claim, the analyzer reports whether the claim is currently supported, which support is stale, which nodes contradict it, which assumptions are unmet, and an experimental propagated confidence value.

The current confidence rule uses the minimum confidence among usable supporting evidence. It is intentionally simple and inspectable and must **not** be interpreted as a probability that a physical system is safe.

### 2. Evidence freshness

Evidence can carry `observed_at` and `valid_until` timestamps. Expired evidence remains in the graph for auditability but no longer counts as current support.

This supports experiments on calibration expiry, monitoring freshness, digital-twin state age, and configuration-sensitive verification evidence.

### 3. Change-impact analysis

When evidence, assumptions, contexts, or subclaims change, the graph identifies downstream claims reachable through support, dependency, and qualification relationships.

```text
Calibration assumption changed
          ↓
State-estimation claim
          ↓
Runtime-shield trust claim
          ↓
System-level assurance claim
```

This makes incremental review possible instead of automatically requiring complete reinspection of the whole assurance case.

### 4. Structural validation

The validator detects or surfaces:

- direct self-loops;
- cycles in support/dependency/qualification paths;
- isolated claims;
- orphan evidence;
- assumptions without recorded status;
- unusual support relationships;
- questionable context usage.

A structurally valid graph is not automatically a valid safety argument. Validation only checks graph coherence.

### 5. Assurance-health metrics

The repository computes descriptive measures such as:

- node and edge counts;
- claim/evidence/assumption/context/defeater counts;
- supported-claim count;
- contradicted-claim count;
- claims relying on stale evidence;
- claims with unmet assumptions;
- support coverage;
- stale-claim rate.

These are argument-quality indicators, not certification scores.

### 6. Provenance-preserving evidence integration

The repository now implements adapters for two external evidence classes.

#### Formal-verification manifests

`evidence_from_verification_manifest()` preserves:

- run identifier;
- timestamp;
- source commit;
- CPS domain;
- verification status and completeness;
- method configuration;
- finite horizon;
- assumptions;
- uncertainty bounds;
- result details;
- reproducibility metadata;
- source schema version.

A `VERIFIED_SAFE` source result stays explicitly tied to its model and assumptions.

#### Runtime-assurance traces

`evidence_from_runtime_trace()` summarizes:

- number of decisions;
- modifications;
- fallbacks;
- observed unsafe-state records;
- minimum safety margin;
- trace-level metadata;
- original runtime records.

The adapter creates evidence about the observed run. It does not convert a runtime trace into a universal safety claim.

### 7. Versioned assurance snapshots

`snapshot_graph()` creates a canonical graph snapshot with:

- a snapshot identifier;
- creation time;
- canonical machine-readable payload;
- SHA-256 digest.

The digest supports reproducibility and change tracking. It is not an attestation that the evidence itself is true.

### 8. Assurance graph differencing

`diff_snapshots()` reports:

- added nodes;
- removed nodes;
- changed nodes;
- added relationships;
- removed relationships.

That diff can then be combined with `affected_claims()` to decide which claims need human reassessment.

## Dynamic assurance workflow

```text
New engineering artifact
        │
        ↓
Source-specific adapter
        │
        ↓
Normalized evidence node
        │
        ↓
Updated evidence graph
        │
        ├──> structural validation
        ├──> claim reassessment
        ├──> graph-health metrics
        └──> snapshot + SHA-256 digest
                    │
                    ↓
               snapshot diff
                    │
                    ↓
             changed node IDs
                    │
                    ↓
             affected claims
                    │
                    ↓
              focused review
```

## Example

```python
from assurance_graph import (
    AssuranceEdge,
    AssuranceGraph,
    AssuranceNode,
    EdgeType,
    NodeType,
    affected_claims,
    diff_snapshots,
    evidence_from_verification_manifest,
    snapshot_graph,
)

graph = AssuranceGraph()

graph.add_node(
    AssuranceNode(
        "claim.system-envelope",
        NodeType.CLAIM,
        "The modeled CPS remains within the declared safety envelope.",
    )
)

manifest = {
    "run_id": "battery-interval-001",
    "timestamp_utc": "2026-10-01T00:00:00Z",
    "domain": "battery",
    "method": {"name": "interval"},
    "result": {"status": "VERIFIED_SAFE", "complete": True},
}

evidence = evidence_from_verification_manifest(manifest)
graph.add_node(evidence)
graph.add_edge(
    AssuranceEdge(
        evidence.id,
        "claim.system-envelope",
        EdgeType.SUPPORTS,
        "Finite-horizon formal verification evidence.",
    )
)

before = snapshot_graph(graph, snapshot_id="baseline")

graph.add_node(
    AssuranceNode(
        "assumption.disturbance-bound",
        NodeType.ASSUMPTION,
        "Runtime disturbances remain inside the modeled bound.",
        metadata={"status": "validated"},
    )
)
graph.add_edge(
    AssuranceEdge(
        "assumption.disturbance-bound",
        "claim.system-envelope",
        EdgeType.DEPENDS_ON,
    )
)

after = snapshot_graph(graph, snapshot_id="updated")
diff = diff_snapshots(before, after)

print(diff.added_nodes)
print(affected_claims(graph, "assumption.disturbance-bound"))
```

## Research questions now enabled

The v0.3 implementation supports more concrete experimental questions:

1. **Traceability** — can reviewers follow a system-level claim back to its assumptions and source artifacts?
2. **Freshness** — can stale support be detected before reviewers rely on it?
3. **Change impact** — can localized changes identify the correct subset of downstream claims?
4. **Contradiction handling** — can negative runtime evidence remain visible beside positive formal evidence?
5. **Argument quality** — can structural metrics reveal weak or circular assurance arguments?
6. **Provenance retention** — how much source information survives normalization?
7. **Assurance evolution** — how often and why do claim-support states change across graph snapshots?
8. **Review workload** — can graph differencing reduce unnecessary full-case review without missing invalidated claims?

## Experimental program

Planned controlled experiments include:

- evidence-expiry scenarios;
- assumption-violation propagation;
- contradictory runtime evidence;
- deliberately defective assurance graphs;
- cross-tool evidence normalization;
- snapshot-based assurance evolution;
- incremental review precision/recall;
- reviewer studies comparing document-only and graph-assisted assurance.

## Candidate evaluation metrics

Potential empirical measures include:

- unsupported-claim detection precision/recall;
- stale-evidence detection accuracy;
- affected-claim precision/recall;
- contradiction detection rate;
- provenance-field retention rate;
- changed-node detection accuracy;
- evidence-to-claim trace length;
- support coverage;
- stale-claim rate;
- number of claims requiring review per update;
- unnecessary full-case reviews avoided;
- reviewer time and agreement.

## Quick start

```bash
python -m pip install -e ".[dev]"
pytest -q
python examples/build_demo_case.py
```

## Repository structure

```text
assurance-case-evidence-graph-cps/
├── .github/
│   └── workflows/
├── docs/
│   ├── research-protocol.md
│   ├── detailed-research-framework.md
│   └── evidence-integration-and-evolution.md
├── examples/
│   └── build_demo_case.py
├── src/
│   └── assurance_graph/
│       ├── __init__.py
│       ├── model.py
│       ├── analysis.py
│       ├── validation.py
│       ├── metrics.py
│       ├── integrations.py
│       ├── snapshots.py
│       └── io.py
├── tests/
│   ├── test_assurance_graph.py
│   ├── test_validation_metrics.py
│   └── test_integrations_snapshots.py
├── pyproject.toml
└── README.md
```

## Research documents

- [`docs/research-protocol.md`](docs/research-protocol.md) defines the initial experimental protocol.
- [`docs/detailed-research-framework.md`](docs/detailed-research-framework.md) defines the expanded research questions, semantics, validation rules, evidence lifecycle, evaluation plan, threats to validity, reproducibility requirements, and roadmap.
- [`docs/evidence-integration-and-evolution.md`](docs/evidence-integration-and-evolution.md) defines provenance-preserving adapters, graph snapshots, differencing, and the incremental review workflow.

## Research boundary

This repository is a research prototype. It does **not** certify a physical system, replace independent safety/security review, or convert incomplete evidence into a safety guarantee.

The project deliberately preserves these distinctions:

- graph support is not physical-system safety;
- confidence is not a calibrated safety probability;
- formal verification remains conditional on its model and assumptions;
- runtime traces remain conditional on a particular execution context;
- a snapshot digest proves payload consistency, not evidence truth;
- absence of detected contradiction is not proof that no contradiction exists;
- automated impact analysis supports but does not replace accountable human review.

## Roadmap

### Phase 1 — Core graph mechanics

Typed graph model, serialization, claim assessment, freshness, contradiction handling, impact analysis, validation, and metrics.

### Phase 2 — Evidence integration

Formal-verification and runtime-assurance adapters are now implemented. Next: digital-twin, CI/test, calibration, model-version, and human-review adapters.

### Phase 3 — Dynamic assurance

Snapshotting and differencing are now implemented. Next: evidence supersession, assumption history, configuration-aware invalidation, graph-version lineage, and incremental re-evaluation.

### Phase 4 — Empirical evaluation

Benchmark suites for provenance retention, affected-claim detection, graph-defect detection, and assurance evolution.

### Phase 5 — Human-centered assurance

Graph visualization, reviewer studies, explanation usefulness, review-effort measurement, disagreement analysis, and evidence-to-decision traceability.

## License

MIT
