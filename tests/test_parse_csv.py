#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste para função parse_csv_file()

Testa se o CSV é parseado e mapeado corretamente para estrutura do Jira
"""

import sys
import os
import json

# Adicionar diretório pai ao path para importar o módulo
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from automatizar_issues import load_bulk_configuration, parse_csv_file

def test_parse_csv():
    """Testa parsing e mapeamento de arquivo CSV"""
    print("="*60)
    print("TESTE: parse_csv_file()")
    print("="*60)
    
    try:
        # Carregar configuração primeiro
        config = load_bulk_configuration()
        if not config:
            print("❌ Não foi possível carregar configuração")
            return False
        
        print("\n✓ Configuração carregada")
        
        # Procurar arquivo CSV na pasta issues
        issues_folder = os.path.join('..', 'issues') if os.path.exists('../issues') else 'issues'
        
        if not os.path.exists(issues_folder):
            print(f"❌ Pasta {issues_folder} não encontrada")
            return False
        
        csv_files = [f for f in os.listdir(issues_folder) 
                     if f.endswith('.csv') and os.path.isfile(os.path.join(issues_folder, f))]
        
        if not csv_files:
            print(f"❌ Nenhum arquivo CSV encontrado em {issues_folder}")
            return False
        
        # Testar com o primeiro arquivo CSV encontrado
        csv_file = csv_files[0]
        csv_path = os.path.join(issues_folder, csv_file)
        
        print(f"\n✓ Testando com arquivo: {csv_file}")
        print(f"  Caminho: {csv_path}")
        
        # Parsear CSV
        issues_data = parse_csv_file(csv_path, config)
        
        if not issues_data:
            print("❌ Nenhuma issue foi parseada")
            return False
        
        print(f"\n✓ Issues parseadas: {len(issues_data)}")
        
        # Mostrar primeiras 3 issues como exemplo
        print("\n📋 Exemplos de issues parseadas:")
        for i, issue in enumerate(issues_data[:3], 1):
            print(f"\n  Issue {i}:")
            print(f"    Project: {issue.get('project', {}).get('key', 'N/A')}")
            print(f"    Type: {issue.get('issuetype', {}).get('name', 'N/A')}")
            print(f"    Summary: {issue.get('summary', 'N/A')[:60]}...")
            
            # Verificar campos customizados
            custom_fields = {k: v for k, v in issue.items() if k.startswith('customfield_')}
            if custom_fields:
                print(f"    Custom Fields: {len(custom_fields)}")
                for field, value in custom_fields.items():
                    print(f"      - {field}: {value}")
        
        # Validações
        for issue in issues_data:
            assert 'project' in issue, "Campo 'project' ausente"
            assert 'issuetype' in issue, "Campo 'issuetype' ausente"
            assert 'summary' in issue, "Campo 'summary' ausente"
        
        print(f"\n✅ TESTE PASSOU - {len(issues_data)} issues parseadas e validadas corretamente")
        return True
        
    except Exception as e:
        print(f"\n❌ TESTE FALHOU - Erro: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = test_parse_csv()
    sys.exit(0 if success else 1)
