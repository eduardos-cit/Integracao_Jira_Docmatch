# 🤖 automatizar_issues.py

Script de automação para criação em massa de issues no Jira a partir de arquivos CSV.

## 📋 Índice

- Visão Geral
- Funcionalidades
- Pré-requisitos
- Configuração
- Como Usar
- Modo Dry-Run
- Estrutura do CSV
- Mapeamento de Campos
- API do Jira
- Logs e Relatórios
- Troubleshooting

---

## 🎯 Visão Geral

O `automatizar_issues.py` é um script Python que automatiza a criação em lote de issues no Jira usando a API oficial Bulk Create. Ele lê arquivos CSV de uma pasta, mapeia as colunas para campos do Jira e cria as issues em uma única chamada de API.

### Principais benefícios

- ⚡ Criação em lote (bulk) - muito mais rápido que criar uma por uma
- 🗺️ Mapeamento flexível de campos via arquivo de configuração
- ✅ Validação automática de campos obrigatórios
- 🔍 Modo dry-run para testar antes de executar
- 📦 Organização automática de arquivos processados
- 📊 Relatórios detalhados de execução

---

## ✨ Funcionalidades

### Processamento de CSV

- 📥 Leitura automática de todos os arquivos `.csv` da pasta configurada
- 🔄 Processamento de múltiplos arquivos em sequência
- 📝 Suporte a diferentes encodings (UTF-8 configurável)
- 🚫 Arquivos iniciados com `template` são automaticamente ignorados

### Mapeamento de Campos

- 🗺️ Mapeamento flexível via `BulkCreate_configuration.txt`
- 🏷️ Suporte a campos padrão (project, issuetype, summary, description)
- 🎨 Suporte a custom fields (customfield_XXXXX)
- 👨‍👩‍👧 Suporte a campos de relacionamento (parent, epic)

### Criação de Issues

- 🚀 Bulk create - uma chamada API para múltiplas issues
- ✅ Validação de campos obrigatórios antes do envio
- 🔐 Autenticação Bearer token
- ⏱️ Timeout configurável (60s por padrão)

### Organização de Arquivos

- 📦 Movimentação automática para `issues/Processados/`
- 🔄 Controle de duplicatas com timestamp
- 🗂️ Criação automática de estrutura de pastas

### Validação e Testes

- 🔍 Modo dry-run - testa sem criar issues
- 📊 Exibição do JSON que seria enviado
- ✅ 6 testes automatizados disponíveis

### Logs e Relatórios

- 📝 Logs detalhados em arquivo
- 📄 Relatório em texto com resultados
- 🔗 Links diretos para issues criadas

---

## 📦 Pré-requisitos

### Python

- Python 3.8 ou superior

### Bibliotecas

``` bash

pip install requests python-dotenv

```

### Arquivos Necessários

- ✅ `.env` - Credenciais e configurações
- ✅ `BulkCreate_configuration.txt` - Mapeamento de campos
- ✅ Arquivo(s) CSV na pasta `issues/`

---

## ⚙️ Configuração

### 1. Arquivo `.env`

Crie o arquivo `.env` na raiz do projeto:

``` properties

# URL do servidor Jira

JIRA_URL=<https://jira.bradesco.com.br:8443>

# Token de autenticação Bearer

# Obtenha em: Jira → Perfil → Segurança → Criar token

JIRA_TOKEN=seu_token_bearer_aqui

# Chave do projeto no Jira

JIRA_PROJECT=PLTFAT

# Nome do time/squad

TEAM_NAME=DocMatch

# Pasta onde estão os arquivos CSV

folder_path=issues

```

### ⚠️ Importante

- Não versione o arquivo `.env` (adicione ao `.gitignore`)
- O token tem acesso total - mantenha seguro
- Use um token de serviço, não seu token pessoal

---

### 2. Arquivo `BulkCreate_configuration.txt`

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

### Campos especiais

- IDs em `existing.custom.field` (ex: `"10401"`) → custom fields (`customfield_10401`)
- `"subtask-parent-id"` → campo `parent` para subtasks
- `Theme` (`10500`) permanece no mapeamento, mas é ignorado no payload final

