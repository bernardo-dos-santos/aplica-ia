# Aplica.ia

Assistente de candidaturas a estágio que **faz tudo menos o último clique**: reúne vagas, filtra, avalia a aderência ao perfil com IA, prepara os textos e pré-preenche o formulário. O envio final é sempre humano.

> Em construção — Fase 0 (base do projeto). Visão, decisões e roteiro em [CONTEXTO.md](CONTEXTO.md).

## Rodando localmente

Requer [uv](https://docs.astral.sh/uv/).

```bash
uv sync
cp perfil.example.yaml perfil.yaml   # preencha com seus dados
cp .env.example .env
```

## Qualidade

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy
uv run pytest
```

## Por que cada tecnologia

| Tecnologia | Por quê |
|---|---|
| **uv** | Gerencia Python, dependências e lock num só lugar, e é rápido. |
| **Pydantic** | Valida o perfil e, depois, a saída do LLM: erro de formato falha cedo e com mensagem clara. |
| **Ruff + mypy (strict)** | Lint, formatação e tipos verificados a cada push. |
| **pytest** | Testes rápidos; fontes externas e LLM são testados com fixtures e mocks. |
| **GitHub Actions** | CI roda lint, tipos e testes em todo push e pull request. |
