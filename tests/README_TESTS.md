# 🧪 Testes - Integração Jira

Documentação completa da suite de testes do projeto de automação Jira.

## 📋 Índice

- Suite Completa de Testes
- Padronização Markdown
- Testes Individuais
- Modo Dry-Run
- Interpretando Resultados
- Troubleshooting

---

## 🎯 Suite Completa de Testes

### Executar Todos os Testes

``` bash

python tests/run_all_tests.py

# ou: py tests/run_all_tests.py

```

## 📝 Padronização Markdown

Como etapa padrão ao atualizar documentação, execute:

``` bash

python tools/fix_markdown.py --all --check

```

Se houver ajustes pendentes, aplique com:

``` bash

python tools/fix_markdown.py --all

```

### O que é testado

A suite executa **6 testes automatizados** que validam toda a cadeia de processamento:

| # | Teste | Arquivo | O que valida |
| --- | ------- | --------- | -------------- |
| 1️⃣ | Carregamento de Variáveis | `test_load_environment.py` | `.env` com 5 variáveis (JIRA_URL, JIRA_TOKEN, JIRA_PROJECT, TEAM_NAME, folder_path) |
| 2️⃣ | Carregamento de Configuração | `test_load_bulk_configuration.py` | `BulkCreate_configuration.txt` com 12 mapeamentos de campos |
| 3️⃣ | Parsing de CSV | `test_parse_csv.py` | Leitura e mapeamento de 28 issues do CSV para estrutura Jira |
| 4️⃣ | Movimentação de Arquivos | `test_move_to_processed.py` | Move CSVs para `issues/Processados/` com controle de duplicatas |
| 5️⃣ | Conexão com API Jira | `test_jira_connection.py` | Valida autenticação e acesso ao projeto PLTFAT |
| 6️⃣ | Validação Bulk Create API | `test_bulk_create_api.py` | Estrutura do payload conforme API oficial Atlassian |

### Resultado Esperado

``` text

======================================================================
  RELATÓRIO FINAL
======================================================================

Total de testes: 6
✅ Passaram: 6
❌ Falharam: 0
⏱️  Tempo total: ~2s

Detalhes:
  ✅ PASSOU - Teste 1: Carregamento de Variáveis de Ambiente (0.28s)
  ✅ PASSOU - Teste 2: Carregamento de Configuração (0.28s)
  ✅ PASSOU - Teste 3: Parsing de CSV (0.29s)
  ✅ PASSOU - Teste 4: Movimentação de Arquivos (0.31s)
  ✅ PASSOU - Teste 5: Conexão com API Jira (0.63s)
  ✅ PASSOU - Teste 6: Validação Bulk Create API (0.29s)

======================================================================
🎉 TODOS OS TESTES PASSARAM!
======================================================================

```

---

## 🔬 Testes Individuais

### 1️⃣ Teste: Carregamento de Variáveis de Ambiente

**Arquivo:** `tests/test_load_environment.py`

### Execução

``` bash

python tests/test_load_environment.py

# ou: py tests/test_load_environment.py

```

### O que faz

- Carrega o arquivo `.env`
- Valida presença de 5 variáveis obrigatórias
- Verifica se valores não estão vazios

### Validações

- ✅ `JIRA_URL` presente e não vazio
- ✅ `JIRA_TOKEN` presente e não vazio (oculto no log por segurança)
- ✅ `JIRA_PROJECT` presente e não vazio
- ✅ `TEAM_NAME` presente e não vazio
- ✅ `folder_path` presente e não vazio

### Output esperado

``` text

✓ Variáveis carregadas com sucesso:

  - JIRA_URL: <https://jira.bradesco.com.br:8443>
  - JIRA_TOKEN: ******************** (oculto por segurança)
  - JIRA_PROJECT: PLTFAT
  - TEAM_NAME: DocMatch
  - folder_path: issues

✅ TESTE PASSOU - Todas as variáveis foram carregadas corretamente

```

---

### 2️⃣ Teste: Carregamento de Configuração

**Arquivo:** `tests/test_load_bulk_configuration.py`

### Execução: (2)

``` bash

python tests/test_load_bulk_configuration.py

# ou: py tests/test_load_bulk_configuration.py

```

### O que faz: (2)