---

### 3. Estrutura de Pastas

``` text

Integracao Jira/
├── .env                          ← Credenciais
├── BulkCreate_configuration.txt  ← Mapeamento
├── automatizar_issues.py         ← Script principal
├── issues/                       ← CSVs para processar
│   ├── arquivo1.csv
│   ├── arquivo2.csv
│   └── Processados/              ← CSVs já processados (criada automaticamente)
└── logs/                         ← Logs de execução

```

---

## 🚀 Como Usar

### Modo Normal (Produção)

### 1. Prepare o CSV

- Coloque o arquivo na pasta `issues/`
- Certifique-se de que as colunas correspondem ao mapeamento
- ⚠️ **Importante**: Arquivos iniciados com `template` são automaticamente ignorados

### 2. Execute o script

``` bash

python automatizar_issues.py

# ou: py automatizar_issues.py

```

### 3. Acompanhe a execução

``` text

======================================================================
    AUTOMATIZAÇÃO CSV → JIRA
======================================================================

Processando arquivos da pasta: issues
Encontrados 1 arquivos .csv para processar

============================================================
Processando arquivo: meu_arquivo.csv
============================================================

Arquivo issues\meu_arquivo.csv: 28 issues mapeadas
Preparando criação em lote de 28 issues
✓ Bulk create concluído: 28 issues criadas

======================================================================
    PROCESSAMENTO CONCLUÍDO
======================================================================
Total de arquivos: 1
Issues criadas: 28
Erros: 0

```

### 4. Verifique os resultados

- Issues criadas no Jira
- Arquivo movido para `issues/Processados/`
- Relatório em `issues/relatorio_processamento_csv.txt`

---

## 🔍 Modo Dry-Run

### Teste o JSON sem criar issues no Jira

### Quando usar

- ✅ Validar mapeamento de campos antes de executar
- ✅ Revisar estrutura do JSON com a equipe
- ✅ Debugar problemas de conversão
- ✅ Conferir valores antes de criar em produção

### Como executar

``` bash

python automatizar_issues.py --dry-run

# ou: py automatizar_issues.py --dry-run

```

### O que acontece

| Etapa | Executa? |
| ------- | ---------- |
| Carregar `.env` | ✅ SIM |
| Ler `BulkCreate_configuration.txt` | ✅ SIM |
| Processar CSV | ✅ SIM |
| Gerar JSON | ✅ SIM |
| **Salvar JSON em `logs/bulk_payload_test_*.json`** | ✅ SIM |
| **Exibir JSON completo** | ✅ SIM |
| Chamar API Jira | ❌ NÃO |
| Criar issues | ❌ NÃO |
| Mover arquivo | ❌ NÃO |

### Output do dry-run

``` bash

# O JSON é exibido no console e salvo em arquivo

📄 JSON salvo em: logs/bulk_payload_test_20260219_143022.json

```

``` json

======================================================================
🔍 MODO DRY-RUN - JSON que seria enviado à API:
======================================================================

{
  "issueUpdates": [
    {
      "fields": {
        "project": {"key": "PLTFAT"},
        "issuetype": {"name": "Sub-Imp"},
        "description": "[DEV]Solicitação e Configuração",
        "timetracking": {
          "originalEstimate": "60d",
          "remainingEstimate": "60d"
        },
        "parent": {"key": "PLTFAT-11431"},
        "summary": "[DEV]Solicitação e Configuração",
        "customfield_10401": "DocMatch"
      },
      "update": {}
    },
    ... (mais issues)
  ]
}

======================================================================
📊 Total de issues no payload: 28
⚠️  API NÃO FOI CHAMADA (modo dry-run)
======================================================================

```

**⚠️ Recomendação:** Sempre execute o dry-run antes da primeira execução em produção!

---

## 📄 Estrutura do CSV

### Formato Esperado

