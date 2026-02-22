# Norse Text Analytics

Some programmatic treatment of Old Norse texts.

Just a hobby project. Perhaps it may also be of use to others.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
python3 scripts/apply_schema.py
```

### `bin/scrapeHávamál.py`

Scrape the Old Norse version of Hávamál from Heimskringla.no,  and print the verses in the terminal.

### `bin/testReadHávamál1.py`

Read the JSON-prepared version of Hávamál in `data/havamal1.json` and print the first strophe in Verse I.

### `bin/numWordsHávamál.py`

Simple count of how many times the same word occurrs in Hávamál.

### `data/Hávamál1.json`

A JSON-structured file containing Hávamál. Perhaps there are better ways to structure it, but at least in theory it makes the text a little easier to work with, line by line, or verse by verse, including access to metadata such as the transliterator.
