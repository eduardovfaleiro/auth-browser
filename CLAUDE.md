# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project purpose

Automate access to pages on `wiki.bridge.ufsc.tech`, which is protected by Google OAuth via the institutional domain `bridge.ufsc.br`. Because the OAuth flow requires human interaction, authentication is done once manually and the session is persisted in `sessao.json` (Playwright storage state — cookies + localStorage). Subsequent runs load this file to bypass the login wall.

## Setup

```bash
# Install dependencies
python -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/playwright install chromium
```

## Workflow

**Step 1 — authenticate (once, or when session expires):**
```bash
.venv/bin/python login.py
```
Opens a visible Chromium window. Optionally pass the target URL as argument (`python login.py https://site.example.com`) to open directly there. Complete the Google login — once redirected back to the target site, the session is saved to `sessao.json` and the browser closes automatically.

**Step 2 — fetch a page:**
```bash
.venv/bin/python fetch_page.py <url>
```
Loads the session, navigates to `<url>`, and writes the page body text to `dados/.pagina_atual.txt`.

## Architecture

| File | Role |
|------|------|
| `login.py` | One-time manual login; saves session state to `sessao.json` |
| `fetch_page.py` | General-purpose fetcher; takes a URL argument, dumps page text to `dados/.pagina_atual.txt` |
| `sessao.json` | Playwright browser storage state (gitignored) |
| `dados/` | Output directory (gitignored) |

All scripts use `playwright.sync_api` (synchronous). Browsers are launched non-headless (`headless=False`) so OAuth redirects are visible.

## /browser skill

The `/browser <url>` slash command (defined in `.claude/skills/browser/SKILL.md`) wraps `fetch_page.py` — it fetches the URL, reads `dados/.pagina_atual.txt`, and answers questions about the page content. Use it to interactively explore authenticated pages.