``` csv

Issue Type,Summary,Description,Team,Original Estimate,Assignee,Parent Id,Sprint ID,Epic Link,Labels
Sub-Imp,[DEV]Solicitação,[DEV]Solicitação e Config,DocMatch,28800,f123456,PLTFAT-11431,,,desenvolvimento
Sub-Test,[QA]Execução Teste,[QA]Execução Teste,DocMatch,216000,f789012,PLTFAT-11431,,,teste

```

### Regras Importantes

1. **Primeira linha = cabeçalho**

  Nomes das colunas devem corresponder ao `config.field.mappings`.

1. **Encoding = UTF-8**

  Caracteres especiais (ã, ç, é) devem funcionar.
  Configure no Excel: "CSV UTF-8 (delimitado por vírgulas)".

1. **Campos obrigatórios no CSV:**

  `Issue Type` → tipo da issue; `Summary` → título da issue; `Project` → geralmente fixo no script, pode ser omitido.

1. **Original Estimate (obrigatório):**

  Valor em **segundos** (formato exportado do Excel).
  O script converte para formato Jira automaticamente: divide por 3600 para obter horas,
  divide por 8 para obter dias (1 dia Jira = 8 horas) e formata como "5d", "3d 4h" ou "6h".
  Exemplo: `28800` segundos → 8 horas → 1 dia → `"1d"`.
  **⚠️ Se não informado ou vazio, o script definirá automaticamente como "0h".**

1. **Parent Id (para subtasks):**

  Formato: `PLTFAT-11431`.
  Usar chave da issue pai.
  Deixar vazio para issues normais (não subtasks).

### Exemplo Completo

``` csv

Issue Type,Summary,Description,Team,Original Estimate,Assignee,Parent Id,Sprint ID,Epic Link,Labels
Sub-Imp,[DEV]Backend API,[DEV]Implementar endpoint,DocMatch,1728000,,PLTFAT-11431,,,backend;api
Sub-Imp,[DEV]Frontend UI,[DEV]Criar tela,DocMatch,1296000,,PLTFAT-11431,,,"frontend,ui"
Sub-Test,[QA]Teste integração,[QA]Testar API,DocMatch,216000,,PLTFAT-11431,,,teste
Task,Análise técnica,Análise de viabilidade,DocMatch,28800,,,,PLTFAT-100,analise

```

---

## 🗺️ Mapeamento de Campos

### Como Funciona

O arquivo `BulkCreate_configuration.txt` mapeia:

``` text

Nome da coluna no CSV → Campo no Jira

```

### Tipos de Campos

#### 1. Campos Padrão do Jira

``` json

"config.field.mappings": {
  "Summary": {"jira.field": "summary"},
  "Description": {"jira.field": "description"},
  "Assignee": {"jira.field": "assignee"},
  "Labels": {"jira.field": "labels"}
}

```

#### 2. Custom Fields (Campos Personalizados)

``` json

"config.field.mappings": {
  "Team": {"existing.custom.field": "10401"},
  "Epic Link": {"existing.custom.field": "10101"},
  "Sprint ID": {"existing.custom.field": "10100"},
  "Theme": {"existing.custom.field": "10500"} // ignorado no envio
}

```

### Como descobrir o ID de um custom field

``` bash

# Via API Jira

curl -H "Authorization: Bearer TOKEN" \
  <https://jira.bradesco.com.br:8443/rest/api/2/field>

# Procure por "customfield_XXXXX"

```

#### 3. Campos de Relacionamento

``` json

"config.field.mappings": {
  "Parent Id": {"jira.field": "subtask-parent-id"}
}

```

#### 4. Conversões Automáticas

| Campo CSV | Valor CSV | Enviado à API |
| ----------- | ----------- | --------------- |
| `Issue Type` | `Sub-Imp` | `{"name": "Sub-Imp"}` |
| `Parent Id` | `PLTFAT-11431` | `{"key": "PLTFAT-11431"}` |
| `Project` | `PLTFAT` | `{"key": "PLTFAT"}` |
| `Original Estimate` | `28800` (segundos) | `{"originalEstimate": "1d"}` |
| `Original Estimate` | `216000` (segundos) | `{"originalEstimate": "7d 4h"}` |
| `Original Estimate` | `14400` (segundos) | `{"originalEstimate": "4h"}` |
| `Original Estimate` | (vazio/não informado) | `{"originalEstimate": "0h"}` |

