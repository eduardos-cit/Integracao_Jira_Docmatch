"""
Módulo de Utilidades para Integração com Jira
==============================================
Centraliza funções comuns usadas pelos scripts de relatórios e automação.

Funções principais:
- Autenticação e conexão com Jira
- Busca e filtragem de issues
- Cálculo de métricas ágeis (Lead Time, Cycle Time, etc.)
- Agrupamento de issues por status
- Manipulação de sprints

Autor: Equipe de Automação Jira
Versão: 1.0
Data: Fevereiro 2026
"""

from collections import defaultdict
from datetime import datetime, timezone, timedelta
from dateutil import parser
import requests
import urllib3
import statistics
import csv
import os
import json
import re

# Suprimir avisos de SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_sprint_info_from_issues(issues):
    """
    Extrai informações da sprint a partir das issues encontradas.
    
    Args:
        issues (list): Lista de issues do Jira
        
    Returns:
        list: Lista de IDs de sprints encontradas nas issues
    """
    sprint_ids = set()
    
    for issue in issues:
        sprint_field = issue.get('customfield_10100')
        if sprint_field:
            if isinstance(sprint_field, list):
                for sprint in sprint_field:
                    if isinstance(sprint, dict) and sprint.get('state') == 'active':
                        sprint_ids.add(sprint['id'])
                    elif isinstance(sprint, str):
                        try:
                            import re
                            match = re.search(r'id=(\d+)', sprint)
                            if match:
                                sprint_ids.add(int(match.group(1)))
                        except:
                            pass
    
    return list(sprint_ids)


def get_sprint_details(jira_url, token, sprint_id):
    """
    Busca detalhes de uma sprint específica via API do Jira.
    
    Args:
        jira_url (str): URL base do Jira
        token (str): Token Bearer de autenticação
        sprint_id (int): ID da sprint
        
    Returns:
        dict: Detalhes da sprint ou None se não encontrada
    """
    try:
        sprint_url = f"{jira_url}/rest/agile/1.0/sprint/{sprint_id}"
        headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
        response = requests.get(sprint_url, headers=headers, verify=False)
        
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Erro ao buscar detalhes da sprint {sprint_id}: {e}")
    
    return None


def get_active_sprints_from_board(jira_url, token, project, board_id=None):
    """
    Busca sprints ativas diretamente da API do Jira usando o board.
    
    Args:
        jira_url (str): URL base do Jira
        token (str): Token Bearer de autenticação
        project (str): Chave do projeto
        board_id (int, optional): ID do board. Se não fornecido, busca o primeiro board do projeto
        
    Returns:
        dict: Informações da sprint ativa ou None
    """
    try:
        if not board_id:
            boards_url = f"{jira_url}/rest/agile/1.0/board"
            headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
            params = {"projectKeyOrId": project}
            response = requests.get(boards_url, headers=headers, params=params, verify=False)
            
            if response.status_code == 200 and response.json().get('values'):
                board_id = response.json()['values'][0]['id']
        
        if board_id:
            sprints_url = f"{jira_url}/rest/agile/1.0/board/{board_id}/sprint"
            params = {"state": "active"}
            response = requests.get(sprints_url, headers=headers, params=params, verify=False)
            
            if response.status_code == 200 and response.json().get('values'):
                return response.json()['values'][0]
    except Exception as e:
        print(f"Erro ao buscar sprints ativas: {e}")
    
    return None


def find_current_sprint_info(jira_url, token, project, issues):
    """
    Encontra informações da sprint atual usando múltiplas abordagens.
    
    Tenta primeiro via API do board, depois extrai das issues.
    
    Args:
        jira_url (str): URL base do Jira
        token (str): Token Bearer de autenticação
        project (str): Chave do projeto
        issues (list): Lista de issues para extrair sprint info
        
    Returns:
        dict: Informações da sprint ativa ou None
    """
    print("Buscando informações da sprint atual...")
    
    # Abordagem 1: Tentar via API do board
    sprint_info = get_active_sprints_from_board(jira_url, token, project)
    if sprint_info:
        return sprint_info
    
    # Abordagem 2: Tentar extrair das issues
    print("Tentando extrair informações de sprint das issues...")
    sprint_ids = get_sprint_info_from_issues(issues)
    
    if not sprint_ids:
        print("Nenhuma sprint encontrada nas issues.")
        return None
    
    # Buscar detalhes de cada sprint e encontrar a ativa
    for sprint_id in sprint_ids:
        sprint_details = get_sprint_details(jira_url, token, sprint_id)
        if sprint_details and sprint_details.get('state') == 'active':
            return sprint_details
    
    print("Nenhuma sprint ativa encontrada, tentando usar a primeira sprint disponível...")
    for sprint_id in sprint_ids:
        sprint_details = get_sprint_details(jira_url, token, sprint_id)
        if sprint_details:
            return sprint_details
    
    return None


def get_company_name(company_field):
    """
    Extrai o nome da company do campo customfield, lidando com diferentes formatos.
    
    Args:
        company_field: Campo customfield_13401 do Jira (pode ser string, dict ou list)
        
    Returns:
        str: Nome da company ou "Sem Company"
    """
    if not company_field:
        return "Sem Company"
    
    if isinstance(company_field, str):
        return company_field
    
    if isinstance(company_field, dict):
        return company_field.get('name') or company_field.get('value') or str(company_field)
    
    if isinstance(company_field, list) and company_field:
        first_item = company_field[0]
        if isinstance(first_item, dict):
            return first_item.get('name') or first_item.get('value') or str(first_item)
        return str(first_item)
    
    return str(company_field)


def get_story_points(issue):
    """
    Extrai Story Points da issue considerando variações de campos.

    Args:
        issue (dict): Dados da issue

    Returns:
        float: Valor de story points (0 se ausente)
    """
    candidates = [
        issue.get('story_points'),
        issue.get('story_points_custom'),
        issue.get('customfield_10106'),
    ]

    for value in candidates:
        if value is None:
            continue
        try:
            return float(value)
        except (TypeError, ValueError):
            continue

    return 0.0


