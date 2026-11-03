"""Knowledge Graph Traversal and Relational Navigation."""

from __future__ import annotations
from typing import Any, Dict, List, Optional
from skillforge.database.models import EdgeType
from skillforge.database.repository import SkillRepository


class GraphTraverser:
    """Provides relational graph navigation, multi-hop CTE querying, and cluster discovery."""

    def __init__(self, repository: SkillRepository):
        self.repo = repository

    def _resolve_node_id(self, identifier: str) -> str:
        """Resolve a name, slug, or alias to a canonical graph node id."""
        identifier = identifier.strip()
        cur = self.repo.conn.cursor()

        # 1. Exact id match
        cur.execute("SELECT id FROM graph_nodes WHERE id = ?", (identifier,))
        row = cur.fetchone()
        if row:
            return row["id"]

        # 2. Try prefix skill:
        cur.execute("SELECT id FROM graph_nodes WHERE id = ?", (f"skill:{identifier}",))
        row = cur.fetchone()
        if row:
            return row["id"]

        # 3. Match by node name
        cur.execute("SELECT id FROM graph_nodes WHERE name = ? COLLATE NOCASE LIMIT 1", (identifier,))
        row = cur.fetchone()
        if row:
            return row["id"]

        # 4. Check entity alias
        alias_target = self.repo.resolve_alias(identifier)
        if alias_target:
            return alias_target

        return identifier

    def get_neighbors(
        self,
        node_id: str,
        relationship_type: Optional[str] = None,
        max_hops: int = 1
    ) -> List[Dict[str, Any]]:
        """Query neighbors using SQLite recursive CTE."""
        canonical_id = self._resolve_node_id(node_id)
        return self.repo.get_graph_neighbors(canonical_id, relationship_type, max_hops)

    def find_skill_prerequisites(self, skill_id: str) -> List[Dict[str, Any]]:
        """Return required tools, packages, or prerequisite skills."""
        canonical_id = self._resolve_node_id(skill_id)
        return self.repo.get_graph_neighbors(canonical_id, EdgeType.PREREQUISITE_FOR.value, max_hops=1)

    def find_skill_complements(self, skill_id: str) -> List[Dict[str, Any]]:
        """Return skills that synergize or complement the target skill."""
        canonical_id = self._resolve_node_id(skill_id)
        return self.repo.get_graph_neighbors(canonical_id, EdgeType.COMPLEMENTS.value, max_hops=1)

    def find_skills_by_technology(self, tech_name: str) -> List[str]:
        """Find all skills linked to a given technology."""
        tech_slug = tech_name.lower().strip().replace(" ", "-")
        node_id = f"tech:{tech_slug}"
        # Check alias if node not directly matching
        alias_target = self.repo.resolve_alias(tech_name)
        if alias_target:
            node_id = alias_target

        cur = self.repo.conn.cursor()
        cur.execute("""
        SELECT source_id FROM graph_edges
        WHERE target_id = ? AND relationship_type = ?
        """, (node_id, EdgeType.USES_TECH.value))
        return [r["source_id"].replace("skill:", "") for r in cur.fetchall()]

    def find_skills_by_concept(self, concept_name: str) -> List[str]:
        """Find all skills associated with a high-level concept."""
        concept_slug = concept_name.lower().strip().replace(" ", "-")
        node_id = f"concept:{concept_slug}"
        cur = self.repo.conn.cursor()
        cur.execute("""
        SELECT source_id FROM graph_edges
        WHERE target_id = ? AND relationship_type = ?
        """, (node_id, EdgeType.ASSOCIATED_WITH_CONCEPT.value))
        return [r["source_id"].replace("skill:", "") for r in cur.fetchall()]

    def find_related_cluster(self, skill_id: str) -> Dict[str, Any]:
        """Synthesize a complete neighborhood cluster: prereqs, complements, tech, and category."""
        canonical_id = self._resolve_node_id(skill_id)
        
        prereqs = self.find_skill_prerequisites(canonical_id)
        complements = self.find_skill_complements(canonical_id)
        
        cur = self.repo.conn.cursor()
        # Find technologies
        cur.execute("""
        SELECT n.name FROM graph_edges e
        JOIN graph_nodes n ON e.target_id = n.id
        WHERE e.source_id = ? AND e.relationship_type = ?
        """, (canonical_id, EdgeType.USES_TECH.value))
        technologies = [r["name"] for r in cur.fetchall()]

        # Find category
        cur.execute("""
        SELECT n.name FROM graph_edges e
        JOIN graph_nodes n ON e.target_id = n.id
        WHERE e.source_id = ? AND e.relationship_type = ?
        """, (canonical_id, EdgeType.BELONGS_TO_CATEGORY.value))
        cat_row = cur.fetchone()
        category = cat_row["name"] if cat_row else "Unknown"

        # Find concepts
        cur.execute("""
        SELECT n.name FROM graph_edges e
        JOIN graph_nodes n ON e.target_id = n.id
        WHERE e.source_id = ? AND e.relationship_type = ?
        """, (canonical_id, EdgeType.ASSOCIATED_WITH_CONCEPT.value))
        concepts = [r["name"] for r in cur.fetchall()]

        return {
            "node_id": canonical_id,
            "category": category,
            "technologies": technologies,
            "concepts": concepts,
            "prerequisites": prereqs,
            "complements": complements
        }
