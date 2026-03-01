# Telegraph Agent Skill

> Publish long-form content to [Telegraph](https://telegra.ph) for instant-view reading in Telegram. Designed for AI agents.

## The Problem

You're an AI agent talking to your user via Telegram. You just generated a 6000-character research report. Now what?

- **Telegram caps messages at 4096 characters** — your report gets truncated or split
- **File attachments require downloads** — friction kills readability
- **Telegraph pages open instantly in Telegram** — tap the link, read in-app, beautiful formatting

This skill gives you a one-command solution: markdown in → Telegraph URL out.

## Quick Start

### 1. Get a Token

```bash
curl -s "https://api.telegra.ph/createAccount" \
  -d "short_name=my-agent" \
  -d "author_name=My Agent" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['result']['access_token'])"
```

Save the token. You'll need it for every publish.

### 2. Configure Token

Pick one (checked in this order):

| Method | How |
|--------|-----|
| CLI argument | `--token YOUR_TOKEN` |
| Environment variable | `export TELEGRAPH_ACCESS_TOKEN=YOUR_TOKEN` |

The env var is the simplest for most agent setups.

### 3. Publish

```bash
# From a markdown file
python scripts/telegraph_publish.py --title "Weekly Report" --file report.md

# From stdin
cat report.md | python scripts/telegraph_publish.py --title "Weekly Report"

# From a string
python scripts/telegraph_publish.py --title "Quick Note" --content "Hello **world**"
```

The script prints a URL like `https://telegra.ph/Weekly-Report-03-01`. Send it to your user.

## Integration

### As an Agent Skill

1. Copy this repo (or just `SKILL.md` + `scripts/`) into your agent's skill directory
2. Set `TELEGRAPH_ACCESS_TOKEN` in your agent's environment
3. Your agent reads `SKILL.md` to know when and how to use it

`SKILL.md` defines trigger conditions (content > 4000 chars, structured reports, etc.) and the publish workflow — most agent frameworks can pick this up directly.

### As a Standalone Script

```bash
export TELEGRAPH_ACCESS_TOKEN="your_token"
python scripts/telegraph_publish.py --title "Title" --file content.md
# → https://telegra.ph/Title-03-01
```

Zero framework dependencies. Just Python 3.

## CLI Reference

```
--title        (required) Page title
--file         Read content from a markdown file
--content      Pass content as a string argument
--author       Author name (default: "Agent")
--author-url   Author profile URL
--token        Telegraph access token (overrides env)
```

**Input priority**: `--file` > `--content` > stdin

**Token priority**: `--token` > `TELEGRAPH_ACCESS_TOKEN` env

## Supported Markdown

Headers (`#` `##` `###`), **bold**, *italic*, `inline code`, fenced code blocks, unordered/ordered lists, blockquotes, [links](https://example.com), horizontal rules.

Covers what most agents produce. No images or tables (Telegraph limitation).

## Dependencies

- Python 3.6+ standard library (zero external dependencies)

## License

MIT — see [LICENSE](LICENSE).
