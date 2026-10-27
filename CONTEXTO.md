# Aplica.ia — Contexto do Projeto

> Documento de contexto para colar no início de qualquer conversa com uma IA (Claude, Claude Code etc.) ou para ler antes de mexer no projeto. Explica **o que** é o projeto, **por que** cada decisão foi tomada e **o que é necessário** para construí-lo.

---

## 1. Visão em uma frase

O Aplica.ia é um assistente de candidaturas que **faz tudo menos o último clique**: reúne vagas num só lugar, avalia se combinam com o meu perfil, prepara textos sob medida, pré-preenche o formulário e deixa tudo numa fila para eu revisar e enviar.

## 2. O problema

- As vagas ficam espalhadas em vários sites (Gupy, IEL, CIEE, LinkedIn, páginas de carreira...).
- Quando paro uma candidatura no meio, preciso voltar ao site específico para continuar. Nada fica centralizado.
- Preencher os mesmos dados em formulários diferentes toma muito tempo.
- Fica difícil acompanhar em que etapa está cada processo e quando cobrar retorno.

## 3. Quem usa (perfil-alvo da v1)

- **Usuário:** eu, Bernardo. Estudante de Ciência da Computação no IFSC Lages (SC), 4ª fase, com conclusão prevista para o 2º semestre de 2028.
- **Vagas buscadas na v1:** estágio em desenvolvimento ou automação de processos.
- **Restrições:** aulas de manhã, então preciso de vagas no período da tarde, remotas, híbridas ou em Lages/SC.
- **Experiência que entra no perfil:** estágio de automação na Prefeitura de Lages (desde jun/2026), com Apps Script, Python e SQL. Lá fiz um gerador de documentos em HTML, um fluxo do Sheets para dashboard no Looker Studio, uma extensão de navegador para o sistema E-Ciga e o envio automático de e-mails de status.
- O perfil fica num **arquivo de configuração** (YAML), então o sistema serve para outras áreas no futuro sem mexer no código.

## 4. Objetivos do projeto

1. **Uso real:** economizar tempo na minha busca por estágio. Se a ferramenta não encontrar vagas que servem para mim, o resto não importa.
2. **Portfólio:** ser um repositório no GitHub que mostre tecnologias que as empresas pedem, cada uma usada por um motivo real.
3. **Aprendizado:** aprender cloud (AWS), infraestrutura como código e engenharia de IA na prática.

## 5. Princípios inegociáveis (e o porquê)

| Princípio | Por quê |
|---|---|
| **O envio final é sempre humano** (human-in-the-loop) | Evita mandar candidatura errada, respeita os termos dos sites e mostra maturidade de design no portfólio. |
| **Sem automação do LinkedIn** (nem Easy Apply, nem scraping) | O User Agreement do LinkedIn proíbe bots e a conta pode ser restrita. Uso o LinkedIn pessoalmente (busca e networking), então não vale o risco. Vagas de lá entram só por importação manual. |
| **Qualidade acima de volume** | Candidatura em massa e genérica tem retorno baixo. O foco é poucas vagas, com boa aderência e bem preparadas. |
| **Regra fixa antes de IA** | Turno, modalidade e cidade são filtros determinísticos, feitos em código comum. O LLM só avalia o que é subjetivo. Fica mais barato, testável e sem alucinação. |
| **A IA nunca inventa experiência** | Os textos gerados usam apenas o que está no `perfil.yaml`. Eu reviso tudo antes de enviar. |
| **Dados só comigo** | Currículo e dados pessoais são sensíveis (LGPD). Segredos ficam fora do Git, em variáveis de ambiente ou num gerenciador de segredos. |
| **Cada tecnologia precisa de um motivo** | Tecnologia empilhada só para enfeitar pesa contra no portfólio. O README explica a escolha de cada peça. |
| **Projeto pequeno e acabado vale mais que grande pela metade** | Cada fase termina usável. A Fase 3 é bônus. |

## 6. Fluxo do sistema (pipeline)

```
[1 Entrada] → [2 Filtro fixo] → [3 Triagem IA] → [4 Fila de revisão] → [5 Preparação] → [6 Pré-preenchimento] → (EU ENVIO) → [7 Tracker/Follow-up]
```

