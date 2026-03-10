#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste de conexão com API do Jira

Valida se as credenciais estão corretas e se a API está acessível
"""

import sys
import os
import requests
from urllib3.exceptions import InsecureRequestWarning

# Suprimir avisos de SSL
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Adicionar diretório pai ao path para importar o módulo
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from automatizar_issues import load_environment

def test_jira_connection():
    """Testa conexão com API do Jira"""
    print("="*60)
    print("TESTE: Conexão com API do Jira")
    print("="*60)
    
    try:
        # Carregar credenciais
        jira_url, jira_token, jira_project, team_name, folder_path = load_environment()
        
        print("\n✓ Credenciais carregadas")
        print(f"  URL: {jira_url}")
        print(f"  Projeto: {jira_project}")
        
        # Testar autenticação - buscar informação do projeto
        headers = {
            'Authorization': f'Bearer {jira_token}',
            'Content-Type': 'application/json'
        }
        
        print(f"\n📡 Testando conexão com {jira_url}...")
        
        # Endpoint para buscar informações do projeto
        project_url = f"{jira_url}/rest/api/2/project/{jira_project}"
        
        response = requests.get(project_url, headers=headers, verify=False, timeout=10)
        
        if response.status_code == 200:
            project_data = response.json()
            print("\n✅ CONEXÃO ESTABELECIDA COM SUCESSO")
            print(f"\n📊 Informações do Projeto:")
            print(f"  - Key: {project_data.get('key')}")
            print(f"  - Name: {project_data.get('name')}")
            print(f"  - ID: {project_data.get('id')}")
            print(f"  - Lead: {project_data.get('lead', {}).get('displayName', 'N/A')}")
            
            # Testar se pode criar issues
            issue_types_url = f"{jira_url}/rest/api/2/project/{jira_project}/statuses"
            response_types = requests.get(issue_types_url, headers=headers, verify=False, timeout=10)
            
            if response_types.status_code == 200:
                issue_types = response_types.json()
                print(f"\n  - Issue Types disponíveis: {len(issue_types)}")
                for issue_type in issue_types[:5]:  # Mostrar primeiros 5
                    print(f"    • {issue_type.get('name', 'N/A')}")
            
            print("\n✅ TESTE PASSOU - API do Jira está acessível e funcionando")
            return True
            
        elif response.status_code == 401:
            print("\n❌ ERRO DE AUTENTICAÇÃO")
            print("  Token inválido ou expirado")
            return False
            
        elif response.status_code == 404:
            print(f"\n❌ PROJETO NÃO ENCONTRADO")
            print(f"  O projeto '{jira_project}' não existe ou você não tem acesso")
            return False
            
        else:
            print(f"\n❌ ERRO HTTP {response.status_code}")
            print(f"  Resposta: {response.text[:200]}")
            return False
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERRO DE CONEXÃO")
        print("  Não foi possível conectar ao servidor Jira")
        print("  Verifique a URL e sua conexão de rede")
        return False
        
    except requests.exceptions.Timeout:
        print("\n❌ TIMEOUT")
        print("  Servidor Jira não respondeu a tempo")
        return False
        
    except Exception as e:
        print(f"\n❌ TESTE FALHOU - Erro: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = test_jira_connection()
    sys.exit(0 if success else 1)
