"""Entity and Relationship Extractor for SkillForge Knowledge Fabric."""

from __future__ import annotations
import re
from typing import Dict, List, Set, Tuple
from skillforge.database.models import (
    EdgeType,
    EntityAlias,
    GraphEdge,
    GraphNode,
    NodeType,
    SkillRecord,
)


KNOWN_CONCEPTS: Dict[str, List[str]] = {
    "concept:rest-api": ["rest", "restful", "api", "endpoint", "crud", "http client"],
    "concept:database-migration": ["migration", "schema migration", "alembic", "evolve schema", "flyway"],
    "concept:containerization": ["docker", "container", "dockerfile", "containerize", "podman"],
    "concept:ci-cd": ["ci/cd", "continuous integration", "github actions", "pipeline", "automation"],
    "concept:browser-testing": ["playwright", "puppeteer", "selenium", "e2e", "browser automation", "devtools"],
    "concept:knowledge-graph": ["graph", "knowledge graph", "nodes", "edges", "ontology", "graphify"],
    "concept:rag-retrieval": ["rag", "retrieval", "vector", "embedding", "rrf", "semantic search"],
    "concept:clean-code": ["refactor", "solid", "clean code", "maintainability", "architecture"],
    "concept:security-hardening": ["security", "audit", "sast", "vulnerability", "hardening", "injection"],
    "concept:performance-optimization": ["performance", "latency", "bottleneck", "profiling", "optimization", "caching"]
}

TECH_ALIASES: Dict[str, List[str]] = {
    "python": ["py", "python3", "cpython"],
    "typescript": ["ts"],
    "javascript": ["js", "es6", "node", "nodejs"],
    "react": ["reactjs", "react.js"],
    "fastapi": ["fast-api"],
    "docker": ["docker-compose", "container"],
    "sqlite": ["sqlite3", "embedded-db"],
    "dbt": ["data-build-tool", "dbt-core"],
    "playwright": ["playwright-browser", "browser-testing"]
}


def slugify(text: str) -> str:
    """Normalize string to slug format."""
    s = text.lower().strip()
    s = re.sub(r"[^\w\s-]", "", s)
    return re.sub(r"[\s_-]+", "-", s)


class GraphEntityExtractor:
    """Extracts typed graph nodes, edges, and aliases from skills."""

    def extract_from_skill(self, skill: SkillRecord) -> Tuple[List[GraphNode], List[GraphEdge], List[EntityAlias]]:
        nodes: Dict[str, GraphNode] = {}
        edges: List[GraphEdge] = []
        aliases: List[EntityAlias] = []

        # 1. Primary Skill Node
        skill_node_id = f"skill:{skill.id}"
        nodes[skill_node_id] = GraphNode(
            id=skill_node_id,
            node_type=NodeType.SKILL,
            name=skill.name,
            metadata={
                "category": skill.category,
                "trust_level": skill.trust_level.value,
                "quality_score": skill.quality_score,
                "source_type": skill.source_type.value,
                "author": skill.author,
                "version": skill.version
            }
        )

        # 2. Category Node & Edge
        cat_slug = slugify(skill.category)
        cat_node_id = f"category:{cat_slug}"
        if cat_node_id not in nodes:
            nodes[cat_node_id] = GraphNode(
                id=cat_node_id,
                node_type=NodeType.CATEGORY,
                name=skill.category,
                metadata={}
            )
        edges.append(GraphEdge(
            source_id=skill_node_id,
            target_id=cat_node_id,
            relationship_type=EdgeType.BELONGS_TO_CATEGORY.value,
            weight=1.0,
            confidence=1.0
        ))

        # 3. Technologies Nodes & Edges
        for tech in skill.technologies:
            t_slug = slugify(tech)
            if not t_slug:
                continue
            tech_node_id = f"tech:{t_slug}"
            if tech_node_id not in nodes:
                nodes[tech_node_id] = GraphNode(
                    id=tech_node_id,
                    node_type=NodeType.TECHNOLOGY,
                    name=tech,
                    metadata={}
                )
            edges.append(GraphEdge(
                source_id=skill_node_id,
                target_id=tech_node_id,
                relationship_type=EdgeType.USES_TECH.value,
                weight=1.0,
                confidence=0.9
            ))

            # Aliases for tech
            if t_slug in TECH_ALIASES:
                for alias in TECH_ALIASES[t_slug]:
                    aliases.append(EntityAlias(
                        alias=alias,
                        canonical_node_id=tech_node_id,
                        alias_type="synonym"
                    ))

        # 4. Dependency Nodes & Edges
        for dep in skill.dependencies:
            dep_slug = slugify(dep.name)
            if not dep_slug:
                continue
            dep_node_id = f"tool:{dep_slug}"
            if dep_node_id not in nodes:
                nodes[dep_node_id] = GraphNode(
                    id=dep_node_id,
                    node_type=NodeType.TOOL,
                    name=dep.name,
                    metadata={"dep_type": dep.dependency_type, "satisfied": dep.is_satisfied}
                )
            edges.append(GraphEdge(
                source_id=skill_node_id,
                target_id=dep_node_id,
                relationship_type=EdgeType.PREREQUISITE_FOR.value,
                weight=1.2,
                confidence=1.0
            ))

        # 5. Explicit Relationships
        for rel in skill.relationships:
            target_slug = slugify(rel.target_skill_id)
            target_node_id = f"skill:{target_slug}"
            rel_type = EdgeType.COMPLEMENTS.value
            if "conflict" in rel.relationship_type.lower():
                rel_type = EdgeType.CONFLICTS_WITH.value
            elif "require" in rel.relationship_type.lower() or "prereq" in rel.relationship_type.lower():
                rel_type = EdgeType.PREREQUISITE_FOR.value
            elif "supersede" in rel.relationship_type.lower():
                rel_type = EdgeType.SUPERSEDES.value

            edges.append(GraphEdge(
                source_id=skill_node_id,
                target_id=target_node_id,
                relationship_type=rel_type,
                weight=1.0,
                confidence=0.85,
                metadata={"reason": rel.reason}
            ))

        # 6. Concept Association
        full_text = f"{skill.name} {skill.description} {' '.join(skill.triggers)}".lower()
        for concept_id, keywords in KNOWN_CONCEPTS.items():
            if any(kw in full_text for kw in keywords):
                concept_name = concept_id.split(":", 1)[1].replace("-", " ").title()
                if concept_id not in nodes:
                    nodes[concept_id] = GraphNode(
                        id=concept_id,
                        node_type=NodeType.CONCEPT,
                        name=concept_name,
                        metadata={}
                    )
                edges.append(GraphEdge(
                    source_id=skill_node_id,
                    target_id=concept_id,
                    relationship_type=EdgeType.ASSOCIATED_WITH_CONCEPT.value,
                    weight=0.8,
                    confidence=0.8
                ))

        return list(nodes.values()), edges, aliases