1. **Entrada de vagas**, por dois caminhos que geram o mesmo formato (título, empresa, local, modalidade, turno, descrição, link, fonte, data):
   - **Importação manual (universal):** colo o link ou o texto de qualquer vaga (Gupy, IEL, CIEE, LinkedIn, site da empresa) e o Claude extrai os campos. Funciona com qualquer site desde o primeiro dia, sem risco de violar termos de uso.
   - **Coleta automática:** adaptadores por fonte (ver seção 7), rodando sob demanda ou agendados.
   - Duplicadas são removidas por hash do conteúdo normalizado.
2. **Filtro fixo:** regras do `perfil.yaml` (turno, modalidade, cidade, tipo de vaga). Vagas reprovadas ficam guardadas com o motivo, mas não chegam ao LLM.
3. **Triagem com IA:** o Claude lê a vaga e o perfil e devolve uma **categoria de aderência** (`forte` / `media` / `fraca`), uma justificativa curta, os requisitos que atendo e os que não atendo e, para fontes não oficiais, sinais de golpe ou vaga fantasma. A saída é JSON validado por schema Pydantic. Uso categorias em vez de nota de 0 a 100 porque LLM não calibra bem escalas finas, e as categorias são mais fáceis de avaliar com evals.
4. **Fila de revisão:** um painel web lista as vagas triadas, ordenadas por aderência, com justificativa e link. Eu decido: descartar ou seguir.
5. **Preparação:** para as vagas que eu escolho seguir, gera um resumo de currículo ajustado, uma carta curta e respostas para perguntas comuns ("por que você quer trabalhar aqui?", pretensão, disponibilidade). Os textos são editáveis no painel.
6. **Pré-preenchimento:** o botão "abrir candidatura" no painel inicia o Playwright **com janela visível, na minha máquina**. Ele abre o formulário, preenche os campos conhecidos, anexa o currículo e **para antes de enviar**. Eu reviso e clico em enviar nessa mesma janela. Para sites com login (como a Gupy), usa um perfil de navegador persistente em que eu mesmo faço login. O sistema registra quais campos preencheu e quais falharam.
7. **Tracker e follow-up:** o banco guarda o status de cada candidatura. Atualizo o status no painel (na Fase 3, a leitura de e-mails sugere as mudanças). Lembretes de follow-up depois de X dias sem resposta.

> **Por que o pré-preenchimento é local e com janela visível:** o Playwright preenche o formulário no navegador que ele controla, não no meu. Uma captura de tela não me deixa enviar. Então a janela preenchida precisa ser a mesma em que eu clico em enviar. Isso também resolve o ponto em aberto da cloud: a nuvem cuida de entrada, filtro e triagem, e o pré-preenchimento sempre roda localmente.

## 7. Fontes de vagas

| Fonte | Como | Observação |
|---|---|---|
| **Importação manual** | Link ou texto colado, extração com Claude | Cobre qualquer site, inclusive LinkedIn, IEL e CIEE. Fonte principal da v1. |
| **Gupy** | API JSON que o portal público (portal.gupy.io) usa | É onde está a maior parte das vagas de estágio no Brasil. **Não é API oficial:** antes de implementar, ler os termos de uso e o robots.txt. Se não for permitido, a Gupy fica só na importação manual. Respeitar rate limit e guardar fixtures, porque o formato pode mudar sem aviso. |
| **Greenhouse** | API pública de job boards (`boards-api.greenhouse.io`) | Oficial e estável, mas com poucas vagas de estágio no Brasil. Serve como exemplo de adaptador limpo com API oficial e tem formulários padronizados, bons para o pré-preenchimento. |
| **Lever** | API pública de postings (`api.lever.co/v0/postings`) | Mesmo papel do Greenhouse. |
| **IEL/SC, CIEE, páginas de carreira** | A investigar | Cada site exige um adaptador próprio. Até lá, entram por importação manual. |

> Todo adaptador implementa a mesma interface (`fetch() -> list[Job]`), o que facilita os testes com respostas gravadas. Começar com a importação manual e **uma** fonte automática bem feita antes de adicionar outras.

## 8. Stack e o porquê de cada escolha

### Fase 1 — MVP local

