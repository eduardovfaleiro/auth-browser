import sys
from playwright.sync_api import sync_playwright

SESSION_FILE = "sessao.json"


def main():
    start_url = sys.argv[1] if len(sys.argv) > 1 else "about:blank"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        page.goto(start_url)

        print("\n" + "=" * 60)
        print("Browser aberto. Faça login com sua conta Google.")
        print("A sessão será salva automaticamente após o redirecionamento.")
        print("=" * 60 + "\n")

        page.wait_for_url("**/accounts.google.com/**", timeout=60000)
        page.wait_for_url(
            lambda url: "accounts.google.com" not in url,
            timeout=300000,
        )
        page.wait_for_load_state("networkidle", timeout=30000)

        context.storage_state(path=SESSION_FILE)
        print(f"\nSessão salva em '{SESSION_FILE}'.")
        browser.close()


if __name__ == "__main__":
    main()
