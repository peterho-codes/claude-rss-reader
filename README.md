# claude-rss-reader

A [Claude Code](https://claude.ai/code) skill that reads RSS/Atom feeds from OPML files. Parse feeds, browse articles, filter by keyword, and summarize content — all from within Claude Code.

## Installation

1. Clone this repo into your project or Claude Code skills directory:
   ```bash
   git clone https://github.com/YOUR_USERNAME/claude-rss-reader.git
   ```

2. Install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # or .venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```

3. The skill is located in `.claude/skills/rss-reader/` and will be automatically picked up by Claude Code.

## Usage

Invoke the skill directly:

```
/rss-reader                              # Show recent articles from all feeds
/rss-reader --list-feeds                 # List all 92 feeds in the default OPML
/rss-reader --keyword "rust"             # Filter articles by keyword
/rss-reader --feed simonwillison.net     # Articles from a specific blog
/rss-reader --limit 10                   # Control number of results
/rss-reader --opml ./my-feeds.opml       # Use your own OPML file
```

Or use natural language — e.g., "check my RSS feeds", "what's new on the blogs", "show me articles about Python".

## Default Feed Source

By default, the skill reads from the [HN Popular Blogs 2025](https://gist.github.com/emschwartz/e6d2bf860ccc367fe37ff953ba6de66b) OPML — a curated list of ~92 popular blogs from the Hacker News community. You can override this with any OPML file via the `--opml` flag.

## Structure

```
.claude/skills/rss-reader/
├── SKILL.md              # Skill definition (triggers, instructions)
└── scripts/
    └── rss_reader.py     # Core logic: OPML parsing, feed fetching, filtering
```
