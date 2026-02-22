from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# Allow direct script execution from repo root without package installation.
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


WORK_ID = "havamal"
EDITION_ID = "havamal_gudni_jonsson_print"
LANGUAGE = "Old Norse"
SOURCE_LABEL = "Sæmundar-Edda: Hávamál"
DATE_START = 900
DATE_END = 1100
DATE_APPROX = True
DATE_NOTE = "placeholder; revise later"
PROVENANCE = "Guðni Jónsson print"
NORMALIZATION_POLICY = "punct_strip_whitespace_collapse_v0"
MORPH_ANALYZER = "placeholder"
MORPH_ANALYZER_VERSION = "0.1"
MORPH_POS = "UNKNOWN"
MORPH_CONFIDENCE = 0.0
MORPH_IS_AMBIGUOUS = False
MORPH_IS_ACTIVE = True
ANALYZER_ID = f"{MORPH_ANALYZER}:{MORPH_ANALYZER_VERSION}"
ANALYZER_NAME = "Placeholder Analyzer"
ANALYZER_DESCRIPTION = "Bootstrap analyzer for morphology scaffolding."
ANALYZER_AUTHOR = "norse_text_analytics"
SURROUNDING_PUNCT = " \t\n\r.,;:!?\"'()[]{}<>«»„“”‘’`´…—-"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ingest Havamal JSON into Neo4j.")
    parser.add_argument(
        "--input",
        type=str,
        default=None,
        help="Optional path to input JSON file. Defaults to data/Hávamál1.json.",
    )
    return parser.parse_args()


def resolve_input_path(explicit_path: str | None) -> Path:
    if explicit_path:
        path = Path(explicit_path)
        if not path.exists():
            raise FileNotFoundError(f"Input file not found: {path}")
        return path

    default_path = REPO_ROOT / "data" / "Hávamál1.json"
    if default_path.exists():
        return default_path
    raise FileNotFoundError(f"Input file not found: {default_path}")


def normalize(surface: str) -> str:
    # v0 normalization: strip surrounding punctuation and collapse whitespace.
    normalized = surface.strip(SURROUNDING_PUNCT)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized


def tokenize(line: str) -> list[str]:
    # Split on whitespace, strip punctuation from ends, skip empties.
    tokens: list[str] = []
    for raw in line.split():
        cleaned = raw.strip(SURROUNDING_PUNCT)
        if cleaned:
            tokens.append(cleaned)
    return tokens


