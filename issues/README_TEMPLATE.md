# Template de Issues para Importação no Jira

## 📄 Arquivo Template

- **Nome**: `template_issues.csv`
- **Localização**: `issues/template_issues.csv`
- **Encoding**: UTF-8

## 📋 Estrutura do CSV

O arquivo CSV deve conter as seguintes colunas (conforme mapeamento em `BulkCreate_configuration.txt`):

| Coluna | Campo Jira | Tipo | Obrigatório | Descrição | Exemplo |
| -------- | ----------- | ------ | ------------- | ----------- | --------- |
| **Issue Type** | issuetype | Select | Sim | Tipo da issue | Story, Bug, Tech Solution, Non Functional Task, Incidente, Epic |
| **Summary** | summary | Text | Sim | Título/resumo da issue | Implementar autenticação biométrica |
| **Description** | description | Text | Não | Descrição detalhada | Como usuário... quero... para... |
| **Team** | customfield_10401 | Text | Não | Nome do time | DocMatch |
| **Original Estimate** | timeoriginalestimate | Time | Não | Estimativa original | 5d, 8h, 2d 4h |
| **Assignee** | assignee | User | Não | Responsável pela issue | F568572 |
| **Parent Id** | subtask-parent-id | Issue Key | Não* | Issue pai (para subtarefas) | PLTFAT-123 |
| **Sprint ID** | customfield_10100 | Sprint | Não | ID numérico da sprint | 235 |
| **Epic Link** | customfield_10101 | Epic | Não | Link para o Epic | PLTFAT-1234 |
| **Labels** | labels | Array | Não | Etiquetas (separadas por vírgula) | autenticacao,biometria,seguranca |

*Obrigatório apenas se Issue Type = Subtask

## 🎯 Tipos de Issue Disponíveis

Conforme configuração do projeto PLTFAT:

- **Story**: Histórias de usuário (funcionalidades)
- **Tech Solution**: Soluções técnicas
- **Bug**: Correções de defeitos
- **Incidente**: Incidentes de produção
- **Non Functional Task**: Tarefas não funcionais
- **Epic**: Épicos (agrupamento de histórias)

## ⏱️ Formato de Estimativas (Original Estimate)

O campo aceita os seguintes formatos:

- **Horas**: `8h`, `4h`, `16h`
- **Dias**: `1d`, `5d`, `10d` (1 dia = 8 horas)
- **Combinado**: `2d 4h`, `1d 2h`
- **Deixar vazio**: Sem estimativa

## 🏷️ Formato de Labels

Múltiplas labels devem ser separadas por **vírgula (,)**:

``` text

autenticacao,biometria,seguranca
metricas,dashboard,gestao
bug,api,performance

```

## 📝 Boas Práticas

### 1. **Summary (Título)**

- Máximo 255 caracteres
- Ser claro e objetivo
- Iniciar com verbo no infinitivo para Stories/Tasks
- Exemplo: "Implementar login com biometria"

### 2. **Description (Descrição)**

- Para Stories, usar formato: "Como [usuário], quero [funcionalidade] para [benefício]"
- Para Bugs, descrever: sintoma, passos para reproduzir, comportamento esperado
- Para Tech Solutions, detalhar a solução técnica proposta

### 3. **Issue Type**

- Usar exatamente os valores aceitos (case-sensitive)
- Confirmar que o tipo existe no projeto

### 4. **Assignee**

- Usar matrícula do usuário (ex: F568572)
- Deixar vazio se não houver responsável definido

### 5. **Sprint ID**

- Usar o ID numérico da sprint (não o nome)
- Para descobrir o ID:
- Acessar a sprint no Jira
- Verificar a URL: `.../sprint/235` → ID = 235
- Deixar vazio para adicionar ao backlog

### 6. **Epic Link**

- Usar a chave do Epic (ex: PLTFAT-1234)
- Deixar vazio se não pertencer a nenhum Epic

## 🚀 Como Usar

### Passo 1: Preparar o arquivo CSV

