#!/usr/bin/python3
# Count word occurrences in Havamal.
from __future__ import annotations

import argparse
import json
from pathlib import Path

from nta.graph.db import Neo4jConfig
from nta.graph.db import get_driver


def strip_line(line: str) -> list[str]:
    """Old JSON tokenization logic kept for compatibility."""
    strip = [".", ",", ";", ":", "!", "?", '"']
    words = line.split(" ")
    for char in strip:
        words = [word.replace(char, "").lower() for word in words]
    return words


def count_from_json() -> dict[str, int]:
    """Original logic: count words from local Havamal JSON."""
    file_path = Path(__file__).resolve().parents[1] / "data" / "Hávamál1.json"
    words_list: list[str] = []

    with file_path.open("rb") as fh:
        data = json.load(fh)

    verses = data["poem"]["verses"]
    for verse in verses:
        for strophe in verse["strophes"]:
            for line in strophe["lines"]:
                words_list.extend(strip_line(line))

    words_list.sort()

    counts: dict[str, int] = {}
    for word in words_list:
        if word not in counts:
            counts[word] = 0
        counts[word] += 1
    return counts


def print_top_tokens_from_graph(limit: int = 20) -> None:
    """Graph logic: count Token nodes grouped by surface in Neo4j."""
    config = Neo4jConfig.from_env()

    query = """
    MATCH (t:Token)
    WHERE t.surface IS NOT NULL AND t.surface <> ""
    RETURN t.surface AS surface, count(*) AS freq
    ORDER BY freq DESC, surface ASC
    LIMIT $limit
    """

    with get_driver(config) as driver:
        with driver.session() as session:
            records = session.run(query, limit=limit)
            for record in records:
                print(f"{record['surface']}: {record['freq']}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source",
        choices=["graph", "json"],
        default="graph",
        help="Use 'graph' (default) for Neo4j counts or 'json' for old local logic.",
    )
    args = parser.parse_args()

    if args.source == "graph":
        print_top_tokens_from_graph(limit=20)
        return

    # Keep old behavior available until fully retired.
    counts = count_from_json()
    for word in counts:
        if counts[word] > 1:
            print(f"{word}: {counts[word]}")


if __name__ == "__main__":
    main()
