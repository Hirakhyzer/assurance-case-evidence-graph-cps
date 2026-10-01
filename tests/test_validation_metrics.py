from datetime import datetime, timedelta, timezone

from assurance_graph.analysis import assess_claim
from assurance_graph.metrics import summarize_assurance_graph
from assurance_graph.model import AssuranceEdge, AssuranceGraph, AssuranceNode, EdgeType, NodeType
from assurance_graph.validation import validate_graph


def test_validator_flags_orphan_evidence_and_assumption_status():
    graph = AssuranceGraph()
    graph.add_node(AssuranceNode("e1", NodeType.EVIDENCE, "Unlinked runtime log"))
    graph.add_node(AssuranceNode("a1", NodeType.ASSUMPTION, "Bound remains valid"))

    report = validate_graph(graph)
    codes = {issue.code for issue in report.warnings}

    assert report.valid is True
    assert "orphan_evidence" in codes
    assert "assumption_without_status" in codes


def test_validator_rejects_dependency_cycle():
    graph = AssuranceGraph()
    graph.add_node(AssuranceNode("c1", NodeType.CLAIM, "Top-level claim"))
    graph.add_node(AssuranceNode("c2", NodeType.CLAIM, "Supporting claim"))
    graph.add_edge(AssuranceEdge("c1", "c2", EdgeType.SUPPORTS))
    graph.add_edge(AssuranceEdge("c2", "c1", EdgeType.SUPPORTS))

    report = validate_graph(graph)

    assert report.valid is False
    assert any(issue.code == "dependency_cycle" for issue in report.errors)


def test_metrics_report_support_staleness_and_contradiction():
    now = datetime.now(timezone.utc)
    graph = AssuranceGraph()
    graph.add_node(AssuranceNode("c1", NodeType.CLAIM, "Freshly supported claim"))
    graph.add_node(AssuranceNode("c2", NodeType.CLAIM, "Stale claim"))
    graph.add_node(AssuranceNode("e1", NodeType.EVIDENCE, "Fresh evidence", confidence=0.9, valid_until=now + timedelta(hours=1)))
    graph.add_node(AssuranceNode("e2", NodeType.EVIDENCE, "Expired evidence", confidence=0.7, valid_until=now - timedelta(hours=1)))
    graph.add_node(AssuranceNode("d1", NodeType.DEFEATER, "Observed contradiction"))
    graph.add_edge(AssuranceEdge("e1", "c1", EdgeType.SUPPORTS))
    graph.add_edge(AssuranceEdge("e2", "c2", EdgeType.SUPPORTS))
    graph.add_edge(AssuranceEdge("d1", "c1", EdgeType.CONTRADICTS))

    metrics = summarize_assurance_graph(graph, now=now)

    assert metrics.claims == 2
    assert metrics.supported_claims == 0
    assert metrics.contradicted_claims == 1
    assert metrics.claims_with_stale_evidence == 1
    assert metrics.support_coverage == 0.0
    assert assess_claim(graph, "c2", now=now).stale_evidence == ("e2",)
