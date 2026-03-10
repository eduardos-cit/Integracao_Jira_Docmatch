#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para analisar issues específicas e descobrir campos utilizados
"""

import os
import json
import requests
from dotenv import load_dotenv
from urllib3.exceptions import InsecureRequestWarning

# Suprimir avisos SSL
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def load_environment():
    """Carrega configuração do .env"""
    load_dotenv()
    return os.getenv('JIRA_URL'), os.getenv('JIRA_TOKEN')

def get_issue_details(jira_url, token, issue_key):
    """Obtém detalhes completos de uma issue"""
    
    url = f"{jira_url}/rest/api/2/issue/{issue_key}"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    response = requests.get(url, headers=headers, verify=False)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Erro ao buscar {issue_key}: {response.status_code} - {response.text}")
        return None

def analyze_issue_fields(issue_data, issue_type_name):
    """Analisa os campos de uma issue"""
    
    if not issue_data:
        return
    
    fields = issue_data.get('fields', {})
    issue_key = issue_data.get('key', 'N/A')
    
    print(f"\n🔍 === ANÁLISE DA {issue_type_name.upper()}: {issue_key} ===")
    print(f"Tipo: {fields.get('issuetype', {}).get('name', 'N/A')} (ID: {fields.get('issuetype', {}).get('id', 'N/A')})")
    print(f"Status: {fields.get('status', {}).get('name', 'N/A')}")
    print(f"Projeto: {fields.get('project', {}).get('key', 'N/A')}")
    
    print(f"\n📋 CAMPOS PRINCIPAIS:")
    print(f"  Summary: {fields.get('summary', 'N/A')[:80]}...")
    print(f"  Description: {'✅ Preenchido' if fields.get('description') else '❌ Vazio'}")
    print(f"  Priority: {fields.get('priority', {}).get('name', 'N/A')} (ID: {fields.get('priority', {}).get('id', 'N/A')})")
    print(f"  Labels: {fields.get('labels', [])}")
    print(f"  Assignee: {fields.get('assignee', {}).get('displayName', 'Unassigned') if fields.get('assignee') else 'Unassigned'}")
    
    print(f"\n🔧 CAMPOS CUSTOMIZADOS PREENCHIDOS:")
    custom_fields = {k: v for k, v in fields.items() if k.startswith('customfield_') and v is not None}
    
    for field_id, value in custom_fields.items():
        # Mostrar valor de forma mais legível
        if isinstance(value, dict):
            if 'name' in value:
                display_value = value['name']
            elif 'value' in value:
                display_value = value['value']
            elif 'displayName' in value:
                display_value = value['displayName']
            else:
                display_value = str(value)[:50]
        elif isinstance(value, list):
            if value and isinstance(value[0], dict):
                display_value = [item.get('name', item.get('value', str(item))) for item in value[:3]]
                if len(value) > 3:
                    display_value.append('...')
            else:
                display_value = value[:3]
        else:
            display_value = str(value)[:50]
        
        print(f"  {field_id}: {display_value}")
    
    return custom_fields

def create_minimal_payload_suggestion(story_fields, imp_fields):
    """Cria sugestão de payload mínimo baseado nas issues analisadas"""
    
    print(f"\n🎯 === SUGESTÃO DE PAYLOAD MÍNIMO ===")
    
    # Campos comuns entre Story e Sub-Imp
    common_fields = set(story_fields.keys()) & set(imp_fields.keys())
    
    print(f"\n📖 PAYLOAD PARA STORY:")
    print(f'  "project": {{"key": "PLTFAT"}}')
    print(f'  "summary": "Título da story"')
    print(f'  "description": "Descrição da story"')
    print(f'  "issuetype": {{"id": "10001"}}')  # Assumindo Story
    
    if common_fields:
        print(f"  # Campos customizados comuns:")
        for field in sorted(common_fields):
            print(f'  "{field}": // Verificar valor correto')
    
    print(f"\n🐛 PAYLOAD PARA SUB-IMP:")
    print(f'  "project": {{"key": "PLTFAT"}}')
    print(f'  "summary": "Título do sub-imp"')
    print(f'  "description": "Descrição do sub-imp"')
    print(f'  "issuetype": {{"id": "10102"}}')  # Assumindo Sub-Imp
    
    if imp_fields:
        print(f"  # Campos customizados específicos do Sub-Imp:")
        for field in sorted(imp_fields.keys()):
            if field not in common_fields:
                print(f'  "{field}": // Verificar valor correto')

def main():
    """Função principal"""
    jira_url, token = load_environment()
    
    if not jira_url or not token:
        print("❌ Configuração não encontrada no .env")
        return
    
    print(f"🔗 Conectando ao Jira: {jira_url}")
    
    # Issues para analisar
    story_key = "PLTFAT-12247"
    imp_key = "PLTFAT-12339"
    
    # Analisar Story
    story_data = get_issue_details(jira_url, token, story_key)
    story_fields = analyze_issue_fields(story_data, "STORY") or {}
    
    # Analisar Sub-Imp  
    imp_data = get_issue_details(jira_url, token, imp_key)
    imp_fields = analyze_issue_fields(imp_data, "Sub-Imp") or {}
    
    # Criar sugestão de payload
    create_minimal_payload_suggestion(story_fields, imp_fields)
    
    print(f"\n📝 === PRÓXIMOS PASSOS ===")
    print("1. Use apenas os campos que aparecem preenchidos nas issues acima")
    print("2. Teste primeiro com um payload super simples (só project, issuetype, summary)")
    print("3. Adicione campos gradualmente até funcionar")
    print("4. Campos como priority e labels podem não estar na tela de criação")

if __name__ == "__main__":
    main()