def ingest(input_path: Path) -> tuple[int, int]:
    from nta.graph.db import Neo4jConfig
    from nta.graph.db import get_driver

    payload = json.loads(input_path.read_text(encoding="utf-8"))

    information = payload["information"]
    poem = payload["poem"]
    title = poem["title"]
    cover = [str(x) for x in information["cover"]]
    writer = [str(x) for x in information["writer"]]
    verses = poem["verses"]

    config = Neo4jConfig.from_env()
    driver = get_driver(config)

    segment_count = 0
    token_count = 0

    try:
        with driver.session() as session:
            session.run(
                """
                MERGE (w:Work {work_id: $work_id})
                ON CREATE SET w.title = $title
                MERGE (e:Edition {edition_id: $edition_id})
                SET e.title = $title,
                    e.cover = $cover,
                    e.writer = $writer,
                    e.language = $language,
                    e.normalization_policy = $normalization_policy,
                    e.source_label = $source_label,
                    e.date_start = $date_start,
                    e.date_end = $date_end,
                    e.date_approx = $date_approx,
                    e.date_note = $date_note,
                    e.provenance = $provenance
                MERGE (w)-[:HAS_EDITION]->(e)
                """,
                work_id=WORK_ID,
                title=title,
                edition_id=EDITION_ID,
                cover=cover,
                writer=writer,
                language=LANGUAGE,
                normalization_policy=NORMALIZATION_POLICY,
                source_label=SOURCE_LABEL,
                date_start=DATE_START,
                date_end=DATE_END,
                date_approx=DATE_APPROX,
                date_note=DATE_NOTE,
                provenance=PROVENANCE,
            ).consume()

            session.run(
                """
                MERGE (a:Analyzer {analyzer_id: $analyzer_id})
                ON CREATE SET a.name = $name,
                              a.version = $version,
                              a.description = $description,
                              a.author = $author,
                              a.created_at = datetime()
                """,
                analyzer_id=ANALYZER_ID,
                name=ANALYZER_NAME,
                version=MORPH_ANALYZER_VERSION,
                description=ANALYZER_DESCRIPTION,
                author=ANALYZER_AUTHOR,
            ).consume()

            for verse in verses:
                verse_ref = str(verse["verse"])

                for strophe in verse["strophes"]:
                    strophe_ref = str(strophe["strophe"])

                    for line_index, line in enumerate(strophe["lines"]):
                        text = str(line)
                        segment_id = (
                            f"{EDITION_ID}:v{verse_ref}:"
                            f"s{strophe_ref}:l{line_index}"
                        )
                        ref = f"{verse_ref}{strophe_ref}{line_index}"

                        session.run(
                            """
                            MERGE (e:Edition {edition_id: $edition_id})
                            MERGE (s:Segment {segment_id: $segment_id})
                            SET s.verse = $verse,
                                s.strophe = $strophe,
                                s.line_index = $line_index,
                                s.ref = $ref,
                                s.text = $text
                            MERGE (e)-[:HAS_SEGMENT]->(s)
                            """,
                            edition_id=EDITION_ID,
                            segment_id=segment_id,
                            verse=verse_ref,
                            strophe=strophe_ref,
                            line_index=line_index,
                            ref=ref,
                            text=text,
                        ).consume()
                        segment_count += 1

                        for token_index, surface in enumerate(tokenize(text)):
                            normalized = normalize(surface)
                            token_id = f"{segment_id}:t{token_index}"
                            form_id = f"non:{surface}"
                            analysis_id = f"{token_id}:{MORPH_ANALYZER}"

                            session.run(
                                """
                                MERGE (s:Segment {segment_id: $segment_id})
                                MERGE (t:Token {token_id: $token_id})
                                SET t.surface = $surface,
                                    t.normalized = $normalized,
                                    t.position = $position
                                MERGE (f:Form {form_id: $form_id})
                                SET f.orthography = $orthography,
                                    f.language = $language
                                MERGE (m:MorphAnalysis {analysis_id: $analysis_id})
                                ON CREATE SET m.analyzer = $analyzer,
                                              m.analyzer_version = $analyzer_version,
                                              m.confidence = $confidence,
                                              m.pos = $pos,
                                              m.is_ambiguous = $is_ambiguous,
                                              m.created_at = datetime(),
                                              m.supersedes = $supersedes,
                                              m.is_active = $is_active
                                MERGE (a:Analyzer {analyzer_id: $analyzer_id})
                                ON CREATE SET a.name = $analyzer_name,
                                              a.version = $analyzer_version,
                                              a.description = $analyzer_description,
                                              a.author = $analyzer_author,
                                              a.created_at = datetime()
                                MERGE (s)-[:HAS_TOKEN]->(t)
                                MERGE (t)-[:INSTANCE_OF_FORM]->(f)
                                MERGE (t)-[:HAS_ANALYSIS]->(m)
                                MERGE (m)-[:PRODUCED_BY]->(a)
                                """,
                                segment_id=segment_id,
                                token_id=token_id,
                                surface=surface,
                                normalized=normalized,
                                position=token_index,
                                form_id=form_id,
                                orthography=surface,
                                language=LANGUAGE,
                                analysis_id=analysis_id,
                                analyzer_id=ANALYZER_ID,
                                analyzer=MORPH_ANALYZER,
                                analyzer_name=ANALYZER_NAME,
                                analyzer_version=MORPH_ANALYZER_VERSION,
                                analyzer_description=ANALYZER_DESCRIPTION,
                                analyzer_author=ANALYZER_AUTHOR,
                                confidence=MORPH_CONFIDENCE,
                                pos=MORPH_POS,
                                is_ambiguous=MORPH_IS_AMBIGUOUS,
                                supersedes=None,
                                is_active=MORPH_IS_ACTIVE,
                            ).consume()
                            token_count += 1
    finally:
        driver.close()

    return segment_count, token_count


def main() -> None:
    args = parse_args()
    input_path = resolve_input_path(args.input)
    segment_count, token_count = ingest(input_path)
    print(f"Segments ingested: {segment_count}")
    print(f"Tokens ingested: {token_count}")


if __name__ == "__main__":
    main()
