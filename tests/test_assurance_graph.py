from datetime import datetime, timedelta, timezone

from assurance_graph import (
    AssuranceEdge,
    AssuranceGraph,
    AssuranceNode,
    EdgeType,
    NodeType,
    affected_claims,
    assess_claim,
    graph_from_dict,
    graph_to_dict,
    unsupported_claims,
)


def test_supported_claim_with_fresh_evidence():
    now = datetime.now(timezone.utc)
    graph = AssuranceGraph()
    graph.add_node(AssuranceNode("c1", NodeType.CLAIM, "System remains within modeled safety envelope"))
    graph.add_node(
        AssuranceNode(
            "e1",
            NodeType.EVIDENCE,
            "Reachability analysis reports VERIFIED_SAFE",
            confidence=0.9,
            observed_at=now,
            valid_until=now + timedelta(days=1),
        )
    )
    graph.add_edge(AssuranceEdge("e1", "c1", EdgeType.SUPPORTS))

    result = assess_claim(graph, "c1", now=now)
    assert result.supported is True
    assert result.propagated_confidence == 0.9


def test_stale_evidence_does_not_support_claim():
    now = datetime.now(timezone.utc)
    graph = AssuranceGraph()
    graph.add_node(AssuranceNode("c1", NodeType.CLAIM, "Runtime condition is acceptably supported"))
    graph.add_node(
        AssuranceNode(
            "e1",
            NodeType.EVIDENCE,
            "Old monitoring snapshot",
            confidence=0.8,
            valid_until=now - timedelta(seconds=1),
        )
    )
    graph.add_edge(AssuranceEdge("e1", "c1", EdgeType.SUPPORTS))

    result = assess_claim(graph, "c1", now=now)
    assert result.supported is False
    assert result.stale_evidence == ("e1",)


def test_contradiction_and_unvalidated_assumption_weaken_claim():
    graph = AssuranceGraph()
    graph.add_node(AssuranceNode("c1", NodeType.CLAIM, "Controller is safe under stated assumptions"))
    graph.add_node(AssuranceNode("e1", NodeType.EVIDENCE, "Verification result", confidence=0.95))
    graph.add_node(AssuranceNode("d1", NodeType.DEFEATER, "Runtime observation contradicts modeled bound"))
    graph.add_node(
        AssuranceNode(
            "a1",
            NodeType.ASSUMPTION,
            "Disturbance bound remains valid",
            metadata={"status": "unvalidated"},
        )
    )
    graph.add_edge(AssuranceEdge("e1", "c1", EdgeType.SUPPORTS))
    graph.add_edge(AssuranceEdge("d1", "c1", EdgeType.CONTRADICTS))
    graph.add_edge(AssuranceEdge("a1", "c1", EdgeType.DEPENDS_ON))

    result = assess_claim(graph, "c1")
    assert result.supported is False
    assert result.contradicted_by == ("d1",)
    assert result.unmet_assumptions == ("a1",)


def test_unsupported_and_affected_claims():
    graph = AssuranceGraph()
    graph.add_node(AssuranceNode("a1", NodeType.ASSUMPTION, "Sensor bias remains bounded"))
    graph.add_node(AssuranceNode("c1", NodeType.CLAIM, "State estimate is trustworthy"))
    graph.add_node(AssuranceNode("c2", NodeType.CLAIM, "Shield decisions use trustworthy state"))
    graph.add_edge(AssuranceEdge("a1", "c1", EdgeType.DEPENDS_ON))
    graph.add_edge(AssuranceEdge("c1", "c2", EdgeType.SUPPORTS))

    assert set(unsupported_claims(graph)) == {"c1"}
    assert affected_claims(graph, "a1") == ("c1", "c2")


def test_json_round_trip():
    graph = AssuranceGraph()
    graph.add_node(AssuranceNode("c1", NodeType.CLAIM, "Example claim"))
    restored = graph_from_dict(graph_to_dict(graph))
    assert restored.nodes["c1"].statement == "Example claim"
