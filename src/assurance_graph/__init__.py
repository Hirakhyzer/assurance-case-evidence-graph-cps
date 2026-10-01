"""Assurance-case evidence graph research package."""

from .analysis import ClaimAssessment, affected_claims, assess_claim, unsupported_claims
from .io import graph_from_dict, graph_to_dict, load_graph, save_graph
from .metrics import AssuranceMetrics, summarize_assurance_graph
from .model import AssuranceEdge, AssuranceGraph, AssuranceNode, EdgeType, NodeType
from .validation import GraphValidationReport, ValidationIssue, validate_graph

__all__ = [
    "AssuranceEdge",
    "AssuranceGraph",
    "AssuranceMetrics",
    "AssuranceNode",
    "ClaimAssessment",
    "EdgeType",
    "GraphValidationReport",
    "NodeType",
    "ValidationIssue",
    "affected_claims",
    "assess_claim",
    "graph_from_dict",
    "graph_to_dict",
    "load_graph",
    "save_graph",
    "summarize_assurance_graph",
    "unsupported_claims",
    "validate_graph",
]
