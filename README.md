# 🔄 Integração Jira - Bradesco PLTFAT

Conjunto de ferramentas Python para automação e geração de relatórios do Jira no projeto PLTFAT (Plataforma | A3C - Fatores de Autenticação).

## 📋 Visão Geral

Este projeto oferece quatro scripts principais:

| Script | Função | Documentação |
| -------- | -------- | -------------- |
| 🤖 `automatizar_issues.py` | Criação em massa de issues via CSV | [📖 Docs](./docs/README_automatizar_issues.md) |
| 🚀 `gerar_relatorios_completos.py` | **Gera ambos os relatórios com 1 conexão** ⚡ | [📖 Docs](./docs/README_gerar_relatorios_completos.md) |
| 📊 `gerar_lista_itens_geral_projeto.py` | Relatório HTML de todas as sprints | [📖 Docs](./docs/README_gerar_lista_itens_geral_projeto.md) |
| 🏃‍♂️ `gerar_lista_itens_sprint_review.py` | Relatório HTML da sprint ativa | [📖 Docs](./docs/README_gerar_lista_itens_sprint_review.md) |

---

## 🚀 Quick Start

### 1. Instalação

``` bash

# Clone o repositório

git clone <repo>
cd "Integracao_Jira_Docmatch"

# Instale dependências

pip install requests python-dotenv python-dateutil

```

### 2. Configuração

Crie o arquivo `.env` na raiz:

``` properties

JIRA_URL=<https://jira.bradesco.com.br:8443>
JIRA_TOKEN=seu_token_bearer_aqui
JIRA_PROJECT=PLTFAT
TEAM_NAME=DocMatch
folder_path=issues

```

### 3. Execute

``` bash

# Automatização de issues (validar primeiro)

# Pode usar 'python' ou 'py'

python automatizar_issues.py --dry-run
python automatizar_issues.py

# Relatórios - RECOMENDADO: Script unificado ⚡

python gerar_relatorios_completos.py

# Gera ambos os relatórios com 1 única conexão (~50% mais rápido)

# Ou relatórios individuais (se precisar de apenas um)

python gerar_lista_itens_geral_projeto.py      # Apenas relatório geral
python gerar_lista_itens_sprint_review.py      # Apenas sprint review

```

---

## 🤖 Automatização de Issues

Cria issues no Jira em lote a partir de arquivos CSV.

### Uso Básico

``` bash

# 1. Validar JSON antes de criar

python automatizar_issues.py --dry-run

# ou: py automatizar_issues.py --dry-run

# 2. Criar issues no Jira

python automatizar_issues.py

# ou: py automatizar_issues.py

```

### Funcionalidades

- ✅ Criação em lote via API Bulk Create
- 🗺️ Mapeamento flexível CSV → Campos Jira
- 🔍 Modo dry-run para validação
- 📦 Organização automática de arquivos processados
- 📊 Relatórios detalhados com links das issues

**📖 Documentação completa:** [docs/README_automatizar_issues.md](./docs/README_automatizar_issues.md)

---

## 📊 Geração de Relatórios

### Relatório Geral de Sprints

``` bash

python gerar_lista_itens_geral_projeto.py

# ou: py gerar_lista_itens_geral_projeto.py

# Com exportação de dados brutos em CSV

python gerar_lista_itens_geral_projeto.py --save-csv

```

- 📈 Visualização de todas as sprints do projeto
- 🎨 Interface interativa com filtros
- 📊 Estatísticas por sprint e company
- 💾 Exportação opcional de dados brutos em CSV

**📖 Documentação:** [docs/README_gerar_lista_itens_geral_projeto.md](./docs/README_gerar_lista_itens_geral_projeto.md)

### Relatório de Sprint Review

``` bash

python gerar_lista_itens_sprint_review.py

# ou: py gerar_lista_itens_sprint_review.py

# Com exportação de dados brutos em CSV (2)

python gerar_lista_itens_sprint_review.py --save-csv

```

