#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para listar projetos disponíveis no Jira
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

def get_all_projects(jira_url, token):
    """Lista todos os projetos disponíveis"""
    
    url = f"{jira_url}/rest/api/2/project"
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

def search_projects_by_name(jira_url, token, search_term):
    """Busca projetos que contenham um termo no nome ou chave"""
    
    all_projects = get_all_projects(jira_url, token)
    
    if not all_projects:
        return []
    
    matching_projects = []
    search_lower = search_term.lower()
    
    for project in all_projects:
        project_key = project.get('key', '').lower()
        project_name = project.get('name', '').lower()
        
        if search_lower in project_key or search_lower in project_name:
            matching_projects.append(project)
    
    return matching_projects

def main():
    """Função principal"""
    jira_url, token = load_environment()
    
    if not jira_url or not token:
        print("❌ Configuração não encontrada no .env")
        return
    
    print(f"🔗 Conectando ao Jira: {jira_url}")
    print("🔍 === LISTANDO PROJETOS DISPONÍVEIS ===\n")
    
    # Listar todos os projetos
    all_projects = get_all_projects(jira_url, token)
    
    if all_projects:
        print(f"📊 Total de projetos encontrados: {len(all_projects)}\n")
        
        # Procurar por projetos que podem ser o PLTFAT
        search_terms = ['eng', 'pdp', 'brad', 'bia', 'agent']
        
        for term in search_terms:
            matching = search_projects_by_name(jira_url, token, term)
            if matching:
                print(f"🎯 Projetos contendo '{term.upper()}' ({len(matching)}):")
                for project in matching:
                    print(f"  Chave: {project['key']:<15} | Nome: {project['name']}")
                print()
        
        print("📋 === TODOS OS PROJETOS (primeiros 20) ===")
        for i, project in enumerate(all_projects[:20]):
            print(f"{i+1:2d}. {project['key']:<15} | {project['name']}")
        
        if len(all_projects) > 20:
            print(f"... e mais {len(all_projects) - 20} projetos")
    
    print(f"\n🎯 === SUGESTÕES ===")
    print("1. Identifique a chave correta do projeto na lista acima")
    print("2. Verifique com o time qual é o projeto correto")
    print("3. Atualize o código com a chave correta")

if __name__ == "__main__":
    main()