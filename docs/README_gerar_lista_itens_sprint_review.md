# 📋 Gerador de Relatório de Sprint Review - Jira

Script Python especializado para geração de relatórios de Sprint Review do projeto PLTFAT no Jira, focado na análise de itens da sprint ativa com métricas detalhadas para cerimônias ágeis.

## 📋 Índice

- Visão Geral
- Diferenças do Relatório Geral
- Funcionalidades
- Instalação
- Configuração
- Como Usar
- Estrutura do Relatório
- Métricas da Sprint
- Análise de Entrega
- Visualizações
- Cerimônias Ágeis
- Troubleshooting

## 🎯 Visão Geral

O **Gerador de Relatório de Sprint Review** é uma ferramenta especializada para criar relatórios focados na **sprint ativa atual**, otimizado para uso nas cerimônias de Sprint Review e Retrospectiva.

### Principais Características

- 🎯 **Foco na Sprint Ativa**: Analisa apenas itens da sprint atual
- 📊 **Métricas de Entrega**: Velocity, commitment vs delivery
- 🔄 **Análise de Fluxo**: Items entregues vs em andamento
- 📈 **Visualizações para Review**: Gráficos otimizados para apresentação
- ⏱️ **Detecção Automática**: Identifica sprint ativa automaticamente
- 📱 **Layout de Apresentação**: Design otimizado para projeção

### Diferencial

Este script é **complementar** ao relatório geral, com foco específico na **análise da sprint atual** para facilitar as cerimônias ágeis.

## 🔄 Diferenças do Relatório Geral

| Aspecto | Relatório Geral | Sprint Review |
| --------- | ----------------- | --------------- |
| **Escopo** | Todos os itens do projeto | Apenas sprint ativa |
| **Query JQL** | Status geral do projeto | `Sprint in openSprints()` |
| **Métricas** | Lead time, pipeline completo | Velocity, burndown, commitment |
| **Visualizações** | Análise histórica | Foco na entrega atual |
| **Uso** | Acompanhamento contínuo | Cerimônias de Review |
| **Período** | Histórico completo | Sprint atual |

## ✨ Funcionalidades

### 1. **Análise da Sprint Ativa**

- Detecção automática da sprint em andamento
- Análise de commitment vs delivery
- Cálculo de velocity da sprint
- Identificação de itens não finalizados

### 2. **Métricas Específicas da Sprint**

- **Velocity**: Story points/itens entregues na sprint
- **Commitment Achievement**: % do comprometimento cumprido
- **Burndown Analysis**: Itens restantes vs tempo
- **Sprint Health**: Indicadores de saúde da sprint

### 3. **Categorização para Review**

- **✅ Itens Entregues**: Finalizados na sprint atual
- **� Itens em Produção**: Issues ativadas em produção
- **🛠️ Em Deploy para Produção**: Issues sendo implantadas
- **🧪 Itens em Homologação**: Issues em validação/homologação
- **🔄 Em Progresso**: Itens ainda em desenvolvimento
- **⏳ Aguardando Desenvolvimento**: Itens em refinamento ou backlog

### 4. **Visualizações para Apresentação**

- Gráfico de entrega por tipo de issue
- Distribuição do trabalho realizado
- Análise de bugs encontrados vs corrigidos
- Timeline de entregas da sprint

## 🛠 Instalação

### Pré-requisitos

- Python 3.7 ou superior
- Acesso à API do Jira Bradesco
- Token de autenticação Bearer
- Sprint ativa configurada no Jira

### Dependências

``` bash

pip install requests python-dotenv python-dateutil

```

### Estrutura de Pastas

``` text

projeto/
├── gerar_lista_itens_sprint_review.py
├── jira_utils.py                        # ⚠️ OBRIGATÓRIO: Módulo de funções compartilhadas
├── .env
└── relatorios/
    └── sprint_review_YYYYMMDD_HHMMSS.html

```

### ⚠️ Dependência Importante: jira_utils.py

