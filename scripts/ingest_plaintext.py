from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Allow direct script execution from repo root without package installation.
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from nta.graph.db import Neo4jConfig
from nta.graph.db import get_driver
from nta.graph.repo import Neo4jRepository
from nta.ingest.text import NORMALIZATION_POLICY_V0
from nta.ingest.text import normalize_v0
from nta.ingest.text import tokenize_v0
from nta.model.types import Edition
from nta.model.types import Form
from nta.model.types import Lemma
from nta.model.types import Segment
from nta.model.types import Token
from nta.model.types import Work


NORMALIZATION_POLICY = NORMALIZATION_POLICY_V0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ingest plain text into Neo4j.")
    parser.add_argument("--path", required=True, help="Path to UTF-8 text file.")
    parser.add_argument("--work-id", required=True, help="Work.work_id")
    parser.add_argument("--edition-id", required=True, help="Edition.edition_id")
    parser.add_argument("--source-label", required=True, help="Edition.source_label")
    parser.add_argument(
        "--language-stage",
        required=True,
        help="Language/stage code (for example: on, own, nb, nn).",
    )
    parser.add_argument(
        "--date-start",
        type=int,
        default=None,
        help="Optional Edition.date_start year.",
    )
    parser.add_argument(
        "--date-end",
        type=int,
        default=None,
        help="Optional Edition.date_end year.",
    )
    parser.add_argument(
        "--segment",
        choices=("line", "paragraph"),
        default="line",
        help="Segmentation mode: line (default) or paragraph.",
    )
    return parser.parse_args()


def split_segments(text: str, mode: str) -> list[str]:
    if mode == "line":
        segments: list[str] = []
        for line in text.splitlines():
            stripped = line.strip()
            if stripped:
                segments.append(stripped)
        return segments

    normalized_newlines = text.replace("\r\n", "\n").replace("\r", "\n")
    raw_paragraphs = re.split(r"\n\s*\n+", normalized_newlines)
    paragraphs = [chunk.strip() for chunk in raw_paragraphs if chunk.strip()]
    return paragraphs


def ingest(args: argparse.Namespace) -> tuple[int, int]:
    input_path = Path(args.path)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    text = input_path.read_text(encoding="utf-8")
    segments = split_segments(text, args.segment)

    config = Neo4jConfig.from_env()
    driver = get_driver(config)
    repo = Neo4jRepository(driver)

    work = Work(work_id=args.work_id, title=args.work_id)
    edition = Edition(
        edition_id=args.edition_id,
        work_id=args.work_id,
        label=args.source_label,
        version="plaintext_v1",
    )

    segment_count = 0
    token_count = 0

    try:
        repo.upsert_work(work)
        repo.upsert_edition(edition)
        repo.link_work_edition(work.work_id, edition.edition_id)

        with driver.session() as session:
            session.run(
                """
                MERGE (e:Edition {edition_id: $edition_id})
                SET e.source_label = $source_label,
                    e.language_stage = $language_stage,
                    e.date_start = $date_start,
                    e.date_end = $date_end,
                    e.normalization_policy = $normalization_policy,
                    e.segment_mode = $segment_mode
                """,
                edition_id=args.edition_id,
                source_label=args.source_label,
                language_stage=args.language_stage,
                date_start=args.date_start,
                date_end=args.date_end,
                normalization_policy=NORMALIZATION_POLICY,
                segment_mode=args.segment,
            ).consume()

        for ordinal, segment_text in enumerate(segments, start=1):
            segment_id = f"{args.edition_id}:seg{ordinal}"
            segment = Segment(
                segment_id=segment_id,
                edition_id=args.edition_id,
                text=segment_text,
                position=ordinal,
                ref=str(ordinal),
            )
            repo.upsert_segment(segment)
            repo.link_edition_segment(args.edition_id, segment_id)
            segment_count += 1

            for token_index, surface in enumerate(tokenize_v0(segment_text)):
                token_id = f"{segment_id}:t{token_index}"
                normalized = normalize_v0(surface)
                form_id = f"{args.language_stage}:{surface}"

                token = Token(
                    token_id=token_id,
                    segment_id=segment_id,
                    surface=surface,
                    position=token_index,
                    normalized=normalized,
                )
                form = Form(
                    form_id=form_id,
                    orthography=surface,
                    language=args.language_stage,
                )
                repo.upsert_token_and_form(token=token, form=form)
                repo.link_segment_token(segment_id=segment_id, token_id=token_id)

                # Temporary 1:1 mapping: Form and Lemma share the same key/headword.
                lemma = Lemma(
                    lemma_id=form_id,
                    headword=surface,
                    language=args.language_stage,
                    pos="UNKNOWN",
                )
                repo.upsert_lemma(lemma)
                repo.link_form_lemma(form_id=form.form_id, lemma_id=lemma.lemma_id)

                token_count += 1
    finally:
        driver.close()

    return segment_count, token_count


def main() -> None:
    args = parse_args()
    segments, tokens = ingest(args)
    print(f"Segments ingested: {segments}")
    print(f"Tokens ingested: {tokens}")


if __name__ == "__main__":
    main()
