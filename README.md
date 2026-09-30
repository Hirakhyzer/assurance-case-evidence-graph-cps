# Assurance Case Evidence Graph CPS

**Machine-readable assurance cases and evidence graphs for continuously updated safety and security assurance in cyber-physical systems.**

This repository studies how safety and security claims for cyber-physical systems can remain traceable as verification results, runtime evidence, digital-twin state, assumptions, and operating conditions change over time.

## Core research question

> Can continuously updated evidence graphs improve the traceability, consistency, and trustworthiness of CPS assurance as evidence and assumptions evolve?

## Research idea

Traditional assurance cases are often reviewed as documents. This project represents the assurance argument as a graph whose nodes include claims, evidence, assumptions, contexts, and defeaters, with typed relationships that make support and dependency explicit.

```text
Digital Twin Evidence ───────┐
Formal Verification ────────┤
Runtime Assurance Logs ─────┤
Test / Validation Evidence ─┼──> Evidence Graph ──> Assurance Claims
Operational Monitoring ─────┤                         │
Assumptions / Context ──────┘                         ├─ supported
                                                      ├─ weakened
                                                      ├─ contradicted
                                                      └─ stale
```

## Initial research capabilities

- typed assurance nodes for claims, evidence, assumptions, contexts, and defeaters;
- explicit support, dependency, contradiction, and qualification edges;
- evidence freshness and expiry analysis;
- unsupported-claim detection;
- assumption-change impact analysis;
- contradiction surfacing;
- confidence propagation as an experimental research mechanism;
- machine-readable JSON assurance-case format;
- reproducible tests and example assurance graphs.

## Research boundary

This repository is a research prototype. It does not certify a physical system, replace independent safety review, or convert incomplete evidence into a safety guarantee. Any confidence score is an experimental prioritization mechanism and must not be interpreted as a probability of real-world safety.

## Planned integrations

The graph is designed to ingest evidence artifacts from related CPS research workflows, including:

- formal verification manifests;
- runtime-assurance decision traces;
- digital-twin state and uncertainty records;
- benchmark outcomes;
- tests and validation artifacts;
- human review decisions.

## Quick start

```bash
python -m pip install -e ".[dev]"
pytest -q
python examples/build_demo_case.py
```

## License

MIT