``` bash

# Copiar o template

cp issues/template_issues.csv issues/minhas_issues.csv

# Editar com seus dados

# Abrir em Excel, LibreOffice, ou editor de texto

```

> ⚠️ **Importante**: Arquivos que começam com `template` são **automaticamente ignorados** pelo script. Sempre copie o template para um novo arquivo antes de editar e executar.

### Passo 2: Validar o conteúdo

- ✅ Todas as linhas têm Summary preenchido
- ✅ Issue Type está correto
- ✅ Sprint ID é numérico (se preenchido)
- ✅ Assignee existe no Jira
- ✅ Epic Link existe no projeto
- ✅ Encoding é UTF-8

### Passo 3: Executar o script

**Modo Dry-Run (testar sem criar)**:

``` bash

python automatizar_issues.py --dry-run

```

**Modo Normal (criar as issues)**:

``` bash

python automatizar_issues.py

```

### Passo 4: Verificar resultado

- Log no console mostrará o status de cada issue
- Arquivo de log: `logs/automatizacao_issues.log`
- Relatório: `issues/relatorio_processamento_csv.txt`
- CSV processado movido para: `issues/Processados/`

## ⚠️ Avisos Importantes

### Caracteres Especiais

- Use UTF-8 para acentos e caracteres especiais
- Evite usar vírgula (,) no conteúdo (é o delimitador do CSV)
- Para textos com vírgula, envolva em aspas: `"Teste, exemplo, vírgula"`

### Campos Customizados

Os seguintes campos são específicos do projeto PLTFAT:

- **Team** (customfield_10401)
- **Epic Link** (customfield_10101)
- **Sprint ID** (customfield_10100)
- **Theme** (customfield_10500) pode aparecer no mapeamento, mas é ignorado no envio do payload

### Limitações

- O campo **Theme** é ignorado no payload final
- Campo **Story Points** não está mapeado (use estimativas em horas/dias)
- Máximo de issues por arquivo: recomendado até 100 por vez

## 📊 Exemplo Completo

``` csv

Issue Type,Summary,Description,Team,Original Estimate,Assignee,Parent Id,Sprint ID,Epic Link,Labels
Story,Cadastrar novo cliente,"Como atendente, quero cadastrar novos clientes para iniciar o relacionamento bancário.",DocMatch,5d,F568572,,235,PLTFAT-1234,"cadastro,cliente"
Bug,Corrigir validação de CPF,"Campo CPF aceita valores inválidos. Corrigir validação frontend e backend.",DocMatch,2d,F568572,,235,PLTFAT-1234,"bug,validacao"
Tech Solution,Migrar banco para PostgreSQL,"Migrar base de dados de Oracle para PostgreSQL para reduzir custos de licenciamento.",DocMatch,10d,F568572,,236,PLTFAT-1235,"database,migracao"

```

## 🔍 Troubleshooting

### Erro: "Issue sem Summary será ignorada"

**Solução**: Preencha o campo Summary em todas as linhas

### Erro: "Issue type inválido"

**Solução**: Use exatamente: Story, Bug, Tech Solution, Non Functional Task, Incidente, ou Epic

### Erro: "Sprint não encontrada"

**Solução**: Verifique se o Sprint ID é numérico e existe no projeto

### Erro: "Assignee não encontrado"

**Solução**: Use matrícula válida ou deixe vazio

### Erro: "Epic Link não encontrado"

**Solução**: Verifique se o Epic existe e você tem permissão para visualizá-lo

## 📚 Referências

- **Script**: `automatizar_issues.py`
- **Configuração**: `BulkCreate_configuration.txt`
- **Documentação**: `docs/README_automatizar_issues.md`
- **Logs**: `logs/automatizacao_issues.log`

## 📞 Suporte

Para dúvidas ou problemas:

1. Verificar logs em `logs/automatizacao_issues.log`
1. Consultar documentação em `docs/`
1. Executar em modo `--dry-run` para testar sem criar issues

---

**Última atualização**: 19/02/2026
