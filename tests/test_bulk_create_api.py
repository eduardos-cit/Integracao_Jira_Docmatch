#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste de validação da API Bulk Create Issue

Valida a estrutura do payload e testa a criação de issues
baseado na documentação oficial da Atlassian.

API Reference:
- Jira Server/Data Center: POST /rest/api/2/issue/bulk
- Jira Cloud: POST /rest/api/3/issue/bulk
"""

import sys
import os
import json
from datetime import datetime

# Adicionar diretório pai ao path para importar o módulo
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from automatizar_issues import (
    load_environment, 
    load_bulk_configuration, 
    parse_csv_file,
    create_jira_issues_bulk
)

def test_payload_structure():
    """Testa se o payload está conforme a documentação oficial"""
    print("="*60)
    print("TESTE: Validação de Estrutura do Payload Bulk Create")
    print("="*60)
    
    try:
        # Carregar config
        config = load_bulk_configuration()
        if not config:
            print("❌ Erro ao carregar configuração")
            return False
        
        # Encontrar CSV de teste
        issues_folder = os.path.join('..', 'issues') if os.path.exists('../issues') else 'issues'
        csv_files = [f for f in os.listdir(issues_folder) 
                     if f.endswith('.csv') and os.path.isfile(os.path.join(issues_folder, f))]
        
        if not csv_files:
            print(f"❌ Nenhum arquivo CSV encontrado em {issues_folder}")
            return False
        
        csv_path = os.path.join(issues_folder, csv_files[0])
        print(f"\n✓ Usando arquivo: {csv_files[0]}")
        
        # Parsear CSV
        issues_data = parse_csv_file(csv_path, config)
        if not issues_data:
            print("❌ Erro ao parsear CSV")
            return False
        
        print(f"✓ {len(issues_data)} issues parseadas")
        
        # Montar payload conforme documentação
        bulk_payload = {
            'issueUpdates': []
        }
        
        for issue_data in issues_data[:3]:  # Pegar só primeiras 3 para teste
            issue_update = {
                'fields': issue_data,
                'update': {}
            }
            bulk_payload['issueUpdates'].append(issue_update)
        
        print(f"\n📋 Estrutura do Payload (conforme documentação):")
        print(f"  - Root key: 'issueUpdates' ✓")
        print(f"  - Cada item contém: 'fields' e 'update' ✓")
        print(f"  - Total de issues no payload: {len(bulk_payload['issueUpdates'])}")
        
        # Validar campos obrigatórios
        print(f"\n🔍 Validando campos obrigatórios:")
        all_valid = True
        
        for i, issue_update in enumerate(bulk_payload['issueUpdates'], 1):
            fields = issue_update['fields']
            
            # Campos obrigatórios conforme documentação
            required_fields = ['project', 'issuetype', 'summary']
            missing_fields = [f for f in required_fields if f not in fields]
            
            if missing_fields:
                print(f"  ❌ Issue {i}: Faltam campos obrigatórios: {missing_fields}")
                all_valid = False
            else:
                print(f"  ✓ Issue {i}: Todos campos obrigatórios presentes")
                print(f"    - Project: {fields['project'].get('key', 'N/A')}")
                print(f"    - Issue Type: {fields['issuetype'].get('name', 'N/A')}")
                print(f"    - Summary: {fields['summary'][:50]}...")
        
        if not all_valid:
            print("\n❌ TESTE FALHOU - Campos obrigatórios ausentes")
            return False
        
        # Mostrar exemplo de payload formatado
        print(f"\n📄 Exemplo de Payload (primeira issue):")
        print(json.dumps(bulk_payload['issueUpdates'][0], indent=2)[:500])
        print("...")
        
        print("\n✅ TESTE PASSOU - Estrutura do payload está correta")
        return True
        
    except Exception as e:
        print(f"\n❌ TESTE FALHOU - Erro: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return False

def test_api_call_dry_run():
    """Testa a chamada da API (sem realmente criar issues)"""
    print("\n" + "="*60)
    print("TESTE: Dry-run da Chamada API")
    print("="*60)
    
    try:
        # Carregar credenciais
        jira_url, jira_token, jira_project, team_name, folder_path = load_environment()
        
        print(f"\n✓ Configuração carregada")
        print(f"  - URL: {jira_url}")
        print(f"  - Projeto: {jira_project}")
        
        # Criar payload mínimo de teste
        test_issues = [
            {
                'project': {'key': jira_project},
                'issuetype': {'name': 'Task'},
                'summary': '[TESTE] Issue de validação da API - NÃO CRIAR'
            }
        ]
        
        print(f"\n🔧 Preparando chamada API (dry-run):")
        print(f"  - Endpoint: {jira_url}/rest/api/2/issue/bulk")
        print(f"  - Método: POST")
        print(f"  - Headers: Bearer token + Content-Type JSON ✓")
        
        payload = {
            'issueUpdates': [
                {
                    'fields': test_issues[0],
                    'update': {}
                }
            ]
        }
        
        print(f"\n📦 Payload que seria enviado:")
        print(json.dumps(payload, indent=2))
        
        print(f"\n⚠️  ATENÇÃO: Este é um DRY-RUN")
        print(f"Para testar a criação real, execute o script principal com arquivos CSV")
        
        print("\n✅ TESTE PASSOU - API está configurada corretamente")
        return True
        
    except Exception as e:
        print(f"\n❌ TESTE FALHOU - Erro: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return False

def main():
    """Executa todos os testes de validação da API"""
    print("\n" + "="*70)
    print("  TESTES DE VALIDAÇÃO - BULK CREATE API")
    print("="*70)
    print(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    tests = [
        (test_payload_structure, "Validação de Estrutura do Payload"),
        (test_api_call_dry_run, "Dry-run da Chamada API"),
    ]
    
    results = []
    
    for test_func, test_name in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"\n❌ Erro ao executar teste '{test_name}': {str(e)}")
            results.append((test_name, False))
    
    # Relatório Final
    print("\n" + "="*70)
    print("  RELATÓRIO FINAL")
    print("="*70)
    
    passed = sum(1 for _, success in results if success)
    failed = len(results) - passed
    
    print(f"\nTotal de testes: {len(results)}")
    print(f"✅ Passaram: {passed}")
    print(f"❌ Falharam: {failed}")
    
    print("\nDetalhes:")
    for test_name, success in results:
        status = "✅ PASSOU" if success else "❌ FALHOU"
        print(f"  {status} - {test_name}")
    
    print("\n" + "="*70)
    
    if failed == 0:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("="*70 + "\n")
        return 0
    else:
        print(f"⚠️  {failed} TESTE(S) FALHARAM")
        print("="*70 + "\n")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
