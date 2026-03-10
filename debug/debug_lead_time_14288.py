#!/usr/bin/env python3
"""
Script de teste específico para validar o cálculo do lead time da issue PLTFAT-14288
"""

import os
import requests
from dotenv import load_dotenv
from datetime import datetime, timezone
from dateutil import parser

# Carregar variáveis do arquivo .env
load_dotenv()

def get_specific_issue(jira_url, token, issue_key):
    """
    Busca uma issue específica do Jira com histórico completo
    """
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }

    issue_url = f"{jira_url}/rest/api/2/issue/{issue_key}"
    params = {
        'expand': 'changelog'
    }

    response = requests.get(issue_url, headers=headers, params=params, verify=False)

    if response.status_code == 200:
        issue_data = response.json()
        return {
            "key": issue_data['key'],
            "id": issue_data['id'],
            "issuetype": issue_data['fields']['issuetype']['name'],
            "status": issue_data['fields']['status']['name'],
            "summary": issue_data['fields']['summary'],
            "created": issue_data['fields']['created'],
            "changelog": issue_data.get('changelog', {})
        }
    else:
        print(f"Erro ao buscar issue {issue_key}: {response.status_code} - {response.text}")
        return None

def test_lead_time_calculation(issue):
    """
    Testa o cálculo de lead time para uma issue específica
    """
    try:
        print(f"\n=== ANÁLISE DETALHADA DA ISSUE {issue['key']} ===")
        print(f"Tipo: {issue['issuetype']}")
        print(f"Status atual: {issue['status']}")
        print(f"Resumo: {issue['summary']}")
        
        created_date = parser.parse(issue['created'])
        print(f"Data de criação: {created_date.strftime('%d/%m/%Y %H:%M')}")
        
        # Definir status inicial baseado no tipo da issue
        issue_type = issue['issuetype'].upper()
        if issue_type == 'BUG':
            initial_status = 'NOVO'
        elif issue_type == 'STORY':
            initial_status = 'PRODUCT BACKLOG'
        elif issue_type in ['TECH SOLUTION', 'INCIDENTE']:
            initial_status = 'BACKLOG'
        else:
            initial_status = None
        
        print(f"Status inicial mapeado para tipo '{issue_type}': {initial_status}")
        
        # Analisar histórico completo
        if 'changelog' in issue and 'histories' in issue['changelog']:
            print(f"\nHistórico de mudanças ({len(issue['changelog']['histories'])} entradas):")
            
            # Ordenar histórico por data
            sorted_histories = sorted(issue['changelog']['histories'], 
                                    key=lambda h: parser.parse(h['created']))
            
            start_date = None
            last_production_date = None
            
            for i, history in enumerate(sorted_histories):
                history_date = parser.parse(history['created'])
                if history_date.tzinfo is None:
                    history_date = history_date.replace(tzinfo=timezone.utc)
                
                print(f"\n{i+1}. {history_date.strftime('%d/%m/%Y %H:%M')}")
                
                for item in history.get('items', []):
                    if item.get('field') == 'status':
                        from_status = item.get('fromString', '')
                        to_status = item.get('toString', '')
                        print(f"   Status: '{from_status}' → '{to_status}'")
                        
                        # Verificar saída do status inicial
                        if initial_status and from_status.upper() == initial_status and start_date is None:
                            start_date = history_date
                            print(f"   ✓ MARCO: Saída do status inicial '{initial_status}'")
                        
                        # Verificar chegada em produção/finalização (CORRIGIDO não é final para bugs)
                        if to_status.upper() in ['EM PRODUÇÃO', 'ATIVADA', 'FINALIZADO', 'FECHADO', 'TESTADA', 'CANCELADO']:
                            last_production_date = history_date
                            print(f"   ✓ MARCO: Chegou em status de finalização '{to_status}'")
                    else:
                        field_name = item.get('field', 'unknown')
                        from_value = item.get('fromString', item.get('from', ''))
                        to_value = item.get('toString', item.get('to', ''))
                        print(f"   {field_name}: '{from_value}' → '{to_value}'")
            
            # Calcular lead time
            print(f"\n=== CÁLCULO DO LEAD TIME ===")
            
            if start_date is None:
                start_date = created_date
                if start_date.tzinfo is None:
                    start_date = start_date.replace(tzinfo=timezone.utc)
                print(f"Data de início: {start_date.strftime('%d/%m/%Y %H:%M')} (data de criação - fallback)")
            else:
                print(f"Data de início: {start_date.strftime('%d/%m/%Y %H:%M')} (saída do status inicial)")
            
            if last_production_date:
                print(f"Data de fim: {last_production_date.strftime('%d/%m/%Y %H:%M')} (chegada em produção/finalização)")
                lead_time = (last_production_date - start_date).days
                print(f"Lead Time: {lead_time} dias")
            else:
                current_date = datetime.now(timezone.utc)
                print(f"Data de fim: {current_date.strftime('%d/%m/%Y %H:%M')} (ainda não finalizada)")
                lead_time = (current_date - start_date).days
                print(f"Lead Time atual: {lead_time} dias")
            
            return max(lead_time, 0)
        else:
            print("Nenhum histórico de mudanças encontrado.")
            return 0
            
    except Exception as e:
        print(f"Erro na análise: {e}")
        return 0

if __name__ == "__main__":
    # Configurações do Jira
    jira_url = os.getenv("JIRA_URL")
    jira_token = os.getenv("JIRA_TOKEN")
    
    if not jira_url or not jira_token:
        print("Erro: JIRA_URL e JIRA_TOKEN devem estar configurados no arquivo .env")
        exit(1)
    
    # Testar issue específica
    issue_key = "PLTFAT-14288"
    
    print(f"Buscando detalhes da issue {issue_key}...")
    issue = get_specific_issue(jira_url, jira_token, issue_key)
    
    if issue:
        lead_time = test_lead_time_calculation(issue)
        print(f"\n=== RESULTADO FINAL ===")
        print(f"Lead Time da issue {issue_key}: {lead_time} dias")
    else:
        print(f"Não foi possível buscar a issue {issue_key}")