Este script depende do módulo `jira_utils.py` que contém funções compartilhadas entre os scripts de relatórios:

- **get_jira_issues()** - Conexão com Jira e busca de issues
- **find_current_sprint_info()** - Detecção de sprint ativa
- **filter_sprint_issues()** - Filtragem de issues por sprint
- **group_issues_by_status()** - Agrupamento por pipeline
- **calculate_metrics()** - Cálculo de métricas ágeis
- **calculate_lead_time()** - Cálculo de lead time
- **calculate_age_since_backlog()** - Idade desde saída do backlog
- E mais 15+ funções utilitárias...

### Certifique-se de que o arquivo `jira_utils.py` está na mesma pasta que este script

## ⚙️ Configuração

### 1. Arquivo `.env`

``` env

JIRA_URL=<https://jira.bradesco.com.br:8443>
JIRA_TOKEN=seu_token_bearer_aqui

```

### 2. Query JQL Padrão

``` jql

project = PLTFAT
AND Sprint in openSprints()
AND issuetype in (Story, "Tech Solution", Bug, Incidente)
AND Team = DocMatch
AND status not in (Validado, Identificado, "Em Medição", Cancelado, Cancelada)
ORDER BY status ASC

```

### 3. Campos Necessários

- `customfield_10100` (Sprint)
- `customfield_13401` (Company)
- `customfield_12318` (Pontos de Função - Métricas)
- `customfield_18100` (Pontos de Função)
- `customfield_10106` (Story Points)

## 🚀 Como Usar

### Execução para Sprint Review

``` bash

python gerar_lista_itens_sprint_review.py

# ou: py gerar_lista_itens_sprint_review.py

```

### Exportar Dados Brutos em CSV

Para salvar os dados brutos extraídos do Jira em formato CSV (útil para análises adicionais, auditoria ou importação em outras ferramentas):

``` bash

python gerar_lista_itens_sprint_review.py --save-csv

```

**Resultado**: Além do relatório HTML, será criado um arquivo CSV na pasta `logs/`:

``` text

logs/jira_raw_data_sprint_YYYYMMDD_HHMMSS.csv

```

**Campos incluídos no CSV**:

- `key` - Chave da issue (ex: PLTFAT-17001)
- `summary` - Título da issue
- `status` - Status atual
- `issuetype` - Tipo da issue (Story, Bug, etc.)
- `assignee` - Responsável
- `created` - Data de criação
- `updated` - Data de última atualização
- `priority` - Prioridade
- `story_points` - Story points
- `story_points_custom` - Story points custom field
- `pf_metricas` - Pontos de Função (Métricas)
- `pf` - Pontos de Função
- `company` - Empresa
- `team` - Time
- `sprint` - Sprint
- `epic_link` - Link para épico
- `parent_key` - Chave da issue pai
- `lead_time_days` - Lead time em dias
- `age_since_backlog` - Idade desde backlog

### Saída Típica

``` text

Buscando issues do Jira...
Sprint ativa encontrada: DocMatch-RT1_Platafo-S3 (ID: 227000)
Data de início da sprint: 02/02/2026
Data de fim da sprint: 15/02/2026
Verificando histórico de status para período da sprint (02/02/2026 a 15/02/2026)...

✓ PLTFAT-17001 mudou para TESTADA em 15/10/2025 14:30 (dentro da sprint)
✓ PLTFAT-17002 mudou para FINALIZADO em 16/10/2025 09:15 (dentro da sprint)

Relatório da Sprint:
==================================================

Itens Entregues (12 itens):
• PLTFAT-17001: Implementar autenticação SSO (Status: TESTADA)
• PLTFAT-17002: Corrigir bug validação (Status: FINALIZADO)
...

Itens em Produção (5 itens):
• PLTFAT-16895: Feature de notificações (Status: EM PRODUÇÃO)
...

Em Deploy para Produção (2 itens):
• PLTFAT-17003: Nova API de integração (Status: EM DEPLOY PARA PRODUÇÃO)
...

Itens em Homologação (3 itens):
• PLTFAT-17004: Dashboard de métricas (Status: EM HOMOLOGAÇÃO)
...

Em Progresso (4 itens):
• PLTFAT-17005: Refatoração de serviços (Status: EM DESENVOLVIMENTO)
...

Aguardando Desenvolvimento (2 itens):
• PLTFAT-17010: Nova feature planejada (Status: PRONTA PARA DESENVOLVIMENTO)
...

Relatório HTML gerado: relatorios/sprint_review_20251024_143022.html
Total de issues encontradas: 28

```

