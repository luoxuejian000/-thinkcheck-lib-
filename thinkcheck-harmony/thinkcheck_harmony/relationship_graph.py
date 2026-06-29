"""
关系图谱（Relationship Graph）
公理一：关系本体论的工程实现
意义不寓于孤立的实体中，而生成于实体之间的关系之中
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from uuid import uuid4


class EdgeType(Enum):
    """关系边类型"""
    RECORD = "record"
    DECLARATION = "declaration"
    CONFLICT = "conflict"
    SUPPORT = "support"
    TRANSFORMATION = "transformation"
    RESOLUTION = "resolution"


@dataclass
class Node:
    """关系图谱中的节点"""
    id: str = field(default_factory=lambda: str(uuid4()))
    type: str = "interaction"
    content: str = ""
    speaker: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "content": self.content,
            "speaker": self.speaker,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }


@dataclass
class Edge:
    """关系图谱中的边"""
    id: str = field(default_factory=lambda: str(uuid4()))
    source_id: str = ""
    target_id: str = ""
    type: EdgeType = EdgeType.RECORD
    confidence: float = 1.0
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "type": self.type.value,
            "confidence": self.confidence,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }


class RelationshipGraph:
    """
    关系图谱
    身份不是实体，而是轨迹；不是属性，而是关系模式
    仅追加日志，永不删除
    """

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.nodes: Dict[str, Node] = {}
        self.edges: List[Edge] = []
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def add_node(self, node: Node) -> str:
        """添加节点（仅追加，永不删除）"""
        self.nodes[node.id] = node
        self.updated_at = datetime.now()
        return node.id

    def add_edge(self, edge: Edge) -> str:
        """添加关系边（仅追加，永不删除）"""
        if edge.source_id not in self.nodes:
            raise ValueError(f"Source node {edge.source_id} not found")
        if edge.target_id not in self.nodes:
            raise ValueError(f"Target node {edge.target_id} not found")
        self.edges.append(edge)
        self.updated_at = datetime.now()
        return edge.id

    def get_node(self, node_id: str) -> Optional[Node]:
        return self.nodes.get(node_id)

    def get_edges_by_type(self, edge_type: EdgeType) -> List[Edge]:
        return [e for e in self.edges if e.type == edge_type]

    def get_conflict_edges(self) -> List[Edge]:
        return self.get_edges_by_type(EdgeType.CONFLICT)

    def get_nodes_by_speaker(self, speaker: str) -> List[Node]:
        return [n for n in self.nodes.values() if n.speaker == speaker]

    def get_neighbors(self, node_id: str) -> List[str]:
        """获取节点的所有邻居节点ID"""
        neighbors = set()
        for edge in self.edges:
            if edge.source_id == node_id:
                neighbors.add(edge.target_id)
            elif edge.target_id == node_id:
                neighbors.add(edge.source_id)
        return list(neighbors)

    def get_contradiction_path(self, node_id: str) -> List[Dict[str, Any]]:
        """获取从指定节点出发的矛盾传播路径"""
        path = []
        visited = set()
        queue = [(node_id, 0)]
        while queue:
            current_id, depth = queue.pop(0)
            if current_id in visited:
                continue
            visited.add(current_id)
            for edge in self.edges:
                if edge.source_id == current_id and edge.type == EdgeType.CONFLICT:
                    path.append({
                        "from": current_id,
                        "to": edge.target_id,
                        "confidence": edge.confidence,
                        "depth": depth
                    })
                    if edge.target_id not in visited:
                        queue.append((edge.target_id, depth + 1))
        return path

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "nodes": [n.to_dict() for n in self.nodes.values()],
            "edges": [e.to_dict() for e in self.edges],
        }

    def export_to_json(self, filepath: str) -> None:
        import json
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)

    def query(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """查询满足条件的节点和边"""
        results = []
        for node in self.nodes.values():
            match = True
            for key, value in filters.items():
                if key == "speaker" and node.speaker != value:
                    match = False
                elif key == "type" and node.type != value:
                    match = False
                elif key == "after_date":
                    if node.timestamp < datetime.fromisoformat(value):
                        match = False
            if match:
                results.append(node.to_dict())
        return results
