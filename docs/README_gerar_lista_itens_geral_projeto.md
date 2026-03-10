# 📊 Gerador de Relatório Geral de Sprints - Jira

Script Python para geração de relatórios completos de sprints do projeto PLTFAT no Jira, com análise de métricas ágeis, visualizações interativas e acompanhamento de pipeline de desenvolvimento.

## 📋 Índice

- Visão Geral
- Funcionalidades
- Instalação
- Configuração
- Como Usar
- Estrutura do Relatório
- Métricas Calculadas
- Campos Customizados
- Filtros e Visualizações
- Troubleshooting

## 🎯 Visão Geral

O **Gerador de Relatório Geral de Sprints** é uma ferramenta avançada que conecta com a API do Jira para extrair dados de issues do projeto PLTFAT e gerar relatórios HTML interativos com métricas ágeis completas.

### Principais Características

- 🔄 **Conexão automática** com API REST do Jira
- 📊 **Métricas ágeis** (Lead Time, Cycle Time, Throughput, WIP)
- 📈 **Gráficos interativos** com Chart.js
- 🎨 **Design System Bradesco Liquid**
- 🔍 **Filtros dinâmicos** por tipo de issue e company
- 📱 **Layout responsivo** para diferentes dispositivos
- 🕒 **Detecção automática** de sprints ativas
- 📋 **Pipeline de desenvolvimento** visualizado

## ✨ Funcionalidades

### 1. **Coleta de Dados**

- Busca issues do projeto PLTFAT via API REST
- Detecção automática de sprints ativas
- Extração de histórico de mudanças (changelog)
- Processamento de campos customizados

### 2. **Análise de Métricas**

- **Lead Time**: Tempo da criação até produção
- **Cycle Time**: Tempo gasto em cada status
- **Throughput**: Itens entregues na sprint
- **WIP (Work in Progress)**: Itens em andamento
- **Eficiência de Entrega**: % de itens concluídos

### 3. **Categorização Inteligente**

- **Itens Entregues**: Issues finalizadas na sprint
- **Em Homologação**: Issues em processo de validação
- **Deploy para Produção**: Issues sendo implantadas
- **Em Produção**: Issues ativas em ambiente produtivo
- **Em Progresso**: Issues em desenvolvimento

### 4. **Visualizações Interativas**

- Gráficos de distribuição por tipo de issue
- Pipeline de desenvolvimento
- Análise de bugs vs features
- Distribuição de bugs por company
- Cycle time por status

## 🛠 Instalação

### Pré-requisitos

- Python 3.7 ou superior
- Acesso à API do Jira Bradesco
- Token de autenticação Bearer

### Dependências

``` bash

pip install requests python-dotenv python-dateutil

```

### Estrutura de Pastas

``` text

projeto/
├── gerar_lista_itens_geral_projeto.py
├── jira_utils.py                        # ⚠️ OBRIGATÓRIO: Módulo de funções compartilhadas
├── .env
└── relatorios/
    └── (arquivos HTML gerados)

```

### ⚠️ Dependência Importante: jira_utils.py

Este script depende do módulo `jira_utils.py` que contém funções compartilhadas entre os scripts de relatórios:

- **get_jira_issues()** - Conexão com Jira e busca de issues
- **find_current_sprint_info()** - Detecção de sprint ativa
- **group_issues_by_status()** - Agrupamento por pipeline
- **calculate_metrics()** - Cálculo de métricas ágeis
- **calculate_lead_time()** - Cálculo de lead time
- E mais 15+ funções utilitárias...

### Certifique-se de que o arquivo `jira_utils.py` está na mesma pasta que este script

## ⚙️ Configuração

### 1. Arquivo `.env`

Crie um arquivo `.env` na raiz do projeto:

``` env

JIRA_URL=<https://jira.bradesco.com.br:8443>
JIRA_TOKEN=seu_token_bearer_aqui

```

### 2. Permissões Necessárias

- Acesso de leitura ao projeto PLTFAT
- Permissão para usar API REST do Jira
- Acesso aos campos customizados:
- `customfield_10100` (Sprint)
- `customfield_13401` (Company)
- `customfield_12318` (Pontos de Função - Métricas)
- `customfield_18100` (Pontos de Função)
- `customfield_10106` (Story Points)

## 🚀 Como Usar

### Execução Básica

``` bash

python gerar_lista_itens_geral_projeto.py

# ou: py gerar_lista_itens_geral_projeto.py

```

### Filtragem por Data

Você pode filtrar as issues por range de datas usando os parâmetros opcionais:

