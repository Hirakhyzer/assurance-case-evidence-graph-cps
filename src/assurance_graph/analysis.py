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
    unsupported_subclaims: tuple[str, ...]
    propagated_confidence: float | None


def _is_stale(valid_until: datetime | None, now: datetime) -> bool:
    if valid_until is None:
        return False
    if valid_until.tzinfo is None:
        valid_until = valid_until.replace(tzinfo=timezone.utc)
    return valid_until < now


def _assess_claim(graph, claim_id, *, now, stack, cache):
    if claim_id in cache:
        return cache[claim_id]
    if claim_id in stack:
        return ClaimAssessment(claim_id, False, (), (), (), (claim_id,), None)

    incoming = graph.incoming(claim_id)
    support_edges = tuple(e for e in incoming if e.kind == EdgeType.SUPPORTS)
    contradiction_edges = tuple(e for e in incoming if e.kind == EdgeType.CONTRADICTS)
    dependency_edges = tuple(e for e in incoming if e.kind == EdgeType.DEPENDS_ON)

    stale_evidence = []
    usable_support = []
    unsupported_subclaims = set()
    next_stack = stack + (claim_id,)

    for edge in support_edges:
        source = graph.nodes[edge.source]
        if source.kind == NodeType.EVIDENCE:
            if _is_stale(source.valid_until, now):
                stale_evidence.append(source.id)
            else:
                usable_support.append(source)
        elif source.kind == NodeType.CLAIM:
            assessment = _assess_claim(
                graph, source.id, now=now, stack=next_stack, cache=cache
            )
            if assessment.supported:
                usable_support.append(source)
            else:
                unsupported_subclaims.add(source.id)
                unsupported_subclaims.update(assessment.unsupported_subclaims)
            stale_evidence.extend(assessment.stale_evidence)

    contradicted_by = tuple(sorted(e.source for e in contradiction_edges))
    unmet_assumptions = tuple(sorted(
        e.source for e in dependency_edges
        if graph.nodes[e.source].kind == NodeType.ASSUMPTION
        and graph.nodes[e.source].metadata.get("status") != "validated"
    ))

    confidences = []
    for node in usable_support:
        if node.kind == NodeType.CLAIM:
            nested = cache.get(node.id)
            if nested and nested.propagated_confidence is not None:
                confidences.append(nested.propagated_confidence)
        elif node.confidence is not None:
            confidences.append(node.confidence)

    result = ClaimAssessment(
        claim_id=claim_id,
        supported=bool(usable_support) and not contradicted_by
        and not unmet_assumptions and not unsupported_subclaims,
        stale_evidence=tuple(sorted(set(stale_evidence))),
        contradicted_by=contradicted_by,
        unmet_assumptions=unmet_assumptions,
        unsupported_subclaims=tuple(sorted(unsupported_subclaims)),
        propagated_confidence=min(confidences) if confidences else None,
    )
    cache[claim_id] = result
    return result


def assess_claim(graph: AssuranceGraph, claim_id: str, *, now: datetime | None = None) -> ClaimAssessment:
    """Assess evidence, assumptions, contradictions, and supporting subclaims."""
    if claim_id not in graph.nodes:
        raise KeyError(claim_id)
    if graph.nodes[claim_id].kind != NodeType.CLAIM:
        raise ValueError("claim_id must identify a claim node")
    return _assess_claim(
        graph, claim_id, now=now or datetime.now(timezone.utc), stack=(), cache={}
    )


def unsupported_claims(graph: AssuranceGraph) -> tuple[str, ...]:
    return tuple(
        node.id for node in graph.nodes.values()
        if node.kind == NodeType.CLAIM and not graph.incoming(node.id, EdgeType.SUPPORTS)
    )


def affected_claims(graph: AssuranceGraph, changed_node_id: str) -> tuple[str, ...]:
    """Return claims transitively affected by any assurance-relevant relationship."""
    if changed_node_id not in graph.nodes:
        raise KeyError(changed_node_id)

    frontier = [changed_node_id]
    seen = {changed_node_id}
    affected = set()

    while frontier:
        current = frontier.pop()
        for edge in graph.outgoing(current):
            if edge.kind not in {
                EdgeType.SUPPORTS, EdgeType.DEPENDS_ON,
                EdgeType.QUALIFIES, EdgeType.CONTRADICTS,
            }:
                continue
            target = edge.target
            if target in seen:
                continue
            seen.add(target)
            frontier.append(target)
            if graph.nodes[target].kind == NodeType.CLAIM:
                affected.add(target)

    return tuple(sorted(affected))