- Lê o arquivo `BulkCreate_configuration.txt`
- Valida estrutura JSON
- Verifica mapeamentos de campos

### Validações: (2)

- ✅ Arquivo JSON válido
- ✅ 11 campos mapeados corretamente
- ✅ Configuração de projeto (key, name, lead)
- ✅ Campos obrigatórios presentes

### Mapeamentos validados

``` text

Assignee → assignee
Issue Type → issuetype
Description → description
Original Estimate → timeoriginalestimate
Parent Id → subtask-parent-id
Summary → summary
Theme → 10500 (customfield, ignorado no payload)
Labels → labels
Team → 10401 (customfield)
Epic Link → 10101 (customfield)
Sprint ID → 10100 (customfield)

```

---

### 3️⃣ Teste: Parsing de CSV

**Arquivo:** `tests/test_parse_csv.py`

### Execução: (3)

``` bash

python tests/test_parse_csv.py

# ou: py tests/test_parse_csv.py

```

### O que faz: (3)

- Lê arquivo CSV da pasta `issues/`
- Mapeia colunas para campos Jira
- Valida estrutura dos objetos gerados

### Validações: (3)

- ✅ 28 issues parseadas do CSV
- ✅ Campo `project` como objeto `{"key": "PLTFAT"}`
- ✅ Campo `issuetype` como objeto `{"name": "Sub-Imp"}`
- ✅ Campo `parent` para subtasks `{"key": "PLTFAT-11431"}`
- ✅ Custom fields com IDs corretos

### Output esperado: (2)

``` text

✓ Issues parseadas: 28

📋 Exemplos de issues parseadas:

  Issue 1:
    Project: PLTFAT
    Type: Sub-Imp
    Summary: [DEV]Solicitação e Configuração...
    Custom Fields: 1+
      - customfield_10401: DocMatch

```

---

### 4️⃣ Teste: Movimentação de Arquivos

**Arquivo:** `tests/test_move_to_processed.py`

### Execução: (4)

``` bash

python tests/test_move_to_processed.py

# ou: py tests/test_move_to_processed.py

```

### O que faz: (4)

- Cria arquivo de teste temporário
- Move arquivo para subpasta `Processados/`
- Testa controle de duplicatas com timestamp

### Validações: (4)

- ✅ Pasta `Processados/` é criada se não existir
- ✅ Arquivo é movido corretamente
- ✅ Arquivo original é removido da pasta principal
- ✅ Duplicatas ganham sufixo com timestamp `_YYYYMMDD_HHMMSS`

### Output esperado: (3)

``` text

📁 Criando estrutura de teste...
  ✓ Arquivo criado: test_temp_folder\test_file.csv

📦 Movendo arquivo para Processados...
  ✓ Pasta Processados existe: test_temp_folder\Processados
  ✓ Arquivo movido: test_temp_folder\Processados\test_file.csv
  ✓ Arquivo original removido

✅ TESTE PASSOU - Arquivos movidos corretamente

```

---

### 5️⃣ Teste: Conexão com API Jira

**Arquivo:** `tests/test_jira_connection.py`

### Execução: (5)

``` bash

python tests/test_jira_connection.py

# ou: py tests/test_jira_connection.py

```

### O que faz: (5)

- Testa conexão com servidor Jira
- Valida autenticação Bearer token
- Lista informações do projeto

### Validações: (5)

- ✅ Conexão estabelecida com sucesso
- ✅ Token válido (autenticação OK)
- ✅ Projeto PLTFAT acessível
- ✅ Tipos de issue disponíveis (60+ tipos)

### Output esperado: (4)

``` text

📡 Testando conexão com <https://jira.bradesco.com.br:8443...>

✅ CONEXÃO ESTABELECIDA COM SUCESSO

📊 Informações do Projeto:

  - Key: PLTFAT
  - Name: PLATAFORMA | A3C - Fatores de Autenticacao
  - ID: 32001
  - Lead: CASSIO GOES DE MORAES CORDEIRO

  - Issue Types disponíveis: 60

    • Action Plan
    • Agile Mastering
    • Analytics
    • Block
    • Bug

```

---

### 6️⃣ Teste: Validação Bulk Create API

**Arquivo:** `tests/test_bulk_create_api.py`

### Execução: (6)

