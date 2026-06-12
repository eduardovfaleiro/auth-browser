import os
import sys
import pytest
from unittest.mock import MagicMock, patch

# conftest.py stubs playwright before this import
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import login  # noqa: E402


def _make_playwright_stack():
    page = MagicMock()
    context = MagicMock()
    context.new_page.return_value = page
    browser = MagicMock()
    browser.new_context.return_value = context
    playwright = MagicMock()
    playwright.chromium.launch.return_value = browser
    ctx_mgr = MagicMock()
    ctx_mgr.__enter__ = MagicMock(return_value=playwright)
    ctx_mgr.__exit__ = MagicMock(return_value=False)
    return ctx_mgr, playwright, browser, context, page


class TestURLHandling:
    def test_defaults_to_about_blank_when_no_arg(self, tmp_path):
        ctx_mgr, _, _, _, page = _make_playwright_stack()
        with patch("sys.argv", ["login.py"]):
            with patch.object(login, "SESSION_FILE", str(tmp_path / "sessao.json")):
                with patch.object(login, "sync_playwright", return_value=ctx_mgr):
                    login.main()
        page.goto.assert_called_once_with("about:blank")

    def test_uses_provided_url_arg(self, tmp_path):
        ctx_mgr, _, _, _, page = _make_playwright_stack()
        with patch("sys.argv", ["login.py", "https://myapp.example.com"]):
            with patch.object(login, "SESSION_FILE", str(tmp_path / "sessao.json")):
                with patch.object(login, "sync_playwright", return_value=ctx_mgr):
                    login.main()
        page.goto.assert_called_once_with("https://myapp.example.com")


class TestSessionSaving:
    def test_saves_session_to_configured_path(self, tmp_path):
        ctx_mgr, _, _, context, _ = _make_playwright_stack()
        session_path = str(tmp_path / "sessao.json")
        with patch("sys.argv", ["login.py", "https://example.com"]):
            with patch.object(login, "SESSION_FILE", session_path):
                with patch.object(login, "sync_playwright", return_value=ctx_mgr):
                    login.main()
        context.storage_state.assert_called_once_with(path=session_path)

    def test_prints_session_saved_confirmation(self, tmp_path, capsys):
        ctx_mgr, _, _, _, _ = _make_playwright_stack()
        session_path = str(tmp_path / "sessao.json")
        with patch("sys.argv", ["login.py"]):
            with patch.object(login, "SESSION_FILE", session_path):
                with patch.object(login, "sync_playwright", return_value=ctx_mgr):
                    login.main()
        out = capsys.readouterr().out
        assert "sessao.json" in out or session_path in out


class TestBrowserLifecycle:
    def test_browser_launched_not_headless(self, tmp_path):
        ctx_mgr, playwright, _, _, _ = _make_playwright_stack()
        with patch("sys.argv", ["login.py"]):
            with patch.object(login, "SESSION_FILE", str(tmp_path / "sessao.json")):
                with patch.object(login, "sync_playwright", return_value=ctx_mgr):
                    login.main()
        playwright.chromium.launch.assert_called_once_with(headless=False)

    def test_browser_closed_after_login(self, tmp_path):
        ctx_mgr, _, browser, _, _ = _make_playwright_stack()
        with patch("sys.argv", ["login.py"]):
            with patch.object(login, "SESSION_FILE", str(tmp_path / "sessao.json")):
                with patch.object(login, "sync_playwright", return_value=ctx_mgr):
                    login.main()
        browser.close.assert_called_once()

    def test_waits_for_google_auth_redirect(self, tmp_path):
        ctx_mgr, _, _, _, page = _make_playwright_stack()
        with patch("sys.argv", ["login.py", "https://example.com"]):
            with patch.object(login, "SESSION_FILE", str(tmp_path / "sessao.json")):
                with patch.object(login, "sync_playwright", return_value=ctx_mgr):
                    login.main()
        first_call = page.wait_for_url.call_args_list[0]
        assert "accounts.google.com" in str(first_call)

    def test_waits_for_network_idle_after_redirect(self, tmp_path):
        ctx_mgr, _, _, _, page = _make_playwright_stack()
        with patch("sys.argv", ["login.py"]):
            with patch.object(login, "SESSION_FILE", str(tmp_path / "sessao.json")):
                with patch.object(login, "sync_playwright", return_value=ctx_mgr):
                    login.main()
        page.wait_for_load_state.assert_called_once_with("networkidle", timeout=30000)