---

## 📁 Arquivos JSON Salvos

### Salvamento Automático

O script **salva automaticamente** o payload JSON em arquivo, tanto no modo teste quanto em produção.

### Localização e Nomenclatura

``` text

logs/
├── bulk_payload_test_20260219_143022.json   # Dry-run (teste)
├── bulk_payload_prod_20260219_150815.json   # Execução real
└── automatizacao_issues.log                 # Log de execução

```

### Formato do nome

``` text

bulk_payload_{tipo}_{timestamp}.json

{tipo}      = "test" (dry-run) ou "prod" (produção)
{timestamp} = YYYYMMDD_HHMMSS

```

### Para que serve

- ✅ **Auditoria:** histórico de todos os payloads enviados
- ✅ **Debug:** investigar erros ou validar conversões
- ✅ **Replay:** reenviar o mesmo payload se necessário
- ✅ **Documentação:** evidência do que foi criado
- ✅ **Análise:** validar mapeamentos antes de produção

### Exemplo de Arquivo

### `logs/bulk_payload_test_20260219_143022.json`

``` json

{
  "issueUpdates": [
    {
      "fields": {
        "project": {"key": "PLTFAT"},
        "issuetype": {"name": "Sub-Imp"},
        "summary": "[DEV]Backend API",
        "timetracking": {
          "originalEstimate": "60d",
          "remainingEstimate": "60d"
        },
        "parent": {"key": "PLTFAT-11431"},
        "customfield_10401": "DocMatch"
      },
      "update": {}
    }
  ]
}

```

---

## 📡 API do Jira

### Endpoint Utilizado

``` text

POST /rest/api/2/issue/bulk

```

### Documentação oficial

- Jira Server/Data Center: <https://docs.atlassian.com/software/jira/docs/api/REST/latest/#api/2/issue-createIssues>
- Jira Cloud: <https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issues/#api-rest-api-3-issue-bulk-post>

### Estrutura do Payload

``` json

{
  "issueUpdates": [
    {
      "fields": {
        "project": {"key": "PLTFAT"},
        "issuetype": {"name": "Task"},
        "summary": "Título da issue",
        "description": "Descrição detalhada",
        "assignee": {"name": "f123456"},
        "customfield_10401": "DocMatch",
        "parent": {"key": "PLTFAT-11431"}
      },
      "update": {}
    }
  ]
}

```

### Campos Obrigatórios

| Campo | Tipo | Obrigatório | Descrição |
| ------- | ------ | ------------- | ----------- |
| `project` | Object | ✅ SIM | `{"key": "PLTFAT"}` |
| `issuetype` | Object | ✅ SIM | `{"name": "Task"}` |
| `summary` | String | ✅ SIM | Título da issue |
| `timetracking.originalEstimate` | String | ✅ SIM | `"0h"` (padrão se não informado) |
| `description` | String | ❌ Não | Descrição da issue |
| `parent` | Object | ⚠️ Subtasks | `{"key": "PARENT-123"}` |

### Autenticação

``` http

POST /rest/api/2/issue/bulk HTTP/1.1
Host: jira.bradesco.com.br:8443
Authorization: Bearer SEU_TOKEN_AQUI
Content-Type: application/json

```

### Resposta de Sucesso (201)

``` json

{
  "issues": [
    {
      "id": "123456",
      "key": "PLTFAT-14501",
      "self": "<https://jira.../rest/api/2/issue/123456">
    }
  ],
  "errors": []
}

```

### Resposta com Erros

``` json

{
  "issues": [...],
  "errors": [
    {
      "status": 400,
      "elementErrors": {
        "errorMessages": ["Field 'summary' is required"]
      }
    }
  ]
}

```

---

## 📊 Logs e Relatórios

### Logs em Arquivo

**Local:** `logs/automatizacao_issues.log`

