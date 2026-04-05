#!/usr/bin/env python3
"""RSS Reader - Parse OPML files, fetch RSS/Atom feeds, filter and display articles."""

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from time import mktime
from urllib.request import urlopen, Request
from urllib.error import URLError

import feedparser

DEFAULT_OPML = "https://gist.githubusercontent.com/emschwartz/e6d2bf860ccc367fe37ff953ba6de66b/raw/hn-popular-blogs-2025.opml"
USER_AGENT = "RSS-Reader-Skill/1.0"
FETCH_TIMEOUT = 15


def parse_opml(source: str) -> list[dict]:
    """Parse OPML from a URL or file path. Returns list of feed dicts."""
    try:
        if source.startswith(("http://", "https://")):
            req = Request(source, headers={"User-Agent": USER_AGENT})
            with urlopen(req, timeout=FETCH_TIMEOUT) as resp:
                data = resp.read()
            root = ET.fromstring(data)
        else:
            root = ET.parse(source).getroot()
    except Exception as e:
        print(json.dumps({"error": f"Failed to parse OPML: {e}"}))
        sys.exit(1)

    feeds = []
    for outline in root.iter("outline"):
        xml_url = outline.get("xmlUrl")
        if xml_url:
            feeds.append({
                "name": outline.get("text", outline.get("title", "Unknown")),
                "xml_url": xml_url,
                "html_url": outline.get("htmlUrl", ""),
            })
    return feeds


def fetch_single_feed(feed: dict, limit: int, keyword: str | None) -> list[dict]:
    """Fetch a single RSS/Atom feed and return its articles."""
    articles = []
    try:
        d = feedparser.parse(feed["xml_url"], agent=USER_AGENT)
        for entry in d.entries[:limit]:
            title = entry.get("title", "No title")
            summary = entry.get("summary", entry.get("description", ""))
            summary = re.sub(r"<[^>]+>", "", summary)
            if len(summary) > 300:
                summary = summary[:300] + "..."

            link = entry.get("link", "")
            published = ""
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                try:
                    published = datetime.fromtimestamp(mktime(entry.published_parsed)).isoformat()
                except (ValueError, OverflowError):
                    pass
            elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
                try:
                    published = datetime.fromtimestamp(mktime(entry.updated_parsed)).isoformat()
                except (ValueError, OverflowError):
                    pass

            if keyword:
                kw = keyword.lower()
                if kw not in title.lower() and kw not in summary.lower():
                    continue

            articles.append({
                "feed": feed["name"],
                "title": title,
                "link": link,
                "published": published,
                "summary": summary,
            })
    except Exception:
        pass  # Skip feeds that fail to fetch
    return articles


def fetch_feeds(feeds: list[dict], limit: int = 5, keyword: str | None = None,
                feed_name: str | None = None) -> list[dict]:
    """Fetch articles from multiple feeds concurrently."""
    if feed_name:
        name_lower = feed_name.lower()
        feeds = [f for f in feeds if name_lower in f["name"].lower()]
        if not feeds:
            return []

    articles = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {
            executor.submit(fetch_single_feed, feed, limit, keyword): feed
            for feed in feeds
        }
        for future in as_completed(futures):
            articles.extend(future.result())

    # Sort by published date (newest first), entries without dates go last
    articles.sort(key=lambda a: a["published"] or "0000", reverse=True)
    return articles[:limit]


def main():
    parser = argparse.ArgumentParser(description="RSS Reader Skill")
    parser.add_argument("--opml", default=DEFAULT_OPML,
                        help="OPML file path or URL (default: HN popular blogs)")
    parser.add_argument("--limit", type=int, default=20,
                        help="Max number of articles to return (default: 20)")
    parser.add_argument("--keyword", help="Filter articles by keyword")
    parser.add_argument("--list-feeds", action="store_true",
                        help="List all feeds in the OPML without fetching")
    parser.add_argument("--feed", help="Fetch articles from a specific feed by name")
    args = parser.parse_args()

    feeds = parse_opml(args.opml)

    if args.list_feeds:
        result = {"feeds": feeds, "count": len(feeds)}
        print(json.dumps(result, indent=2))
        return

    # When fetching a single feed, give it a higher per-feed limit
    per_feed_limit = args.limit if args.feed else max(5, args.limit)
    articles = fetch_feeds(feeds, limit=per_feed_limit, keyword=args.keyword,
                           feed_name=args.feed)
    articles = articles[:args.limit]

    result = {
        "articles": articles,
        "count": len(articles),
        "source": args.opml,
    }
    if args.keyword:
        result["keyword"] = args.keyword
    if args.feed:
        result["feed_filter"] = args.feed

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
