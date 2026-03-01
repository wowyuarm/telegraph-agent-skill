#!/usr/bin/env python3
"""Publish content to Telegraph and return the URL.

Usage:
    # From file:
    python telegraph_publish.py --title "My Report" --file report.md

    # From stdin:
    echo "# Hello" | python telegraph_publish.py --title "My Report"

    # From argument:
    python telegraph_publish.py --title "My Report" --content "Hello **world**"

Token sources (priority):
1) --token argument
2) TELEGRAPH_ACCESS_TOKEN environment variable
"""

import argparse
import json
import os
import re
import sys
import urllib.request
from pathlib import Path


def load_token(cli_token: str | None = None) -> str:
    if cli_token:
        return cli_token

    env_token = os.environ.get("TELEGRAPH_ACCESS_TOKEN")
    if env_token:
        return env_token

    print(
        "Error: No token found. Provide --token or set TELEGRAPH_ACCESS_TOKEN.\n"
        "Register one with: curl -s https://api.telegra.ph/createAccount "
        '-d "short_name=my-agent" -d "author_name=Agent"',
        file=sys.stderr,
    )
    sys.exit(1)


def md_to_telegraph_nodes(md_text: str) -> list:
    """Convert markdown to Telegraph Node format (simplified but covers common cases)."""
    nodes = []
    lines = md_text.split("\n")
    i = 0

    while i < len(lines):
        line = lines[i]

        # Headers
        if line.startswith("### "):
            nodes.append({"tag": "h4", "children": ensure_children(inline_format(line[4:]))})
        elif line.startswith("## "):
            nodes.append({"tag": "h3", "children": ensure_children(inline_format(line[3:]))})
        elif line.startswith("# "):
            nodes.append({"tag": "h3", "children": ensure_children(inline_format(line[2:]))})

        # Code blocks
        elif line.startswith("```"):
            lang = line[3:].strip()
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                code_lines.append(lines[i])
                i += 1
            nodes.append({"tag": "pre", "children": ["\n".join(code_lines)]})

        # Unordered list items
        elif re.match(r"^[-*]\s", line):
            list_items = []
            while i < len(lines) and re.match(r"^[-*]\s", lines[i]):
                item_text = re.sub(r"^[-*]\s", "", lines[i])
                list_items.append({"tag": "li", "children": ensure_children(inline_format(item_text))})
                i += 1
            nodes.append({"tag": "ul", "children": list_items})
            continue  # skip i increment at bottom

        # Ordered list items
        elif re.match(r"^\d+\.\s", line):
            list_items = []
            while i < len(lines) and re.match(r"^\d+\.\s", lines[i]):
                item_text = re.sub(r"^\d+\.\s", "", lines[i])
                list_items.append({"tag": "li", "children": ensure_children(inline_format(item_text))})
                i += 1
            nodes.append({"tag": "ol", "children": list_items})
            continue

        # Blockquote
        elif line.startswith("> "):
            quote_lines = []
            while i < len(lines) and lines[i].startswith("> "):
                quote_lines.append(lines[i][2:])
                i += 1
            nodes.append({"tag": "blockquote", "children": ensure_children(inline_format("\n".join(quote_lines)))})
            continue

        # Horizontal rule
        elif re.match(r"^[-*_]{3,}\s*$", line):
            nodes.append({"tag": "hr"})

        # Empty line → skip
        elif line.strip() == "":
            pass

        # Regular paragraph
        else:
            # Collect consecutive non-special lines as one paragraph
            para_lines = [line]
            i += 1
            while i < len(lines) and lines[i].strip() and not lines[i].startswith(("#", "```", ">", "- ", "* ")) and not re.match(r"^\d+\.\s", lines[i]) and not re.match(r"^[-*_]{3,}\s*$", lines[i]):
                para_lines.append(lines[i])
                i += 1
            nodes.append({"tag": "p", "children": ensure_children(inline_format(" ".join(para_lines)))})
            continue

        i += 1

    return nodes


def inline_format(text: str):
    """Handle bold, italic, code, and links inline formatting.
    Returns a list of nodes/strings for Telegraph."""
    # For simplicity, handle the most common patterns and return as mixed list
    parts = []
    # Process inline code first
    segments = re.split(r'(`[^`]+`)', text)
    for seg in segments:
        if seg.startswith('`') and seg.endswith('`'):
            parts.append({"tag": "code", "children": [seg[1:-1]]})
        else:
            # Bold
            sub_parts = re.split(r'(\*\*[^*]+\*\*)', seg)
            for sp in sub_parts:
                if sp.startswith('**') and sp.endswith('**'):
                    parts.append({"tag": "strong", "children": [sp[2:-2]]})
                else:
                    # Italic
                    it_parts = re.split(r'(\*[^*]+\*)', sp)
                    for ip in it_parts:
                        if ip.startswith('*') and ip.endswith('*') and len(ip) > 2:
                            parts.append({"tag": "em", "children": [ip[1:-1]]})
                        else:
                            # Links
                            link_parts = re.split(r'(\[[^\]]+\]\([^)]+\))', ip)
                            for lp in link_parts:
                                m = re.match(r'\[([^\]]+)\]\(([^)]+)\)', lp)
                                if m:
                                    parts.append({"tag": "a", "attrs": {"href": m.group(2)}, "children": [m.group(1)]})
                                elif lp:
                                    parts.append(lp)

    if len(parts) == 1:
        return parts[0]
    # Telegraph expects a flat list of children, not nested lists
    return parts


def ensure_children(result):
    """Wrap inline_format result into a flat children list."""
    r = result
    if isinstance(r, list):
        return r
    return [r]


def publish(title: str, content: str, author_name: str = "Agent", author_url: str | None = None, token: str | None = None) -> str:
    access_token = load_token(cli_token=token)
    nodes = md_to_telegraph_nodes(content)

    payload = {
        "access_token": access_token,
        "title": title,
        "author_name": author_name,
        "content": nodes,
    }
    if author_url:
        payload["author_url"] = author_url

    data = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(
        "https://api.telegra.ph/createPage",
        data=data,
        headers={"Content-Type": "application/json"},
    )
    resp = urllib.request.urlopen(req)
    result = json.loads(resp.read())

    if not result.get("ok"):
        print(f"Error: {result}", file=sys.stderr)
        sys.exit(1)

    return result["result"]["url"]


def main():
    parser = argparse.ArgumentParser(description="Publish to Telegraph")
    parser.add_argument("--title", required=True, help="Page title")
    parser.add_argument("--content", help="Content string")
    parser.add_argument("--file", help="Read content from file")
    parser.add_argument("--author", default="Agent", help="Author name")
    parser.add_argument("--author-url", help="Author URL")
    parser.add_argument("--token", help="Telegraph access token")
    args = parser.parse_args()

    if args.file:
        content = Path(args.file).read_text(encoding="utf-8")
    elif args.content:
        content = args.content
    else:
        content = sys.stdin.read()

    url = publish(args.title, content, args.author, args.author_url, args.token)
    print(url)


if __name__ == "__main__":
    main()
