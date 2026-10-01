# Assurance Case Evidence Graph CPS

**Machine-readable assurance cases and evidence graphs for continuously updated safety and security assurance in cyber-physical systems.**

This repository studies how CPS safety and security arguments can remain traceable as verification results, runtime evidence, digital-twin state, assumptions, software versions, and operating conditions change over time.

The project treats an assurance case as a **living evidence graph** rather than a static document. Claims remain connected to the evidence, assumptions, contexts, and defeaters on which they depend, enabling automated freshness checks, contradiction surfacing, change-impact analysis, graph validation, and descriptive assurance-health metrics.

## Core research question

> **Can continuously updated evidence graphs improve the traceability, consistency, maintainability, and reviewability of CPS assurance as evidence and assumptions evolve?**

## Research objectives

The project investigates whether machine-readable assurance graphs can:

- expose unsupported or weakly supported claims;
- identify evidence that has become stale or expired;
- preserve contradictory evidence instead of silently replacing earlier results;
- propagate assumption changes to downstream claims;
- identify circular or structurally weak assurance arguments;
- reduce unnecessary full-case review after localized system changes;
- preserve source provenance across formal verification, runtime assurance, digital twins, tests, and monitoring;
- support reproducible human-centered assurance experiments.

## Architecture

```text
Formal Verification Manifest ─┐
Runtime Safety-Shield Trace ──┤
Digital Twin State ───────────┤
Test / CI Evidence ───────────┼──> Evidence Normalization
Operational Monitoring ───────┤             │
Human Review Decisions ───────┘             ↓
                                  Assurance Evidence Graph
                                             │
                     ┌───────────────────────┼───────────────────────┐
                     ↓                       ↓                       ↓
              Claim Assessment       Structural Validation    Change Impact
                     │                       │                       │
                     ├─ stale support        ├─ cycles              ├─ assumptions
                     ├─ contradictions       ├─ orphan evidence     ├─ evidence
                     ├─ unmet assumptions    ├─ isolated claims     └─ contexts
                     └─ experimental         └─ missing status
                        confidence
                                             │
                                             ↓
                                   Human Assurance Review
```

## Graph model

The v0.2 research model uses five node types:

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
| `qualifies` | Source limits or constrains the interpretation of the target. |

## Implemented capabilities

### Claim assessment

For a selected claim, the analyzer reports:

- whether the claim is currently supported;
- stale supporting evidence;
- explicit contradictions;
- unmet assumptions;
- an experimental propagated confidence value.

The default confidence rule uses the minimum confidence among usable supporting evidence. It is deliberately simple and inspectable and must **not** be interpreted as a probability that a physical system is safe.

### Evidence freshness

Evidence nodes can carry `observed_at` and `valid_until` timestamps. Expired evidence remains in the graph for auditability but no longer counts as current support.

This enables research on evidence ageing, calibration expiry, digital-twin freshness, monitoring validity windows, and configuration-sensitive verification evidence.

### Change-impact analysis

When an evidence item, assumption, context, or supporting claim changes, the graph can identify downstream claims reachable through support, dependency, and qualification relationships.

```text
Assumption changed
      ↓
State-estimation claim
      ↓
Runtime-shield trust claim
      ↓
System-level safety claim
```

This supports incremental assurance review instead of automatically requiring a complete review of the entire case after every change.

### Structural validation

The validator now detects or surfaces:

- direct self-loops;
- cycles in assurance dependency paths;
- isolated claims;
- orphan evidence;
- assumptions without recorded status;
- unusual support relationships;
- questionable use of context as contradictory evidence.

A structurally valid graph is **not** automatically a valid safety argument. Validation only checks whether the graph is coherent enough for further assurance analysis.

### Assurance health metrics

The repository now computes descriptive graph-health measures including:

- total nodes and edges;
- counts of claims, evidence, assumptions, contexts, and defeaters;
- number of supported claims;
- number of contradicted claims;
- number of claims with stale evidence;
- number of claims with unmet assumptions;
- support coverage;
- stale-claim rate.

These are argument-quality indicators, not certification scores.

### Machine-readable persistence

Assurance cases can be serialized to and restored from JSON while preserving node type, statement, confidence, timestamps, metadata, edge type, and rationale.

## Example usage

