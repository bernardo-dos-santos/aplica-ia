# Projeto AplicaAI

## Projeto
Assistente de candidaturas a estágio que faz tudo menos o último clique. Visão, decisões e roteiro completos em `CONTEXTO.md` — leia a seção relevante antes de uma tarefa nova.

- Stack: Python 3.12, uv, FastAPI + HTMX/Jinja2, Pydantic, SQLAlchemy + Alembic (SQLite local, Postgres na Fase 2), httpx, SDK `anthropic`, Playwright (Fase 1.5), pytest, Ruff, mypy, Docker. Cloud (Fase 2): AWS Lambda, EventBridge, S3, SSM, Terraform.
- Como rodar: `uv sync` e `uv run fastapi dev src/aplica/web/app.py` (ou `docker compose up`).
- Como testar: `uv run pytest tests/<arquivo>` (um módulo por vez, depois tudo), `uv run ruff check . && uv run mypy src`, evals com `uv run python evals/run.py`.
- Estrutura principal: `src/aplica/` com `sources/` (adaptadores de fonte, interface comum), `filtering/` (regras fixas), `screening/` (triagem com Claude), `preparation/`, `autofill/` (Playwright), `tracker/`, `db/`, `web/`; `tests/fixtures/` (respostas gravadas), `evals/`, `infra/` (Terraform).
- Convenções:
  - Código e identificadores em inglês; documentação em português.
  - Nunca automatizar envio de candidatura nem LinkedIn; o Playwright para antes de enviar.
  - Filtro fixo antes do LLM; saída do LLM sempre validada por schema Pydantic; testes nunca chamam a API real (usar mocks/fixtures).
  - Nada de dados pessoais ou segredos no Git (`perfil.yaml`, `.env`, currículos ficam no `.gitignore`).
  - Commits breves, **sem co-autor e sem menção a IA** (sem linha `Co-Authored-By`).
  - Mudou prompt → rodar os evals.