``` text

2026-02-07 16:22:50,515 - INFO - Conectando ao Jira: <https://jira.bradesco.com.br:8443>
2026-02-07 16:22:50,517 - INFO - Projeto: PLTFAT
2026-02-07 16:22:50,519 - INFO - Encontrados 1 arquivos .csv para processar
2026-02-07 16:22:50,520 - INFO - Arquivo issues\arquivo.csv: 28 issues mapeadas
2026-02-07 16:22:50,520 - INFO - Preparando criação em lote de 28 issues
2026-02-07 16:22:51,234 - INFO - ✓ Bulk create concluído: 28 issues criadas

```

### Relatório de Processamento

**Local:** `issues/relatorio_processamento_csv.txt`

``` text

======================================================================
  RELATÓRIO DE PROCESSAMENTO CSV → JIRA
======================================================================
Data/Hora: 07/02/2026 16:22:51

----------------------------------------------------------------------
  RESUMO GERAL
----------------------------------------------------------------------
Total de arquivos processados: 1
Total de issues criadas: 28
Total de erros: 0

======================================================================
  ARQUIVOS PROCESSADOS COM SUCESSO
======================================================================

Arquivo: meu_arquivo.csv
Issues criadas: 28
Erros: 0

Issues criadas neste arquivo:

  - PLTFAT-14501: [DEV]Solicitação e Configuração

    URL: <https://jira.bradesco.com.br:8443/browse/PLTFAT-14501>

  - PLTFAT-14502: [DEV]Deploy em DEV

    URL: <https://jira.bradesco.com.br:8443/browse/PLTFAT-14502>

  ... (26 issues adicionais)

======================================================================

```

### Console Output

### Modo Normal

``` text

✅ Processamento concluído!
📊 Total de issues criadas: 28
❌ Total de erros: 0
📄 Relatório salvo: issues/relatorio_processamento_csv.txt

```

### Modo Dry-Run

``` text

🔍 Dry-run concluído!
📊 Issues que seriam criadas: 28
⚠️  Nenhuma issue foi criada (modo teste)

```

---

## 🛠️ Troubleshooting

### Erro: "Arquivo .env não encontrado"

**Causa:** Arquivo `.env` não existe ou não está na raiz do projeto

### Solução

``` bash

# Crie o arquivo .env na raiz

touch .env

# Adicione as variáveis necessárias

echo "JIRA_URL=<https://jira.bradesco.com.br:8443"> >> .env
echo "JIRA_TOKEN=seu_token" >> .env
echo "JIRA_PROJECT=PLTFAT" >> .env
echo "TEAM_NAME=DocMatch" >> .env
echo "folder_path=issues" >> .env

```

---

### Erro: "Arquivo BulkCreate_configuration.txt não encontrado"

**Causa:** Arquivo de configuração não existe na raiz

### Solução: (2)

1. Verifique se o arquivo existe: `ls BulkCreate_configuration.txt`
1. Nome deve ser exatamente: `BulkCreate_configuration.txt` (case-sensitive)
1. Deve estar na raiz do projeto, não em subpasta

---

### Erro: "401 Unauthorized"

**Causa:** Token inválido ou expirado

### Solução: (3)

``` bash

# 1. Teste o token manualmente

curl -H "Authorization: Bearer SEU_TOKEN" \
  <https://jira.bradesco.com.br:8443/rest/api/2/myself>

# 2. Se falhar, gere novo token

# Jira → Perfil → Segurança → Criar token de API

# 3. Atualize o .env

JIRA_TOKEN=novo_token_aqui

```

---

### Erro: "400 Bad Request - Field 'summary' is required"

**Causa:** Campo obrigatório ausente no CSV

### Solução: (4)

1. Verifique se a coluna `Summary` existe no CSV
1. Certifique-se de que há valores em todas as linhas
1. Use dry-run para ver o JSON: `python automatizar_issues.py --dry-run` (ou `py automatizar_issues.py --dry-run`)

---

### Erro: "Issue Type 'Sub-Imp' não existe"