def get_jira_issues(jira_url, token, jql_query=None, max_results=10000, include_custom_fields=True, 
                    project=None, team=None, filter_open_sprints=False):
    """
    Busca issues do Jira via API REST com todos os campos necessários.
    
    Args:
        jira_url (str): URL base do Jira
        token (str): Token Bearer de autenticação
        jql_query (str, optional): Query JQL customizada. Se não fornecida, será construída automaticamente
        max_results (int): Número máximo de resultados (padrão: 10000)
        include_custom_fields (bool): Se deve incluir campos customizados de métricas
        project (str, optional): Chave do projeto (usado se jql_query não fornecida)
        team (str, optional): Nome do time (usado se jql_query não fornecida)
        filter_open_sprints (bool): Se True, filtra apenas sprints ativas (padrão: False)
        
    Returns:
        list: Lista de dicionários com dados das issues
    """
    # Construir JQL query automaticamente se não fornecida
    if jql_query is None:
        if not project:
            raise ValueError("project é obrigatório quando jql_query não é fornecida")
        
        jql_parts = [f'project = {project}']
        
        # Adicionar filtro de sprint se solicitado
        if filter_open_sprints:
            jql_parts.append('Sprint in openSprints()')
        
        # Adicionar filtro de tipos de issue
        jql_parts.append('issuetype in (Story, "Tech Solution", Bug, Incidente, "Non Functional Task")')
        
        # Adicionar filtro de team se fornecido
        if team:
            jql_parts.append(f'Team = {team}')
        
        # Adicionar filtro de status (excluir cancelados e validados)
        jql_parts.append('status not in (Validado, Identificado, "Em Medição", Cancelado, Cancelada)')
        
        # Construir query e adicionar ordenação
        jql_query = ' AND '.join(jql_parts) + ' ORDER BY status ASC'
        print(f"JQL Query construída: {jql_query}")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }

    search_url = f"{jira_url}/rest/api/2/search"
    
    # Campos base 
    fields = 'id,key,issuetype,status,summary,description,timetracking,assignee,reporter,updated,created,issuelinks,customfield_10100,customfield_10101,customfield_10106,customfield_10401,customfield_13401'
    
    # Adicionar campos customizados de métricas se solicitado
    if include_custom_fields:
        fields += ',customfield_12318,customfield_18100'
    
    params = {
        'jql': jql_query,
        'fields': fields,
        'maxResults': max_results,
        'expand': 'changelog'
    }

    print(f"Buscando issues do Jira...")
    response = requests.get(search_url, headers=headers, params=params, verify=False)

    if response.status_code == 200:
        data = response.json()
        issues = []
        
        for item in data.get('issues', []):
            issue_data = {
                'key': item['key'],
                'id': item['id'],
                'summary': item['fields']['summary'],
                'description': item['fields'].get('description', ''),
                'status': item['fields']['status']['name'],
                'issuetype': item['fields']['issuetype']['name'],
                'assignee': item['fields'].get('assignee', {}).get('displayName', 'Não atribuído') if item['fields'].get('assignee') else 'Não atribuído',
                'reporter': item['fields'].get('reporter', {}).get('displayName', 'Desconhecido') if item['fields'].get('reporter') else 'Desconhecido',
                'created': item['fields']['created'],
                'updated': item['fields']['updated'],
                'customfield_10100': item['fields'].get('customfield_10100'),
                'customfield_10101': item['fields'].get('customfield_10101'),
                'customfield_10106': item['fields'].get('customfield_10106', 0) or 0,
                'story_points': item['fields'].get('customfield_10106', 0) or 0,
                'story_points_custom': item['fields'].get('customfield_10106', 0) or 0,
                'customfield_10401': item['fields'].get('customfield_10401'),
                'customfield_13401': get_company_name(item['fields'].get('customfield_13401')),
                'changelog': item.get('changelog', {})
            }
            
            # Adicionar campos customizados de métricas se incluídos
            if include_custom_fields:
                issue_data.update({
                    'customfield_12318': item['fields'].get('customfield_12318', 0) or 0,
                    'customfield_18100': item['fields'].get('customfield_18100', 0) or 0,
                    'pontos_funcao_metricas': item['fields'].get('customfield_12318', 0) or 0,
                    'pontos_funcao': item['fields'].get('customfield_18100', 0) or 0,
                    'company': get_company_name(item['fields'].get('customfield_13401'))
                })
            
            issues.append(issue_data)
        
        print(f"Total de {len(issues)} issues encontradas.")
        return issues
    else:
        print(f"Erro ao buscar issues: {response.status_code} - {response.text}")
        return []


def link_issues(issues):
    """
    Processa os links entre issues (como Test Plans e Test Executions).
    
    Args:
        issues (list): Lista de issues com dados do Jira
        
    Returns:
        list: Lista de issues com campos test_plans e test_executions adicionados
    """
    for issue in issues:
        # Inicializar listas para armazenar links
        issue['test_plans'] = []
        issue['test_executions'] = []
        
        # Verificar se há links de issues nos dados (campo issuelinks pode estar presente)
        # Como não estamos incluindo issuelinks no get_jira_issues, essa funcionalidade
        # será expandida futuramente se necessário
    
    return issues


def filter_issues_by_date(issues, start_date=None, end_date=None):
    """
    Filtra issues baseado em um range de datas usando o campo 'created'.
    
    Args:
        issues (list): Lista de issues
        start_date (str, optional): Data de início no formato 'DD/MM/YYYY' ou 'YYYY-MM-DD'
        end_date (str, optional): Data de fim no formato 'DD/MM/YYYY' ou 'YYYY-MM-DD'
        
    Returns:
        list: Issues filtradas pelo range de datas
    """
    if not start_date and not end_date:
        # Se nenhuma data foi informada, retorna todas as issues
        return issues
    
    sao_paulo_tz = timezone(timedelta(hours=-3))
    filtered_issues = []
    
    # Converter strings de data para datetime
    start_dt = None
    end_dt = None
    
    if start_date:
        try:
            # Tentar formato DD/MM/YYYY
            if '/' in start_date:
                start_dt = datetime.strptime(start_date, '%d/%m/%Y')
            else:
                start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            start_dt = start_dt.replace(hour=0, minute=0, second=0, tzinfo=sao_paulo_tz)
            print(f"Filtrando issues a partir de: {start_dt.strftime('%d/%m/%Y')}")
        except Exception as e:
            print(f"Erro ao converter data de início '{start_date}': {e}")
            return issues
    
    if end_date:
        try:
            # Tentar formato DD/MM/YYYY
            if '/' in end_date:
                end_dt = datetime.strptime(end_date, '%d/%m/%Y')
            else:
                end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            end_dt = end_dt.replace(hour=23, minute=59, second=59, tzinfo=sao_paulo_tz)
            print(f"Filtrando issues até: {end_dt.strftime('%d/%m/%Y')}")
        except Exception as e:
            print(f"Erro ao converter data de fim '{end_date}': {e}")
            return issues
    
    # Filtrar issues baseado nas datas
    for issue in issues:
        try:
            created_date = parser.parse(issue['created'])
            if created_date.tzinfo is None:
                created_date = created_date.replace(tzinfo=timezone.utc)
            created_date = created_date.astimezone(sao_paulo_tz)
            
            # Aplicar a lógica de filtro
            include_issue = True
            
            if start_dt and end_dt:
                # Ambas as datas informadas: respeitar o range
                include_issue = start_dt <= created_date <= end_dt
            elif start_dt:
                # Apenas data início: da data início até o futuro
                include_issue = created_date >= start_dt
            elif end_dt:
                # Apenas data fim: do passado até a data fim
                include_issue = created_date <= end_dt
            
            if include_issue:
                filtered_issues.append(issue)
        except Exception as e:
            print(f"Erro ao processar data da issue {issue.get('key', 'UNKNOWN')}: {e}")
            continue
    
    print(f"Total de {len(filtered_issues)} issues após filtro de datas (de {len(issues)} originais).")
    return filtered_issues


def filter_sprint_issues(all_issues, sprint_info):
    """
    Filtra apenas as issues que pertencem à sprint ativa.
    
    Args:
        all_issues (list): Lista completa de issues
        sprint_info (dict): Informações da sprint
        
    Returns:
        list: Issues filtradas que pertencem à sprint
    """
    if not sprint_info:
        print("Sem informações de sprint, não é possível filtrar issues da sprint.")
        return []
    
    sprint_id = sprint_info.get('id')
    sprint_name = sprint_info.get('name')
    sprint_issues = []
    
    for issue in all_issues:
        sprint_field = issue.get('customfield_10100')
        if sprint_field:
            if isinstance(sprint_field, list):
                for sprint in sprint_field:
                    if isinstance(sprint, dict) and sprint.get('id') == sprint_id:
                        sprint_issues.append(issue)
                        break
                    elif isinstance(sprint, str) and str(sprint_id) in sprint:
                        sprint_issues.append(issue)
                        break
    
    print(f"Total de {len(sprint_issues)} issues encontradas na sprint '{sprint_name}'.")
    return sprint_issues


def check_status_history_in_sprint_period(issue, sprint_start_date=None, sprint_end_date=None):
    """
    Verifica se a issue passou pelos status TESTADA, FINALIZADO ou FECHADO durante o período da sprint.
    
    Args:
        issue (dict): Dados da issue
        sprint_start_date (datetime): Data de início da sprint
        sprint_end_date (datetime): Data de fim da sprint
        
    Returns:
        bool: True se a issue foi entregue no período da sprint
    """
    target_statuses = ["TESTADA", "FINALIZADO", "FECHADO"]
    sao_paulo_tz = timezone(timedelta(hours=-3))
    
    if not sprint_start_date or not sprint_end_date:
        return any(status.upper() in issue['status'].upper() for status in target_statuses)
    
    if 'changelog' not in issue or 'histories' not in issue['changelog']:
        return False
    
    for history in issue['changelog']['histories']:
        try:
            history_date = parser.parse(history['created'])
            if history_date.tzinfo is None:
                history_date = history_date.replace(tzinfo=sao_paulo_tz)
            else:
                history_date = history_date.astimezone(sao_paulo_tz)
            
            if sprint_start_date <= history_date <= sprint_end_date:
                for item in history.get('items', []):
                    if item.get('field') == 'status':
                        to_status = item.get('toString', '').upper()
                        if to_status in target_statuses:
                            print(f"✓ {issue['key']} mudou para {to_status} em {history_date.strftime('%d/%m/%Y %H:%M')} (dentro da sprint)")
                            return True
        except Exception as e:
            continue
    
    return False