- 🎯 Foco na sprint ativa
- 📋 Layout otimizado para apresentações
- 🔗 Links diretos para o Jira
- 💾 Exportação opcional de dados brutos em CSV

**📖 Documentação:** [docs/README_gerar_lista_itens_sprint_review.md](./docs/README_gerar_lista_itens_sprint_review.md)

### ⚡ Relatórios Unificados (RECOMENDADO)

``` bash

python gerar_relatorios_completos.py

# ou: py gerar_relatorios_completos.py

# Com exportação de dados brutos em CSV (sprint + geral)

python gerar_relatorios_completos.py --save-csv

```

- 🚀 **Uma única conexão** gera ambos os relatórios
- ⚡ **~50% mais rápido** que executar os scripts separadamente
- 📊 Gera simultaneamente: Sprint Review + Relatório Geral
- 🎯 **Dados consistentes** com timestamp único
- 💾 **Menos carga** na API do Jira
- 📄 Exportação opcional de dados brutos em CSV (2 arquivos: sprint + completo)

**📖 Documentação:** [docs/README_gerar_relatorios_completos.md](./docs/README_gerar_relatorios_completos.md)

### Quando usar

- ✅ Precisa de ambos os relatórios
- ✅ Automação/agendamento diário
- ✅ Apresentações completas
- ✅ CI/CD pipelines

---

## 📁 Estrutura do Projeto

``` text

Integracao Jira/
├── 📄 README.md                     # Este arquivo (visão geral)
├── ⚙️ .env                          # Configurações (não versionado)
├── 📋 BulkCreate_configuration.txt  # Mapeamento de campos CSV
│
├── 🤖 Scripts principais
│   ├── automatizar_issues.py
│   ├── gerar_relatorios_completos.py         # ⚡ NOVO: Relatórios unificados
│   ├── gerar_lista_itens_geral_projeto.py
│   ├── gerar_lista_itens_sprint_review.py
│   └── jira_utils.py                         # 🔧 Módulo de utilidades compartilhadas
│
├── 📁 docs/                         # Documentação detalhada
│   ├── README_automatizar_issues.md
│   ├── README_gerar_relatorios_completos.md  # ⚡ NOVO: Script unificado
│   ├── README_gerar_lista_itens_geral_projeto.md
│   └── README_gerar_lista_itens_sprint_review.md
│
├── � jira_utils.py                 # Módulo centralizado (20+ funções)
│   # Contém todas as funções compartilhadas entre os 3 scripts:
│   # - Conexão e autenticação com Jira
│   # - Busca e filtragem de issues
│   # - Detecção de sprint ativa
│   # - Cálculo de métricas ágeis (Lead Time, Cycle Time, etc.)
│   # - Agrupamento por status do pipeline
│   # - Análise de entregas
│
├── �📁 tests/                        # Suite de testes (6 testes)
│   ├── README_TESTS.md              # Documentação dos testes
│   ├── run_all_tests.py             # Executor da suite
│   ├── test_load_environment.py
│   ├── test_load_bulk_configuration.py
│   ├── test_parse_csv.py
│   ├── test_move_to_processed.py
│   ├── test_jira_connection.py
│   └── test_bulk_create_api.py
│
├── 📁 issues/                       # CSVs para processamento
│   └── Processados/                 # CSVs já processados
│
├── 📁 relatorios/                   # Relatórios HTML gerados
├── 📁 logs/                         # Logs de execução
└── 📁 debug/                        # Scripts utilitários

```

---

## 🧪 Testes e Validação

### Suite Completa (6 testes)

``` bash

python tests/run_all_tests.py

# ou: py tests/run_all_tests.py

```

Valida:

- ✅ Carregamento de variáveis (.env)
- ✅ Configuração de mapeamento (BulkCreate_configuration.txt)
- ✅ Parsing e mapeamento de CSV
- ✅ Movimentação de arquivos
- ✅ Conexão com API Jira
- ✅ Estrutura do payload Bulk Create