``` bash

# Filtrar por data de início e data de fim

python gerar_lista_itens_geral_projeto.py 01/01/2026 31/01/2026

# Filtrar apenas a partir de uma data de início

python gerar_lista_itens_geral_projeto.py 01/01/2026

# Usar com exportação CSV

python gerar_lista_itens_geral_projeto.py 01/01/2026 31/01/2026 --save-csv

```

### Formatos de Data Aceitos

- `DD/MM/YYYY` (ex: 01/01/2026)
- `YYYY-MM-DD` (ex: 2026-01-01)

### Regras de Filtro

- **Ambas as datas informadas**: Retorna issues criadas entre a data de início e data de fim
- **Apenas data de início**: Retorna issues criadas a partir da data de início até a última issue conhecida
- **Apenas data de fim**: Retorna issues criadas desde o início até a data de fim informada
- **Nenhuma data**: Retorna todas as issues do projeto

### Exportar Dados Brutos em CSV

Para salvar os dados brutos extraídos do Jira em formato CSV (útil para análises adicionais, auditoria ou importação em outras ferramentas):

``` bash

# Exportar todas as issues

python gerar_lista_itens_geral_projeto.py --save-csv

# Exportar com filtro de data

python gerar_lista_itens_geral_projeto.py 01/01/2026 31/01/2026 --save-csv

```

**Resultado**: Além do relatório HTML, será criado um arquivo CSV na pasta `logs/`:

``` text

logs/jira_raw_data_geral_YYYYMMDD_HHMMSS.csv

```

**Campos incluídos no CSV**: O arquivo CSV contém 19 colunas com dados completos de cada issue:

- `key`, `summary`, `status`, `issuetype`, `assignee`
- `created`, `updated`, `priority`
- `story_points`, `story_points_custom`
- `pf_metricas`, `pf`, `company`, `team`
- `sprint`, `epic_link`, `parent_key`
- `lead_time_days`, `age_since_backlog`

### Saída do Script

``` text

Buscando issues do Jira...
Sprint ativa encontrada: DocMatch-RT1_Platafo-S3 (ID: 227000)
Data de início da sprint: 02/02/2026
Data de fim da sprint: 15/02/2026
Verificando histórico de status para período da sprint...

Relatório da Sprint:
==================================================

Itens Entregues (15 itens):
• PLTFAT-17001: Implementar autenticação SSO
• PLTFAT-17002: Corrigir bug na validação de CPF
...

Relatório HTML gerado: relatorios/backlog_geral_20251024_143022.html

```

## 📋 Estrutura do Relatório

### 1. **Cabeçalho**

- Nome da sprint atual
- Período da sprint (início/fim)
- Data/hora de geração
- Logo Bradesco

### 2. **Métricas Principais**

- **Throughput**: Número de itens entregues
- **Lead Time Médio**: Tempo médio da criação à produção
- **WIP Atual**: Work in Progress
- **Eficiência**: Percentual de entrega
- **Tempo no Status**: Tempo médio no status atual

### 3. **Totalizadores**

- **PF (Métricas)**: Soma dos Pontos de Função (Métricas)
- **Pontos de Função**: Soma total de Pontos de Função
- **Story Points**: Soma de Story Points customizados

### 4. **Gráficos Analíticos**

- **Cycle Time por Status**: Tempo gasto em cada etapa
- **Distribuição por Tipo**: Issues entregues vs geral
- **Pipeline de Desenvolvimento**: Fluxo atual de trabalho
- **Bugs vs Features**: Análise qualitativa
- **Bugs por Company**: Distribuição por fornecedor

### 5. **Seções de Issues**

Cada seção é colapsável e contém:

- **Filtros dinâmicos** por tipo e company
- **Tags coloridas** para identificação rápida
- **Links diretos** para issues no Jira
- **Informações de idade** para items em progresso

## 📊 Métricas Calculadas

### Lead Time

``` python

# Tempo da criação até chegada em produção

lead_time = (data_producao - data_criacao).days

```

### Cycle Time por Status

``` python

# Tempo médio gasto em cada status do workflow

# Calculado apenas para itens entregues

avg_cycle_time = soma_tempos_status / numero_issues

```

### Throughput

``` python

# Items que passaram por TESTADA, FINALIZADO ou FECHADO na sprint

throughput = count(issues_com_transicao_na_sprint)

```

### Eficiência de Entrega

``` python

delivery_efficiency = (itens_entregues / total_itens) * 100

```

### Idade desde Backlog

``` python

# Dias desde que o item saiu do status Backlog

age = (data_atual - data_saida_backlog).days

```

