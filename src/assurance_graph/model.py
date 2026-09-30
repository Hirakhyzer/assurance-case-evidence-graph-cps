from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class NodeType(str, Enum):
    CLAIM = "claim"
    EVIDENCE = "evidence"
    ASSUMPTION = "assumption"
    CONTEXT = "context"
    DEFEATER = "defeater"


class EdgeType(str, Enum):
    SUPPORTS = "supports"
    DEPENDS_ON = "depends_on"
    CONTRADICTS = "contradicts"
    QUALIFIES = "qualifies"


@dataclass(frozen=True)
class AssuranceNode:
    id: str
    kind: NodeType
    statement: str
    confidence: float | None = None
    observed_at: datetime | None = None
    valid_until: datetime | None = None
    metadata: dict[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError("node id must not be empty")
        if not self.statement.strip():
            raise ValueError("node statement must not be empty")
        if self.confidence is not None and not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
        if self.valid_until and self.observed_at and self.valid_until < self.observed_at:
            raise ValueError("valid_until cannot precede observed_at")


@dataclass(frozen=True)
class AssuranceEdge:
    source: str
    target: str
    kind: EdgeType
    rationale: str = ""


@dataclass
class AssuranceGraph:
    nodes: dict[str, AssuranceNode] = field(default_factory=dict)
    edges: list[AssuranceEdge] = field(default_factory=list)

    def add_node(self, node: AssuranceNode) -> None:
        if node.id in self.nodes:
            raise ValueError(f"duplicate node id: {node.id}")
        self.nodes[node.id] = node

    def add_edge(self, edge: AssuranceEdge) -> None:
        if edge.source not in self.nodes or edge.target not in self.nodes:
            raise ValueError("edge endpoints must exist before adding the edge")
        self.edges.append(edge)

    def incoming(self, node_id: str, kind: EdgeType | None = None) -> tuple[AssuranceEdge, ...]:
        return tuple(
            edge for edge in self.edges
            if edge.target == node_id and (kind is None or edge.kind == kind)
        )

    def outgoing(self, node_id: str, kind: EdgeType | None = None) -> tuple[AssuranceEdge, ...]:
        return tuple(
            edge for edge in self.edges
            if edge.source == node_id and (kind is None or edge.kind == kind)
        )