**Resultado esperado:** 6/6 passando em ~2s

### Modo Dry-Run (Validação de Produção)

``` bash

python automatizar_issues.py --dry-run

# ou: py automatizar_issues.py --dry-run (2)

```

- 🔍 Processa o CSV completo
- 📄 Exibe o JSON que seria enviado
- ⚠️ **NÃO** cria issues no Jira
- ⚠️ **NÃO** move arquivos

### Padronização da Documentação (Markdown)

Use como etapa padrão sempre que atualizar documentação:

``` bash

python tools/fix_markdown.py --all --check

```

Se o comando apontar ajustes pendentes, aplique com:

``` bash

python tools/fix_markdown.py --all

```

**📖 Documentação completa:** [tests/README_TESTS.md](./tests/README_TESTS.md)

---

## ⚙️ Configuração

### Arquivo `.env`

Variáveis de ambiente necessárias:

``` properties

# URL do servidor Jira

JIRA_URL=<https://jira.bradesco.com.br:8443>

# Token de autenticação Bearer

# Gere em: Jira → Perfil → Segurança → API Token

JIRA_TOKEN=seu_token_bearer_aqui

# Chave do projeto

JIRA_PROJECT=PLTFAT

# Nome do team/squad

TEAM_NAME=DocMatch

# Pasta de arquivos CSV (para automatizar_issues.py)

folder_path=issues

```

### Arquivo `BulkCreate_configuration.txt`

Mapeamento de colunas CSV para campos Jira:

``` json

{
  "config.version": "2.0",
  "config.encoding": "UTF-8",
  "config.delimiter": ",",
  "config.field.mappings": {
    "Assignee": {"jira.field": "assignee"},
    "Issue Type": {"jira.field": "issuetype"},
    "Description": {"jira.field": "description"},
    "Original Estimate": {"jira.field": "timeoriginalestimate"},
    "Parent Id": {"jira.field": "subtask-parent-id"},
    "Summary": {"jira.field": "summary"},
    "Theme": {"existing.custom.field": "10500"},
    "Labels": {"jira.field": "labels"},
    "Team": {"existing.custom.field": "10401"},
    "Epic Link": {"existing.custom.field": "10101"},
    "Sprint ID": {"existing.custom.field": "10100"}
  },
  "config.project": {
    "project.key": "PLTFAT",
    "project.name": "PLATAFORMA | A3C - Fatores de Autenticacao",
    "project.lead": "F568572"
  }
}

```

