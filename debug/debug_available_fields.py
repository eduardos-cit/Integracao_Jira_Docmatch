#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para descobrir campos disponíveis para criação de Bug e Story no Jira
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

def get_create_meta(jira_url, token, project_key, issue_type_id):
    """Obtém metadados de criação para um tipo de issue específico"""
    
    url = f"{jira_url}/rest/api/2/issue/createmeta"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    params = {
        'projectKeys': project_key,
        'issuetypeIds': issue_type_id,
        'expand': 'projects.issuetypes.fields'
    }
    
    response = requests.get(url, headers=headers, params=params, verify=False)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Erro {response.status_code}: {response.text}")
        return None

def analyze_available_fields(jira_url, token):
    """Analisa campos disponíveis para Bug e Story"""
    
    project_key = "PLTFAT"
    
    # IDs dos tipos de issue
    bug_id = "10102"
    story_id = "10001"
    
    print("🔍 === ANALISANDO CAMPOS DISPONÍVEIS ===\n")
    
    # Analisar Bug
    print("🐛 Campos disponíveis para BUG (ID: 10102):")
    bug_meta = get_create_meta(jira_url, token, project_key, bug_id)
    
    if bug_meta and bug_meta.get('projects'):
        project = bug_meta['projects'][0]
        if project.get('issuetypes'):
            bug_issue_type = project['issuetypes'][0]
            bug_fields = bug_issue_type.get('fields', {})
            
            print(f"📋 Total de campos disponíveis: {len(bug_fields)}")
            print("\n📝 Campos principais:")
            
            important_fields = ['summary', 'description', 'priority', 'labels', 'assignee']
            for field in important_fields:
                if field in bug_fields:
                    field_info = bug_fields[field]
                    required = "✅ OBRIGATÓRIO" if field_info.get('required') else "⚪ OPCIONAL"
                    print(f"  {field}: {required}")
                else:
                    print(f"  {field}: ❌ NÃO DISPONÍVEL")
            
            print("\n🔧 Campos customizados disponíveis:")
            for field_id, field_info in bug_fields.items():
                if field_id.startswith('customfield_'):
                    required = "✅ OBRIG." if field_info.get('required') else "⚪ OPC."
                    name = field_info.get('name', 'Nome não disponível')
                    print(f"  {field_id}: {name} ({required})")
    
    print("\n" + "="*60 + "\n")
    
    # Analisar Story
    print("📖 Campos disponíveis para STORY (ID: 10001):")
    story_meta = get_create_meta(jira_url, token, project_key, story_id)
    
    if story_meta and story_meta.get('projects'):
        project = story_meta['projects'][0]
        if project.get('issuetypes'):
            story_issue_type = project['issuetypes'][0]
            story_fields = story_issue_type.get('fields', {})
            
            print(f"📋 Total de campos disponíveis: {len(story_fields)}")
            print("\n📝 Campos principais:")
            
            important_fields = ['summary', 'description', 'priority', 'labels', 'assignee']
            for field in important_fields:
                if field in story_fields:
                    field_info = story_fields[field]
                    required = "✅ OBRIGATÓRIO" if field_info.get('required') else "⚪ OPCIONAL"
                    print(f"  {field}: {required}")
                else:
                    print(f"  {field}: ❌ NÃO DISPONÍVEL")
            
            print("\n🔧 Campos customizados disponíveis:")
            for field_id, field_info in story_fields.items():
                if field_id.startswith('customfield_'):
                    required = "✅ OBRIG." if field_info.get('required') else "⚪ OPC."
                    name = field_info.get('name', 'Nome não disponível')
                    print(f"  {field_id}: {name} ({required})")

def main():
    """Função principal"""
    jira_url, token = load_environment()
    
    if not jira_url or not token:
        print("❌ Configuração não encontrada no .env")
        return
    
    print(f"🔗 Conectando ao Jira: {jira_url}")
    analyze_available_fields(jira_url, token)
    
    print("\n🎯 === PRÓXIMOS PASSOS ===")
    print("1. Use apenas campos que aparecem como disponíveis acima")
    print("2. Priorize campos obrigatórios (✅ OBRIGATÓRIO)")
    print("3. Teste com payload mínimo primeiro")

if __name__ == "__main__":
    main()