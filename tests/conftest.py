import sys
from unittest.mock import MagicMock

# Inject a fake playwright into sys.modules so login.py / fetch_page.py
# can be imported without the real Playwright being installed.
_playwright_stub = MagicMock()
sys.modules.setdefault("playwright", _playwright_stub)
sys.modules.setdefault("playwright.sync_api", _playwright_stub.sync_api)