def calculate_lead_time(issue):
    """
    Calcula o lead time da issue (da saída do status inicial até "EM PRODUÇÃO").
    
    IMPORTANTE: Lead time é calculado apenas para:
    - Issue types: Story e Non Functional Task
    - Status final: EM PRODUÇÃO
    
    Status iniciais por tipo:
    - Story: PRODUCT BACKLOG
    - Non Functional Task: BACKLOG
    
    Args:
        issue (dict): Dados da issue
        
    Returns:
        int: Lead time em dias (0 se não calculável ou tipo não elegível)
    """
    try:
        issue_type = issue.get('issuetype', 'Unknown')
        
        # Calcular lead time APENAS para Story e Non Functional Task
        if issue_type not in ['Story', 'Non Functional Task']:
            return 0
        
        initial_statuses = {
            'Story': 'PRODUCT BACKLOG',
            'Non Functional Task': 'BACKLOG'
        }
        
        initial_status = initial_statuses.get(issue_type)
        
        if not initial_status or 'changelog' not in issue or 'histories' not in issue['changelog']:
            return 0
        
        start_date = None
        end_date = None
        
        for history in issue['changelog']['histories']:
            for item in history.get('items', []):
                if item.get('field') == 'status':
                    from_status = item.get('fromString', '').upper()
                    to_status = item.get('toString', '').upper()
                    
                    if from_status == initial_status.upper() and start_date is None:
                        start_date = parser.parse(history['created'])
                    
                    # Status final: apenas EM PRODUÇÃO
                    if to_status == 'EM PRODUÇÃO':
                        end_date = parser.parse(history['created'])
        
        if start_date and end_date:
            return (end_date - start_date).days
        
        return 0
    except Exception as e:
        return 0


def calculate_age_since_backlog(issue):
    """
    Calcula quantos dias se passaram desde que o item saiu do status Backlog.
    
    Args:
        issue (dict): Dados da issue
        
    Returns:
        int: Idade em dias desde saída do backlog
    """
    try:
        if 'changelog' not in issue or 'histories' not in issue['changelog']:
            created_date = parser.parse(issue['created'])
            return (datetime.now(timezone.utc) - created_date).days
        
        backlog_statuses = ['BACKLOG', 'PRODUCT BACKLOG', 'NOVO']
        
        for history in reversed(issue['changelog']['histories']):
            for item in history.get('items', []):
                if item.get('field') == 'status':
                    from_status = item.get('fromString', '').upper()
                    
                    if from_status in backlog_statuses:
                        exit_date = parser.parse(history['created'])
                        current_date = datetime.now(timezone.utc)
                        return (current_date - exit_date).days
        
        created_date = parser.parse(issue['created'])
        return (datetime.now(timezone.utc) - created_date).days
    except Exception as e:
        return 0


def calculate_cycle_time_by_status(delivered_issues):
    """
    Calcula o tempo médio gasto em cada status para os itens entregues.
    
    Args:
        delivered_issues (list): Lista de issues entregues
        
    Returns:
        dict: Dicionário com status como chave e tempo médio como valor
    """
    status_times = defaultdict(list)
    
    for issue in delivered_issues:
        if 'changelog' not in issue or 'histories' not in issue['changelog']:
            continue
        
        status_entries = {}
        
        for history in issue['changelog']['histories']:
            for item in history.get('items', []):
                if item.get('field') == 'status':
                    to_status = item.get('toString')
                    timestamp = parser.parse(history['created'])
                    
                    if to_status not in status_entries:
                        status_entries[to_status] = {'entry': timestamp, 'exit': None}
        
        sorted_histories = sorted(issue['changelog']['histories'], key=lambda h: h['created'])
        for i, history in enumerate(sorted_histories):
            for item in history.get('items', []):
                if item.get('field') == 'status':
                    from_status = item.get('fromString')
                    if from_status and from_status in status_entries:
                        status_entries[from_status]['exit'] = parser.parse(history['created'])
        
        for status, times in status_entries.items():
            if times['entry'] and times['exit']:
                duration = (times['exit'] - times['entry']).total_seconds() / 86400
                status_times[status].append(duration)
    
    avg_cycle_times = {}
    for status, times in status_times.items():
        avg_cycle_times[status] = round(statistics.mean(times), 1)
    
    return avg_cycle_times


