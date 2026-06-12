import sys
import os
from playwright.sync_api import sync_playwright

SESSION_FILE = "sessao.json"
OUTPUT_FILE = "dados/.pagina_atual.txt"


def main():
    if len(sys.argv) < 2:
        print("Uso: python fetch_page.py <url>")
        sys.exit(1)

    url = sys.argv[1]

    if not os.path.exists(SESSION_FILE):
        print(f"ERRO: '{SESSION_FILE}' não encontrado. Execute 'python login.py' primeiro.")
        sys.exit(1)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(storage_state=SESSION_FILE)
        page = context.new_page()

        page.goto(url, wait_until="load", timeout=90000)
        page.wait_for_timeout(1000)

        title = page.title()
        current_url = page.url
        body_text = page.inner_text("body")

        browser.close()

    # Detecta se acabou numa tela de autenticação em vez do conteúdo real
    auth_indicators = [
        "accounts.google.com" in current_url,
        "google.com/accounts" in current_url,
        "sign in" in title.lower(),
        "fazer login" in title.lower(),
    ]
    if any(auth_indicators):
        print(
            "ERRO: Sessão expirada ou inválida — a página retornou tela de login.\n"
            "Execute 'python login.py' para renovar a sessão."
        )
        sys.exit(1)

    os.makedirs("dados", exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(f"URL: {current_url}\n")
        f.write(f"Título: {title}\n")
        f.write("=" * 60 + "\n")
        f.write(body_text)

    print(f"OK: '{title}' — conteúdo salvo em {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
