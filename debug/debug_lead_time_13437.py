import requests
import json
import os
from dotenv import load_dotenv
from datetime import datetime, timezone
from dateutil import parser

# Carregar variáveis do arquivo .env
load_dotenv()

def calculate_lead_time(issue):
    """
    Calcula o lead time da issue (da saída do status inicial até a produção/finalização)
    Status iniciais por tipo:
    - Bug: NOVO
    - Story: PRODUCT BACKLOG  
    - Tech Solution: BACKLOG
    - Incidente: BACKLOG
    """
    try:
        # Definir status inicial baseado no tipo da issue
        issue_type = issue['issuetype'].upper()
        if issue_type == 'BUG':
            initial_status = 'NOVO'
        elif issue_type == 'STORY':
            initial_status = 'PRODUCT BACKLOG'
        elif issue_type in ['TECH SOLUTION', 'INCIDENTE']:
            initial_status = 'BACKLOG'
        else:
            # Fallback para tipos não mapeados - usar data de criação
            initial_status = None
        
        print(f"Tipo: {issue_type}")
        print(f"Status atual: {issue['status']}")
        print(f"Status inicial mapeado para tipo '{issue_type}': {initial_status}")
        
        # Procurar pela data de saída do status inicial
        start_date = None
        
        if initial_status and 'changelog' in issue and 'histories' in issue['changelog']:
            print(f"\nAnalisando {len(issue['changelog']['histories'])} mudanças no histórico...")
            
            # Ordenar histórico por data para processar cronologicamente
            sorted_histories = sorted(issue['changelog']['histories'], 
                                    key=lambda h: parser.parse(h['created']))
            
            for i, history in enumerate(sorted_histories, 1):
                history_date = parser.parse(history['created'])
                if history_date.tzinfo is None:
                    history_date = history_date.replace(tzinfo=timezone.utc)
                
                print(f"\n{i}. {history_date.strftime('%d/%m/%Y %H:%M')}")
                
                for item in history.get('items', []):
                    if item.get('field') == 'status':
                        from_status = item.get('fromString', '').upper()
                        to_status = item.get('toString', '').upper()
                        print(f"   Status: '{from_status}' → '{to_status}'")
                        
                        # Encontrou saída do status inicial (primeira vez)
                        if from_status == initial_status and to_status != initial_status:
                            start_date = history_date
                            print(f"   ✓ MARCO: Saída do status inicial '{initial_status}'")
                            break
                    else:
                        field_name = item.get('field', 'N/A')
                        from_value = item.get('fromString', 'None')
                        to_value = item.get('toString', 'None')
                        print(f"   {field_name}: '{from_value}' → '{to_value}'")
                
                # Parar no primeiro match encontrado (mais antigo)
                if start_date:
                    break
        
        # Se não encontrou data de saída do status inicial, verificar se ainda está no status inicial
        if start_date is None:
            current_status = issue['status'].upper()
            print(f"\nNão encontrou saída do status inicial '{initial_status}'")
            print(f"Status atual: '{current_status}'")
            
            # Se ainda está no status inicial, lead time é 0 (não começou a fluir)
            if current_status == initial_status:
                print("✓ Ainda está no status inicial - Lead time = 0")
                return 0
            
            # Se não está no status inicial mas não tem histórico de saída, usar data de criação como fallback
            print("⚠ Não está mais no status inicial mas sem histórico - usando data de criação")
            start_date = parser.parse(issue['created'])
            if start_date.tzinfo is None:
                start_date = start_date.replace(tzinfo=timezone.utc)
        
        print(f"\n=== CÁLCULO DO LEAD TIME ===")
        if start_date:
            print(f"Data de início: {start_date.strftime('%d/%m/%Y %H:%M')} (saída do status inicial)")
        else:
            print("Sem data de início válida")
            return 0
        
        # Procurar pela última transição para produção ou finalização
        last_production_date = None
        
        if 'changelog' in issue and 'histories' in issue['changelog']:
            # Ordenar histórico por data para encontrar a última transição
            sorted_histories = sorted(issue['changelog']['histories'], 
                                    key=lambda h: parser.parse(h['created']))
            
            for history in sorted_histories:
                history_date = parser.parse(history['created'])
                if history_date.tzinfo is None:
                    history_date = history_date.replace(tzinfo=timezone.utc)
                
                for item in history.get('items', []):
                    if item.get('field') == 'status':
                        to_status = item.get('toString', '').upper()
                        # Incluir status de finalização (CORRIGIDO não é final para bugs)
                        if to_status in ['EM PRODUÇÃO', 'ATIVADA', 'FINALIZADO', 'FECHADO', 'TESTADA', 'CANCELADO']:
                            last_production_date = history_date
        
        if last_production_date:
            lead_time = (last_production_date - start_date).days
            print(f"Data de fim: {last_production_date.strftime('%d/%m/%Y %H:%M')} (finalização)")
            print(f"Lead Time: {lead_time} dias")
            return max(lead_time, 0)  # Evitar valores negativos
        else:
            # Se não chegou em produção, calcular até agora
            current_date = datetime.now(timezone.utc)
            lead_time = (current_date - start_date).days
            print(f"Data de fim: {current_date.strftime('%d/%m/%Y %H:%M')} (ainda não finalizada)")
            print(f"Lead Time atual: {lead_time} dias")
            return max(lead_time, 0)
            
    except Exception as e:
        print(f"Erro ao calcular lead time para {issue['key']}: {e}")
        return 0

def get_jira_issue(jira_url, token, issue_key):
    """
    Busca uma issue específica do Jira com changelog expandido
    """
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }

    search_url = f"{jira_url}/rest/api/2/issue/{issue_key}"
    params = {
        'fields': 'id,key,issuetype,status,summary,description,created,changelog',
        'expand': 'changelog'
    }

    response = requests.get(search_url, headers=headers, params=params, verify=False)

    if response.status_code == 200:
        issue_data = response.json()
        return {
            "key": issue_data['key'],
            "id": issue_data['id'],
            "issuetype": issue_data['fields']['issuetype']['name'],
            "status": issue_data['fields']['status']['name'],
            "summary": issue_data['fields']['summary'],
            "description": issue_data['fields'].get('description', ''),
            "created": issue_data['fields']['created'],
            "changelog": issue_data.get('changelog', {})
        }
    else:
        raise Exception(f"Failed to fetch issue {issue_key}: {response.status_code} - {response.text}")

# Configuração
jira_url = os.getenv("JIRA_URL")
token = os.getenv("JIRA_TOKEN")
issue_key = "PLTFAT-13437"

print(f"Buscando detalhes da issue {issue_key}...")

try:
    issue = get_jira_issue(jira_url, token, issue_key)
    print(f"\n=== ANÁLISE DETALHADA DA ISSUE {issue_key} ===")
    print(f"Resumo: {issue['summary']}")
    print(f"Data de criação: {parser.parse(issue['created']).strftime('%d/%m/%Y %H:%M')}")
    
    lead_time = calculate_lead_time(issue)
    
    print(f"\n=== RESULTADO FINAL ===")
    print(f"Lead Time da issue {issue_key}: {lead_time} dias")
    
except Exception as e:
    print(f"Erro: {e}")