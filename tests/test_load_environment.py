#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste para função load_environment()

Testa se as variáveis de ambiente são carregadas corretamente do arquivo .env
"""

import sys
import os

# Adicionar diretório pai ao path para importar o módulo
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from automatizar_issues import load_environment

def test_load_environment():
    """Testa carregamento de variáveis do .env"""
    print("="*60)
    print("TESTE: load_environment()")
    print("="*60)
    
    try:
        jira_url, jira_token, jira_project, team_name, folder_path = load_environment()
        
        print("\n✓ Variáveis carregadas com sucesso:")
        print(f"  - JIRA_URL: {jira_url}")
        print(f"  - JIRA_TOKEN: {'*' * 20} (oculto por segurança)")
        print(f"  - JIRA_PROJECT: {jira_project}")
        print(f"  - TEAM_NAME: {team_name}")
        print(f"  - folder_path: {folder_path}")
        
        # Validações
        assert jira_url, "JIRA_URL não pode ser vazio"
        assert jira_token, "JIRA_TOKEN não pode ser vazio"
        assert jira_project, "JIRA_PROJECT não pode ser vazio"
        assert team_name, "TEAM_NAME não pode ser vazio"
        assert folder_path, "folder_path não pode ser vazio"
        
        print("\n✅ TESTE PASSOU - Todas as variáveis foram carregadas corretamente")
        return True
        
    except Exception as e:
        print(f"\n❌ TESTE FALHOU - Erro: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_load_environment()
    sys.exit(0 if success else 1)