```python
from datetime import datetime, timedelta, timezone

from assurance_graph import (
    AssuranceEdge,
    AssuranceGraph,
    AssuranceNode,
    EdgeType,
    NodeType,
    assess_claim,
    summarize_assurance_graph,
    validate_graph,
)

now = datetime.now(timezone.utc)
graph = AssuranceGraph()

graph.add_node(
    AssuranceNode(
        "claim.safe",
        NodeType.CLAIM,
        "The modeled CPS remains within its declared safety envelope.",
    )
)
graph.add_node(
    AssuranceNode(
        "evidence.verification",
        NodeType.EVIDENCE,
        "Finite-horizon reachability analysis reports VERIFIED_SAFE.",
        confidence=0.95,
        observed_at=now,
        valid_until=now + timedelta(days=7),
        metadata={"source": "formal-verification-manifest"},
    )
)
graph.add_node(
    AssuranceNode(
        "assumption.bounds",
        NodeType.ASSUMPTION,
        "Runtime disturbances remain within the modeled uncertainty bounds.",
        metadata={"status": "validated"},
    )
)

graph.add_edge(
    AssuranceEdge(
        "evidence.verification",
        "claim.safe",
        EdgeType.SUPPORTS,
        "Formal verification provides bounded-model evidence.",
    )
)
graph.add_edge(
    AssuranceEdge(
        "assumption.bounds",
        "claim.safe",
        EdgeType.DEPENDS_ON,
        "The verification result is conditional on this uncertainty bound.",
    )
)

assessment = assess_claim(graph, "claim.safe", now=now)
validation = validate_graph(graph)
metrics = summarize_assurance_graph(graph, now=now)

print(assessment)
print(validation.valid)
print(metrics.to_dict())
```

## Planned evidence integrations

The graph is designed to ingest artifacts from related CPS workflows while preserving source semantics and provenance:

| Source | Candidate evidence |
|---|---|
| Formal verification | verification status, horizon, assumptions, uncertainty bounds, witness/intersection metadata |
| Runtime assurance | accepted/modified/fallback decisions, predicted reachable sets, margins, intervention reasons |
| Digital twins | state estimates, uncertainty, freshness, model-version metadata, drift indicators |
| Testing / CI | test outcomes, coverage, regression evidence, configuration identity |
| Operational monitoring | anomalies, calibration state, observed bounds, incident indicators |
| Human review | accepted defeaters, review rationale, assumption validation, disposition decisions |

The next engineering stage is to implement provenance-preserving adapters for these evidence sources.

## Experimental program

The detailed research framework defines several controlled experiments:

1. **Freshness degradation** — expire selected evidence and measure whether invalidated claims are detected.
2. **Assumption violation** — change a validated assumption to violated and compare automated affected-claim results with a hand-labeled reference set.
3. **Contradictory runtime evidence** — add a defeater after prior positive evidence and test whether positive support is prevented from masking the contradiction.
4. **Graph defects** — inject cycles, orphan evidence, isolated claims, and missing assumption status and measure validator performance.
5. **Cross-tool integration** — ingest formal-verification and runtime-assurance artifacts and evaluate provenance retention and claim traceability.
6. **Human review study** — compare document-only review with graph-assisted review using review time, missed issues, unnecessary inspections, and agreement as outcomes.

## Candidate evaluation metrics

Research evaluation may include:

- unsupported-claim detection precision and recall;
- stale-evidence detection accuracy;
- affected-claim identification precision and recall;
- contradiction detection rate;
- evidence-to-claim trace length;
- proportion of assumptions with explicit status;
- support coverage;
- stale-claim rate;
- reviewer time to identify invalidated claims;
- reviewer agreement;
- unnecessary full-case reviews avoided by incremental impact analysis.

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
│   └── detailed-research-framework.md
├── examples/
│   └── build_demo_case.py
├── src/
│   └── assurance_graph/
│       ├── __init__.py
│       ├── model.py
│       ├── analysis.py
│       ├── validation.py
│       ├── metrics.py
│       └── io.py
├── tests/
│   ├── test_assurance_graph.py
│   └── test_validation_metrics.py
├── pyproject.toml
└── README.md
```

## Research documents

- [`docs/research-protocol.md`](docs/research-protocol.md) defines the initial experimental protocol.
- [`docs/detailed-research-framework.md`](docs/detailed-research-framework.md) provides the expanded research questions, semantics, validation rules, evidence lifecycle, integration architecture, evaluation plan, threats to validity, reproducibility requirements, and roadmap.

## Research boundary

This repository is a research prototype. It does **not** certify a physical system, replace independent safety/security review, or convert incomplete evidence into a safety guarantee.

The project deliberately preserves these distinctions:

- graph support is not physical-system safety;
- confidence is not a calibrated safety probability;
- formal verification results remain conditional on their models and assumptions;
- runtime observations remain conditional on their operating context;
- absence of detected contradiction is not proof that no contradiction exists;
- automated impact analysis supports but does not replace accountable human review.

## Roadmap

### Phase 1 — Core graph mechanics

Typed graph model, serialization, claim assessment, evidence freshness, contradiction handling, impact analysis, structural validation, and assurance-health metrics.

### Phase 2 — Evidence ingestion

Formal-verification manifest adapters, runtime-assurance trace adapters, digital-twin state adapters, CI/test evidence adapters, and provenance metadata.

### Phase 3 — Dynamic assurance

Evidence supersession, graph snapshots, assumption history, diff-based review, configuration-aware evidence invalidation, and incremental re-evaluation.

### Phase 4 — Human-centered assurance

Graph visualization, reviewer studies, explanation usefulness, review-effort measurement, disagreement analysis, and evidence-to-decision traceability.

## License

MIT
