"""Task Intent and Domain Classification Engine."""

import re
from dataclasses import dataclass, field
from typing import List, Set


INTENT_PATTERNS = {
    "build": [r"\b(build|create|implement|add|scaffold|develop|author|make|generate)\b"],
    "refactor": [r"\b(refactor|clean|simplify|modernize|rewrite|reorganize)\b"],
    "debug": [r"\b(debug|fix|repair|troubleshoot|resolve|error|broken|crash|failing)\b"],
    "review": [r"\b(review|audit|critique|inspect|assess|evaluate)\b"],
    "test": [r"\b(test|spec|tdd|e2e|qa|coverage|unit test|integration test)\b"],
    "design": [r"\b(design|ui|ux|styling|style|palette|layout|component|typography|banner|slide)\b"],
    "optimize": [r"\b(optimize|speed|fast|latency|bottleneck|performance|memory|profile)\b"],
    "document": [r"\b(document|docs|architecture|adr|diagram|readme|guide|specification)\b"],
    "security": [r"\b(security|vulnerability|threat|harden|exploit|penetration|auth|credential)\b"],
    "reverse_engineer": [r"\b(reverse[- ]engineer|binary|decompile|disassemble|deobfuscate|unpack|asar)\b"],
}

DOMAIN_KEYWORDS = {
    "ai": ["agent", "agents", "langgraph", "langchain", "rag", "llm", "prompt", "vector", "embedding", "crewai", "autogen", "copilot"],
    "ml": ["machine learning", "ml", "pytorch", "tensorflow", "training", "inference", "dataset", "sklearn", "model"],
    "data": ["data", "bigquery", "spark", "pyspark", "dbt", "dataform", "pipeline", "etl", "sql", "analytics", "parquet"],
    "frontend": ["frontend", "react", "next.js", "nextjs", "vue", "svelte", "tailwind", "css", "html", "browser", "dom", "ui"],
    "backend": ["backend", "api", "rest", "graphql", "fastapi", "flask", "django", "server", "endpoint", "microservice"],
    "android": ["android", "mobile", "apk", "gradle", "jetpack", "compose", "kotlin"],
    "devops": ["docker", "kubernetes", "k8s", "terraform", "ci/cd", "github actions", "deploy", "infrastructure", "ansible"],
    "security": ["security", "reverse engineering", "rea", "penetration", "auth", "audit", "threat"],
    "testing": ["test", "playwright", "cypress", "pytest", "jest", "mock", "stub"],
    "core": ["clean code", "karpathy", "solid", "refactoring", "best practices", "engineering"],
}


@dataclass
class TaskAnalysis:
    raw_task: str
    intents: List[str] = field(default_factory=list)
    domains: List[str] = field(default_factory=list)
    extracted_terms: List[str] = field(default_factory=list)
    technologies: List[str] = field(default_factory=list)


class TaskClassifier:
    def classify(self, task_description: str) -> TaskAnalysis:
        """Classify task description into intents, domains, and relevant terms."""
        text = task_description.lower()
        intents: Set[str] = set()
        domains: Set[str] = set()
        extracted_terms: Set[str] = set()
        technologies: Set[str] = set()

        # Classify intents
        for intent, patterns in INTENT_PATTERNS.items():
            for pat in patterns:
                if re.search(pat, text):
                    intents.add(intent)
                    break

        # Classify domains
        for domain, keywords in DOMAIN_KEYWORDS.items():
            for kw in keywords:
                if kw in text:
                    domains.add(domain)
                    extracted_terms.add(kw)

        # Extract words (clean alphanumeric tokens > 2 chars)
        tokens = [w.strip() for w in re.findall(r"[a-zA-Z0-9_\-]+", text)]
        for t in tokens:
            if len(t) > 2 and t not in ("the", "and", "for", "with", "this", "that", "from"):
                extracted_terms.add(t)

        return TaskAnalysis(
            raw_task=task_description,
            intents=sorted(list(intents)),
            domains=sorted(list(domains)),
            extracted_terms=sorted(list(extracted_terms)),
            technologies=sorted(list(technologies))
        )