def calculate_metrics(issues, grouped_issues, report_type='geral'):
    """
    Calcula métricas ágeis importantes para os relatórios.
    
    Args:
        issues (list): Lista de issues
        grouped_issues (dict): Issues agrupadas por categoria
        report_type (str): Tipo do relatório ('geral' ou 'sprint')
        
    Returns:
        dict: Dicionário com todas as métricas calculadas
    """
    metrics = {}
    
    # 1. Distribuição por tipo de issue
    issue_types = defaultdict(int)
    for issue in issues:
        issue_types[issue['issuetype']] += 1
    
    # 2. Lead time médio
    lead_times = [calculate_lead_time(issue) for issue in issues]
    valid_lead_times = [lt for lt in lead_times if lt > 0]
    avg_lead_time = statistics.mean(valid_lead_times) if valid_lead_times else 0
    
    # 3. Throughput (itens entregues)
    throughput = len(grouped_issues.get('Itens Entregues', []))
    
    # 4. Work in Progress (WIP)
    wip = len(grouped_issues.get('Em Progresso', []))
    
    # 5. Distribuição no pipeline
    pipeline_distribution = {
        'Desenvolvendo': len([i for i in issues if 'DESENVOLVIMENTO' in i['status'].upper()]),
        'Testando': len([i for i in issues if any(s in i['status'].upper() for s in ['TESTE', 'TESTADA'])]),
        'Homologando': len(grouped_issues.get('Itens em Homologação', [])),
        'Deploy Prod': len(grouped_issues.get('Em Deploy para Produção', [])),
        'Produção': len(grouped_issues.get('Itens em Produção', []))
    }
    
    # 6. Eficiência de entrega
    delivery_efficiency = (throughput / len(issues) * 100) if issues else 0
    
    # 7. Tempo médio no status atual
    current_status_times = []
    for issue in issues:
        if 'changelog' in issue and 'histories' in issue['changelog']:
            sorted_histories = sorted(issue['changelog']['histories'], key=lambda h: h['created'], reverse=True)
            if sorted_histories:
                last_status_change = parser.parse(sorted_histories[0]['created'])
                time_in_status = (datetime.now(timezone.utc) - last_status_change).days
                current_status_times.append(time_in_status)
    
    avg_status_time = statistics.mean(current_status_times) if current_status_times else 0
    
    # 8. Bugs vs Historias
    bugs = issue_types.get('Bug', 0) + issue_types.get('Incidente', 0)
    historias = (
        issue_types.get('Story', 0)
        + issue_types.get('Tech Solution', 0)
        + issue_types.get('Non Functional Task', 0)
    )
    
    # 9. Bugs por company
    bugs_by_company = defaultdict(int)
    for issue in issues:
        if issue['issuetype'] in ['Bug', 'Incidente']:
            bugs_by_company[issue.get('customfield_13401', 'Sem Company')] += 1
    
    # 10. Cycle time
    delivered_items = grouped_issues.get('Itens Entregues', [])
    cycle_times = calculate_cycle_time_by_status(delivered_items)
    
    # 11. Distribuição por tipo dos itens entregues
    delivered_issue_types = defaultdict(int)
    for issue in delivered_items:
        delivered_issue_types[issue['issuetype']] += 1
    
    metrics = {
        'issue_types': dict(issue_types),
        'avg_lead_time': round(avg_lead_time, 1),
        'throughput': throughput,
        'wip': wip,
        'pipeline_distribution': pipeline_distribution,
        'delivery_efficiency': round(delivery_efficiency, 1),
        'avg_status_time': round(avg_status_time, 1),
        'bugs_count': bugs,
        'historias_count': historias,
        'total_issues': len(issues),
        'bugs_vs_historias_ratio': round((bugs / historias * 100) if historias > 0 else 0, 1),
        'bugs_by_company': dict(bugs_by_company),
        'cycle_times': cycle_times,
        'delivered_issue_types': dict(delivered_issue_types)
    }
    
    # Adicionar métricas específicas do relatório geral
    if report_type == 'geral':
        total_pontos_funcao_metricas = sum(issue.get('customfield_12318', 0) or 0 for issue in issues)
        total_pontos_funcao = sum(issue.get('customfield_18100', 0) or 0 for issue in issues)
        
        metrics.update({
            'total_pontos_funcao_metricas': round(total_pontos_funcao_metricas, 1),
            'total_pontos_funcao': round(total_pontos_funcao, 1)
        })

    # Adicionar métricas específicas do relatório sprint (v2)
    if report_type == 'sprint':
        delivered_items = grouped_issues.get('Itens Entregues', [])
        total_items = len(issues)

        velocity_items = len(delivered_items)
        velocity_story_points = round(sum(get_story_points(issue) for issue in delivered_items), 1)
        commitment_rate = round((velocity_items / total_items * 100) if total_items > 0 else 0, 1)

        items_at_risk = len(grouped_issues.get('Em Progresso', []))

        bugs_found = len([i for i in issues if i.get('issuetype') in ['Bug', 'Incidente']])
        bugs_delivered = len([i for i in delivered_items if i.get('issuetype') in ['Bug', 'Incidente']])
        features_delivered = len([i for i in delivered_items if i.get('issuetype') not in ['Bug', 'Incidente']])

        quality_score = round((features_delivered / (features_delivered + bugs_found) * 100)
                              if (features_delivered + bugs_found) > 0 else 100, 1)

        predictability = round((100 - (items_at_risk / total_items * 100)) if total_items > 0 else 100, 1)
        sprint_health_score = round(
            (commitment_rate * 0.4) +
            (quality_score * 0.3) +
            (predictability * 0.3),
            1
        )

        delivery_timeline = defaultdict(int)
        status_targets = ["TESTADA", "FINALIZADO", "FECHADO"]
        sprint_start = None
        sprint_end = None

        for issue in issues:
            sprint_field = issue.get('customfield_10100')
            if not sprint_field:
                continue

            sprint_candidates = sprint_field if isinstance(sprint_field, list) else [sprint_field]
            for sprint_item in sprint_candidates:
                if isinstance(sprint_item, dict):
                    if not sprint_start and sprint_item.get('startDate'):
                        sprint_start = parser.parse(sprint_item.get('startDate'))
                    if not sprint_end and sprint_item.get('endDate'):
                        sprint_end = parser.parse(sprint_item.get('endDate'))

            if 'changelog' not in issue or 'histories' not in issue['changelog']:
                continue

            for history in issue['changelog']['histories']:
                history_date = parser.parse(history['created'])
                if sprint_start and history_date < sprint_start:
                    continue
                if sprint_end and history_date > sprint_end:
                    continue

                for item in history.get('items', []):
                    if item.get('field') == 'status' and item.get('toString', '').upper() in status_targets:
                        timeline_key = history_date.strftime('%d/%m')
                        delivery_timeline[timeline_key] += 1
                        break

        timeline_labels = sorted(
            delivery_timeline.keys(),
            key=lambda date_str: datetime.strptime(date_str, '%d/%m')
        )
        timeline_values = [delivery_timeline[label] for label in timeline_labels]

        burndown_labels = []
        burndown_real = []
        burndown_ideal = []

        if timeline_labels:
            cumulative_delivered = 0
            total_for_burndown = total_items
            days_count = len(timeline_labels)

            for index, label in enumerate(timeline_labels):
                cumulative_delivered += delivery_timeline[label]
                remaining = max(total_for_burndown - cumulative_delivered, 0)
                ideal_remaining = max(total_for_burndown - ((index + 1) * total_for_burndown / days_count), 0)

                burndown_labels.append(label)
                burndown_real.append(remaining)
                burndown_ideal.append(round(ideal_remaining, 1))

        metrics.update({
            'velocity_items': velocity_items,
            'velocity_story_points': velocity_story_points,
            'commitment_rate': commitment_rate,
            'items_at_risk': items_at_risk,
            'bugs_found': bugs_found,
            'bugs_delivered': bugs_delivered,
            'features_delivered': features_delivered,
            'quality_score': quality_score,
            'sprint_health_score': sprint_health_score,
            'timeline_labels': timeline_labels,
            'timeline_values': timeline_values,
            'burndown_labels': burndown_labels,
            'burndown_real': burndown_real,
            'burndown_ideal': burndown_ideal
        })
    
    return metrics


def group_issues_by_status(issues, sprint_info=None):
    """
    Agrupa issues por status/estágio do pipeline de desenvolvimento.
    
    Args:
        issues (list): Lista de issues
        sprint_info (dict, optional): Informações da sprint para detecção de itens entregues
        
    Returns:
        dict: Issues agrupadas por categoria
    """
    # Definir os grupos de status
    itens_homologacao = ["DISPONIVEL PARA HOMOLOGAÇÃO", "EM DEPLOY PARA HOMOLOGAÇÃO", 
                        "EM HOMOLOGAÇÃO", "HOMOLOGADA"]
    itens_deploy_producao = ["EM DEPLOY PARA PRODUÇÃO"]
    itens_producao = ["EM PRODUÇÃO", "ATIVADA"]
    aguardando_desenvolvimento = ["BACKLOG", "EM REFINAMENTO", "REFINADO", "PRODUCT BACKLOG",
                                  "SELECIONADO PARA GROOMING", "EM ANÁLISE", "ANÁLISE REALIZADA",
                                  "PRONTA PARA DESENVOLVIMENTO"]
    
    sprint_start_date = None
    sprint_end_date = None
    
    if sprint_info:
        try:
            sao_paulo_tz = timezone(timedelta(hours=-3))
            
            if 'startDate' in sprint_info:
                sprint_start_date = parser.parse(sprint_info['startDate'])
                if sprint_start_date.tzinfo is None:
                    sprint_start_date = sprint_start_date.replace(tzinfo=sao_paulo_tz)
                else:
                    sprint_start_date = sprint_start_date.astimezone(sao_paulo_tz)
            
            if 'endDate' in sprint_info:
                sprint_end_date = parser.parse(sprint_info['endDate'])
                if sprint_end_date.tzinfo is None:
                    sprint_end_date = sprint_end_date.replace(tzinfo=sao_paulo_tz)
                else:
                    sprint_end_date = sprint_end_date.astimezone(sao_paulo_tz)
            
            if sprint_start_date and sprint_end_date:
                print(f"Verificando histórico de status para período da sprint ({sprint_start_date.strftime('%d/%m/%Y')} a {sprint_end_date.strftime('%d/%m/%Y')})...")
        except Exception as e:
            print(f"Erro ao processar datas da sprint: {e}")
    
    grouped = {
        "Itens Entregues": [],
        "Itens em Homologação": [],
        "Em Deploy para Produção": [],
        "Itens em Produção": [],
        "Em Progresso": [],
        "Aguardando Desenvolvimento": []
    }
    
    for issue in issues:
        status_upper = issue['status'].upper()
        
        if check_status_history_in_sprint_period(issue, sprint_start_date, sprint_end_date):
            grouped["Itens Entregues"].append(issue)
        elif status_upper in [s.upper() for s in itens_producao]:
            grouped["Itens em Produção"].append(issue)
        elif status_upper in [s.upper() for s in itens_deploy_producao]:
            grouped["Em Deploy para Produção"].append(issue)
        elif status_upper in [s.upper() for s in itens_homologacao]:
            grouped["Itens em Homologação"].append(issue)
        elif status_upper in [s.upper() for s in aguardando_desenvolvimento]:
            grouped["Aguardando Desenvolvimento"].append(issue)
        else:
            grouped["Em Progresso"].append(issue)
    
    # Ordenar por lead time (do mais velho para o mais novo)
    grouped["Em Progresso"].sort(key=lambda issue: calculate_lead_time(issue), reverse=True)
    grouped["Aguardando Desenvolvimento"].sort(key=lambda issue: calculate_lead_time(issue), reverse=True)
    
    return grouped