| Tecnologia | Para quê | Por que essa |
|---|---|---|
| **Python 3.12** | Linguagem principal | Já domino, tem o melhor ecossistema para IA e automação. |
| **uv** | Dependências e ambiente virtual | Rápido, um só arquivo de lock, cada vez mais usado. |
| **FastAPI** | API e painel de revisão | Moderno, tipado, gera documentação automática e é muito pedido em vagas. |
| **Pydantic** | Validação dos dados e da saída do LLM | Garante que o JSON do Claude tem o formato certo. |
| **SQLAlchemy + Alembic** | Acesso ao banco e migrações | Padrão de mercado. Facilita trocar SQLite por Postgres depois. |
| **SQLite** (local) | Banco no início | Zero configuração. Na Fase 2 vira Postgres. |
| **httpx** | Chamar as APIs das fontes | Cliente HTTP assíncrono. |
| **Claude API (SDK `anthropic`)** | Extração, triagem e geração de textos | Saída estruturada e boa escrita em português. Modelo configurável por etapa: um modelo barato (Haiku) para extração e triagem, um melhor (Sonnet) para os textos. Prompt caching no perfil, que se repete em toda chamada. |
| **HTMX + Jinja2** | Interface do painel | Mantém o projeto simples e só em Python. React aumentaria o escopo sem ajudar o objetivo principal. |
| **pytest** | Testes | Testa adaptadores com respostas gravadas (fixtures) e o LLM com mocks. |
| **Evals básicos** | Medir a qualidade da triagem desde o início | ~30 vagas rotuladas à mão (`forte` / `media` / `fraca`) e um script que compara com a triagem. Barato de fazer e é o que mostra engenharia de IA de verdade. Rodar a cada mudança de prompt. |
| **Ruff + mypy** | Lint, formatação e tipos | Qualidade de código visível para quem avalia o repositório. |
| **Docker + docker-compose** | Rodar tudo igual em qualquer máquina | Pré-requisito para a cloud e muito pedido em vagas. |
| **GitHub Actions** | CI: lint, tipos e testes a cada push | Selo de projeto sério. |

### Fase 1.5 — Preparação e pré-preenchimento

| Tecnologia | Para quê | Por que essa |
|---|---|---|
| **Playwright** (com janela) | Pré-preencher formulários | Mais estável que o Selenium, com bom suporte a páginas dinâmicas. Começar pelos formulários do Greenhouse e do Lever, que são padronizados. |

### Fase 2 — Cloud (foco em aprendizado)

| Tecnologia | Para quê | Por que essa |
|---|---|---|
| **AWS** | Provedor de cloud | É a mais pedida em vagas. |
| **Terraform** | Criar toda a infraestrutura como código | Reprodutível, versionado e muito valorizado. Dá para destruir e recriar tudo com um comando. |
| **Lambda** (imagem de container) | Coleta, filtro e triagem | Tarefas curtas e esporádicas: Lambda custa quase nada. Fargate ligado 24h não se justifica. |
| **EventBridge Scheduler** | Rodar a coleta todo dia | Agendamento gerenciado, como um cron na nuvem. |
| **Postgres gerenciado gratuito** (Neon ou Supabase) | Banco | Postgres é o padrão de mercado e permite pgvector na Fase 3. RDS não tem custo zero contínuo, então fica como alternativa documentada no Terraform. |
| **S3** | Currículos gerados | Armazenamento barato. |
| **SSM Parameter Store** | Chaves de API e credenciais | Grátis no nível padrão. Nunca deixar segredo no código. |
| **CloudWatch** | Logs, métricas e alertas | Observabilidade básica. |
| **GitHub Actions (CD)** | Deploy automático com OIDC na AWS | Sem chaves fixas no GitHub, que é a prática segura. |

> **Atenção ao custo:** criar um **alerta de orçamento (AWS Budgets) antes de qualquer outra coisa**. O free tier da AWS mudou em 2025: contas novas recebem créditos por tempo limitado em vez dos 12 meses grátis de antes. Conferir as condições atuais ao criar a conta e planejar para custo zero depois dos créditos.

> **Decidido:** o pré-preenchimento nunca roda na cloud (ver seção 6). A cloud entrega a fila pronta; o painel local abre o formulário.

### Fase 3 — Diferencial de IA (bônus)

