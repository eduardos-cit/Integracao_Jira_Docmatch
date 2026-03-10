# 🚀 Quick Start - Criação de Issues em Massa

## Templates Disponíveis

📁 **Localização**: `issues/`

| Arquivo | Descrição | Casos de Uso |
| --------- | ----------- | -------------- |
| `template_vazio.csv` | Template vazio com apenas cabeçalhos | Começar do zero |
| `template_issues.csv` | 7 exemplos básicos de diferentes tipos | Referência rápida |
| `template_issues_completo.csv` | 10 exemplos detalhados com casos reais | Aprender boas práticas |

> 💡 **Nota**: Arquivos iniciados com `template` são automaticamente ignorados pelo script. Copie o template para um novo arquivo antes de usar.

## ⚡ Início Rápido (3 passos)

### 1️⃣ Escolha seu template

``` bash

# Opção A: Começar do zero

cp issues/template_vazio.csv issues/minhas_issues.csv

# Opção B: Usar exemplos como base

cp issues/template_issues.csv issues/minhas_issues.csv

# Opção C: Ver exemplos completos

cp issues/template_issues_completo.csv issues/minhas_issues.csv

```

### 2️⃣ Edite o arquivo CSV

### Campos Obrigatórios

- ✅ `Summary` - Título da issue
- ✅ `Issue Type` - Story, Bug, Tech Solution, Non Functional Task, Incidente, Epic
- ✅ `Original Estimate` - Estimativa (ex: 5d, 8h, 2d 4h) - **Se não informado, será definido como "0h"**

### Campos Opcionais

- `Description` - Descrição detalhada
- `Assignee` - Matrícula (ex: F568572)
- `Team` - Nome do time (ex: DocMatch)
- `Epic Link` - Chave do epic (ex: PLTFAT-1234)
- `Sprint ID` - ID numérico da sprint (ex: 235)
- `Labels` - Tags separadas por vírgula (ex: bug,api,urgente)

### 3️⃣ Execute o script

**Testar sem criar (recomendado primeiro)**:

``` bash

python automatizar_issues.py --dry-run

```

**Criar as issues**:

``` bash

python automatizar_issues.py

```

## 📋 Exemplos por Tipo

### Story (História de Usuário)

``` csv

Story,Implementar login com Google,"Como usuário, quero fazer login com minha conta Google para ter acesso rápido ao sistema.",DocMatch,3d,F568572,,235,PLTFAT-100,"autenticacao,oauth"

```

### Bug (Defeito)

``` csv

Bug,Sistema trava ao importar CSV grande,"Sistema apresenta erro de timeout ao importar arquivos CSV maiores que 5MB. Corrigir processamento em lote.",DocMatch,2d,F568572,,235,PLTFAT-100,"bug,performance,csv"

```

### Tech Solution (Solução Técnica)

``` csv

Tech Solution,Migrar arquivos para S3,"Migrar storage de arquivos do servidor local para AWS S3 para melhorar escalabilidade e reduzir custos.",DocMatch,5d,F568572,,236,PLTFAT-101,"infra,cloud,storage"

```

### Non Functional Task (Tarefa Não Funcional)

``` csv

Non Functional Task,Documentar endpoints da API,"Criar documentação Swagger/OpenAPI de todos os endpoints REST da API v2.",DocMatch,2d,F568572,,236,PLTFAT-101,"documentacao,api"

```

### Incidente

``` csv

Incidente,Resolver falha no deploy de produção,"Deploy da versão 2.5.0 causou indisponibilidade. Realizar rollback e investigar causa raiz.",DocMatch,1d,F568572,,235,PLTFAT-100,"incidente,producao,p1"

```

### Epic (Épico)

``` csv

Epic,Portal de Autoatendimento,"Desenvolver portal web completo de autoatendimento para clientes com funcionalidades de consulta, transações e investimentos.",DocMatch,60d,F568572,,236,,"epic,portal,cliente"

```

## 🎯 Dicas Importantes

### ✅ DO (Faça)

- Use UTF-8 como encoding do arquivo
- Teste com `--dry-run` antes de executar
- Valide que Summary está preenchido em todas as linhas
- Use tipos de issue exatamente como especificado
- Verifique que Sprint ID é numérico
- Confirme que Epic Link existe no projeto

### ❌ DON'T (Não Faça)

- Não use vírgulas dentro dos textos sem aspas
- Não deixe Summary vazio
- Não use tipos de issue que não existem no projeto
- Não use nome da sprint (use o ID)
- Não conte com o campo Theme no payload final (ele é ignorado)

## 🔧 Troubleshooting Rápido

| Problema | Solução |
| ---------- | --------- |
| "Issue sem Summary" | Preencha o campo Summary |
| "Issue type inválido" | Use: Story, Bug, Tech Solution, Non Functional Task, Incidente ou Epic |
| "Sprint não encontrada" | Use ID numérico da sprint ou deixe vazio |
| "Assignee não encontrado" | Use matrícula válida (F######) ou deixe vazio |
| Arquivo não processado | Verifique encoding UTF-8 e formato CSV |

## 📊 Workflow Completo

``` text

┌─────────────────────┐
│ 1. Copiar Template  │
│  template_*.csv     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 2. Editar Dados     │
│  Excel/LibreOffice  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 3. Testar Dry-Run   │
│  --dry-run          │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 4. Executar Real    │
│  automatizar_issues │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 5. Verificar Log    │
│  logs/*.log         │
└─────────────────────┘

```

## 📚 Documentação Completa

Para mais detalhes, consulte:

- **Template Detalhado**: `issues/README_TEMPLATE.md`
- **Script**: `docs/README_automatizar_issues.md`
- **Configuração**: `BulkCreate_configuration.txt`

## 💡 Exemplo Mínimo Funcional

Arquivo CSV com apenas o essencial:

``` csv

Issue Type,Summary,Description,Team,Original Estimate,Assignee,Parent Id,Sprint ID,Epic Link,Labels
Story,Minha primeira issue,Descrição da issue,,,,,,,,

```

Executar:

``` bash

python automatizar_issues.py

```

## 🎓 Próximos Passos

1. ✅ Copiar `template_vazio.csv` ou `template_issues.csv`
1. ✅ Editar com suas issues
1. ✅ Testar com `--dry-run`
1. ✅ Executar para criar no Jira
1. ✅ Verificar resultado no Jira
1. ✅ Consultar logs em caso de erro

---

💬 **Dúvidas?** Consulte `issues/README_TEMPLATE.md` ou os logs em `logs/automatizacao_issues.log`

**Última atualização**: 19/02/2026
