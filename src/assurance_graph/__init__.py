"""Assurance-case evidence graph research package."""

from .analysis import ClaimAssessment, affected_claims, assess_claim, unsupported_claims
from .integrations import evidence_from_runtime_trace, evidence_from_verification_manifest
from .io import graph_from_dict, graph_to_dict, load_graph, save_graph
from .metrics import AssuranceMetrics, summarize_assurance_graph
from .model import AssuranceEdge, AssuranceGraph, AssuranceNode, EdgeType, NodeType
from .snapshots import GraphDiff, GraphSnapshot, changed_node_ids, diff_snapshots, snapshot_graph
from .validation import GraphValidationReport, ValidationIssue, validate_graph

__all__ = [
    "AssuranceEdge",
    "AssuranceGraph",
    "AssuranceMetrics",
    "AssuranceNode",
    "ClaimAssessment",
    "EdgeType",
    "GraphDiff",
    "GraphSnapshot",
    "GraphValidationReport",
    "NodeType",
    "ValidationIssue",
    "affected_claims",
    "assess_claim",
    "changed_node_ids",
    "diff_snapshots",
    "evidence_from_runtime_trace",
    "evidence_from_verification_manifest",
    "graph_from_dict",
    "graph_to_dict",
    "load_graph",
    "save_graph",
    "snapshot_graph",
    "summarize_assurance_graph",
    "unsupported_claims",
    "validate_graph",
]
