# Assurance Evidence Graph Research Protocol

## Research objective

This project studies whether explicit, machine-readable evidence graphs can make CPS assurance easier to update, inspect, and challenge when evidence changes over time.

The central hypothesis is that assurance quality depends not only on the existence of evidence, but on traceability between claims, assumptions, contexts, defeaters, and time-sensitive evidence artifacts.

## Initial research questions

1. Can unsupported or weakly supported assurance claims be detected automatically?
2. Can stale evidence be surfaced before reviewers rely on outdated assurance arguments?
3. Can assumption changes be propagated to the claims they affect?
4. Can contradictory runtime evidence be surfaced without silently overwriting prior formal evidence?
5. Can assurance review effort be reduced while preserving or improving defect discovery in the argument?

## Graph semantics

The initial graph uses five node types:

- `claim` — a statement requiring assurance support;
- `evidence` — an artifact or observation offered in support;
- `assumption` — a condition on which a claim or evidence interpretation depends;
- `context` — scope, model, environment, or interpretation information;
- `defeater` — evidence or reasoning that challenges a claim.

Edges represent `supports`, `depends_on`, `contradicts`, and `qualifies` relationships.

## Evidence freshness

Evidence may contain `observed_at` and `valid_until` timestamps. Expiry is treated as an assurance concern rather than deletion: stale evidence remains in the graph for auditability but no longer counts as current support in the default claim assessment.

This is especially important for runtime monitoring, digital-twin state, calibration evidence, and environment-dependent validation.

## Confidence boundary

The current confidence propagation rule uses the minimum confidence among usable supporting evidence. This is deliberately simple and interpretable.

It is **not** a probability that the system is safe. Confidence values are experimental metadata for comparing evidence-handling strategies. Future work should compare alternative aggregation rules and assess whether numerical confidence helps or misleads reviewers.

## Change-impact analysis

When evidence or assumptions change, the graph traverses support, dependency, and qualification relationships to identify downstream claims requiring review.

A key evaluation target is review prioritization: whether impact analysis can reduce the number of claims a human must inspect without omitting claims actually affected by the change.

## Planned experiments

### E1 — Unsupported claim detection

Construct assurance cases containing deliberately unsupported claims and measure detection precision and recall.

### E2 — Evidence ageing

Vary evidence expiry times and measure whether stale support is surfaced before incorrect assurance conclusions are accepted.

### E3 — Assumption violation propagation

Change selected assumptions from validated to unvalidated or violated and evaluate whether all dependent claims are identified.

### E4 — Contradictory evidence

Inject runtime evidence that contradicts a previously supported claim and measure whether the contradiction is visible and traceable to its source.

### E5 — Human review study

Compare document-only assurance review against graph-assisted review using time-to-detection, missed issues, unnecessary inspections, and reviewer confidence as outcomes.

## Validity threats

Synthetic assurance cases can be biased toward the graph model. Results should therefore be separated into synthetic benchmark findings and findings from externally defined assurance cases. Confidence propagation and freshness policies should be frozen before held-out evaluation.

## Integration roadmap

The intended next integrations are:

- import of formal-verification evidence manifests;
- import of runtime-assurance audit traces;
- digital-twin evidence freshness updates;
- evidence hashing and provenance metadata;
- structured assurance-case export;
- benchmark suites for change-impact and contradiction detection.