``` bash

python tests/test_bulk_create_api.py

# ou: py tests/test_bulk_create_api.py

```

### O que faz: (6)

- Valida estrutura do payload conforme API oficial
- Testa formato de campos obrigatórios
- Dry-run da chamada API (sem criar issues)

### Validações: (6)

- ✅ Payload tem chave raiz `issueUpdates`
- ✅ Cada item contém `fields` e `update`
- ✅ Campos obrigatórios presentes (project, issuetype, summary)
- ✅ Estrutura conforme documentação Atlassian

### Estrutura validada

``` json

{
  "issueUpdates": [
    {
      "fields": {
        "project": {"key": "PLTFAT"},
        "issuetype": {"name": "Sub-Imp"},
        "summary": "[DEV]Solicitação e Configuração",
        "description": "...",
        "customfield_10401": "DocMatch"
      },
      "update": {}
    }
  ]
}

```

---

## 🔍 Modo Dry-Run

### O que é

O **modo dry-run** permite testar o processamento completo **sem criar issues no Jira**.

É ideal para:

- 🔍 Validar o JSON antes de executar em produção
- ✅ Verificar mapeamento de campos
- 🐛 Debugar problemas de conversão
- 📊 Revisar estrutura com a equipe

### Como usar

``` bash

python automatizar_issues.py --dry-run

# ou: py automatizar_issues.py --dry-run

```

### O que acontece no dry-run

| Etapa | Executa? | Descrição |
| ------- | ---------- | ----------- |
| 1️⃣ Carregar `.env` | ✅ SIM | Valida configurações |
| 2️⃣ Ler `BulkCreate_configuration.txt` | ✅ SIM | Carrega mapeamentos |
| 3️⃣ Processar CSV | ✅ SIM | Lê e mapeia todos os campos |
| 4️⃣ Gerar JSON | ✅ SIM | Cria payload completo |
| 5️⃣ **Exibir JSON** | ✅ SIM | **Mostra o JSON que seria enviado** |
| 6️⃣ Chamar API Jira | ❌ NÃO | **API não é chamada** |
| 7️⃣ Criar issues | ❌ NÃO | **Nenhuma issue é criada** |
| 8️⃣ Mover CSV | ❌ NÃO | **Arquivo permanece na pasta `issues/`** |

### Output do Dry-Run

``` text

======================================================================
    AUTOMATIZAÇÃO CSV → JIRA (MODO DRY-RUN)
======================================================================
⚠️  MODO DRY-RUN ATIVO: API não será chamada, apenas JSON será exibido

Processando arquivos da pasta: issues
Encontrados 1 arquivos .csv para processar

============================================================
Processando arquivo: [pltfat]_docmatch_-_import-jira_csv.csv
============================================================

Arquivo issues\[pltfat]_docmatch_-_import-jira_csv.csv: 28 issues mapeadas
Preparando criação em lote de 28 issues

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
    ... (27 issues adicionais)
  ]
}

======================================================================
📊 Total de issues no payload: 28
⚠️  API NÃO FOI CHAMADA (modo dry-run)
======================================================================

🔍 Dry-run concluído!
📊 Issues que seriam criadas: 28
⚠️  Nenhuma issue foi criada (modo teste)

```

### Comparação: Modo Normal vs Dry-Run

| Aspecto | Modo Normal | Modo Dry-Run |
| --------- | ------------- | -------------- |
| **Comando** | `python automatizar_issues.py` ou `py automatizar_issues.py` | `python automatizar_issues.py --dry-run` ou `py automatizar_issues.py --dry-run` |
| **Processa CSV** | ✅ | ✅ |
| **Gera JSON** | ✅ | ✅ |
| **Exibe JSON** | ❌ (apenas log) | ✅ (console completo) |
| **Chama API** | ✅ | ❌ |
| **Cria issues** | ✅ | ❌ |
| **Move arquivo** | ✅ para Processados/ | ❌ permanece em issues/ |
| **Use quando** | Pronto para produção | Validando antes de executar |

---

## 📊 Interpretando Resultados

### ✅ Teste Passou

Quando um teste passa, significa que:

- ✅ Funcionalidade está operacional
- ✅ Dados estão no formato esperado
- ✅ Integrações funcionando corretamente

### Exemplo

