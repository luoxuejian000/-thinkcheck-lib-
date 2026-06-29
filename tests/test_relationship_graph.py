import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'thinkcheck-harmony'))

import pytest
from thinkcheck_harmony.relationship_graph import RelationshipGraph, Node, Edge, EdgeType


class TestRelationshipGraph:
    def test_add_node(self):
        graph = RelationshipGraph("test")
        node = Node(content="测试", speaker="user")
        node_id = graph.add_node(node)
        assert node_id in graph.nodes
        assert graph.nodes[node_id].content == "测试"

    def test_add_edge(self):
        graph = RelationshipGraph("test")
        n1 = Node(content="A", speaker="user")
        n2 = Node(content="B", speaker="user")
        graph.add_node(n1)
        graph.add_node(n2)
        edge = Edge(source_id=n1.id, target_id=n2.id, type=EdgeType.CONFLICT)
        graph.add_edge(edge)
        assert len(graph.get_conflict_edges()) == 1

    def test_get_neighbors(self):
        graph = RelationshipGraph("test")
        n1 = Node(content="A", speaker="user")
        n2 = Node(content="B", speaker="user")
        n3 = Node(content="C", speaker="user")
        graph.add_node(n1)
        graph.add_node(n2)
        graph.add_node(n3)
        graph.add_edge(Edge(source_id=n1.id, target_id=n2.id, type=EdgeType.SUPPORT))
        graph.add_edge(Edge(source_id=n1.id, target_id=n3.id, type=EdgeType.CONFLICT))
        neighbors = graph.get_neighbors(n1.id)
        assert set(neighbors) == {n2.id, n3.id}

    def test_only_append(self):
        graph = RelationshipGraph("test")
        n1 = Node(content="A", speaker="user")
        graph.add_node(n1)
        assert len(graph.nodes) == 1

    def test_get_contradiction_path(self):
        graph = RelationshipGraph("test")
        n1 = Node(content="A", speaker="user")
        n2 = Node(content="B", speaker="user")
        n3 = Node(content="C", speaker="user")
        graph.add_node(n1)
        graph.add_node(n2)
        graph.add_node(n3)
        graph.add_edge(Edge(source_id=n1.id, target_id=n2.id, type=EdgeType.CONFLICT))
        graph.add_edge(Edge(source_id=n2.id, target_id=n3.id, type=EdgeType.CONFLICT))
        path = graph.get_contradiction_path(n1.id)
        assert len(path) >= 1

    def test_export_to_dict(self):
        graph = RelationshipGraph("test")
        n1 = Node(content="A", speaker="user")
        graph.add_node(n1)
        data = graph.to_dict()
        assert data["session_id"] == "test"
        assert len(data["nodes"]) == 1