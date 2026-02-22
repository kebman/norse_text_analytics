from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from neo4j import GraphDatabase
from neo4j import Driver


@dataclass
class Neo4jConfig:
    uri: str
    user: str
    password: str

    @classmethod
    def from_env(cls) -> "Neo4jConfig":
        uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        user = os.getenv("NEO4J_USER", "neo4j")
        password = os.getenv("NEO4J_PASSWORD", "")
        if not password:
            raise ValueError("NEO4J_PASSWORD is not set. Create .env or export it.")
        return cls(uri=uri, user=user, password=password)


def get_driver(config: Neo4jConfig) -> Driver:
    return GraphDatabase.driver(config.uri, auth=(config.user, config.password))


def apply_schema(driver: Driver, schema_path: str | Path | None = None) -> None:
    if schema_path is None:
        schema_path = Path(__file__).with_name("schema.cypher")
    else:
        schema_path = Path(schema_path)

    content = schema_path.read_text(encoding="utf-8")
    statements = [stmt.strip() for stmt in content.split(";") if stmt.strip()]

    with driver.session() as session:
        for statement in statements:
            session.run(statement).consume()