## 📋 Estrutura do Relatório

### 1. **Cabeçalho da Sprint**

``` html

Sprint Review - DocMatch-RT1_Platafo-S3
Período: 02/02/2026 a 15/02/2026
Gerado em: 24/10/2025 às 14:30

```

### 2. **Dashboard de Métricas**

- **Velocity Atual**: Itens/pontos entregues
- **Taxa de Entrega**: % do commitment cumprido
- **Itens em Risco**: Ainda em desenvolvimento
- **Bugs Encontrados**: Defeitos identificados na sprint
- **Quality Score**: Razão features/bugs

### 3. **Análise de Entrega**

``` text

📊 RESUMO DA SPRINT
┌─────────────────────────┬─────────┐
│ Comprometido            │    20   │
│ Entregue                │    17   │
│ Em Andamento            │     3   │
│ Taxa de Sucesso         │   85%   │
└─────────────────────────┴─────────┘

```

### 4. **Seções Principais**

#### ✅ **Itens Entregues**

- Issues que passaram por TESTADA, FINALIZADO ou FECHADO durante a sprint
- Links diretos para o Jira
- Métricas de complexity (Story Points, PF)
- Company responsável
- Filtros por tipo: Story, Tech Solution, Bug

#### 🚀 **Itens em Produção**

- Issues com status EM PRODUÇÃO ou ATIVADA
- Funcionalidades já disponíveis para usuários finais
- Data de ativação em produção

#### 🛠️ **Em Deploy para Produção**

- Issues em processo de implantação
- Status: EM DEPLOY PARA PRODUÇÃO
- Acompanhamento do processo de release

#### 🧪 **Itens em Homologação**

- Issues em processo de validação
- Status: DISPONÍVEL PARA HOMOLOGAÇÃO, EM DEPLOY PARA HOMOLOGAÇÃO, EM HOMOLOGAÇÃO, HOMOLOGADA
- Aguardando aprovação para produção

#### 🔄 **Em Progresso**

- Issues em desenvolvimento ativo
- Idade desde início do trabalho
- Ordenadas por idade (mais antigas primeiro)
- Filtros por tipo: Story, Tech Solution, Bug

#### ⏳ **Aguardando Desenvolvimento**

- Issues em backlog ou refinamento
- Status: BACKLOG, EM REFINAMENTO, REFINADO, PRODUCT BACKLOG, SELECIONADO PARA GROOMING, EM ANÁLISE, ANÁLISE REALIZADA, PRONTA PARA DESENVOLVIMENTO
- Ordenadas por idade (mais antigas primeiro)
- Filtros por tipo: Story, Tech Solution, Bug

## 📊 Métricas da Sprint

### Velocity da Sprint

``` python

# Cálculo da velocity baseado em story points

velocity_sp = sum(issue['story_points_custom'] for issue in delivered_items)

# Velocity baseado em número de itens

velocity_items = len(delivered_items)

```

### Taxa de Commitment

``` python

# Comparação entre comprometido vs entregue

commitment_rate = (delivered_items / total_sprint_items) * 100

```

### Quality Metrics

``` python

# Análise da qualidade da entrega

bugs_ratio = bugs_found / (features_delivered + bugs_found) * 100

```

### Sprint Health Score

``` python

# Indicador geral de saúde da sprint

health_score = (
    commitment_rate * 0.4 +
    (100 - bugs_ratio) * 0.3 +
    velocity_trend * 0.3
)

```

