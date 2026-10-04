from assurance_graph import (
    AssuranceEdge, AssuranceGraph, AssuranceNode, EdgeType, NodeType,
    affected_claims, assess_claim,
)


def test_unsupported_subclaim_cannot_support_parent_claim():
    graph = AssuranceGraph()
    graph.add_node(AssuranceNode("child", NodeType.CLAIM, "State estimate is trustworthy"))
    graph.add_node(AssuranceNode("parent", NodeType.CLAIM, "Shield decision is trustworthy"))
    graph.add_edge(AssuranceEdge("child", "parent", EdgeType.SUPPORTS))

    result = assess_claim(graph, "parent")

    assert result.supported is False
    assert result.unsupported_subclaims == ("child",)


def test_supported_subclaim_can_support_parent_and_propagate_confidence():
    graph = AssuranceGraph()
    graph.add_node(AssuranceNode("e1", NodeType.EVIDENCE, "Fresh verification", confidence=0.87))
    graph.add_node(AssuranceNode("child", NodeType.CLAIM, "State estimate is trustworthy"))
    graph.add_node(AssuranceNode("parent", NodeType.CLAIM, "Shield decision is trustworthy"))
    graph.add_edge(AssuranceEdge("e1", "child", EdgeType.SUPPORTS))
    graph.add_edge(AssuranceEdge("child", "parent", EdgeType.SUPPORTS))

    result = assess_claim(graph, "parent")

    assert result.supported is True
    assert result.propagated_confidence == 0.87


def test_missing_assumption_status_is_fail_closed():
    graph = AssuranceGraph()
    graph.add_node(AssuranceNode("e1", NodeType.EVIDENCE, "Verification result"))
    graph.add_node(AssuranceNode("a1", NodeType.ASSUMPTION, "Sensor bias remains bounded"))
    graph.add_node(AssuranceNode("c1", NodeType.CLAIM, "System is within modeled envelope"))
    graph.add_edge(AssuranceEdge("e1", "c1", EdgeType.SUPPORTS))
    graph.add_edge(AssuranceEdge("a1", "c1", EdgeType.DEPENDS_ON))

    result = assess_claim(graph, "c1")

    assert result.supported is False
    assert result.unmet_assumptions == ("a1",)


def test_contradiction_change_marks_target_and_parent_as_affected():
    graph = AssuranceGraph()
    graph.add_node(AssuranceNode("d1", NodeType.DEFEATER, "Runtime evidence challenges bound"))
    graph.add_node(AssuranceNode("c1", NodeType.CLAIM, "Bound remains credible"))
    graph.add_node(AssuranceNode("c2", NodeType.CLAIM, "System-level claim"))
    graph.add_edge(AssuranceEdge("d1", "c1", EdgeType.CONTRADICTS))
    graph.add_edge(AssuranceEdge("c1", "c2", EdgeType.SUPPORTS))

    assert affected_claims(graph, "d1") == ("c1", "c2")


def test_claim_cycle_fails_closed_instead_of_recursing_forever():
    graph = AssuranceGraph()
    graph.add_node(AssuranceNode("c1", NodeType.CLAIM, "Claim one"))
    graph.add_node(AssuranceNode("c2", NodeType.CLAIM, "Claim two"))
    graph.add_edge(AssuranceEdge("c1", "c2", EdgeType.SUPPORTS))
    graph.add_edge(AssuranceEdge("c2", "c1", EdgeType.SUPPORTS))

    result = assess_claim(graph, "c1")

    assert result.supported is False
    assert result.unsupported_subclaims
