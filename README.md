# auth-browser

A `/browser` skill for Claude Code — fetches pages behind Google OAuth and loads their content so you can ask questions about them.

## Usage

Inside Claude Code, invoke the skill with a URL:

```
/browser <url>
```

Claude will fetch the page authenticated with your Google account and be ready to answer questions about its content.

**Example:**

```
/browser https://docs.google.com/document/d/abc123/edit
```

## Authentication

On the first run (or when the session expires), Claude opens a browser for you to log in with Google. After login, the session is saved automatically and reused on subsequent calls.

## Setup

**Prerequisite:** Python 3.12+

```bash
git clone <repo>
cd auth-browser
python -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/playwright install chromium
```

Set this project folder as the working directory in Claude Code — the skill is loaded automatically.