``` text

✅ TESTE PASSOU - 28 issues parseadas e validadas corretamente

```

### ❌ Teste Falhou

Quando um teste falha, investigue:

1. **Erro de configuração**
   - Verifique `.env` e `BulkCreate_configuration.txt`
   - Confira se os arquivos existem e estão no formato correto

1. **Erro de conectividade**
   - Teste conexão com o Jira
   - Verifique se o token está válido

1. **Erro de estrutura**
   - Confira se o CSV tem todas as colunas esperadas
   - Valide se os valores estão no formato correto

### Exemplo de falha

``` text

❌ TESTE FALHOU - Arquivo BulkCreate_configuration.txt não encontrado

```

### Solução

- Certifique-se de que o arquivo existe na raiz do projeto
- Valide o formato JSON com um validador online

---

## 🐛 Troubleshooting

### Problema: "Arquivo .env não encontrado"

**Causa:** Arquivo `.env` não existe ou não está na raiz do projeto

### Solução: (2)

``` bash

# Crie o arquivo .env na raiz do projeto

# com as 5 variáveis obrigatórias

JIRA_URL=<https://jira.bradesco.com.br:8443>
JIRA_TOKEN=seu_token_aqui
JIRA_PROJECT=PLTFAT
TEAM_NAME=DocMatch
folder_path=issues

```

---

### Problema: "Arquivo BulkCreate_configuration.txt não encontrado"

**Causa:** Arquivo de configuração não existe ou nome está incorreto

### Solução: (3)

``` bash

# Certifique-se de que o arquivo está na raiz

# Nome deve ser exatamente: BulkCreate_configuration.txt

# O conteúdo deve ser JSON válido

```

---

### Problema: "AttributeError: 'str' object has no attribute 'get'"

**Causa:** Campo `issuetype` sendo tratado como string em vez de objeto

### Solução: (4)

- Este erro foi corrigido na versão atual
- O campo `issuetype` agora retorna `{"name": "valor"}` corretamente
- Se ainda ocorrer, atualize o script `automatizar_issues.py`

---

### Problema: "UnboundLocalError: cannot access local variable 'datetime'"

**Causa:** Conflito de import do módulo `datetime`

### Solução: (5)

- Este erro foi corrigido na versão atual
- O import `from datetime import datetime` foi movido para o topo do arquivo
- Se ainda ocorrer, atualize os arquivos de teste

---

### Problema: Testes passam individualmente mas falham na suite

**Causa:** Working directory diferente quando executados via `run_all_tests.py`

### Solução: (6)

- Este erro foi corrigido na versão atual
- O `run_all_tests.py` agora define o working directory como raiz do projeto
- Todos os testes devem passar tanto individualmente quanto na suite

---

### Problema: "Conexão recusada" ou "Timeout"

**Causa:** Problemas de rede ou servidor Jira indisponível

### Solução: (7)

``` bash

# 1. Teste conectividade básica

ping jira.bradesco.com.br

# 2. Teste acesso via browser

# Acesse: <https://jira.bradesco.com.br:8443>

# 3. Verifique se está na VPN (se necessário)

# 4. Teste com curl

curl -H "Authorization: Bearer SEU_TOKEN" \
  <https://jira.bradesco.com.br:8443/rest/api/2/myself>

```

---

## 📚 Referências

- **API Oficial Jira:** <https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issues/>
- **Endpoint Bulk Create:** `POST /rest/api/2/issue/bulk` (Server/Data Center)
- **Autenticação:** Bearer Token via header `Authorization: Bearer {token}`

---

## 🔄 Workflow Recomendado

Para garantir qualidade antes de executar em produção:

``` bash

# 1. Execute a suite completa de testes

python tests/run_all_tests.py

# 2. Se todos os 6 testes passarem, teste o dry-run

python automatizar_issues.py --dry-run

# 3. Revise o JSON gerado no console

# 4. Se estiver tudo OK, execute em produção

python automatizar_issues.py

# 5. Verifique o relatório gerado

cat issues/relatorio_processamento_csv.txt

# Nota: Pode substituir 'python' por 'py' em todos os comandos acima

```

---

**Última atualização:** 07/02/2026
**Versão dos testes:** 1.0
**Status da suite:** ✅ 6/6 testes passando
