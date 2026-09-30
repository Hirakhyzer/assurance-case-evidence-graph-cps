from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from .model import AssuranceGraph, EdgeType, NodeType


@dataclass(frozen=True)
class ClaimAssessment:
    claim_id: str
    supported: bool
    stale_evidence: tuple[str, ...]
    contradicted_by: tuple[str, ...]
    unmet_assumptions: tuple[str, ...]
    propagated_confidence: float | None


def _is_stale(valid_until: datetime | None, now: datetime) -> bool:
    if valid_until is None:
        return False
    if valid_until.tzinfo is None:
        valid_until = valid_until.replace(tzinfo=timezone.utc)
    return valid_until < now


def assess_claim(
    graph: AssuranceGraph,
    claim_id: str,
    *,
    now: datetime | None = None,
) -> ClaimAssessment:
    if claim_id not in graph.nodes:
        raise KeyError(claim_id)
    claim = graph.nodes[claim_id]
    if claim.kind != NodeType.CLAIM:
        raise ValueError("claim_id must identify a claim node")

    current_time = now or datetime.now(timezone.utc)
    incoming = graph.incoming(claim_id)

    support_edges = tuple(e for e in incoming if e.kind == EdgeType.SUPPORTS)
    contradiction_edges = tuple(e for e in incoming if e.kind == EdgeType.CONTRADICTS)
    dependency_edges = tuple(e for e in incoming if e.kind == EdgeType.DEPENDS_ON)

    stale_evidence = tuple(
        e.source
        for e in support_edges
        if _is_stale(graph.nodes[e.source].valid_until, current_time)
    )
    contradicted_by = tuple(e.source for e in contradiction_edges)
    unmet_assumptions = tuple(
        e.source
        for e in dependency_edges
        if graph.nodes[e.source].kind == NodeType.ASSUMPTION
        and graph.nodes[e.source].metadata.get("status") in {"violated", "unvalidated"}
    )

    usable_support = [
        graph.nodes[e.source]
        for e in support_edges
        if e.source not in stale_evidence
    ]
    confidences = [n.confidence for n in usable_support if n.confidence is not None]
    propagated_confidence = min(confidences) if confidences else None

    supported = bool(usable_support) and not contradicted_by and not unmet_assumptions

    return ClaimAssessment(
        claim_id=claim_id,
        supported=supported,
        stale_evidence=stale_evidence,
        contradicted_by=contradicted_by,
        unmet_assumptions=unmet_assumptions,
        propagated_confidence=propagated_confidence,
    )


def unsupported_claims(graph: AssuranceGraph) -> tuple[str, ...]:
    return tuple(
        node.id
        for node in graph.nodes.values()
        if node.kind == NodeType.CLAIM and not graph.incoming(node.id, EdgeType.SUPPORTS)
    )


def affected_claims(graph: AssuranceGraph, changed_node_id: str) -> tuple[str, ...]:
    """Return claims transitively downstream from a changed node."""
    if changed_node_id not in graph.nodes:
        raise KeyError(changed_node_id)

    frontier = [changed_node_id]
    seen = {changed_node_id}
    affected: set[str] = set()

    while frontier:
        current = frontier.pop()
        for edge in graph.outgoing(current):
            if edge.kind not in {EdgeType.SUPPORTS, EdgeType.DEPENDS_ON, EdgeType.QUALIFIES}:
                continue
            target = edge.target
            if target in seen:
                continue
            seen.add(target)
            frontier.append(target)
            if graph.nodes[target].kind == NodeType.CLAIM:
                affected.add(target)

    return tuple(sorted(affected))
