from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

# Allow direct script execution from repo root without package installation.
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

TOP_FORMS_QUERY = """
MATCH (l:Lemma {lemma_id: $lemma_id})<-[:REALIZES]-(f:Form)<-[:INSTANCE_OF_FORM]-(t:Token)
MATCH (s:Segment)-[:HAS_TOKEN]->(t)
MATCH (e:Edition)-[:HAS_SEGMENT]->(s)
WHERE ($from_year IS NULL OR COALESCE(e.date_end, e.date_start, 999999) >= $from_year)
  AND ($to_year IS NULL OR COALESCE(e.date_start, e.date_end, -999999) <= $to_year)
  AND ($source_like IS NULL OR toLower(COALESCE(e.source_label, "")) CONTAINS toLower($source_like))
RETURN t.surface AS surface,
       count(*) AS freq
ORDER BY freq DESC, surface ASC
LIMIT $limit
"""

TOP_FORMS_BY_SOURCE_FALLBACK_QUERY = """
MATCH (l:Lemma {lemma_id: $lemma_id})<-[:REALIZES]-(f:Form)<-[:INSTANCE_OF_FORM]-(t:Token)
MATCH (s:Segment)-[:HAS_TOKEN]->(t)
MATCH (e:Edition)-[:HAS_SEGMENT]->(s)
WHERE ($source_like IS NULL OR toLower(COALESCE(e.source_label, "")) CONTAINS toLower($source_like))
RETURN COALESCE(e.source_label, "(unknown source)") AS source_label,
       e.date_start AS date_start,
       e.date_end AS date_end,
       t.surface AS surface,
       count(*) AS freq
ORDER BY source_label ASC, freq DESC, surface ASC
LIMIT $limit
"""

FEATURE_COUNTS_QUERY = """
MATCH (l:Lemma {lemma_id: $lemma_id})<-[:ANALYZES_AS]-(m:MorphAnalysis)<-[:HAS_ANALYSIS]-(t:Token)
MATCH (s:Segment)-[:HAS_TOKEN]->(t)
MATCH (e:Edition)-[:HAS_SEGMENT]->(s)
WHERE ($from_year IS NULL OR COALESCE(e.date_end, e.date_start, 999999) >= $from_year)
  AND ($to_year IS NULL OR COALESCE(e.date_start, e.date_end, -999999) <= $to_year)
  AND ($source_like IS NULL OR toLower(COALESCE(e.source_label, "")) CONTAINS toLower($source_like))
OPTIONAL MATCH (m)-[:HAS_FEATURE]->(f_case:Feature {key: "case"})
OPTIONAL MATCH (m)-[:HAS_FEATURE]->(f_number:Feature {key: "number"})
OPTIONAL MATCH (m)-[:HAS_FEATURE]->(f_gender:Feature {key: "gender"})
RETURN COALESCE(f_case.value, "NA") AS case,
       COALESCE(f_number.value, "NA") AS number,
       COALESCE(f_gender.value, "NA") AS gender,
       count(*) AS freq
ORDER BY freq DESC, case, number, gender
LIMIT $limit
"""

EXAMPLES_QUERY = """
MATCH (l:Lemma {lemma_id: $lemma_id})<-[:REALIZES]-(f:Form)<-[:INSTANCE_OF_FORM]-(t:Token)
MATCH (s:Segment)-[:HAS_TOKEN]->(t)
MATCH (e:Edition)-[:HAS_SEGMENT]->(s)
WHERE ($from_year IS NULL OR COALESCE(e.date_end, e.date_start, 999999) >= $from_year)
  AND ($to_year IS NULL OR COALESCE(e.date_start, e.date_end, -999999) <= $to_year)
  AND ($source_like IS NULL OR toLower(COALESCE(e.source_label, "")) CONTAINS toLower($source_like))
RETURN COALESCE(e.source_label, "(unknown source)") AS source_label,
       e.date_start AS date_start,
       e.date_end AS date_end,
       s.ref AS segment_ref,
       t.surface AS surface,
       s.text AS segment_text
ORDER BY COALESCE(e.date_start, 999999), source_label, segment_ref, t.position
LIMIT $limit
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Report inflection observations for a lemma.")
    parser.add_argument("--lemma-id", required=True, help="Lemma identifier (required).")
    parser.add_argument("--from-year", type=int, default=None, help="Optional inclusive lower bound year.")
    parser.add_argument("--to-year", type=int, default=None, help="Optional inclusive upper bound year.")
    parser.add_argument(
        "--source-like",
        default=None,
        help="Optional case-insensitive substring filter on Edition.source_label.",
    )
    parser.add_argument("--limit", type=int, default=20, help="Max rows per section (default: 20).")
    return parser.parse_args()


def print_rows(title: str, rows: list[dict[str, Any]]) -> None:
    print(f"\n== {title} ==")
    if not rows:
        print("(no rows)")
        return
    for row in rows:
        parts = [f"{k}={row[k]}" for k in row]
        print(" | ".join(parts))


def main() -> None:
    args = parse_args()
    from nta.graph.db import Neo4jConfig
    from nta.graph.db import get_driver

    params = {
        "lemma_id": args.lemma_id,
        "from_year": args.from_year,
        "to_year": args.to_year,
        "source_like": args.source_like,
        "limit": args.limit,
    }

    config = Neo4jConfig.from_env()
    driver = get_driver(config)
    try:
        with driver.session() as session:
            if args.from_year is None and args.to_year is None:
                top_forms_result = session.run(TOP_FORMS_BY_SOURCE_FALLBACK_QUERY, **params)
            else:
                top_forms_result = session.run(TOP_FORMS_QUERY, **params)

            feature_result = session.run(FEATURE_COUNTS_QUERY, **params)
            examples_result = session.run(EXAMPLES_QUERY, **params)

            top_forms = [record.data() for record in top_forms_result]
            feature_rows = [record.data() for record in feature_result]
            examples = [record.data() for record in examples_result]

            print(f"lemma_id={args.lemma_id}")
            print(
                "filters="
                f"from_year={args.from_year},to_year={args.to_year},"
                f"source_like={args.source_like},limit={args.limit}"
            )

            if args.from_year is None and args.to_year is None:
                print_rows("Top surfaces by source/date fallback", top_forms)
            else:
                print_rows("Top observed surfaces", top_forms)

            print_rows("Morph feature counts (case/number/gender)", feature_rows)
            print_rows("Example attestations", examples)
    finally:
        driver.close()


if __name__ == "__main__":
    main()
