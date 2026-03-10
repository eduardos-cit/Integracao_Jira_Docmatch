#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para descobrir tipos de issue e IDs corretos no projeto PLTFAT
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

def get_project_info(jira_url, token, project_key):
    """Obtém informações do projeto incluindo tipos de issue"""
    
    url = f"{jira_url}/rest/api/2/project/{project_key}"
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

def get_create_meta_simple(jira_url, token, project_key):
    """Obtém metadados simples de criação"""
    
    url = f"{jira_url}/rest/api/2/issue/createmeta"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    params = {
        'projectKeys': project_key
    }
    
    response = requests.get(url, headers=headers, params=params, verify=False)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Erro {response.status_code}: {response.text}")
        return None

def main():
    """Função principal"""
    jira_url, token = load_environment()
    
    if not jira_url or not token:
        print("❌ Configuração não encontrada no .env")
        return
    
    project_key = "PLTFAT"
    
    print(f"🔗 Conectando ao Jira: {jira_url}")
    print(f"📋 Analisando projeto: {project_key}\n")
    
    # Obter informações básicas do projeto
    print("📊 === INFORMAÇÕES DO PROJETO ===")
    project_info = get_project_info(jira_url, token, project_key)
    
    if project_info:
        print(f"Nome: {project_info.get('name', 'N/A')}")
        print(f"Chave: {project_info.get('key', 'N/A')}")
        
        issue_types = project_info.get('issueTypes', [])
        print(f"\n🏷️ Tipos de Issue disponíveis ({len(issue_types)}):")
        
        for issue_type in issue_types:
            print(f"  ID: {issue_type['id']:<6} | Nome: {issue_type['name']:<20} | Descrição: {issue_type.get('description', 'N/A')}")
    
    print("\n" + "="*80 + "\n")
    
    # Obter metadados de criação
    print("🔍 === METADADOS DE CRIAÇÃO ===")
    create_meta = get_create_meta_simple(jira_url, token, project_key)
    
    if create_meta and create_meta.get('projects'):
        project = create_meta['projects'][0]
        issue_types = project.get('issuetypes', [])
        
        print(f"Tipos de issue que podem ser criados ({len(issue_types)}):")
        
        for issue_type in issue_types:
            print(f"\n📝 {issue_type['name']} (ID: {issue_type['id']})")
            print(f"   Descrição: {issue_type.get('description', 'N/A')}")
            
            # Se tiver campos, mostrar alguns principais
            fields = issue_type.get('fields', {})
            if fields:
                required_fields = [f for f, info in fields.items() if info.get('required')]
                optional_fields = [f for f, info in fields.items() if not info.get('required')]
                
                print(f"   Campos obrigatórios: {len(required_fields)}")
                print(f"   Campos opcionais: {len(optional_fields)}")
                
                # Mostrar campos básicos importantes
                basic_fields = ['summary', 'description', 'priority', 'assignee', 'labels']
                available_basic = [f for f in basic_fields if f in fields]
                print(f"   Campos básicos disponíveis: {', '.join(available_basic) if available_basic else 'Nenhum'}")

if __name__ == "__main__":
    main()