| Tecnologia | Para quê | Por que essa |
|---|---|---|
| **Embeddings + pgvector** | Matching semântico entre vaga e perfil | Entende "automação de processos" ≈ "RPA" ≈ "scripts de integração", o que só palavra-chave não faz. Serve de primeiro filtro barato antes do LLM. |
| **Evals ampliados** | Comparar prompts e modelos | Mais vagas rotuladas, métricas por categoria e relatório de regressão no CI. |
| **Rastreamento de custo e tokens** | Saber quanto cada candidatura custa | Mostra preocupação com custo, o que empresa valoriza. Os campos já existem no banco desde a Fase 1. |
| **Leitura de e-mails (IMAP + senha de app)** | Sugerir mudança de status ("recebemos sua candidatura", "próxima etapa") | Mais simples que a Gmail API: um app OAuth em modo de teste tem o token expirando a cada 7 dias. Só leitura. |
| **Servidor MCP** | Consultar o tracker pelo Claude ("quais candidaturas estão paradas há 7 dias?") | Tecnologia nova e em alta. |

## 9. Modelo de dados (inicial)

Nomes no código em inglês (ver seção 14).

- **jobs:** id, source, external_id, title, company, location, work_mode, shift, description, url, posted_at, collected_at, content_hash (para deduplicar), filter_reason (preenchido se reprovada no filtro fixo).
- **evaluations:** id, job_id, fit (`strong` / `medium` / `weak`), rationale, met_requirements, missing_requirements, scam_signals, model, prompt_version, input_tokens, output_tokens, cost_usd, created_at.
- **applications:** id, job_id, status (`new` → `prepared` → `ready_for_review` → `submitted` → `in_process` → `interview` → `approved` / `rejected` / `no_response`; ou `discarded`), generated_texts, resume_path, autofill_log, submitted_at, next_followup_at.
- **events:** id, application_id, type, origin (`manual` / `email`), content, created_at. Guarda o histórico de cada processo.

> `prompt_version` e os campos de tokens existem desde o início para que evals e custo da Fase 3 não exijam migração de dados antigos.

## 10. Estrutura de pastas

```
aplica-ia/
├── README.md              # visão, arquitetura, porquê de cada tecnologia, GIF de demonstração (PT + EN)
├── CONTEXTO.md            # este arquivo
├── CLAUDE.md              # instruções para o Claude Code
├── perfil.example.yaml    # modelo do perfil (o real fica fora do Git)
├── .env.example
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
├── src/aplica/
│   ├── sources/           # um adaptador por fonte (manual.py, gupy.py, greenhouse.py, lever.py)
│   ├── filtering/         # regras fixas do perfil
│   ├── screening/         # prompts, schemas Pydantic, chamada ao Claude
│   ├── preparation/       # geração de currículo e textos
│   ├── autofill/          # Playwright
│   ├── tracker/           # status, follow-up (e e-mail na Fase 3)
│   ├── db/                # modelos e migrações
│   └── web/               # FastAPI + painel HTMX
├── evals/                 # vagas rotuladas e script de avaliação
├── tests/
│   └── fixtures/          # respostas gravadas das fontes
├── infra/                 # Terraform (Fase 2)
└── .github/workflows/     # CI/CD
```

## 11. O que vai ser necessário (checklist)

### Contas e chaves
- [ ] Conta no GitHub e repositório `aplica-ia` (verificar se o nome está livre).
- [ ] Chave da **Claude API** (console da Anthropic), com **limite de gastos** configurado.
- [ ] Conta na **AWS** com **MFA** na conta root, um usuário IAM para o dia a dia e um **alerta de orçamento** (Fase 2).
- [ ] Conta no Neon ou Supabase (Fase 2).
- [ ] Senha de app do e-mail, só para leitura via IMAP (Fase 3).

### Ferramentas instaladas
- [ ] Python 3.12+ e uv.
- [ ] Docker Desktop.
- [ ] Playwright (`uv run playwright install chromium`) (Fase 1.5).
- [ ] Terraform e AWS CLI (Fase 2).
- [ ] Git, e o VS Code ou outro editor.

### Materiais meus
- [ ] Currículo base atualizado (em Markdown ou YAML, para a IA conseguir adaptar).
- [ ] `perfil.yaml` com formação, experiência, habilidades, disponibilidade (tarde), cidade, modalidades aceitas, pretensão e regras do filtro fixo.
- [ ] Respostas-base para as perguntas comuns de formulário.
- [ ] **~30 vagas reais rotuladas à mão** como `forte` / `media` / `fraca` (Fase 1, para os evals).
- [ ] Lista inicial de empresas para monitorar (SC + remotas que contratam estagiários).

