# /browser

Acessa uma URL em site protegido por Google OAuth e carrega o conteúdo para que o usuário possa fazer perguntas sobre ele.

## Como usar

```
/browser <url>
```

## Restrições

- **Nunca** crie, edite, sobrescreva ou delete arquivos do projeto (`fetch_page.py`, `login.py`, `requirements.txt`, etc.).
- Se identificar que uma mudança no código seria útil, **descreva a sugestão e pergunte ao usuário** antes de qualquer ação. Nunca aplique por conta própria.
- Comandos permitidos: apenas `fetch_page.py` e `login.py` via Bash, e leitura de `dados/.pagina_atual.txt`.

## Instruções

Quando o usuário invocar esta skill com uma URL:

### 0. Setup (executar antes de qualquer outra coisa)

```bash
which uv || curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"
uvx playwright install chromium
```

### 1. Buscar a página

```bash
cd "$(git rev-parse --show-toplevel)" && uv run --with playwright fetch_page.py <url>
```

### 2. Se sessão ausente ou expirada

Se o resultado indicar sessão ausente (`ERRO: 'sessao.json' não encontrado`) ou expirada:

- Informe o usuário: "Abrindo browser para login — faça login com sua conta Google e a sessão será salva automaticamente."
- Execute o login com timeout de 6 minutos:
  ```bash
  cd "$(git rev-parse --show-toplevel)" && uv run --with playwright login.py <url>
  ```
  (timeout: 360000ms)
- Após o login completar, execute `fetch_page.py` novamente:
  ```bash
  cd "$(git rev-parse --show-toplevel)" && uv run --with playwright fetch_page.py <url>
  ```

### 3. Se retornar `OK:`

- Leia o arquivo `dados/.pagina_atual.txt`
- Informe ao usuário o título da página que foi carregada e diga que está pronto para responder perguntas sobre o conteúdo

### 4. A partir daí

Responda as perguntas do usuário com base no conteúdo lido. Se o usuário pedir para acessar outra URL, repita o processo a partir do passo 1 (sem repetir o setup).
