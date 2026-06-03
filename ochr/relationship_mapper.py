"""
关系映射器 (Relationship Mapper)
分析文档各部分之间的依赖关系
"""

import re
from typing import List, Dict, Any, Set, Tuple
from dataclasses import dataclass
from collections import defaultdict
import networkx as nx
from loguru import logger


@dataclass
class DocumentSection:
    id: str
    content: str
    start_index: int
    end_index: int
    dependencies: Set[str] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = set()


class RelationshipMapper:
    """
    分析文档各部分之间的依赖关系
    """
    
    def __init__(self):
        self.sections: List[DocumentSection] = []
        self.graph = nx.DiGraph()
        self.section_keywords: Dict[str, Set[str]] = {}
    
    def analyze(self, text: str) -> Dict[str, Any]:
        """
        分析文档的关系结构
        """
        logger.info("开始分析文档关系结构")
        
        # 1. 分段
        self._split_into_sections(text)
        
        # 2. 提取关键词
        self._extract_section_keywords()
        
        # 3. 构建依赖关系
        self._build_dependencies()
        
        # 4. 构建图
        self._build_graph()
        
        # 5. 分析关键节点
        critical_nodes = self._identify_critical_nodes()
        
        logger.info(f"关系分析完成: {len(self.sections)} 个部分, {len(critical_nodes)} 个关键节点")
        
        return {
            'sections': [s.id for s in self.sections],
            'critical_nodes': critical_nodes,
            'dependency_count': self.graph.number_of_edges(),
            'centrality': dict(nx.betweenness_centrality(self.graph)) if self.graph.nodes else {}
        }
    
    def _split_into_sections(self, text: str):
        """
        将文档分割成章节
        """
        self.sections = []
        
        # 按标题分割（简单实现）
        title_pattern = r'^(?:第[一二三四五六七八九十百]+[章节篇节]|[\d]+\.)\s*[^\n]+'
        lines = text.split('\n')
        
        current_section = ""
        current_start = 0
        section_id = 0
        
        for i, line in enumerate(lines):
            if re.match(title_pattern, line.strip()):
                if current_section.strip():
                    self.sections.append(DocumentSection(
                        id=f"section_{section_id}",
                        content=current_section.strip(),
                        start_index=current_start,
                        end_index=len('\n'.join(lines[:i]))
                    ))
                    section_id += 1
                current_section = line + '\n'
                current_start = len('\n'.join(lines[:i]))
            else:
                current_section += line + '\n'
        
        if current_section.strip():
            self.sections.append(DocumentSection(
                id=f"section_{section_id}",
                content=current_section.strip(),
                start_index=current_start,
                end_index=len(text)
            ))
    
    def _extract_section_keywords(self):
        """
        提取每个章节的关键词
        """
        from thinkcheck_harmony.utils import extract_keywords
        
        for section in self.sections:
            keywords = extract_keywords(section.content, top_n=15)
            self.section_keywords[section.id] = set(keywords)
    
    def _build_dependencies(self):
        """
        构建章节间的依赖关系
        """
        for i, section in enumerate(self.sections):
            section_words = self.section_keywords[section.id]
            
            # 检查与前面章节的关系
            for j in range(i):
                prev_section = self.sections[j]
                prev_words = self.section_keywords[prev_section.id]
                
                # 计算关键词重叠
                overlap = len(section_words & prev_words)
                
                if overlap > 3:  # 阈值
                    section.dependencies.add(prev_section.id)
    
    def _build_graph(self):
        """
        构建依赖图
        """
        for section in self.sections:
            self.graph.add_node(section.id)
        
        for section in self.sections:
            for dep_id in section.dependencies:
                self.graph.add_edge(dep_id, section.id)
    
    def _identify_critical_nodes(self) -> List[str]:
        """
        识别关键节点（高中心性的节点）
        """
        if not self.graph.nodes:
            return []
        
        try:
            centrality = nx.betweenness_centrality(self.graph)
            sorted_nodes = sorted(centrality.items(), key=lambda x: x[1], reverse=True)
            threshold = sorted_nodes[len(sorted_nodes) // 4][1] if sorted_nodes else 0
            critical = [node_id for node_id, score in sorted_nodes if score >= threshold]
            return critical
        except:
            # 如果图计算失败，返回前几个章节
            return [s.id for s in self.sections[:3]]
    
    def get_priority_order(self) -> List[str]:
        """
        获取修复的优先级顺序
        """
        try:
            # 拓扑排序 + 中心性
            if not self.graph.nodes:
                return [s.id for s in self.sections]
            
            critical = self._identify_critical_nodes()
            order = []
            
            # 先关键节点，再其他
            for node_id in critical:
                if node_id not in order:
                    order.append(node_id)
            
            for node_id in self.graph.nodes:
                if node_id not in order:
                    order.append(node_id)
            
            return order
        except:
            return [s.id for s in self.sections]
    
    def get_section_by_id(self, section_id: str) -> DocumentSection:
        """
        根据 ID 获取章节
        """
        for section in self.sections:
            if section.id == section_id:
                return section
        return None