def print_summary(grouped_issues, report_type='geral'):
    """
    Imprime resumo das issues agrupadas no console.
    
    Args:
        grouped_issues (dict): Issues agrupadas por categoria
        report_type (str): Tipo do relatório ('geral' ou 'sprint')
    """
    print(f"\nRelatório {'da Sprint' if report_type == 'sprint' else 'Geral do Projeto'}:")
    print("=" * 50)
    
    order = ["Itens Entregues", "Itens em Produção", "Em Deploy para Produção", 
             "Itens em Homologação", "Em Progresso", "Aguardando Desenvolvimento"]
    
    for category in order:
        issues = grouped_issues.get(category, [])
        print(f"\n{category} ({len(issues)} itens):")
        for issue in issues[:5]:  # Mostrar apenas 5 primeiros
            print(f"  • {issue['key']}: {issue['summary'][:60]}... (Status: {issue['status']})")
        if len(issues) > 5:
            print(f"  ... e mais {len(issues) - 5} itens")


def save_issues_to_csv(issues_list, report_type='geral'):
    """
    Salva dados brutos das issues em arquivo CSV na pasta logs.
    
    Campos incluídos:
    - Campos padrão do Jira (definidos em BulkCreate_configuration.txt)
    - Campos customizados (customfield_*)
    - Campos calculados (pontos, métricas, etc.)
    
    Args:
        issues_list (list): Lista de issues do Jira
        report_type (str): Tipo do relatório - 'sprint', 'geral', ou 'completo'
        
    Returns:
        str: Caminho do arquivo CSV gerado
    """
    try:
        # Garantir que a pasta logs existe
        os.makedirs('logs', exist_ok=True)
        
        # Nome do arquivo com timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_filename = f"logs/jira_raw_data_{report_type}_{timestamp}.csv"
        
        if not issues_list:
            print(f"⚠️  Nenhuma issue para salvar em CSV")
            return None
        
        # Função auxiliar para processar campos complexos
        def clean_text(text):
            """Remove quebras de linha e caracteres especiais que quebram CSV"""
            if not text:
                return ''
            text = str(text)
            # Substituir quebras de linha por espaço
            text = text.replace('\n', ' ').replace('\r', ' ')
            # Remover múltiplos espaços
            text = ' '.join(text.split())
            return text
        
        def extract_sprint_name(sprint_field):
            """Extrai nome da sprint do campo customfield_10100"""
            if not sprint_field:
                return ''
            if isinstance(sprint_field, list):
                # Pegar a última sprint (mais recente)
                for sprint in reversed(sprint_field):
                    if isinstance(sprint, dict):
                        return sprint.get('name', '')
                    elif isinstance(sprint, str):
                        # Tentar extrair nome usando regex
                        import re
                        match = re.search(r'name=([^,\]]+)', sprint)
                        if match:
                            return match.group(1)
                return str(sprint_field[0]) if sprint_field else ''
            return str(sprint_field)
        
        def extract_simple_value(field):
            """Extrai valor simples de campos que podem ser dict, list ou string"""
            if not field:
                return ''
            if isinstance(field, dict):
                return field.get('value') or field.get('name') or field.get('key') or str(field)
            if isinstance(field, list):
                if field and isinstance(field[0], dict):
                    return field[0].get('value') or field[0].get('name') or field[0].get('key') or ''
                return ', '.join(str(item) for item in field)
            return str(field)
        
        # Definir campos para o CSV (baseado em BulkCreate_configuration.txt + campos adicionais)
        fieldnames = [
            # Campos padrão do Jira (config.field.mappings)
            'key',                      # Issue Key
            'id',                       # ID interno
            'summary',                  # Summary
            'issuetype',                # Issue Type
            'status',                   # Status
            'assignee',                 # Assignee
            'reporter',                 # Reporter
            'created',                  # Created date
            'updated',                  # Updated date
            'labels',                   # Labels
            'timeoriginalestimate',     # Original Estimate
            
            # Campos customizados principais (valores processados)
            'sprint',                   # Sprint (customfield_10100 processado)
            'epic_link',                # Epic Link (customfield_10101)
            'team',                     # Team (customfield_10401)
            'company',                  # Company (customfield_13401 processado)
            'pf_metricas',              # Pontos de Função Métricas (customfield_12318)
            'pf',                       # Pontos de Função (customfield_18100)
        ]
        
        with open(csv_filename, 'w', encoding='utf-8', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            
            for issue in issues_list:
                # Preparar dados da issue para CSV
                row = {
                    # Campos padrão
                    'key': issue.get('key', ''),
                    'id': issue.get('id', ''),
                    'summary': clean_text(issue.get('summary', '')),
                    'issuetype': issue.get('issuetype', ''),
                    'status': issue.get('status', ''),
                    'assignee': issue.get('assignee', ''),
                    'reporter': issue.get('reporter', ''),
                    'created': issue.get('created', ''),
                    'updated': issue.get('updated', ''),
                    'labels': ', '.join(issue.get('labels', [])) if isinstance(issue.get('labels'), list) else str(issue.get('labels', '')),
                    'timeoriginalestimate': issue.get('timeoriginalestimate', ''),
                    
                    # Campos customizados (valores processados)
                    'sprint': extract_sprint_name(issue.get('customfield_10100')),
                    'epic_link': extract_simple_value(issue.get('customfield_10101')),
                    'team': extract_simple_value(issue.get('customfield_10401')),
                    'company': issue.get('company', '') or issue.get('customfield_13401', ''),
                    'pf_metricas': issue.get('pontos_funcao_metricas', 0) or issue.get('customfield_12318', 0) or 0,
                    'pf': issue.get('pontos_funcao', 0) or issue.get('customfield_18100', 0) or 0,
                }
                writer.writerow(row)
        
        print(f"📄 Dados brutos salvos em CSV: {csv_filename}")
        print(f"   {len(issues_list)} issues exportadas com {len(fieldnames)} campos")
        return csv_filename
        
    except Exception as e:
        print(f"⚠️  Erro ao salvar CSV: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def generate_html_report(grouped_issues, metrics, jira_url, sprint_info=None, report_type='geral', filter_start_date=None, filter_end_date=None):
    """
    Gera relatório HTML com visualização das issues e métricas.
    Função centralizada usada por todos os scripts de relatório.
    
    Args:
        grouped_issues (dict): Issues agrupadas por categoria de status
        metrics (dict): Métricas calculadas do projeto/sprint
        jira_url (str): URL base do Jira para links
        sprint_info (dict, optional): Informações da sprint ativa
        report_type (str): Tipo do relatório - 'sprint' (Sprint Review) ou 'geral' (Geral do Projeto)
        filter_start_date (str, optional): Data de início do filtro aplicado
        filter_end_date (str, optional): Data de fim do filtro aplicado
        
    Returns:
        str: Caminho do arquivo HTML gerado
    """
    import os
    
    # Configuração do arquivo de saída
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if report_type == 'sprint':
        filename = f"relatorios/sprint_review_{timestamp}.html"
        sprint_name = sprint_info.get('name') if sprint_info else None
        page_title = f"Sprint Review - {sprint_name}" if sprint_name else "Sprint Review"
        main_heading = "Sprint Review"
        sprint_heading = f"Sprint Review - {sprint_name}" if sprint_name else "Sprint Review"
    else:  # 'geral'
        filename = f"relatorios/backlog_geral_{timestamp}.html"
        sprint_name = sprint_info.get('name') if sprint_info else None
        page_title = f"Sprint atual - {sprint_name}" if sprint_name else "Relatório Geral"
        main_heading = "Relatório geral do Backlog"
        sprint_heading = f"Sprint atual - {sprint_name}" if sprint_name else "Sprint atual"
    
    jira_base_url = jira_url or "https://jira.bradesco.com.br:8443"
    
    # Formatizar datas da sprint para o timezone São Paulo
    sprint_dates_info = ""
    if sprint_info and 'startDate' in sprint_info and 'endDate' in sprint_info:
        try:
            sao_paulo_tz = timezone(timedelta(hours=-3))
            
            start_date = parser.parse(sprint_info['startDate'])
            end_date = parser.parse(sprint_info['endDate'])
            
            # Converter para timezone de São Paulo se necessário
            if start_date.tzinfo is None:
                start_date = start_date.replace(tzinfo=timezone.utc)
            if end_date.tzinfo is None:
                end_date = end_date.replace(tzinfo=timezone.utc)
                
            start_date_sp = start_date.astimezone(sao_paulo_tz)
            end_date_sp = end_date.astimezone(sao_paulo_tz)
            
            sprint_dates_info = f"📅 Período da sprint: {start_date_sp.strftime('%d/%m/%Y')} a {end_date_sp.strftime('%d/%m/%Y')}"
        except Exception as e:
            print(f"Erro ao formatar datas da sprint: {e}")
            sprint_dates_info = ""
    
    # Formatizar período executado (filtro de datas)
    filter_dates_info = ""
    if filter_start_date or filter_end_date:
        if filter_start_date and filter_end_date:
            filter_dates_info = f"🔍 Período executado: {filter_start_date} a {filter_end_date}"
        elif filter_start_date:
            filter_dates_info = f"🔍 Período executado: a partir de {filter_start_date}"
        elif filter_end_date:
            filter_dates_info = f"🔍 Período executado: até {filter_end_date}"
    
    print(f"\n{'='*50}")
    print(f"Gerando relatório HTML: {filename}")
    print(f"Tipo: {report_type.upper()}")
    print(f"{'='*50}\n")
    
    # Garantir que o diretório existe
    os.makedirs("relatorios", exist_ok=True)
    
    # Gerar conteúdo HTML
    html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{page_title}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2"></script>
    <!-- Bradesco Design System Liquid -->
    <link href="https://cdn.jsdelivr.net/npm/@bradesco/liquid-design-system@latest/dist/liquid.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Nunito+Sans:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        /* Design System Liquid Bradesco */
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Nunito Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background-color: #f8f9fa;
            color: #212529;
            line-height: 1.6;
            font-weight: 400;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            background: linear-gradient(135deg, #cc092f, #e31837);
            color: white;
            padding: 30px 20px;
            border-radius: 8px;
            margin-bottom: 30px;
            box-shadow: 0 4px 12px rgba(204, 9, 47, 0.2);
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}
        
        .header-content {{
            flex: 1;
        }}
        
        .header h1 {{
            font-size: 2.8rem;
            font-weight: 700;
            margin-bottom: 10px;
            font-family: 'Nunito Sans', sans-serif;
        }}
        
        .header .subtitle {{
            font-size: 1.1rem;
            opacity: 0.9;
            font-weight: 400;
        }}
        
        .section {{
            background: white;
            margin-bottom: 25px;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }}
        
        .section-header {{
            background-color: #cc092f;
            color: white;
            padding: 15px 20px;
            font-size: 1.3rem;
            font-weight: 500;
            cursor: pointer;
            position: relative;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}
        
        .section-header.entregues {{
            background-color: #cc092f;
        }}
        
        .section-header.homologacao {{
            background-color: #f39c12;
        }}
        
        .section-header.deploy {{
            background-color: #e67e22;
        }}
        
        .section-header.producao {{
            background-color: #27ae60;
        }}
        
        .section-header.progresso {{
            background-color: #3498db;
        }}
        
        .section-header.aguardando {{
            background-color: #95a5a6;
        }}
        
        .section-content {{
            padding: 0;
            transition: max-height 0.3s ease, opacity 0.3s ease;
            overflow: hidden;
        }}
        
        .section-content.collapsed {{
            max-height: 0 !important;
            opacity: 0;
        }}
        
        .section-content.expanded {{
            opacity: 1;
        }}
        
        .issue-item {{
            padding: 15px 20px;
            border-bottom: 1px solid #eee;
            transition: background-color 0.2s;
        }}
        
        .issue-item:hover {{
            background-color: #f8f9fa;
        }}
        
        .issue-item:last-child {{
            border-bottom: none;
        }}
        
        .issue-key {{
            font-weight: bold;
            color: #cc092f;
            text-decoration: none;
            font-size: 1rem;
            transition: color 0.2s ease;
            position: relative;
        }}
        
        .issue-key:hover {{
            color: #e31837;
            text-decoration: underline;
        }}
        
        .issue-key:after {{
            content: "↗";
            font-size: 0.8rem;
            opacity: 0.6;
            margin-left: 4px;
        }}
        
        .issue-type {{
            display: inline-block;
            color: white;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 500;
            margin-right: 8px;
            min-width: 50px;
            text-align: center;
        }}
        
        .issue-type.story {{
            background-color: #09ab47;
        }}
        
        .issue-type.tech-solution {{
            background-color: #ffbc01;
            color: #333;
        }}
        
        .issue-type.bug {{
            background-color: #b00f2f;
        }}
        
        .issue-type.incidente {{
            background-color: #b00f2f;
        }}

        .issue-type.non-functional-task {{
            background-color: #2563eb;
        }}
        
        .issue-summary {{
            margin: 5px 0;
            font-size: 0.95rem;
        }}
        
        .issue-status {{
            display: inline-block;
            background-color: #e9ecef;
            color: #495057;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 0.8rem;
            font-weight: 500;
        }}
        
        .company-tag {{
            display: inline-block;
            color: white;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 0.8rem;
            font-weight: 500;
            margin-left: 8px;
        }}
        
        .company-tag.mckinsey {{
            background-color: #3b69ff;
        }}
        
        .company-tag.cit {{
            background-color: #e1173f;
        }}
        
        .company-tag.default {{
            background-color: #ff6b35;
        }}
        
        .age-tag {{
            background-color: #f39c12;
            color: white;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 600;
            margin-left: 8px;
            display: inline-block;
        }}
        
        .age-tag.old {{
            background-color: #e74c3c;
        }}
        
        .age-tag.very-old {{
            background-color: #8b0000;
        }}
        
        .points-tag {{
            color: white;
            padding: 2px 6px;
            border-radius: 10px;
            font-size: 0.7rem;
            font-weight: 600;
            margin-left: 6px;
            display: inline-block;
        }}
        
        .points-tag.pf-metricas {{
            background-color: #9b59b6;  /* Roxo */
        }}
        
        .points-tag.pf {{
            background-color: #3498db;  /* Azul */
        }}
        
        .points-tag.sp {{
            background-color: #e67e22;  /* Laranja */
        }}
        
        .counter {{
            background-color: rgba(255, 255, 255, 0.2);
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 0.9rem;
            margin-left: 10px;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .stat-card {{
            background: white;
            text-align: center;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            border-left: 4px solid #cc092f;
        }}
        
        .stat-number {{
            font-size: 2rem;
            font-weight: bold;
            color: #cc092f;
        }}
        
        .stat-label {{
            color: #666;
            font-size: 0.9rem;
            margin-top: 5px;
        }}
        
        .footer {{
            text-align: center;
            color: #666;
            margin-top: 40px;
            padding: 20px;
        }}
        
        .toggle-icon {{
            transition: transform 0.3s ease;
        }}
        
        .toggle-icon.collapsed {{
            transform: rotate(180deg);
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="header-content">
                <h1>{main_heading}</h1>
                <div class="subtitle">{sprint_heading}</div>"""
    
    # Adicionar datas da sprint se disponíveis
    if sprint_dates_info:
        html_content += f"""
                <div class="subtitle">{sprint_dates_info}</div>"""
    
    # Adicionar período executado (filtro de datas) se disponível
    if filter_dates_info:
        html_content += f"""
                <div class="subtitle">{filter_dates_info}</div>"""
    
    html_content += f"""
                <div class="subtitle">Gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}</div>
            </div>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">{metrics.get('throughput', 0)}</div>
                <div class="stat-label">Itens Entregues</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{metrics.get('avg_lead_time', 0)}</div>
                <div class="stat-label">Lead Time Médio (dias)</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{metrics.get('wip', 0)}</div>
                <div class="stat-label">Work in Progress</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{metrics.get('delivery_efficiency', 0)}%</div>
                <div class="stat-label">Eficiência de Entrega</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{metrics.get('total_issues', 0)}</div>
                <div class="stat-label">Total de Issues</div>
            </div>"""
    
    # Adicionar métricas específicas do relatório geral
    if report_type == 'geral':
        html_content += f"""
            <div class="stat-card">
                <div class="stat-number">{metrics.get('total_pontos_funcao_metricas', 0)}</div>
                <div class="stat-label">PF (Métricas)</div>
            </div>"""
    
    html_content += """
        </div>
"""
    
    # Adicionar seções de issues
    section_classes = {
        "Itens Entregues": "entregues",
        "Itens em Homologação": "homologacao",
        "Em Deploy para Produção": "deploy",
        "Itens em Produção": "producao",
        "Em Progresso": "progresso",
        "Aguardando Desenvolvimento": "aguardando"
    }
    
    section_order = ["Itens Entregues", "Itens em Produção", "Em Deploy para Produção", 
                    "Itens em Homologação", "Em Progresso", "Aguardando Desenvolvimento"]
    
    for category in section_order:
        if category in grouped_issues and grouped_issues[category]:
            issues = grouped_issues[category]
            html_content += f"""
        <div class="section">
            <div class="section-header {section_classes[category]}" onclick="toggleSection(this)">
                <div>
                    {category}
                    <span class="counter">{len(issues)} itens</span>
                </div>
                <span class="toggle-icon collapsed">▲</span>
            </div>
            <div class="section-content collapsed">
"""
            for issue in issues:
                # Company tag para bugs
                company_tag = ""
                if issue['issuetype'].upper() in ['BUG', 'INCIDENTE']:
                    company_name = issue.get('customfield_13401', 'Sem Company')
                    company_class = "default"
                    if 'mckinsey' in company_name.lower():
                        company_class = "mckinsey"
                    elif 'ci&t' in company_name.lower() or 'cit' in company_name.lower():
                        company_class = "cit"
                    company_tag = f'<span class="company-tag {company_class}">{company_name}</span>'
                
                # Issue type class
                issue_type_class = ""
                issue_type_normalized = issue['issuetype'].strip().lower().replace('_', ' ').replace('-', ' ')
                issue_type_normalized = re.sub(r"\s+", " ", issue_type_normalized)

                if issue_type_normalized == 'story':
                    issue_type_class = "story"
                elif issue_type_normalized == 'tech solution':
                    issue_type_class = "tech-solution"
                elif issue_type_normalized in ['bug', 'incidente']:
                    issue_type_class = "bug"
                elif issue_type_normalized == 'non functional task':
                    issue_type_class = "non-functional-task"
                
                # Age tag para itens em progresso
                age_tag = ""
                if category == "Em Progresso":
                    age_days = calculate_lead_time(issue)
                    age_class = ""
                    if age_days > 60:
                        age_class = " very-old"
                    elif age_days > 30:
                        age_class = " old"
                    day_text = "dia" if age_days == 1 else "dias"
                    age_tag = f'<span class="age-tag{age_class}">{age_days} {day_text}</span>'
                
                # Points tags para relatório geral
                points_tags = ""
                if report_type == 'geral':
                    pf_metricas = issue.get('customfield_13417', 0) or 0
                    pf = issue.get('customfield_10108', 0) or 0
                    
                    if pf_metricas:
                        points_tags += f'<span class="points-tag pf-metricas">PF(M): {pf_metricas}</span>'
                    if pf:
                        points_tags += f'<span class="points-tag pf">PF: {pf}</span>'
                
                html_content += f"""
                <div class="issue-item">
                    <span class="issue-type {issue_type_class}">{issue['issuetype']}</span>
                    <a href="{jira_base_url}/browse/{issue['key']}" class="issue-key" target="_blank">{issue['key']}</a>
                    <div class="issue-summary">{issue['summary']}</div>
                    <span class="issue-status">{issue['status']}</span>{company_tag}{age_tag}{points_tags}
                </div>
"""
            html_content += """
            </div>
        </div>
"""
    
    html_content += """
        <div class="footer">
            <p>Relatório gerado automaticamente pelo sistema de integração Jira</p>
        </div>
    </div>
    
    <script>
        function toggleSection(header) {
            const section = header.parentElement;
            const content = section.querySelector('.section-content');
            const icon = header.querySelector('.toggle-icon');
            
            if (content.classList.contains('collapsed')) {
                content.classList.remove('collapsed');
                content.style.maxHeight = content.scrollHeight + 'px';
                icon.classList.remove('collapsed');
                icon.innerHTML = '▼';
            } else {
                content.classList.add('collapsed');
                content.style.maxHeight = '0px';
                icon.classList.add('collapsed');
                icon.innerHTML = '▲';
            }
        }
    </script>
</body>
</html>
"""
    
    # Salvar arquivo
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(html_content)
    
    print(f"✓ Relatório HTML gerado: {filename}")
    print(f"  - Itens Entregues: {len(grouped_issues.get('Itens Entregues', []))}")
    print(f"  - Itens em Produção: {len(grouped_issues.get('Itens em Produção', []))}")
    print(f"  - Em Deploy: {len(grouped_issues.get('Em Deploy para Produção', []))}")
    print(f"  - Em Homologação: {len(grouped_issues.get('Itens em Homologação', []))}")
    print(f"  - Em Progresso: {len(grouped_issues.get('Em Progresso', []))}")
    print(f"  - Aguardando Desenvolvimento: {len(grouped_issues.get('Aguardando Desenvolvimento', []))}")
    
    return filename


def generate_html_report_sprint_v2(grouped_issues, metrics, jira_url, sprint_info=None, filter_start_date=None, filter_end_date=None):
    """
    Gera relatório HTML v2 para Sprint Review com métricas avançadas e visualizações.

    Mantém o relatório v1 existente para comparação.

    Args:
        grouped_issues (dict): Issues agrupadas por categoria
        metrics (dict): Métricas calculadas da sprint
        jira_url (str): URL base do Jira
        sprint_info (dict, optional): Dados da sprint ativa
        filter_start_date (str, optional): Filtro inicial aplicado
        filter_end_date (str, optional): Filtro final aplicado

    Returns:
        str: Caminho do arquivo HTML gerado
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"relatorios/sprint_review_v2_{timestamp}.html"
    os.makedirs("relatorios", exist_ok=True)

    sprint_name = sprint_info.get('name') if sprint_info else "Sprint ativa"
    jira_base_url = jira_url or "https://jira.bradesco.com.br:8443"

    sprint_dates_info = ""
    if sprint_info and 'startDate' in sprint_info and 'endDate' in sprint_info:
        try:
            start_date = parser.parse(sprint_info['startDate']).strftime('%d/%m/%Y')
            end_date = parser.parse(sprint_info['endDate']).strftime('%d/%m/%Y')
            sprint_dates_info = f"Período da sprint: {start_date} a {end_date}"
        except Exception:
            sprint_dates_info = ""

    filter_dates_info = ""
    if filter_start_date or filter_end_date:
        if filter_start_date and filter_end_date:
            filter_dates_info = f"Período executado: {filter_start_date} a {filter_end_date}"
        elif filter_start_date:
            filter_dates_info = f"Período executado: a partir de {filter_start_date}"
        elif filter_end_date:
            filter_dates_info = f"Período executado: até {filter_end_date}"

    timeline_labels = metrics.get('timeline_labels', [])
    timeline_values = metrics.get('timeline_values', [])
    burndown_labels = metrics.get('burndown_labels', [])
    burndown_real = metrics.get('burndown_real', [])
    burndown_ideal = metrics.get('burndown_ideal', [])

    issue_type_labels = list(metrics.get('issue_types', {}).keys())
    issue_type_values = list(metrics.get('issue_types', {}).values())

    html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sprint Review v2 - {sprint_name}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://cdn.jsdelivr.net/npm/@bradesco/liquid-design-system@latest/dist/liquid.min.css" rel="stylesheet">
    <style>
        body {{
            font-family: 'Nunito Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background-color: #f8f9fa;
            color: #212529;
            margin: 0;
            padding: 0;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            background: linear-gradient(135deg, #cc092f, #e31837);
            color: white;
            padding: 28px;
            border-radius: 8px;
            margin-bottom: 24px;
        }}
        .header h1 {{
            margin: 0 0 10px 0;
            font-size: 2.2rem;
        }}
        .subtitle {{
            opacity: 0.95;
            margin-top: 4px;
            font-size: 0.98rem;
        }}
        .badge {{
            display: inline-block;
            background: rgba(255,255,255,0.2);
            color: white;
            border: 1px solid rgba(255,255,255,0.4);
            border-radius: 999px;
            padding: 4px 12px;
            font-size: 0.75rem;
            margin-bottom: 10px;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }}
        .stat-card {{
            background: white;
            border-radius: 8px;
            padding: 16px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.08);
            border-left: 4px solid #cc092f;
        }}
        .stat-value {{
            font-size: 1.8rem;
            font-weight: 700;
            color: #cc092f;
            margin-bottom: 4px;
        }}
        .stat-label {{
            font-size: 0.9rem;
            color: #555;
        }}
        .charts-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }}
        .chart-card {{
            background: white;
            border-radius: 8px;
            padding: 16px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.08);
        }}
        .chart-card h3 {{
            margin: 0 0 10px 0;
            font-size: 1rem;
            color: #333;
        }}
        .chart-wrapper {{
            height: 260px;
        }}
        .section {{
            background: white;
            border-radius: 8px;
            margin-bottom: 16px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.08);
            overflow: hidden;
        }}
        .section-header {{
            background-color: #cc092f;
            color: white;
            padding: 12px 16px;
            font-weight: 600;
        }}
        .issue-item {{
            padding: 12px 16px;
            border-bottom: 1px solid #eee;
        }}
        .issue-item:last-child {{
            border-bottom: none;
        }}
        .issue-key {{
            color: #cc092f;
            font-weight: 700;
            text-decoration: none;
        }}
        .issue-key:hover {{
            text-decoration: underline;
        }}
        .issue-meta {{
            margin-top: 4px;
            font-size: 0.85rem;
            color: #666;
        }}
        .footer {{
            text-align: center;
            color: #666;
            margin-top: 28px;
            padding: 10px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="badge">NOVA VERSÃO (v2)</div>
            <h1>Sprint Review</h1>
            <div class="subtitle">{sprint_name}</div>
            <div class="subtitle">{sprint_dates_info}</div>
            <div class="subtitle">{filter_dates_info}</div>
            <div class="subtitle">Gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}</div>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">{metrics.get('velocity_items', 0)}</div>
                <div class="stat-label">Velocity (itens entregues)</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{metrics.get('velocity_story_points', 0)}</div>
                <div class="stat-label">Velocity (story points)</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{metrics.get('commitment_rate', 0)}%</div>
                <div class="stat-label">Commitment Achievement</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{metrics.get('items_at_risk', 0)}</div>
                <div class="stat-label">Itens em Risco</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{metrics.get('bugs_found', 0)}</div>
                <div class="stat-label">Bugs Encontrados</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{metrics.get('quality_score', 0)}%</div>
                <div class="stat-label">Quality Score (features/bugs)</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{metrics.get('sprint_health_score', 0)}</div>
                <div class="stat-label">Sprint Health Score</div>
            </div>
        </div>

        <div class="charts-grid">
            <div class="chart-card">
                <h3>Gráfico de Velocity</h3>
                <div class="chart-wrapper"><canvas id="velocityChart"></canvas></div>
            </div>
            <div class="chart-card">
                <h3>Burndown Chart</h3>
                <div class="chart-wrapper"><canvas id="burndownChart"></canvas></div>
            </div>
            <div class="chart-card">
                <h3>Distribuição por Tipo</h3>
                <div class="chart-wrapper"><canvas id="typeDistributionChart"></canvas></div>
            </div>
            <div class="chart-card">
                <h3>Timeline de Entregas</h3>
                <div class="chart-wrapper"><canvas id="timelineChart"></canvas></div>
            </div>
        </div>
"""

    section_order = [
        "Itens Entregues",
        "Itens em Produção",
        "Em Deploy para Produção",
        "Itens em Homologação",
        "Em Progresso",
        "Aguardando Desenvolvimento"
    ]

    for category in section_order:
        issues = grouped_issues.get(category, [])
        if not issues:
            continue

        html_content += f"""
        <div class="section">
            <div class="section-header">{category} ({len(issues)} itens)</div>
"""

        for issue in issues:
            age_text = ""
            if category in ["Em Progresso", "Aguardando Desenvolvimento"]:
                age_text = f" • Idade: {calculate_lead_time(issue)} dias"

            html_content += f"""
            <div class="issue-item">
                <a href="{jira_base_url}/browse/{issue['key']}" class="issue-key" target="_blank">{issue['key']}</a>
                - {issue['summary']}
                <div class="issue-meta">{issue['issuetype']} • {issue['status']}{age_text}</div>
            </div>
"""

        html_content += """
        </div>
"""

    html_content += f"""
        <div class="footer">
            <p>Relatório Sprint Review v2 gerado automaticamente</p>
        </div>
    </div>

    <script>
        const velocityItems = {metrics.get('velocity_items', 0)};
        const velocityStoryPoints = {metrics.get('velocity_story_points', 0)};

        const burndownLabels = {json.dumps(burndown_labels if burndown_labels else ['Sem dados'])};
        const burndownReal = {json.dumps(burndown_real if burndown_real else [0])};
        const burndownIdeal = {json.dumps(burndown_ideal if burndown_ideal else [0])};

        const issueTypeLabels = {json.dumps(issue_type_labels if issue_type_labels else ['Sem dados'])};
        const issueTypeValues = {json.dumps(issue_type_values if issue_type_values else [0])};

        const timelineLabels = {json.dumps(timeline_labels if timeline_labels else ['Sem dados'])};
        const timelineValues = {json.dumps(timeline_values if timeline_values else [0])};

        new Chart(document.getElementById('velocityChart'), {{
            type: 'bar',
            data: {{
                labels: ['Itens Entregues', 'Story Points Entregues'],
                datasets: [{{
                    label: 'Velocity',
                    data: [velocityItems, velocityStoryPoints],
                    backgroundColor: ['#cc092f', '#f39c12']
                }}]
            }},
            options: {{ responsive: true, maintainAspectRatio: false }}
        }});

        new Chart(document.getElementById('burndownChart'), {{
            type: 'line',
            data: {{
                labels: burndownLabels,
                datasets: [
                    {{ label: 'Real', data: burndownReal, borderColor: '#cc092f', fill: false }},
                    {{ label: 'Ideal', data: burndownIdeal, borderColor: '#3498db', borderDash: [6, 4], fill: false }}
                ]
            }},
            options: {{ responsive: true, maintainAspectRatio: false }}
        }});

        new Chart(document.getElementById('typeDistributionChart'), {{
            type: 'doughnut',
            data: {{
                labels: issueTypeLabels,
                datasets: [{{
                    data: issueTypeValues,
                    backgroundColor: ['#cc092f', '#e67e22', '#27ae60', '#3498db', '#9b59b6', '#95a5a6']
                }}]
            }},
            options: {{ responsive: true, maintainAspectRatio: false }}
        }});

        new Chart(document.getElementById('timelineChart'), {{
            type: 'bar',
            data: {{
                labels: timelineLabels,
                datasets: [{{
                    label: 'Entregas por data',
                    data: timelineValues,
                    backgroundColor: '#cc092f'
                }}]
            }},
            options: {{ responsive: true, maintainAspectRatio: false }}
        }});
    </script>
</body>
</html>
"""

    with open(filename, 'w', encoding='utf-8') as file:
        file.write(html_content)

    print(f"✓ Relatório HTML v2 gerado: {filename}")
    return filename