## 📈 Análise de Entrega

### Detecção de Itens Entregues

O script identifica itens entregues através do histórico de status:

``` python

def check_status_history_in_sprint_period(issue, sprint_start_date, sprint_end_date):
    """
    Verifica se a issue passou por status de conclusão durante a sprint
    """
    target_statuses = ["TESTADA", "FINALIZADO", "FECHADO"]

    # Analisa changelog para mudanças dentro do período da sprint
    for history in issue['changelog']['histories']:
        history_date = parser.parse(history['created'])

        if sprint_start_date <= history_date <= sprint_end_date:
            for item in history.get('items', []):
                if item.get('field') == 'status':
                    if item.get('toString', '').upper() in target_statuses:
                        return True
    return False

```

### Categorização Inteligente

``` python

grouped = {
    "Itens Entregues": [],      # Finalizados na sprint
    "Itens em Produção": [],    # Ativos em produção
    "Em Deploy para Produção": [], # Sendo implantados
    "Itens em Homologação": [], # Em validação
    "Em Progresso": [],          # Ainda em desenvolvimento
    "Aguardando Desenvolvimento": [] # Backlog, refinamento, análise
}

```

### Status por Agrupamento

#### Itens Entregues

- Issues que passaram por **TESTADA**, **FINALIZADO** ou **FECHADO** durante a sprint

#### Itens em Produção

- Status: **EM PRODUÇÃO**, **ATIVADA**

#### Em Deploy para Produção

- Status: **EM DEPLOY PARA PRODUÇÃO**

#### Itens em Homologação

- Status: **DISPONÍVEL PARA HOMOLOGAÇÃO**, **EM DEPLOY PARA HOMOLOGAÇÃO**, **EM HOMOLOGAÇÃO**, **HOMOLOGADA**

#### Em Progresso

- Issues em desenvolvimento ativo que não estão nos status acima e não foram entregues

#### Aguardando Desenvolvimento

- Status: **BACKLOG**, **EM REFINAMENTO**, **REFINADO**, **PRODUCT BACKLOG**, **SELECIONADO PARA GROOMING**, **EM ANÁLISE**, **ANÁLISE REALIZADA**, **PRONTA PARA DESENVOLVIMENTO**

## 🎨 Visualizações

### 1. **Gráfico de Velocity**

- Comparação com sprints anteriores
- Tendência de entrega
- Projeção para próximas sprints

### 2. **Burndown Chart**

- Itens restantes por dia
- Linha ideal vs real
- Identificação de desvios

### 3. **Distribuição por Tipo**

- Stories vs Tech Solutions vs Bugs
- Análise de balanceamento do trabalho
- Foco em valor vs manutenção

### 4. **Timeline de Entregas**

- Quando cada item foi finalizado
- Identificação de gargalos
- Padrões de entrega

## 🏆 Cerimônias Ágeis

### Sprint Review

``` markdown

📋 AGENDA SUGERIDA:

1. Apresentar métricas da sprint (5 min)
2. Demonstrar itens entregues (20 min)
3. Discutir impedimentos e aprendizados (10 min)
4. Próximos passos (5 min)

```

### Dados para Review

- ✅ **Commitment**: O que foi comprometido vs entregue
- 📊 **Velocity**: Capacidade atual do time
- 🐛 **Quality**: Bugs encontrados e corrigidos
- ⚠️ **Riscos**: Itens em andamento que podem atrasar

### Sprint Retrospective

``` markdown

🔄 PERGUNTAS ORIENTADORAS:

- Conseguimos entregar o que foi comprometido?
- Onde tivemos mais impedimentos?
- Qual foi nossa velocity média?
- Como melhorar para a próxima sprint?

```

## 🔧 Troubleshooting

### Problemas Específicos

#### 1. **Sprint Não Detectada**

``` text

Nenhuma sprint ativa encontrada

```

