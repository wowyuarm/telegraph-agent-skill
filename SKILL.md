---
name: telegraph
description: >
  Publish long-form content to Telegraph for clean, instant-view reading in Telegram.
  Use when sending reports, research results, analysis, documentation, or any content
  that exceeds ~4000 characters. Do NOT use for short messages — send those directly.
  Do NOT use when the user explicitly asks for a file attachment.
---

# Telegraph Publishing

## When to Use

- Response or deliverable exceeds ~4000 characters
- Content has structure (headers, lists, code blocks) that benefits from proper rendering
- Delivering reports, research, analysis, documentation

## When NOT to Use

- Short messages (< 4000 chars) → send directly in Telegram
- User explicitly requests a file download → use file/media attachment

## Token Setup

Get a token (one-time):

```bash
curl -s "https://api.telegra.ph/createAccount" \
  -d "short_name=my-agent" -d "author_name=Agent" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['result']['access_token'])"
```

Store it as `TELEGRAPH_ACCESS_TOKEN` env var, or pass via `--token`.

## How to Publish

```bash
# From a file
python ./scripts/telegraph_publish.py --title "Report Title" --file /path/to/content.md

# From stdin
echo "$CONTENT" | python ./scripts/telegraph_publish.py --title "Report Title"

# From argument
python ./scripts/telegraph_publish.py --title "Title" --content "markdown here"
```

The script outputs a URL. Send that URL to the user.

## Workflow

1. Prepare content as markdown (write to a temp file if needed)
2. Run the script with `--file` (or pipe via stdin) to publish
3. Send the returned URL to the user via your messaging tool
4. Clean up any temp files

## Supported Markdown

Headers (`#`, `##`, `###`), **bold**, *italic*, `inline code`, code blocks, unordered/ordered lists, blockquotes, links, horizontal rules.

## Dependencies

- Python 3.6+ standard library (zero external dependencies)
