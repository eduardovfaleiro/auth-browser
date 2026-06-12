import os
import sys
import pytest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import fetch_page  # noqa: E402  (conftest stubs playwright before this)


def _make_page(title="My Page", url="https://example.com", body="Page content"):
    page = MagicMock()
    page.title.return_value = title
    page.url = url
    page.inner_text.return_value = body
    return page


def _make_playwright_stack(page):
    context = MagicMock()
    context.new_page.return_value = page
    browser = MagicMock()
    browser.new_context.return_value = context
    playwright = MagicMock()
    playwright.chromium.launch.return_value = browser
    ctx_mgr = MagicMock()
    ctx_mgr.__enter__ = MagicMock(return_value=playwright)
    ctx_mgr.__exit__ = MagicMock(return_value=False)
    return ctx_mgr, browser


class TestArgValidation:
    def test_exits_when_no_url_argument(self, capsys):
        with patch("sys.argv", ["fetch_page.py"]):
            with pytest.raises(SystemExit) as exc:
                fetch_page.main()
        assert exc.value.code == 1
        assert "Uso:" in capsys.readouterr().out

    def test_exits_when_session_file_missing(self, capsys, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)  # no sessao.json here
        with patch("sys.argv", ["fetch_page.py", "https://example.com"]):
            with pytest.raises(SystemExit) as exc:
                fetch_page.main()
        assert exc.value.code == 1
        out = capsys.readouterr().out
        assert "ERRO" in out
        assert "login.py" in out


class TestAuthDetection:
    @pytest.fixture(autouse=True)
    def _cwd(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "sessao.json").write_text("{}")
        self.output_path = tmp_path / "dados" / ".pagina_atual.txt"

    def _run(self, page, url="https://example.com"):
        ctx_mgr, browser = _make_playwright_stack(page)
        with patch("sys.argv", ["fetch_page.py", url]):
            with patch.object(fetch_page, "sync_playwright", return_value=ctx_mgr):
                fetch_page.main()
        return browser

    @pytest.mark.parametrize("bad_url", [
        "https://accounts.google.com/signin",
        "https://www.google.com/accounts/login",
    ])
    def test_exits_on_google_auth_url(self, bad_url, capsys):
        page = _make_page(url=bad_url)
        ctx_mgr, _ = _make_playwright_stack(page)
        with patch("sys.argv", ["fetch_page.py", "https://example.com"]):
            with patch.object(fetch_page, "sync_playwright", return_value=ctx_mgr):
                with pytest.raises(SystemExit) as exc:
                    fetch_page.main()
        assert exc.value.code == 1
        assert "Sessão expirada" in capsys.readouterr().out

    @pytest.mark.parametrize("auth_title", ["Sign in - Google", "Fazer login"])
    def test_exits_on_auth_page_title(self, auth_title):
        page = _make_page(title=auth_title, url="https://example.com")
        ctx_mgr, _ = _make_playwright_stack(page)
        with patch("sys.argv", ["fetch_page.py", "https://example.com"]):
            with patch.object(fetch_page, "sync_playwright", return_value=ctx_mgr):
                with pytest.raises(SystemExit) as exc:
                    fetch_page.main()
        assert exc.value.code == 1

    def test_succeeds_on_normal_page(self, capsys):
        page = _make_page(title="Dashboard", url="https://app.example.com")
        self._run(page, url="https://app.example.com")
        out = capsys.readouterr().out
        assert "OK" in out
        assert "Dashboard" in out


class TestFileOutput:
    @pytest.fixture(autouse=True)
    def _cwd(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "sessao.json").write_text("{}")
        self.output_path = tmp_path / "dados" / ".pagina_atual.txt"

    def _run(self, page, url="https://example.com"):
        ctx_mgr, browser = _make_playwright_stack(page)
        with patch("sys.argv", ["fetch_page.py", url]):
            with patch.object(fetch_page, "sync_playwright", return_value=ctx_mgr):
                fetch_page.main()
        return browser

    def test_creates_output_directory_if_missing(self, tmp_path):
        assert not (tmp_path / "dados").exists()
        self._run(_make_page())
        assert (tmp_path / "dados").exists()

    def test_output_contains_url_title_and_body(self):
        page = _make_page(title="My Title", url="https://example.com/page", body="Body content")
        self._run(page, url="https://example.com/page")
        content = self.output_path.read_text(encoding="utf-8")
        assert "https://example.com/page" in content
        assert "My Title" in content
        assert "Body content" in content

    def test_output_uses_final_url_after_redirects(self):
        page = _make_page(title="Result", url="https://final.example.com")
        self._run(page, url="https://original.example.com")
        content = self.output_path.read_text(encoding="utf-8")
        assert "https://final.example.com" in content

    def test_browser_closed_on_success(self):
        browser = self._run(_make_page())
        browser.close.assert_called_once()

    def test_browser_closed_on_auth_error(self):
        page = _make_page(url="https://accounts.google.com/signin")
        ctx_mgr, browser = _make_playwright_stack(page)
        with patch("sys.argv", ["fetch_page.py", "https://example.com"]):
            with patch.object(fetch_page, "sync_playwright", return_value=ctx_mgr):
                with pytest.raises(SystemExit):
                    fetch_page.main()
        browser.close.assert_called_once()