**Causa:** Tipo de issue não disponível no projeto

### Solução: (5)

``` bash

# Liste os tipos disponíveis

curl -H "Authorization: Bearer TOKEN" \
  <https://jira.bradesco.com.br:8443/rest/api/2/project/PLTFAT>

# Use um tipo válido no CSV

# Exemplos: Task, Story, Bug, Sub-task

```

---

### Erro: "UnicodeDecodeError"

**Causa:** Encoding incorreto do CSV

### Solução: (6)

1. Abra o CSV no Excel
1. Salvar Como → CSV UTF-8 (delimitado por vírgulas)
1. Ou converta via Python:

``` python

import pandas as pd
df = pd.read_csv('arquivo.csv', encoding='latin-1')
df.to_csv('arquivo_utf8.csv', encoding='utf-8', index=False)

```

---

### Erro: "Parent issue 'PLTFAT-11431' not found"

**Causa:** Issue pai não existe ou você não tem acesso

### Solução: (7)

1. Verifique se a issue pai existe: `<https://jira.../browse/PLTFAT-11431`>
1. Certifique-se de que você tem permissão para visualizá-la
1. Se for criar subtask, a issue pai deve ser criada primeiro

---

### Issues não aparecem após criação bem-sucedida

**Causa:** Issues criadas mas não aparecem na busca

### Solução: (8)

1. Aguarde alguns minutos (indexação do Jira)
1. Use o link direto do relatório
1. Verifique filtros ativos na busca do Jira
1. Confirme que está no projeto correto

---

### Arquivo não é movido para Processados/

**Causa:** No modo dry-run, arquivos não são movidos

### Solução: (9)

- Modo dry-run: Arquivos permanecem em `issues/` ✅ Esperado
- Modo normal: Arquivos vão para `issues/Processados/`
- Se no modo normal não moveu, verifique permissões da pasta

---

### Performance: Script muito lento

**Causa:** Timeout padrão é 60s por arquivo

### Solução: (10)

``` python

# Edite automatizar_issues.py

# Linha ~253

response = requests.post(create_url, headers=headers, json=bulk_payload,
                        verify=False, timeout=120)  # Aumentar para 120s

```

### Ou divida o CSV

``` python

# Processar 50 issues por vez

import pandas as pd
df = pd.read_csv('arquivo_grande.csv')

for i in range(0, len(df), 50):
    chunk = df[i:i+50]
    chunk.to_csv(f'arquivo_parte_{i//50 + 1}.csv', index=False)

```

---

## 📚 Referências

- **API Oficial Jira:** <https://developer.atlassian.com/cloud/jira/platform/rest/v3/>
- **Bulk Create Endpoint:** POST /rest/api/2/issue/bulk
- **Custom Fields:** <https://confluence.atlassian.com/adminjiraserver/custom-fields-938847222.html>
- **Issue Types:** <https://support.atlassian.com/jira-cloud-administration/docs/what-are-issue-types/>

---

## 🔄 Workflow Completo

``` bash

# 1. Configure o ambiente

cp .env.example .env
vim .env  # Adicione suas credenciais

# 2. Valide a configuração

python tests/run_all_tests.py

# 3. Prepare o CSV

# - Coloque em issues/

# - Verifique encoding UTF-8

# - Confirme mapeamento de colunas

# 4. Teste com dry-run

python automatizar_issues.py --dry-run

# 5. Revise o JSON gerado

# - Verifique campos obrigatórios

# - Confirme custom fields

# - Valide valores

# 6. Execute em produção

python automatizar_issues.py

# 7. Valide resultados

cat issues/relatorio_processamento_csv.txt

# Acesse os links das issues criadas

# Nota: Pode usar 'py' em vez de 'python' em todos os comandos

# 8. Confirme no Jira

# Abra o projeto e verifique as issues

```

---

**Última atualização:** 07/02/2026
**Versão:** 1.0
**Autor:** GitHub Copilot
**Suporte:** Consulte [tests/README_TESTS.md](../tests/README_TESTS.md) para testes e troubleshooting