**Causa**: Não há sprints com status 'active' no board.
**Solução**: Verificar se existe sprint ativa configurada no Jira.

#### 2. **Itens Não Aparecem**

``` text

0 issues encontradas na sprint

```

**Causa**: Query JQL não retorna resultados.
**Solução**: Verificar se `Sprint in openSprints()` está correto.

#### 3. **Datas Incorretas**

``` text

Usando período padrão da sprint

```

**Causa**: Sprint não tem datas configuradas.
**Solução**: Configurar startDate e endDate na sprint.

#### 4. **Métricas Zeradas**

``` text

Velocity: 0, Commitment: 0%

```

**Causa**: Nenhum item foi finalizado durante a sprint.
**Solução**: Verificar se os status de conclusão estão corretos.

### Validações Importantes

#### Verificar Sprint Ativa

``` python

# Teste manual

jql = 'project = PLTFAT AND Sprint in openSprints()'
response = requests.get(f"{jira_url}/rest/api/2/search?jql={jql}")
print(f"Itens na sprint ativa: {response.json()['total']}")

```

#### Validar Período da Sprint

``` python

# Verificar se as datas fazem sentido

if sprint_info:
    start = parser.parse(sprint_info['startDate'])
    end = parser.parse(sprint_info['endDate'])
    print(f"Sprint: {start.strftime('%d/%m')} a {end.strftime('%d/%m')}")

```

## 📊 Personalização

### Modificar Critérios de Entrega

``` python

# Alterar status que indicam conclusão

target_statuses = ["TESTADA", "FINALIZADO", "FECHADO", "ATIVADA"]

```

### Ajustar Query da Sprint

``` python

# Incluir outras teams ou projects

jql_query = '''
    project = PLTFAT
    AND Sprint in openSprints()
    AND Team in (DocMatch)
    AND status not in (Cancelado, Cancelada)
'''

```

### Customizar Métricas

``` python

# Adicionar nova métrica

def calculate_sprint_focus(issues):
    """Calcula foco da sprint (features vs bugs)"""
    features = len([i for i in issues if i['issuetype'] == 'Story'])
    bugs = len([i for i in issues if i['issuetype'] == 'Bug'])
    return (features / (features + bugs)) * 100 if (features + bugs) > 0 else 0

```

## 📅 Casos de Uso

### 1. **Sprint Review Semanal**

``` bash

# Executar toda sexta-feira

python gerar_lista_itens_sprint_review.py

# ou: py gerar_lista_itens_sprint_review.py (2)

```

### 2. **Demo para Stakeholders**

- Usar seção "Itens Entregues" para demonstração
- Focar em valor de negócio entregue
- Destacar métricas de qualidade

### 3. **Planning da Próxima Sprint**

- Analisar velocity atual
- Verificar itens não finalizados
- Planejar capacidade baseada no histórico

### 4. **Acompanhamento Diário**

- Verificar progresso dos itens
- Identificar impedimentos
- Ajustar expectativas de entrega

## 📈 Melhorias Contínuas

### Sugestões de Evolução

1. **Integração com Slack**: Notificações automáticas
1. **Comparação Histórica**: Trend de velocity
1. **Previsão de Entrega**: ML para estimativas
1. **Dashboard Real-time**: Atualização automática

---

## 📄 Informações Adicionais

**Autor**: Equipe de Automação Jira
**Versão**: 2.0
**Data**: Outubro 2025
**Licença**: Uso interno Bradesco
**Relacionado**: `gerar_lista_itens_geral_projeto.py`

Para dúvidas sobre cerimônias ágeis ou configuração, entre em contato com o Scrum Master ou equipe de DevOps.

---

> 🎯 **Dica para Sprint Review**: Execute o script 1 hora antes da cerimônia para ter dados atualizados e identificar possíveis ajustes de última hora!
> 📊 **Dica para Retrospectiva**: Compare os dados com sprints anteriores para identificar tendências de melhoria ou pontos de atenção.
