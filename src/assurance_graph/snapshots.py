from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from typing import Iterable

from .io import graph_to_dict
from .model import AssuranceGraph


@dataclass(frozen=True)
class GraphSnapshot:
    snapshot_id: str
    created_at: str
    digest_sha256: str
    payload: dict[str, object]


@dataclass(frozen=True)
class GraphDiff:
    added_nodes: tuple[str, ...]
    removed_nodes: tuple[str, ...]
    changed_nodes: tuple[str, ...]
    added_edges: tuple[tuple[str, str, str], ...]
    removed_edges: tuple[tuple[str, str, str], ...]


def _canonical_payload(graph: AssuranceGraph) -> dict[str, object]:
    payload = graph_to_dict(graph)
    payload["nodes"] = sorted(payload["nodes"], key=lambda item: item["id"])
    payload["edges"] = sorted(
        payload["edges"],
        key=lambda item: (item["source"], item["target"], item["kind"], item.get("rationale", "")),
    )
    return payload


def _digest(payload: dict[str, object]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def snapshot_graph(
    graph: AssuranceGraph,
    *,
    snapshot_id: str,
    created_at: datetime | None = None,
) -> GraphSnapshot:
    if not snapshot_id.strip():
        raise ValueError("snapshot_id must not be empty")
    payload = _canonical_payload(graph)
    timestamp = (created_at or datetime.now(timezone.utc)).isoformat()
    return GraphSnapshot(snapshot_id, timestamp, _digest(payload), payload)


def _nodes_by_id(payload: dict[str, object]) -> dict[str, dict[str, object]]:
    return {str(node["id"]): dict(node) for node in payload.get("nodes", [])}


def _edge_keys(payload: dict[str, object]) -> set[tuple[str, str, str]]:
    return {
        (str(edge["source"]), str(edge["target"]), str(edge["kind"]))
        for edge in payload.get("edges", [])
    }


def diff_snapshots(before: GraphSnapshot, after: GraphSnapshot) -> GraphDiff:
    before_nodes = _nodes_by_id(before.payload)
    after_nodes = _nodes_by_id(after.payload)

    before_ids = set(before_nodes)
    after_ids = set(after_nodes)

    common = before_ids & after_ids
    changed = tuple(
        sorted(node_id for node_id in common if before_nodes[node_id] != after_nodes[node_id])
    )

    before_edges = _edge_keys(before.payload)
    after_edges = _edge_keys(after.payload)

    return GraphDiff(
        added_nodes=tuple(sorted(after_ids - before_ids)),
        removed_nodes=tuple(sorted(before_ids - after_ids)),
        changed_nodes=changed,
        added_edges=tuple(sorted(after_edges - before_edges)),
        removed_edges=tuple(sorted(before_edges - after_edges)),
    )


def changed_node_ids(diff: GraphDiff) -> tuple[str, ...]:
    """Return all node ids directly changed between snapshots."""
    return tuple(sorted(set(diff.added_nodes + diff.removed_nodes + diff.changed_nodes)))
