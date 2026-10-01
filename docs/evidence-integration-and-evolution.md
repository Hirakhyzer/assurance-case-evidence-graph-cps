# Evidence Integration and Assurance Evolution

## Purpose

A continuously maintained assurance case needs more than a graph data structure. It needs a disciplined way to ingest evidence from heterogeneous engineering tools, preserve provenance, compare assurance states over time, and identify exactly what changed.

This document defines the repository's first integration and evolution layer.

## 1. Provenance-preserving normalization

The project now includes adapters for two high-value evidence sources:

- formal-verification evidence manifests;
- runtime-assurance decision traces.

The adapters convert source artifacts into `evidence` nodes while retaining the original source-specific fields in metadata.

Normalization must not erase semantic distinctions. A formal verification result is evidence about a mathematical model under explicit assumptions; a runtime trace is evidence about observed shield behavior during a particular execution. They should not be treated as equivalent merely because both become evidence nodes.

## 2. Formal-verification manifest adapter

`evidence_from_verification_manifest()` records:

- source run identifier;
- timestamp;
- repository commit when available;
- CPS domain;
- verification status;
- completeness;
- method and method configuration;
- finite horizon;
- assumptions;
- uncertainty description;
- result details;
- reproducibility metadata;
- source schema version.

The adapter does not reinterpret `VERIFIED_SAFE` as real-world certification. It preserves the source result so downstream assurance claims can remain conditional on the original model and assumptions.

## 3. Runtime-assurance trace adapter

`evidence_from_runtime_trace()` summarizes:

- number of decision records;
- number of modifications;
- number of fallbacks;
- number of observed unsafe-state records;
- minimum observed safety margin;
- trace-level metadata;
- original runtime records.

This creates a compact evidence node while retaining the underlying records for audit and later re-analysis.

A runtime trace can support a claim such as "the safety shield intervened as designed in this experiment." It should not automatically support a broader claim such as "the physical system is safe."

## 4. Versioned assurance snapshots

The repository now supports immutable logical snapshots of an assurance graph.

Each `GraphSnapshot` records:

- a researcher-defined snapshot identifier;
- creation timestamp;
- a canonical machine-readable graph payload;
- a SHA-256 digest of that canonical payload.

The digest is intended for reproducibility and change tracking. It is not a cryptographic attestation of evidence truth or source authenticity.

## 5. Snapshot differencing

`diff_snapshots()` identifies:

- added nodes;
- removed nodes;
- changed nodes;
- added typed relationships;
- removed typed relationships.

This creates a foundation for incremental assurance review.

Example:

```text
Snapshot t0
  verification evidence -> system claim
  disturbance assumption -> system claim

                |
                | runtime evidence arrives
                v

Snapshot t1
  verification evidence -> system claim
  disturbance assumption -> system claim
  runtime trace evidence -> shield-behavior claim
  shield-behavior claim -> system claim
```

The diff exposes exactly which assurance elements were added or modified.

## 6. Incremental review workflow

A target workflow is:

```text
New engineering artifact
        |
        v
Source-specific adapter
        |
        v
Normalized evidence node
        |
        v
Updated assurance graph
        |
        +--> snapshot + digest
        |
        +--> snapshot diff
        |
        +--> changed node ids
        |
        +--> affected-claim traversal
        |
        v
Focused human review
```

This combines graph evolution with the repository's existing `affected_claims()` analysis.

## 7. Research questions enabled by this layer

The integration and snapshot mechanisms enable more concrete experiments:

### RQ-I1 — Provenance retention

How much source information is preserved after normalization, and which fields are lost or transformed?

### RQ-I2 — Incremental review precision

When one artifact changes, can snapshot differencing plus change-impact analysis identify the correct subset of claims for reassessment?

### RQ-I3 — Cross-source contradiction

Can a runtime trace introduce evidence that challenges a claim previously supported by formal verification without deleting or overwriting either source?

### RQ-I4 — Assurance evolution

How often do claims change support status across a sequence of software, model, or evidence updates?

### RQ-I5 — Review workload

Does graph differencing reduce reviewer workload compared with full assurance-case reinspection, while preserving detection of invalidated claims?

## 8. Evaluation measures

Candidate measures include:

- provenance-field retention rate;
- changed-node detection precision/recall;
- affected-claim precision/recall;
- number of claims requiring review per update;
- false-negative affected claims;
- evidence normalization latency;
- assurance graph growth rate;
- number of superseded evidence nodes retained for audit;
- contradiction visibility after source updates;
- reviewer time per graph change.

## 9. Next integration targets

Priority adapters after the current two are:

1. software-quality and CPS digital-twin state records;
2. CI/test result bundles;
3. calibration and sensor-health evidence;
4. model/version provenance;
5. human review dispositions;
6. structured incident and anomaly evidence.

## 10. Integrity boundary

The new snapshot and adapter features improve traceability and reproducibility, but they do not establish truth by themselves.

A valid digest proves only that the same canonical graph payload produces the same digest. A normalized evidence node remains only as trustworthy as its source artifact, provenance, assumptions, and interpretation.
