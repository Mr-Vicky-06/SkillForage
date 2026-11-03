"""Knowledge Graph Builder for SkillForge Knowledge Fabric."""

from __future__ import annotations
import logging
import time
from typing import Any, Dict
from skillforge.database.repository import SkillRepository
from skillforge.graph.extractor import GraphEntityExtractor

logger = logging.getLogger(__name__)


class KnowledgeGraphBuilder:
    """Builds and populates the Knowledge Fabric from indexed skills."""

    def __init__(self, repository: SkillRepository):
        self.repo = repository
        self.extractor = GraphEntityExtractor()

    def build_graph(self) -> Dict[str, Any]:
        """Scan all skills in database, extract nodes/edges/aliases, and populate graph tables."""
        t0 = time.perf_counter()
        
        # Ensure graph tables exist
        cur = self.repo.conn.cursor()
        
        # Clear existing graph data for idempotent rebuild
        with self.repo.conn:
            cur.execute("DELETE FROM entity_aliases;")
            cur.execute("DELETE FROM graph_evidence;")
            cur.execute("DELETE FROM graph_edges;")
            cur.execute("DELETE FROM graph_nodes;")

        skills = self.repo.list_all_skills()
        node_count = 0
        edge_count = 0
        alias_count = 0

        # Cache seen nodes to avoid duplicate insertions within memory
        seen_nodes = set()

        for skill in skills:
            nodes, edges, aliases = self.extractor.extract_from_skill(skill)
            
            for node in nodes:
                if node.id not in seen_nodes:
                    self.repo.upsert_graph_node(node)
                    seen_nodes.add(node.id)
                    node_count += 1
            
            for edge in edges:
                # Ensure target node exists or create a stub node if missing (e.g. external skill)
                if edge.target_id not in seen_nodes:
                    from skillforge.database.models import GraphNode, NodeType
                    target_type = NodeType.SKILL if edge.target_id.startswith("skill:") else NodeType.CONCEPT
                    target_name = edge.target_id.split(":", 1)[1].replace("-", " ")
                    stub = GraphNode(id=edge.target_id, node_type=target_type, name=target_name)
                    self.repo.upsert_graph_node(stub)
                    seen_nodes.add(edge.target_id)
                    node_count += 1
                
                self.repo.upsert_graph_edge(edge)
                edge_count += 1

            for alias in aliases:
                self.repo.add_entity_alias(alias.alias, alias.canonical_node_id, alias.alias_type)
                alias_count += 1

        duration_ms = round((time.perf_counter() - t0) * 1000, 2)
        stats = self.repo.get_graph_stats()
        stats["build_duration_ms"] = duration_ms
        return stats
