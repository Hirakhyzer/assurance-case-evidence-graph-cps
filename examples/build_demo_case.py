from datetime import datetime, timedelta, timezone

from assurance_graph import (
    AssuranceEdge,
    AssuranceGraph,
    AssuranceNode,
    EdgeType,
    NodeType,
    assess_claim,
    graph_to_dict,
)


def build_demo() -> AssuranceGraph:
    now = datetime.now(timezone.utc)
    graph = AssuranceGraph()

    graph.add_node(
        AssuranceNode(
            "claim.safe-operation",
            NodeType.CLAIM,
            "The CPS remains within its modeled safety envelope over the current assurance window.",
        )
    )
    graph.add_node(
        AssuranceNode(
            "evidence.formal-verification",
            NodeType.EVIDENCE,
            "Finite-horizon reachability result reports VERIFIED_SAFE under recorded uncertainty bounds.",
            confidence=0.95,
            observed_at=now,
            valid_until=now + timedelta(hours=12),
            metadata={"source": "verification-manifest"},
        )
    )
    graph.add_node(
        AssuranceNode(
            "evidence.runtime-shield",
            NodeType.EVIDENCE,
            "Runtime assurance trace reports no unsafe applied action in the current window.",
            confidence=0.9,
            observed_at=now,
            valid_until=now + timedelta(minutes=30),
            metadata={"source": "runtime-audit"},
        )
    )
    graph.add_node(
        AssuranceNode(
            "assumption.disturbance-bound",
            NodeType.ASSUMPTION,
            "Operational disturbances remain inside the bound used by verification and runtime assurance.",
            metadata={"status": "validated"},
        )
    )

    graph.add_edge(
        AssuranceEdge(
            "evidence.formal-verification",
            "claim.safe-operation",
            EdgeType.SUPPORTS,
            "Offline verification supports finite-horizon model safety.",
        )
    )
    graph.add_edge(
        AssuranceEdge(
            "evidence.runtime-shield",
            "claim.safe-operation",
            EdgeType.SUPPORTS,
            "Runtime decisions provide current operational evidence.",
        )
    )
    graph.add_edge(
        AssuranceEdge(
            "assumption.disturbance-bound",
            "claim.safe-operation",
            EdgeType.DEPENDS_ON,
            "The claim is conditional on the recorded disturbance envelope.",
        )
    )
    return graph


if __name__ == "__main__":
    graph = build_demo()
    print(graph_to_dict(graph))
    print(assess_claim(graph, "claim.safe-operation"))