## 🏷️ Campos Customizados

| Campo | ID | Descrição | Uso no Relatório |
| ------- | ---- | ----------- | -------------------- |
| Sprint | `customfield_10100` | Informações da sprint | Detecção de sprint ativa |
| Company | `customfield_13401` | Empresa responsável | Filtros e análise de bugs |
| PF (Métricas) | `customfield_12318` | Pontos de Função para métricas | Totalizador de complexidade |
| Pontos de Função | `customfield_18100` | Pontos de Função padrão | Sizing de funcionalidades |
| Story Points | `customfield_10106` | Story Points customizados | Estimativas ágeis |

## 🎛️ Filtros e Visualizações

### Filtros Disponíveis

- **Todos**: Exibe todas as issues
- **Story**: Apenas User Stories
- **Tech Solution**: Soluções técnicas
- **Bug**: Issues de defeitos
- **Incidente**: Problemas em produção

### Filtros por Company

- **CI&T**: Issues da CI&T
- **McKinsey**: Issues da McKinsey
- **Outras**: Demais companies

### Elementos Visuais

- **Tags de Tipo**: Cores diferentes por tipo de issue
- **Tags de Company**: Identificação visual por fornecedor
- **Tags de Idade**: Indicadores para items antigos
- **Tags de Pontos**: PF, Story Points, etc.

### Código de Cores

``` css

.issue-type.story { background-color: #09ab47; }      /* Verde */
.issue-type.tech-solution { background-color: #ffbc01; } /* Amarelo */
.issue-type.bug { background-color: #b00f2f; }       /* Vermelho */
.issue-type.incidente { background-color: #b00f2f; } /* Vermelho */

```

## 🔧 Troubleshooting

### Problemas Comuns

#### 1. **Erro de Autenticação**

``` text

Failed to fetch issues: 401 - Unauthorized

```

**Solução**: Verificar se o token no `.env` está correto e válido.

#### 2. **Sprint não Encontrada**

``` text

Nenhuma sprint ativa encontrada

```

**Solução**: O script usará período padrão. Verificar se existem sprints ativas no board.

#### 3. **Erro de Conexão**

``` text

requests.exceptions.ConnectionError

```

**Solução**: Verificar conectividade com o Jira e URL no `.env`.

#### 4. **Campos Customizados Vazios**

``` text

KeyError: 'customfield_xxxxx'

```

**Solução**: Verificar se os campos existem no projeto e têm dados.

### Logs de Debug

Para habilitar logs detalhados:

``` python

import logging
logging.basicConfig(level=logging.DEBUG)

```

### Validação de Configuração

``` python

# Teste de conexão

response = requests.get(f"{jira_url}/rest/api/2/myself",
                       headers={"Authorization": f"Bearer {token}"})
print(f"Status: {response.status_code}")

```

## 📈 Personalização

### Modificar JQL Query

``` python

# Linha ~1883

jql_query = 'project = PLTFAT AND issuetype in (Story, "Tech Solution", Bug, Incidente) AND Team = DocMatch AND status not in (Validado, Identificado, "Em Medição", Cancelado, Cancelada) ORDER BY status ASC'

```

### Adicionar Novos Status

``` python

# Função group_issues_by_status()

itens_homologacao = ["DISPONIVEL PARA HOMOLOGAÇÃO", "EM DEPLOY PARA HOMOLOGAÇÃO",
                    "EM HOMOLOGAÇÃO", "HOMOLOGADA", "SEU_NOVO_STATUS"]

```

### Customizar Cores

``` css

/* No CSS do template HTML */
.issue-type.seu-tipo { background-color: #sua-cor; }

```

## 📝 Exemplos de Uso

### Relatório para Múltiplos Teams

``` python

jql_query = 'project = PLTFAT AND Team in (DocMatch)'

```

### Filtrar por Período Específico

``` python

jql_query = 'project = PLTFAT AND created >= "2025-01-01" AND created <= "2025-01-31"'

```

### Incluir Outros Tipos de Issue

``` python

jql_query = 'project = PLTFAT AND issuetype in (Story, Bug, Epic, Task)'

```

---

## 📄 Informações Adicionais

**Autor**: Equipe de Automação Jira
**Versão**: 2.0
**Data**: Outubro 2025
**Licença**: Uso interno Bradesco

Para dúvidas ou sugestões, entre em contato com a equipe de DevOps do projeto PLTFAT.

---

> 💡 **Dica**: Execute o script regularmente para acompanhar o progresso das sprints e identificar gargalos no pipeline de desenvolvimento!
