#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste para função load_bulk_configuration()

Testa se o arquivo BulkCreate_configuration.txt é carregado e parseado corretamente
"""

import sys
import os
import json

# Adicionar diretório pai ao path para importar o módulo
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from automatizar_issues import load_bulk_configuration

def test_load_bulk_configuration():
    """Testa carregamento do arquivo de configuração de mapeamento"""
    print("="*60)
    print("TESTE: load_bulk_configuration()")
    print("="*60)
    
    try:
        config = load_bulk_configuration()
        
        if not config:
            print("❌ TESTE FALHOU - Configuração não foi carregada")
            return False
        
        print("\n✓ Configuração carregada com sucesso")
        print(f"\nVersão: {config.get('config.version', 'N/A')}")
        print(f"Encoding: {config.get('config.encoding', 'N/A')}")
        print(f"Delimiter: {config.get('config.delimiter', 'N/A')}")
        
        # Validar estrutura esperada
        assert 'config.field.mappings' in config, "config.field.mappings não encontrado"
        assert 'config.project' in config, "config.project não encontrado"
        
        field_mappings = config['config.field.mappings']
        project_config = config['config.project']
        
        print(f"\n✓ Campo de mapeamentos encontrado: {len(field_mappings)} campos")
        print("\nCampos mapeados:")
        for csv_field, jira_mapping in field_mappings.items():
            jira_field = jira_mapping.get('jira.field', jira_mapping.get('existing.custom.field'))
            print(f"  - {csv_field} → {jira_field}")
        
        print(f"\n✓ Configuração do projeto:")
        print(f"  - Project Key: {project_config.get('project.key')}")
        print(f"  - Project Name: {project_config.get('project.name')}")
        print(f"  - Project Lead: {project_config.get('project.lead')}")
        
        # Validações críticas
        assert project_config.get('project.key'), "Project key não pode ser vazio"
        assert 'Summary' in field_mappings, "Campo Summary deve estar mapeado"
        assert 'Issue Type' in field_mappings, "Campo Issue Type deve estar mapeado"
        
        print("\n✅ TESTE PASSOU - Configuração carregada e validada corretamente")
        return True
        
    except Exception as e:
        print(f"\n❌ TESTE FALHOU - Erro: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = test_load_bulk_configuration()
    sys.exit(0 if success else 1)
