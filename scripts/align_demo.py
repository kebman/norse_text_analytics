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

from nta.model import ids as model_ids
from nta.model.types import Edition
from nta.model.types import Segment
from nta.model.types import Work


DEFAULT_SOURCE_EDITION_ID = "havamal_json_v1"
DEFAULT_TRANSLATION_EDITION_ID = "havamal_en_demo_v1"
DEFAULT_DATA_FILE = REPO_ROOT / "data" / "Hávamál1.json"

# Minimal manual translation for first stanza, line-aligned to source lines.
DEMO_TRANSLATION_LINES = [
    "All doors,",
    "before one walks forward,",
    "should be looked over,",
    "should be looked around,",
    "for it is uncertain to know,",
    "where enemies",
    "sit ahead in the hall.",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a manual segment-level translation alignment demo."
    )
    parser.add_argument(
        "--input",
        type=str,
        default=str(DEFAULT_DATA_FILE),
        help="Path to Havamal JSON (default: data/Hávamál1.json).",
    )
    parser.add_argument(
        "--source-edition-id",
        type=str,
        default=DEFAULT_SOURCE_EDITION_ID,
        help="Edition ID for source (Old Norse) segments.",
    )
    parser.add_argument(
        "--translation-edition-id",
        type=str,
        default=DEFAULT_TRANSLATION_EDITION_ID,
        help="Edition ID for translation demo segments.",
    )
    return parser.parse_args()


def _safe_ref_part(value: str) -> str:
    text = value.strip() or "x"
    text = re.sub(r"\s+", "_", text)
    text = re.sub(r"[^0-9A-Za-z_-]+", "", text)
    return text.lower() or "x"


def segment_id(
    edition_id: str,
    verse_ref: str,
    strophe_ref: str,
    line_ref: int,
) -> str:
    return (
        f"{edition_id}:{_safe_ref_part(verse_ref)}:"
        f"{_safe_ref_part(strophe_ref)}:{line_ref}"
    )


def segment_ref(verse_ref: str, strophe_ref: str, line_ref: int) -> str:
    return f"verse={verse_ref}|strophe={strophe_ref}|line={line_ref}"


def load_first_stanza_lines(input_path: Path) -> tuple[str, str, list[str]]:
    if input_path.exists():
        payload = json.loads(input_path.read_text(encoding="utf-8"))
        verse = payload["poem"]["verses"][0]
        strophe = verse["strophes"][0]
        verse_ref = str(verse.get("verse") or "I.")
        strophe_ref = str(strophe.get("strophe") or "1.")
        lines = [str(line).strip() for line in strophe.get("lines", []) if str(line).strip()]
        if lines:
            return verse_ref, strophe_ref, lines

    # Fallback keeps script usable if input file is absent or malformed.
    return (
        "I.",
        "1.",
        [
            "Gáttir allar,",
            "áðr gangi fram,",
            "um skoðask skyli,",
            "um skyggnast skyli,",
            "því at óvíst er at vita,",
            "hvar óvinir",
            "sitja á fleti fyrir.",
        ],
    )


def main() -> None:
    args = parse_args()

    from nta.graph.db import Neo4jConfig
    from nta.graph.db import get_driver
    from nta.graph.repo import Neo4jRepository

    input_path = Path(args.input)
    verse_ref, strophe_ref, source_lines = load_first_stanza_lines(input_path)

    # Keep one-to-one line mapping for demo; cap to common length.
    pair_count = min(len(source_lines), len(DEMO_TRANSLATION_LINES))
    source_lines = source_lines[:pair_count]
    target_lines = DEMO_TRANSLATION_LINES[:pair_count]

    work = Work(work_id=model_ids.work_id("havamal"), title="Hávamál")
    source_edition = Edition(
        edition_id=args.source_edition_id,
        work_id=work.work_id,
        label="Old Norse source (demo alignment subset)",
        version="v1",
    )
    translation_edition = Edition(
        edition_id=args.translation_edition_id,
        work_id=work.work_id,
        label="English translation demo",
        version="v1",
    )

    config = Neo4jConfig.from_env()
    driver = get_driver(config)
    try:
        repo = Neo4jRepository(driver)
        repo.upsert_work(work)
        repo.upsert_edition(source_edition)
        repo.upsert_edition(translation_edition)
        repo.link_work_edition(work.work_id, source_edition.edition_id)
        repo.link_work_edition(work.work_id, translation_edition.edition_id)
        repo.link_edition_translates(
            translation_edition_id=translation_edition.edition_id,
            source_edition_id=source_edition.edition_id,
        )

        for line_index, (source_text, target_text) in enumerate(
            zip(source_lines, target_lines), start=1
        ):
            ref = segment_ref(verse_ref, strophe_ref, line_index)

            source_segment = Segment(
                segment_id=segment_id(
                    source_edition.edition_id, verse_ref, strophe_ref, line_index
                ),
                edition_id=source_edition.edition_id,
                text=source_text,
                position=line_index,
                ref=ref,
            )
            target_segment = Segment(
                segment_id=segment_id(
                    translation_edition.edition_id, verse_ref, strophe_ref, line_index
                ),
                edition_id=translation_edition.edition_id,
                text=target_text,
                position=line_index,
                ref=ref,
            )

            repo.upsert_segment(source_segment)
            repo.upsert_segment(target_segment)
            repo.link_edition_segment(source_edition.edition_id, source_segment.segment_id)
            repo.link_edition_segment(
                translation_edition.edition_id, target_segment.segment_id
            )
            repo.link_segment_aligned_to(
                segment_id=target_segment.segment_id,
                aligned_segment_id=source_segment.segment_id,
                method="manual",
                confidence=1.0,
            )

        # Future extension: derive token-level translation links from aligned segments.
        print(
            "Created alignment demo: "
            f"edition {translation_edition.edition_id} translates {source_edition.edition_id}; "
            f"aligned_segments={pair_count}"
        )
    finally:
        driver.close()


if __name__ == "__main__":
    main()
