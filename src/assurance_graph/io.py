from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path

from .model import AssuranceEdge, AssuranceGraph, AssuranceNode, EdgeType, NodeType


def graph_to_dict(graph: AssuranceGraph) -> dict[str, object]:
    return {
        "schema_version": "0.1.0",
        "nodes": [
            {
                "id": node.id,
                "kind": node.kind.value,
                "statement": node.statement,
                "confidence": node.confidence,
                "observed_at": node.observed_at.isoformat() if node.observed_at else None,
                "valid_until": node.valid_until.isoformat() if node.valid_until else None,
                "metadata": node.metadata,
            }
            for node in graph.nodes.values()
        ],
        "edges": [
            {
                "source": edge.source,
                "target": edge.target,
                "kind": edge.kind.value,
                "rationale": edge.rationale,
            }
            for edge in graph.edges
        ],
    }


def graph_from_dict(payload: dict[str, object]) -> AssuranceGraph:
    graph = AssuranceGraph()
    for raw in payload.get("nodes", []):
        raw = dict(raw)
        graph.add_node(
            AssuranceNode(
                id=raw["id"],
                kind=NodeType(raw["kind"]),
                statement=raw["statement"],
                confidence=raw.get("confidence"),
                observed_at=datetime.fromisoformat(raw["observed_at"]) if raw.get("observed_at") else None,
                valid_until=datetime.fromisoformat(raw["valid_until"]) if raw.get("valid_until") else None,
                metadata=dict(raw.get("metadata") or {}),
            )
        )
    for raw in payload.get("edges", []):
        raw = dict(raw)
        graph.add_edge(
            AssuranceEdge(
                source=raw["source"],
                target=raw["target"],
                kind=EdgeType(raw["kind"]),
                rationale=raw.get("rationale", ""),
            )
        )
    return graph


def save_graph(graph: AssuranceGraph, path: str | Path) -> None:
    Path(path).write_text(json.dumps(graph_to_dict(graph), indent=2) + "\n", encoding="utf-8")


def load_graph(path: str | Path) -> AssuranceGraph:
    return graph_from_dict(json.loads(Path(path).read_text(encoding="utf-8")))
