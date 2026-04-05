---
name: rss-reader
description: >
  Use this skill when the user asks to read RSS feeds, check blogs, browse or import OPML files,
  get news summaries, fetch articles from feeds, or anything related to RSS/Atom content.
  Triggers on: "read my feeds", "check blogs", "what's new on RSS", "import OPML",
  "show me articles", "news from feeds", "latest blog posts", "fetch RSS".
version: 1.0.0
user-invocable: true
allowed-tools:
  - Read
  - Write
  - Bash
  - WebFetch
---

# RSS Reader

You are an RSS feed reader. You parse OPML files, fetch RSS/Atom feeds, and present articles to the user.

## How to use the script

The core logic is in `scripts/rss_reader.py` relative to this skill directory. Run it with the project's Python venv:

```bash
"$PROJECT_DIR/.venv/Scripts/python" "$SKILL_DIR/scripts/rss_reader.py" [OPTIONS]
```

On Mac/Linux, use `.venv/bin/python` instead of `.venv/Scripts/python`.

### Commands

| Command | Description |
|---------|-------------|
| `--list-feeds` | List all feeds in the OPML |
| `--limit N` | Max articles to return (default: 20) |
| `--keyword TERM` | Filter articles containing the keyword |
| `--feed NAME` | Show articles from a specific feed (partial match) |
| `--opml URL_OR_PATH` | Use a custom OPML source |

### Default OPML
If no `--opml` is provided, the script uses the HN Popular Blogs 2025 OPML:
`https://gist.githubusercontent.com/emschwartz/e6d2bf860ccc367fe37ff953ba6de66b/raw/hn-popular-blogs-2025.opml`

## Presenting results

- The script outputs JSON to stdout. Parse it and present results in a readable format.
- For **--list-feeds**: Show a table or numbered list of feed names and URLs.
- For **articles**: Show each article with its feed name, title, date, summary, and link.
- Use markdown formatting for readability.
- If the user wants to read a full article, use WebFetch to retrieve and summarize it.

## Handling arguments from $ARGUMENTS

Parse `$ARGUMENTS` to extract flags. Examples:
- `/rss-reader` → run with defaults (show recent articles)
- `/rss-reader --keyword rust` → filter by "rust"
- `/rss-reader --list-feeds` → list feeds only
- `/rss-reader --feed simonwillison.net --limit 10` → 10 articles from that feed
- `/rss-reader --opml ./my-feeds.opml` → use a local OPML file

Pass `$ARGUMENTS` directly to the script as command-line arguments.

## Error handling

- If the OPML source fails to load, tell the user and suggest checking the URL/path.
- If no articles match a keyword filter, let the user know and suggest broadening the search.
- If feedparser is not installed, run: `"$PROJECT_DIR/.venv/Scripts/pip" install feedparser`
