from __future__ import annotations

from datetime import datetime
from typing import Any, Iterable

from .model import AssuranceNode, NodeType


def _parse_time(value: str | None) -> datetime | None:
    return datetime.fromisoformat(value.replace("Z", "+00:00")) if value else None


def evidence_from_verification_manifest(
    manifest: dict[str, Any],
    *,
    node_id: str | None = None,
) -> AssuranceNode:
    """Normalize a formal-verification evidence manifest into an evidence node.

    The source payload is retained in metadata so normalization does not erase
    method, horizon, assumptions, uncertainty, completeness, or provenance.
    """
    result = dict(manifest.get("result") or {})
    method = dict(manifest.get("method") or {})
    domain = str(manifest.get("domain") or "unknown-domain")
    run_id = str(manifest.get("run_id") or "unknown-run")
    status = str(result.get("status") or "UNKNOWN")
    complete = bool(result.get("complete", False))

    return AssuranceNode(
        id=node_id or f"verification:{run_id}",
        kind=NodeType.EVIDENCE,
        statement=(
            f"Formal verification run {run_id} for {domain} reported "
            f"{status} using {method.get('name', 'unspecified-method')}."
        ),
        observed_at=_parse_time(manifest.get("timestamp_utc")),
        metadata={
            "source_type": "formal_verification_manifest",
            "source_run_id": run_id,
            "domain": domain,
            "verification_status": status,
            "complete": complete,
            "git_commit": manifest.get("git_commit"),
            "method": method,
            "horizon": manifest.get("horizon"),
            "assumptions": manifest.get("assumptions"),
            "uncertainty": manifest.get("uncertainty"),
            "result": result,
            "reproducibility": manifest.get("reproducibility"),
            "schema_version": manifest.get("schema_version"),
        },
    )


def evidence_from_runtime_trace(
    trace: dict[str, Any] | Iterable[dict[str, Any]],
    *,
    node_id: str = "runtime:trace",
    source_id: str | None = None,
) -> AssuranceNode:
    """Summarize a runtime-assurance trace without discarding raw provenance.

    The adapter intentionally creates evidence about observed shield behavior,
    not a claim that the underlying physical system is safe.
    """
    if isinstance(trace, dict):
        records = list(trace.get("records") or trace.get("trace") or [])
        metadata_root = {k: v for k, v in trace.items() if k not in {"records", "trace"}}
    else:
        records = list(trace)
        metadata_root = {}

    statuses = [str(row.get("status", "UNKNOWN")) for row in records]
    fallback_count = sum(status == "FALLBACK" for status in statuses)
    modification_count = sum(status == "MODIFY" for status in statuses)
    unsafe_count = sum(not bool(row.get("safe", True)) for row in records)
    min_margin_values = [
        float(row["margin"])
        for row in records
        if row.get("margin") is not None
    ]
    min_margin = min(min_margin_values) if min_margin_values else None

    statement = (
        f"Runtime-assurance trace contains {len(records)} decisions, "
        f"{modification_count} modifications, {fallback_count} fallbacks, "
        f"and {unsafe_count} observed unsafe-state records."
    )

    return AssuranceNode(
        id=node_id,
        kind=NodeType.EVIDENCE,
        statement=statement,
        metadata={
            "source_type": "runtime_assurance_trace",
            "source_id": source_id,
            "record_count": len(records),
            "modification_count": modification_count,
            "fallback_count": fallback_count,
            "unsafe_state_count": unsafe_count,
            "minimum_margin": min_margin,
            "trace_metadata": metadata_root,
            "raw_records": records,
        },
    )
