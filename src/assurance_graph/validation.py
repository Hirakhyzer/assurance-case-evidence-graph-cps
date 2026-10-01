from __future__ import annotations

from dataclasses import dataclass

from .model import AssuranceGraph, EdgeType, NodeType


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    message: str
    node_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class GraphValidationReport:
    valid: bool
    errors: tuple[ValidationIssue, ...]
    warnings: tuple[ValidationIssue, ...]


def _find_dependency_cycles(graph: AssuranceGraph) -> tuple[tuple[str, ...], ...]:
    adjacency: dict[str, list[str]] = {node_id: [] for node_id in graph.nodes}
    for edge in graph.edges:
        if edge.kind in {EdgeType.SUPPORTS, EdgeType.DEPENDS_ON, EdgeType.QUALIFIES}:
            adjacency[edge.source].append(edge.target)

    cycles: set[tuple[str, ...]] = set()
    visiting: list[str] = []
    active: set[str] = set()
    visited: set[str] = set()

    def visit(node_id: str) -> None:
        if node_id in visited:
            return
        if node_id in active:
            try:
                start = visiting.index(node_id)
            except ValueError:
                return
            cycle = tuple(visiting[start:] + [node_id])
            cycles.add(cycle)
            return

        active.add(node_id)
        visiting.append(node_id)
        for target in adjacency[node_id]:
            visit(target)
        visiting.pop()
        active.remove(node_id)
        visited.add(node_id)

    for node_id in graph.nodes:
        visit(node_id)

    return tuple(sorted(cycles))


def validate_graph(graph: AssuranceGraph) -> GraphValidationReport:
    """Check structural and semantic integrity of an assurance graph.

    The validator intentionally focuses on graph quality rather than declaring a
    system safe. A valid graph can still contain unsupported or contradicted
    claims; validation only ensures that the assurance argument is structurally
    inspectable and internally coherent enough for analysis.
    """
    errors: list[ValidationIssue] = []
    warnings: list[ValidationIssue] = []

    for edge in graph.edges:
        source = graph.nodes[edge.source]
        target = graph.nodes[edge.target]

        if edge.source == edge.target:
            errors.append(
                ValidationIssue(
                    "self_loop",
                    f"node {edge.source} cannot directly relate to itself",
                    (edge.source,),
                )
            )

        if edge.kind == EdgeType.SUPPORTS and target.kind != NodeType.CLAIM:
            warnings.append(
                ValidationIssue(
                    "support_target_not_claim",
                    f"support edge {edge.source}->{edge.target} does not target a claim",
                    (edge.source, edge.target),
                )
            )

        if edge.kind == EdgeType.CONTRADICTS and source.kind == NodeType.CONTEXT:
            warnings.append(
                ValidationIssue(
                    "context_contradiction",
                    f"context node {edge.source} is used as contradictory evidence",
                    (edge.source, edge.target),
                )
            )

    for node in graph.nodes.values():
        incoming = graph.incoming(node.id)
        outgoing = graph.outgoing(node.id)

        if node.kind == NodeType.CLAIM and not incoming:
            warnings.append(
                ValidationIssue(
                    "isolated_claim",
                    f"claim {node.id} has no incoming assurance relationships",
                    (node.id,),
                )
            )

        if node.kind == NodeType.EVIDENCE and not outgoing:
            warnings.append(
                ValidationIssue(
                    "orphan_evidence",
                    f"evidence {node.id} is not connected to any assurance element",
                    (node.id,),
                )
            )

        if node.kind == NodeType.ASSUMPTION and "status" not in node.metadata:
            warnings.append(
                ValidationIssue(
                    "assumption_without_status",
                    f"assumption {node.id} does not record a validation status",
                    (node.id,),
                )
            )

    for cycle in _find_dependency_cycles(graph):
        errors.append(
            ValidationIssue(
                "dependency_cycle",
                "assurance dependency cycle detected: " + " -> ".join(cycle),
                cycle,
            )
        )

    return GraphValidationReport(
        valid=not errors,
        errors=tuple(errors),
        warnings=tuple(warnings),
    )
