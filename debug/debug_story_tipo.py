#!/usr/bin/env python3
"""
Script para descobrir valores válidos para o campo Tipo (customfield_14103) de Story
"""

import os
import requests
from dotenv import load_dotenv
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def get_field_options(jira_url, token, field_id):
    """Obtém opções válidas para um campo customizado"""
    
    url = f"{jira_url}/rest/api/2/field/{field_id}"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    response = requests.get(url, headers=headers, verify=False)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Erro {response.status_code}: {response.text}")
        return None

def main():
    """Função principal"""
    load_dotenv()
    jira_url = os.getenv('JIRA_URL')
    token = os.getenv('JIRA_TOKEN')
    
    print("🔍 === DESCOBRINDO VALORES DO CAMPO TIPO ===")
    print("Campo: customfield_14103 (Tipo) - obrigatório para Story\n")
    
    field_info = get_field_options(jira_url, token, "customfield_14103")
    
    if field_info:
        print("📋 Informações do campo:")
        print(f"Nome: {field_info.get('name', 'N/A')}")
        print(f"Tipo: {field_info.get('schema', {}).get('type', 'N/A')}")
        
        # Tentar obter opções do campo
        schema = field_info.get('schema', {})
        if 'allowedValues' in schema:
            print(f"\n✅ Valores permitidos:")
            for value in schema['allowedValues']:
                print(f"  ID: {value.get('id', 'N/A')} | Nome: {value.get('value', 'N/A')}")
    
    # Como alternativa, vamos tentar criar uma Story com um valor genérico
    print(f"\n🧪 === TESTANDO CRIAÇÃO DE STORY ===")
    
    # Payload de teste com diferentes valores para o campo Tipo
    test_values = ["19000", "19001", "19002", "1", "2", "3"]
    
    for test_id in test_values:
        print(f"\n🔄 Testando com customfield_14103 = {test_id}")
        
        payload = {
            "fields": {
                "project": {"key": "PLTFAT"},
                "summary": f"Teste Story - Tipo {test_id}",
                "description": "Teste para descobrir valor correto do campo Tipo",
                "issuetype": {"id": "10001"},  # Story
                "customfield_14103": {"id": test_id}  # Tipo
            }
        }
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(f"{jira_url}/rest/api/2/issue", headers=headers, json=payload, verify=False)
        
        if response.status_code == 201:
            issue_data = response.json()
            print(f"✅ SUCESSO! Story criada: {issue_data['key']} com Tipo ID {test_id}")
            break
        else:
            print(f"❌ Falhou com ID {test_id}: {response.status_code}")
            if response.status_code == 400:
                error_data = response.json()
                if "customfield_14103" in error_data.get('errors', {}):
                    print(f"   Erro do campo: {error_data['errors']['customfield_14103']}")

if __name__ == "__main__":
    main()