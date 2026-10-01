from datetime import datetime, timezone

from assurance_graph import (
    AssuranceEdge,
    AssuranceGraph,
    AssuranceNode,
    EdgeType,
    NodeType,
    changed_node_ids,
    diff_snapshots,
    evidence_from_runtime_trace,
    evidence_from_verification_manifest,
    snapshot_graph,
)


def test_verification_manifest_preserves_provenance():
    manifest = {
        "schema_version": "1.0.0",
        "run_id": "battery-interval-001",
        "timestamp_utc": "2026-10-01T00:00:00Z",
        "git_commit": "abc123",
        "domain": "battery",
        "method": {"name": "interval", "configuration": {"steps": 40}},
        "horizon": {"steps": 40, "time": 40.0},
        "assumptions": [{"id": "A1", "status": "explicit"}],
        "uncertainty": {"disturbance_bounds": "configured box"},
        "result": {"status": "VERIFIED_SAFE", "complete": True},
        "reproducibility": {"python_version": "3.12"},
    }

    node = evidence_from_verification_manifest(manifest)

    assert node.kind == NodeType.EVIDENCE
    assert node.id == "verification:battery-interval-001"
    assert node.metadata["source_type"] == "formal_verification_manifest"
    assert node.metadata["verification_status"] == "VERIFIED_SAFE"
    assert node.metadata["method"]["name"] == "interval"
    assert node.metadata["assumptions"][0]["id"] == "A1"


def test_runtime_trace_is_summarized_without_dropping_records():
    trace = {
        "domain": "battery",
        "seed": 7,
        "records": [
            {"status": "ACCEPT", "safe": True, "margin": 0.4},
            {"status": "MODIFY", "safe": True, "margin": 0.2},
            {"status": "FALLBACK", "safe": False, "margin": -0.1},
        ],
    }

    node = evidence_from_runtime_trace(trace, source_id="battery-seed7")

    assert node.metadata["record_count"] == 3
    assert node.metadata["modification_count"] == 1
    assert node.metadata["fallback_count"] == 1
    assert node.metadata["unsafe_state_count"] == 1
    assert node.metadata["minimum_margin"] == -0.1
    assert len(node.metadata["raw_records"]) == 3


def test_snapshot_digest_is_stable_for_same_graph():
    graph = AssuranceGraph()
    graph.add_node(AssuranceNode("c1", NodeType.CLAIM, "Top-level claim"))

    when = datetime(2026, 10, 1, tzinfo=timezone.utc)
    first = snapshot_graph(graph, snapshot_id="s1", created_at=when)
    second = snapshot_graph(graph, snapshot_id="s2", created_at=when)

    assert first.digest_sha256 == second.digest_sha256


def test_snapshot_diff_finds_changed_nodes_and_edges():
    graph = AssuranceGraph()
    graph.add_node(AssuranceNode("c1", NodeType.CLAIM, "System claim"))
    graph.add_node(AssuranceNode("e1", NodeType.EVIDENCE, "Initial evidence"))
    graph.add_edge(AssuranceEdge("e1", "c1", EdgeType.SUPPORTS))

    before = snapshot_graph(graph, snapshot_id="before")

    graph.nodes["e1"] = AssuranceNode(
        "e1",
        NodeType.EVIDENCE,
        "Refreshed evidence",
        metadata={"revision": 2},
    )
    graph.add_node(AssuranceNode("a1", NodeType.ASSUMPTION, "Bounds remain valid"))
    graph.add_edge(AssuranceEdge("a1", "c1", EdgeType.DEPENDS_ON))

    after = snapshot_graph(graph, snapshot_id="after")
    diff = diff_snapshots(before, after)

    assert diff.added_nodes == ("a1",)
    assert diff.changed_nodes == ("e1",)
    assert ("a1", "c1", "depends_on") in diff.added_edges
    assert changed_node_ids(diff) == ("a1", "e1")
