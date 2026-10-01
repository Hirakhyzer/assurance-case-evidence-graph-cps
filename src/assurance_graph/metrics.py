from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone

from .analysis import assess_claim
from .model import AssuranceGraph, NodeType


@dataclass(frozen=True)
class AssuranceMetrics:
    total_nodes: int
    total_edges: int
    claims: int
    evidence_nodes: int
    assumptions: int
    contexts: int
    defeaters: int
    supported_claims: int
    contradicted_claims: int
    claims_with_stale_evidence: int
    claims_with_unmet_assumptions: int
    support_coverage: float
    stale_claim_rate: float

    def to_dict(self) -> dict[str, int | float]:
        return asdict(self)


def summarize_assurance_graph(
    graph: AssuranceGraph,
    *,
    now: datetime | None = None,
) -> AssuranceMetrics:
    """Compute descriptive metrics for assurance-case health.

    These values describe the state of the argument graph. They are not safety
    probabilities and must not be interpreted as certification scores.
    """
    current_time = now or datetime.now(timezone.utc)
    counts = {kind: 0 for kind in NodeType}
    for node in graph.nodes.values():
        counts[node.kind] += 1

    claim_ids = [node.id for node in graph.nodes.values() if node.kind == NodeType.CLAIM]
    assessments = [assess_claim(graph, claim_id, now=current_time) for claim_id in claim_ids]

    supported = sum(assessment.supported for assessment in assessments)
    contradicted = sum(bool(assessment.contradicted_by) for assessment in assessments)
    stale = sum(bool(assessment.stale_evidence) for assessment in assessments)
    unmet = sum(bool(assessment.unmet_assumptions) for assessment in assessments)

    claim_count = len(claim_ids)
    return AssuranceMetrics(
        total_nodes=len(graph.nodes),
        total_edges=len(graph.edges),
        claims=claim_count,
        evidence_nodes=counts[NodeType.EVIDENCE],
        assumptions=counts[NodeType.ASSUMPTION],
        contexts=counts[NodeType.CONTEXT],
        defeaters=counts[NodeType.DEFEATER],
        supported_claims=supported,
        contradicted_claims=contradicted,
        claims_with_stale_evidence=stale,
        claims_with_unmet_assumptions=unmet,
        support_coverage=supported / claim_count if claim_count else 0.0,
        stale_claim_rate=stale / claim_count if claim_count else 0.0,
    )