**📖 Detalhes:** [docs/README_automatizar_issues.md#mapeamento-de-campos](./docs/README_automatizar_issues.md#mapeamento-de-campos)

---

## 🔄 Workflow Recomendado

``` bash

# 1️⃣ Validar ambiente

python tests/run_all_tests.py

# 2️⃣ Preparar CSV

# Colocar arquivo na pasta issues/

# 3️⃣ Validar JSON (dry-run)

python automatizar_issues.py --dry-run

# 4️⃣ Revisar payload exibido

# Verificar campos, valores, estrutura

# 5️⃣ Executar em produção

python automatizar_issues.py

# 6️⃣ Confirmar resultados

cat issues/relatorio_processamento_csv.txt

# Acessar links das issues criadas

```

---

## 📡 API do Jira

### Endpoint Utilizado

``` text

POST /rest/api/2/issue/bulk

```

### Estrutura do Payload

``` json

{
  "issueUpdates": [
    {
      "fields": {
        "project": {"key": "PLTFAT"},
        "issuetype": {"name": "Task"},
        "summary": "Título da issue",
        "customfield_10401": "DocMatch"
      },
      "update": {}
    }
  ]
}

```

### Campos Obrigatórios

- `project` - Chave do projeto
- `issuetype` - Tipo de issue
- `summary` - Título

**Referência:** [Atlassian REST API Documentation](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issues/)

---

## 🛠️ Troubleshooting

### Problemas Comuns

| Erro | Solução Rápida | Documentação |
| ------ | ---------------- | -------------- |
| "Arquivo .env não encontrado" | Criar `.env` na raiz com 5 variáveis | [Docs](./docs/README_automatizar_issues.md#configuração) |
| "401 Unauthorized" | Verificar/renovar token no Jira | [Docs](./docs/README_automatizar_issues.md#troubleshooting) |
| "Field 'summary' is required" | Verificar coluna Summary no CSV | [Docs](./docs/README_automatizar_issues.md#estrutura-do-csv) |
| "Issue Type não existe" | Usar tipo válido do projeto | [Docs](./docs/README_automatizar_issues.md#troubleshooting) |

### Validação Rápida

``` bash

# Teste conexão com Jira

python tests/test_jira_connection.py

# ou: py tests/test_jira_connection.py

# Teste estrutura do payload

python tests/test_bulk_create_api.py

# ou: py tests/test_bulk_create_api.py

# Valide JSON antes de criar

python automatizar_issues.py --dry-run

# ou: py automatizar_issues.py --dry-run (3)

```

**📖 Troubleshooting completo:** [docs/README_automatizar_issues.md#troubleshooting](./docs/README_automatizar_issues.md#troubleshooting)

---

## 📚 Documentação

### Por Script

- 🤖 **automatizar_issues.py** - [docs/README_automatizar_issues.md](./docs/README_automatizar_issues.md)
- � **gerar_relatorios_completos.py** - [docs/README_gerar_relatorios_completos.md](./docs/README_gerar_relatorios_completos.md)
- 📊 **gerar_lista_itens_geral_projeto.py** - [docs/README_gerar_lista_itens_geral_projeto.md](./docs/README_gerar_lista_itens_geral_projeto.md)
- 🏃‍♂️ **gerar_lista_itens_sprint_review.py** - [docs/README_gerar_lista_itens_sprint_review.md](./docs/README_gerar_lista_itens_sprint_review.md)
- 🔧 **jira_utils.py** - [docs/README_jira_utils.md](./docs/README_jira_utils.md) ⭐ **NOVO**

### Por Tópico

- 🧪 **Testes** - [tests/README_TESTS.md](./tests/README_TESTS.md)
- 🐛 **Debug** - Scripts em `/debug/`

---

## 📊 Output e Relatórios

### Logs

- **Local:** `logs/`
- **Arquivos:**
- `automatizacao_issues.log` - Logs detalhados com timestamp
- `bulk_payload_test_*.json` - JSON do dry-run (modo teste)
- `bulk_payload_prod_*.json` - JSON enviado em produção
- **Uso:** Troubleshooting, auditoria e replay de payloads

### Relatórios CSV → Jira

- **Local:** `issues/relatorio_processamento_csv.txt`
- **Conteúdo:**
- Issues criadas com links
- Erros encontrados
- Estatísticas de processamento

### Relatórios HTML

- **Local:** `relatorios/`
- **Formato:** `sprint_review_YYYYMMDD_HHMMSS.html`
- **Visualização:** Abrir diretamente no navegador

---

## 🔐 Segurança

- ⚠️ **Não versione o arquivo `.env`** (adicione ao `.gitignore`)
- 🔑 Use tokens de serviço, não tokens pessoais
- 🔒 Tokens têm acesso total - mantenha seguros
- 📝 Revogue tokens antigos periodicamente

---

## 🐛 Debug

Scripts utilitários disponíveis em `/debug/`:

- `debug_available_fields.py` - Lista campos do Jira
- `debug_issue_types.py` - Tipos de issues do projeto
- `debug_projects.py` - Projetos acessíveis
- `debug_team_field.py` - Custom fields de team
- `import_requests.py` - Importação de issues

---

## 📦 Requisitos

### Python

- **Versão:** 3.8+

### Bibliotecas

``` bash

pip install requests python-dotenv python-dateutil

```

### Ambiente

- Acesso ao Jira: <https://jira.bradesco.com.br:8443>
- Token de autenticação Bearer
- Projeto PLTFAT com permissões de escrita

---

## 🤝 Contribuindo

1. Execute os testes antes de modificar: `python tests/run_all_tests.py` (ou `py tests/run_all_tests.py`)
1. Valide mudanças com dry-run: `python automatizar_issues.py --dry-run` (ou `py automatizar_issues.py --dry-run`)
1. Padronize documentação: `python tools/fix_markdown.py --all --check`
1. Atualize documentação relevante em `/docs/`
1. Mantenha logs e relatórios funcionando

---

**Desenvolvido por:** GitHub Copilot
**Última atualização:** 07/02/2026
**Versão:** 1.0

## ⚙️ Configuração (2)

### Pré-requisitos

``` bash

pip install requests python-dotenv python-dateutil

```

### Arquivo `.env` (2)

Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

``` properties

# Configurações do Jira

JIRA_URL=<https://jira.bradesco.com.br:8443>
JIRA_TOKEN=seu_token_bearer_aqui
JIRA_PROJECT=PLTFAT

# Configurações do Team

TEAM_NAME=DocMatch

# Pasta de arquivos CSV (para automatizar_issues.py) (2)

folder_path=issues

```

### Arquivo `BulkCreate_configuration.txt` (2)

Arquivo JSON que mapeia colunas do CSV para campos do Jira:

``` json

{
  "config.version": "2.0",
  "config.encoding": "UTF-8",
  "config.delimiter": ",",
  "config.field.mappings": {
    "Assignee": {"jira.field": "assignee"},
    "Issue Type": {"jira.field": "issuetype"},
    "Description": {"jira.field": "description"},
    "Original Estimate": {"jira.field": "timeoriginalestimate"},
    "Parent Id": {"jira.field": "subtask-parent-id"},
    "Summary": {"jira.field": "summary"},
    "Theme": {"existing.custom.field": "10500"},
    "Labels": {"jira.field": "labels"},
    "Team": {"existing.custom.field": "10401"},
    "Epic Link": {"existing.custom.field": "10101"},
    "Sprint ID": {"existing.custom.field": "10100"}
  },
  "config.project": {
    "project.key": "PLTFAT",
    "project.name": "PLATAFORMA | A3C - Fatores de Autenticacao",
    "project.lead": "F568572"
  }
}

```

## 📁 Estrutura do Projeto (2)

``` text

Integracao Jira/
├── 🤖 automatizar_issues.py         # Automação de criação de issues
├── 📊 gerar_lista_itens_geral_projeto.py      # Relatório geral de sprints
├── 🏃‍♂️ gerar_lista_itens_sprint_review.py    # Relatório sprint review
├── ⚙️ .env                          # Configurações (não versionado)
├── 📋 BulkCreate_configuration.txt  # Mapeamento de campos CSV->Jira
├── 📄 README.md                     # Este arquivo
├── 📁 issues/                       # Arquivos CSV para processamento
│   ├── [pltfat]_docmatch_-_import-jira_csv_1770061793248.csv
│   └── 📁 Processados/              # CSVs já processados
├── 📁 relatorios/                   # Relatórios HTML gerados
│   ├── sprint_review_20260122_174938.html
│   └── backlog_geral_20260122_175359.html
├── 📁 tests/                        # Suite de testes automatizados
│   ├── run_all_tests.py             # Executor de todos os testes
│   ├── test_load_environment.py     # Teste de carregamento .env
│   ├── test_load_bulk_configuration.py  # Teste de config
│   ├── test_parse_csv.py            # Teste de parsing CSV
│   ├── test_move_to_processed.py    # Teste de movimentação
│   ├── test_jira_connection.py      # Teste de conexão API
│   ├── test_bulk_create_api.py      # Teste de validação API
│   ├── teste_description_field.py   # Validação campo descrição
│   ├── teste_lead_time.py           # Teste de lead time
│   ├── test_issue_types.py          # Teste de tipos de issue
│   └── test_team_config.py          # Teste de config team
├── 📁 docs/                         # Documentação detalhada
│   ├── README_gerar_lista_itens_geral_projeto.md
│   └── README_gerar_lista_itens_sprint_review.md
├── 📁 debug/                        # Scripts de debug e utilitários
│   ├── debug_available_fields.py
│   ├── debug_issue_types.py
│   ├── debug_lead_time_13437.py
│   ├── debug_lead_time_14288.py
│   ├── debug_projects.py
│   ├── debug_specific_issues.py
│   ├── debug_story_tipo.py
│   ├── debug_team_field.py
│   └── import_requests.py
└── 📁 logs/                         # Arquivos de log

```

## 🚀 Como Usar

### Automatização de Issues

#### Modo Teste (Dry-Run) 🔍

Recomendado para **validar o JSON antes** de criar as issues:

``` bash

# 1. Configure o arquivo .env com suas credenciais

# 2. Ajuste o BulkCreate_configuration.txt com o mapeamento de campos

# 3. Coloque os arquivos CSV na pasta issues/

# 4. Execute em modo teste

python automatizar_issues.py --dry-run

# ou: py automatizar_issues.py --dry-run (4)

```

O modo dry-run irá:

- ✅ Processar o CSV e gerar o JSON completo
- ✅ Validar a estrutura dos campos
- ✅ Exibir o payload que seria enviado à API
- ⚠️ **NÃO** criar issues no Jira
- ⚠️ **NÃO** mover arquivos para Processados/

#### Modo Normal (Produção) 🚀

Depois de validar o JSON no modo teste:

``` bash

python automatizar_issues.py

# ou: py automatizar_issues.py (2)

```

O script irá processar automaticamente todos os arquivos `.csv` da pasta `issues/` e criar as issues no Jira.

### Relatório Geral

``` bash

python gerar_lista_itens_geral_projeto.py

# ou: py gerar_lista_itens_geral_projeto.py (2)

```

### Relatório Sprint Review

``` bash

python gerar_lista_itens_sprint_review.py

# ou: py gerar_lista_itens_sprint_review.py (2)

```

## 🧪 Testes

### Suite Completa de Testes

Execute todos os testes de uma vez:

``` bash

python tests/run_all_tests.py

# ou: py tests/run_all_tests.py (2)

```

A suite executa 6 testes automatizados que validam:

- ✅ **Teste 1**: Carregamento de variáveis de ambiente (.env)
- ✅ **Teste 2**: Carregamento de configuração (BulkCreate_configuration.txt)
- ✅ **Teste 3**: Parsing de CSV e mapeamento de campos
- ✅ **Teste 4**: Movimentação de arquivos para Processados/
- ✅ **Teste 5**: Conexão com API Jira
- ✅ **Teste 6**: Validação de payload da API Bulk Create

### Resultado esperado

``` text

Total de testes: 6
✅ Passaram: 6
❌ Falharam: 0
⏱️  Tempo total: ~2s

```

### Modo Dry-Run (Teste de Produção) 🔍

Antes de criar issues reais, valide o JSON gerado:

``` bash

python automatizar_issues.py --dry-run

```

O dry-run irá:

- ✅ Processar o CSV completo
- ✅ Gerar o JSON que seria enviado à API
- ✅ Exibir o payload no console
- ⚠️ **NÃO** criar issues no Jira
- ⚠️ **NÃO** mover arquivos

**📖 Documentação completa:** [tests/README_TESTS.md](./tests/README_TESTS.md)
❌ Falharam: 0
⏱️  Tempo total: ~2s

``` text

### Testes Individuais

Execute testes específicos conforme necessário:

``` bash

# Teste de automação de issues

python tests/test_load_environment.py
python tests/test_load_bulk_configuration.py
python tests/test_parse_csv.py
python tests/test_move_to_processed.py
python tests/test_jira_connection.py
python tests/test_bulk_create_api.py

# Testes de relatórios

python tests/test_team_config.py
python tests/test_issue_types.py
python tests/teste_description_field.py
python tests/teste_lead_time.py

# Nota: Pode substituir 'python' por 'py' em qualquer comando acima

``` text

## � API do Jira

O script `automatizar_issues.py` utiliza a API oficial do Jira Server/Data Center:

**Endpoint:** `POST /rest/api/2/issue/bulk`

### Estrutura do Payload (2)

``` json

{
  "issueUpdates": [
    {
      "fields": {
        "project": {"key": "PLTFAT"},
        "issuetype": {"name": "Task"},
        "summary": "Título da issue",
        "description": "Descrição detalhada",
        "customfield_10401": "DocMatch"
      },
      "update": {}
    }
  ]
}

``` text

### Campos obrigatórios (2)

- `project`: Chave do projeto (ex: PLTFAT)
- `issuetype`: Tipo de issue (ex: Task, Story, Sub-task)
- `summary`: Título da issue

**Referência oficial:** <https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issues/>

## 🐛 Debug (2)

Scripts auxiliares para depuração e análise:

- [`debug/debug_available_fields.py`](./debug/debug_available_fields.py) - Lista campos disponíveis no Jira
- [`debug/debug_issue_types.py`](./debug/debug_issue_types.py) - Analisa tipos de issues
- [`debug/debug_projects.py`](./debug/debug_projects.py) - Lista projetos disponíveis
- [`debug/debug_specific_issues.py`](./debug/debug_specific_issues.py) - Analisa issues específicas
- [`debug/debug_story_tipo.py`](./debug/debug_story_tipo.py) - Analisa campo de tipo de story
- [`debug/debug_team_field.py`](./debug/debug_team_field.py) - Análise de campos customizados de team
- [`debug/debug_lead_time_13437.py`](./debug/debug_lead_time_13437.py) - Análise de lead time da issue 13437
- [`debug/debug_lead_time_14288.py`](./debug/debug_lead_time_14288.py) - Análise de lead time da issue 14288
- [`debug/import_requests.py`](./debug/import_requests.py) - Importação de issues do Jira

## 📊 Relatórios

Os relatórios HTML são salvos automaticamente na pasta `relatorios/` com timestamp e podem ser visualizados diretamente no navegador:

- `sprint_review_YYYYMMDD_HHMMSS.html` - Relatório de Sprint Review
- `backlog_geral_YYYYMMDD_HHMMSS.html` - Relatório geral do Backlog

## 🔧 Manutenção

### Logs (2)

Logs de execução são salvos automaticamente em `logs/` para rastreamento e debug.

### Processamento de CSVs

Arquivos CSV processados são automaticamente movidos para `issues/Processados/` com controle de duplicatas via timestamp.

## � Workflow Recomendado

Para garantir qualidade antes de executar em produção:

``` bash

# 1️⃣ Execute a suite completa de testes

python tests/run_all_tests.py

# 2️⃣ Coloque o CSV na pasta issues/

# Certifique-se de que está no formato esperado

# 3️⃣ Teste com dry-run (valide o JSON)

python automatizar_issues.py --dry-run

# 4️⃣ Revise o JSON exibido no console

# Verifique campos obrigatórios, custom fields, etc

# 5️⃣ Se tudo estiver OK, execute em produção

python automatizar_issues.py

# 6️⃣ Verifique o relatório gerado

cat issues/relatorio_processamento_csv.txt

# 7️⃣ Confirme issues criadas no Jira

# Acesse os links fornecidos no relatório

# Nota: Pode usar 'py' em vez de 'python' em todos os comandos

``` text

**⚠️ IMPORTANTE:** Sempre execute o dry-run antes de criar issues em produção!

## �🛠️ Troubleshooting

### Erro: "Arquivo BulkCreate_configuration.txt não encontrado"

- Certifique-se de que o arquivo existe na raiz do projeto
- Valide que o JSON está bem formatado

### Erro: "JIRA_TOKEN não definido"

- Configure o arquivo `.env` com todas as variáveis necessárias
- Verifique se o token Bearer está correto

### Erro: "AttributeError: 'str' object has no attribute 'get'"

- Este erro foi corrigido na versão atual
- O campo `issuetype` agora retorna objeto `{'name': value}` corretamente

### Issues não criadas

- Execute `tests/test_jira_connection.py` para validar conectividade
- Execute `tests/test_bulk_create_api.py` para validar estrutura do payload
- Use `python automatizar_issues.py --dry-run` (ou `py automatizar_issues.py --dry-run`) para verificar o JSON gerado
- Verifique os logs para detalhes do erro

### Dúvida: "Como validar o JSON antes de criar?"

- Use o **modo dry-run**: `python automatizar_issues.py --dry-run` (ou `py automatizar_issues.py --dry-run`)
- Isso mostra o JSON completo sem chamar a API
- Valide campos obrigatórios: `project`, `issuetype`, `summary`
- Confira custom fields esperados no seu CSV (ex.: `customfield_10401`, `customfield_10101`, `customfield_10100`).

### Dúvida: "Qual script de relatório usar?"

- **Precisa de ambos os relatórios?** → Use `gerar_relatorios_completos.py` ⚡ (50% mais rápido)
- **Apenas Sprint Review?** → Use `gerar_lista_itens_sprint_review.py`
- **Apenas Relatório Geral?** → Use `gerar_lista_itens_geral_projeto.py`
- **Automação diária?** → Use `gerar_relatorios_completos.py` (melhor custo-benefício)

---

## 🔧 Arquitetura do Código

### Módulo Centralizado: jira_utils.py

Todos os 3 scripts de relatórios foram refatorados para eliminar duplicação de código, utilizando o módulo compartilhado `jira_utils.py` que contém 20+ funções utilitárias:

#### Funções Principais

- **get_jira_issues()** - Conexão e busca de issues com campos configuráveis
- **find_current_sprint_info()** - Detecção multi-estratégia de sprint ativa
- **filter_sprint_issues()** - Filtragem de issues por sprint
- **group_issues_by_status()** - Agrupamento em 6 categorias do pipeline
- **calculate_metrics()** - Cálculo completo de métricas ágeis
- **calculate_lead_time()** - Lead time diferenciado por tipo de issue
- **calculate_age_since_backlog()** - Idade desde saída do backlog
- **calculate_cycle_time_by_status()** - Tempo médio por status
- **check_status_history_in_sprint_period()** - Detecção de itens entregues
- **print_summary()** - Formatação de resumos no console

#### Benefícios da Refatoração

- ✅ **~1500 linhas de código duplicado eliminadas**
- ✅ **Ponto único de manutenção**: Alterar jira_utils.py afeta todos os scripts
- ✅ **Melhor testabilidade**: Funções centralizadas podem ser testadas independentemente
- ✅ **Código mais limpo**: Scripts focados apenas em lógica específica
- ✅ **Consistência**: Mesma lógica aplicada em todos os relatórios

#### Exemplo de Benefício Prático

Antes da refatoração: Para alterar a autenticação do Jira, era necessário editar 3 arquivos diferentes.
Após a refatoração: Altere apenas 1 linha em `jira_utils.py` e todos os scripts são atualizados automaticamente! 🎉

---

**Desenvolvido por:** GitHub Copilot
**Última atualização:** 09/02/2026

# Integracao_Jira_Docmatch
