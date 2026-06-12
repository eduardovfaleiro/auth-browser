# auth-browser

A minimal toolkit for giving Claude Code authenticated access to pages protected by Google OAuth. Authenticate once manually — subsequent sessions reuse the saved state automatically.

## How it works

OAuth flows require human interaction. This project handles that by separating authentication (done once, manually, in a visible browser) from page fetching (automated). The session is persisted as a Playwright storage state file (`sessao.json`) and reused on every subsequent run.

```
login.py          →  sessao.json  →  fetch_page.py  →  dados/.pagina_atual.txt
(manual, once)       (persisted)     (automated)        (page content)
```

## Requirements

- Python 3.8+
- [Claude Code](https://claude.ai/code) (for the `/browser` skill)

## Setup

```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/playwright install chromium
```

## Usage

### Step 1 — Authenticate (once, or when session expires)

```bash
.venv/bin/python login.py https://your-protected-site.com
```

A visible Chromium window opens. Complete the Google login — once you are redirected back to the target site, the session is saved to `sessao.json` and the browser closes automatically.

### Step 2 — Fetch a page

```bash
.venv/bin/python fetch_page.py <url>
```

Loads the saved session, navigates to `<url>`, and writes the page body text to `dados/.pagina_atual.txt`.

### Step 3 — Browse interactively with Claude Code

With Claude Code open in this project, run:

```
/browser <url>
```

Claude fetches the page, reads its content, and answers your questions about it. If the session is missing or expired, it opens the browser for you to log in again automatically.

## Project structure

```
auth-browser/
├── login.py                        # One-time manual login; saves session to sessao.json
├── fetch_page.py                   # Fetches a URL and dumps page text to dados/.pagina_atual.txt
├── requirements.txt
├── .claude/
│   └── skills/browser/SKILL.md    # /browser slash command for Claude Code
├── sessao.json                     # Playwright storage state — gitignored, created by login.py
└── dados/                          # Output directory — gitignored
    └── .pagina_atual.txt
```

## Notes

- `sessao.json` and `dados/` are gitignored — never commit session files.
- Browsers run in non-headless mode (`headless=False`) so OAuth redirects remain visible.
- All scripts use `playwright.sync_api` (synchronous).
- Session duration depends on the target site's OAuth policy; re-run `login.py` when it expires.

## Alternatives

If you need a more complete solution, the official [Playwright MCP server](https://github.com/microsoft/playwright-mcp) by Microsoft exposes 40+ browser automation tools directly to Claude Code and handles session persistence natively.