### Conhecimentos que vou praticar
- Requisições HTTP e APIs REST; automação de navegador; modelagem de banco e migrações.
- Prompt engineering com saída estruturada; evals; mocks e testes.
- Docker; CI/CD; Terraform; IAM e segurança básica na AWS; observabilidade.
- (Fase 3) Embeddings, busca vetorial e MCP.

## 12. Roteiro e definição de "pronto"

| Fase | Duração estimada | Entregável |
|---|---|---|
| **0 — Base** | 2–3 dias | Repositório, `pyproject.toml` com uv, Ruff, mypy, pytest, CI verde com um teste, `perfil.example.yaml`, 30 vagas rotuladas. |
| **1 — MVP local** | 2–3 semanas | Importação manual + uma fonte automática (Gupy se permitido, senão Greenhouse/Lever) → filtro fixo → triagem → painel com fila de revisão → tracker manual com follow-up. Evals básicos, Docker e testes. **Já é usável na busca real.** |
| **1.5 — Preparação e pré-preenchimento** | 1–2 semanas | Geração de textos editáveis no painel e Playwright com janela para Greenhouse/Lever (e Gupy, se possível). |
| **2 — Cloud** | 2–3 semanas | Infra em Terraform, coleta e triagem agendadas em Lambda, Postgres gerenciado, segredos no SSM, deploy com OIDC e alerta de custo. |
| **3 — IA avançada** | opcional | pgvector, evals ampliados, painel de custo, leitura de e-mails, servidor MCP. |

Estimativa total (Fases 0 a 2): **2 a 3 meses** com 2–3 h por dia. O que mais costuma atrasar é o pré-preenchimento, porque cada formulário é diferente e as páginas mudam — por isso ele fica numa fase própria, depois que o resto já funciona.

**Pronto =** Fases 0, 1, 1.5 e 2 funcionando, README com arquitetura e o porquê de cada tecnologia, GIF de demonstração, CI verde, testes cobrindo adaptadores, filtro e triagem, e o resultado dos evals publicado no README.

## 13. Riscos e cuidados

- **Termos de uso das fontes:** respeitar robots.txt e rate limits, preferir APIs oficiais e nunca contornar CAPTCHA. Na dúvida, a fonte fica só na importação manual.
- **Fontes não oficiais mudam:** o adaptador da Gupy pode quebrar sem aviso. Ter testes com fixtures e um alerta claro quando a resposta mudar de formato.
- **Formulários mudam:** o pré-preenchimento vai quebrar. Registrar qual campo falhou e nunca bloquear o envio manual por causa disso.
- **Alucinação da IA:** a IA nunca inventa experiência. O prompt usa apenas o `perfil.yaml`, os evals medem a triagem e eu reviso tudo antes de enviar.
- **Custo:** limite de gastos na Claude API e AWS Budgets. Filtro fixo antes do LLM, modelo barato na triagem, prompt caching e cache das avaliações para não reavaliar a mesma vaga.
- **Dados pessoais:** `perfil.yaml`, `.env`, currículos e o perfil persistente do navegador ficam no `.gitignore`. O repositório público usa dados de exemplo.
- **Escopo:** cada fase termina usável. Se o tempo apertar, a Fase 3 sai inteira e o projeto continua "pronto".

## 14. Convenções

- Commits **breves e objetivos**, sem descrição longa e **sem co-autor** ou menção a IA. Eu sou o único autor.
- **Código, nomes de arquivos, tabelas e identificadores em inglês.** Documentação (`CONTEXTO.md`, comentários de decisão) em português. README em português com versão em inglês.
- Toda tecnologia nova entra no README com uma linha explicando o porquê.
- Mudança em prompt → rodar os evals e registrar o resultado.

---

### Como usar este arquivo com uma IA

Colar este documento no início da conversa e depois dizer em que fase/tarefa estamos, por exemplo: *"Estamos na Fase 1, tarefa: adaptador de importação manual com testes."* Pedir passos pequenos e testáveis, um por vez.
