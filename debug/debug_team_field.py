#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para descobrir o ID do campo Team no Jira
"""

import os
import requests
from dotenv import load_dotenv
from urllib3.exceptions import InsecureRequestWarning

# Suprimir avisos de SSL
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def load_environment():
    """Carrega variáveis de ambiente"""
    load_dotenv()
    return os.getenv('JIRA_URL'), os.getenv('JIRA_TOKEN')

def get_issue_details(jira_url, token, issue_key):
    """
    Busca todos os campos de uma issue específica para encontrar o Team
    """
    try:
        issue_url = f"{jira_url}/rest/api/2/issue/{issue_key}"
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(issue_url, headers=headers, verify=False)
        
        if response.status_code == 200:
            issue_data = response.json()
            
            print(f"=== ISSUE {issue_key} ===")
            print(f"Summary: {issue_data['fields']['summary']}")
            print(f"Status: {issue_data['fields']['status']['name']}")
            print("\n=== CAMPOS CUSTOMFIELD ===")
            
            # Procurar por campos customfield que podem ser Team
            for field_key, field_value in issue_data['fields'].items():
                if field_key.startswith('customfield_'):
                    if field_value is not None:
                        # Se é um dict com name ou value, mostrar
                        if isinstance(field_value, dict):
                            if 'value' in field_value:
                                print(f"{field_key}: {field_value['value']}")
                            elif 'name' in field_value:
                                print(f"{field_key}: {field_value['name']}")
                            else:
                                print(f"{field_key}: {field_value}")
                        elif isinstance(field_value, str):
                            # Se contém "docmatch" pode ser o Team
                            if 'docmatch' in field_value.lower():
                                print(f"🎯 {field_key}: {field_value} (POSSÍVEL TEAM)")
                            else:
                                print(f"{field_key}: {field_value}")
                        else:
                            print(f"{field_key}: {field_value}")
            
            return True
        else:
            print(f"Erro: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"Erro ao buscar issue: {str(e)}")
        return False

def get_field_metadata(jira_url, token):
    """
    Busca metadados dos campos para encontrar o campo Team
    """
    try:
        fields_url = f"{jira_url}/rest/api/2/field"
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(fields_url, headers=headers, verify=False)
        
        if response.status_code == 200:
            fields_data = response.json()
            
            print("\n=== CAMPOS QUE CONTÊM 'TEAM' ===")
            for field in fields_data:
                field_name = field.get('name', '').lower()
                if 'team' in field_name:
                    print(f"🎯 {field['id']}: {field['name']} (type: {field.get('schema', {}).get('type', 'N/A')})")
            
            return True
        else:
            print(f"Erro: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"Erro ao buscar campos: {str(e)}")
        return False

def main():
    """Função principal"""
    jira_url, jira_token = load_environment()
    
    if not jira_url or not jira_token:
        print("❌ Variáveis JIRA_URL e JIRA_TOKEN devem estar definidas no .env")
        return
    
    print(f"🔍 Buscando campo Team no Jira: {jira_url}")
    
    # Buscar metadados dos campos
    print("\n1. Buscando metadados dos campos...")
    get_field_metadata(jira_url, jira_token)
    
    # Buscar issue específica conhecida do DocMatch
    print("\n2. Analisando issue específica...")
    get_issue_details(jira_url, jira_token, "PLTFAT-12232")

if __name__ == "__main__":
    main()