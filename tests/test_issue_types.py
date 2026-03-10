#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste para validar a diferenciação entre Bug e Story
"""

def determine_issue_type(tipo_solicitacao):
    """Função copiada do script principal para teste"""
    tipo_normalizado = tipo_solicitacao.lower().strip()
    
    if 'sugerir melhorias' in tipo_normalizado or 'novas funcionalidades' in tipo_normalizado:
        return {'id': '10001', 'name': 'Story', 'labels': ['STORY_BEX_AGENTIX']}
    elif 'solicitar suporte' in tipo_normalizado or 'reportar bug' in tipo_normalizado:
        return {'id': '10102', 'name': 'Bug', 'labels': ['BUG_PROD_AGENTIX']}
    else:
        return {'id': '10102', 'name': 'Bug', 'labels': ['BUG_PROD_AGENTIX']}

def test_issue_type_mapping():
    """Testa o mapeamento de tipos de solicitação"""
    test_cases = [
        ("Sugerir melhorias e novas funcionalidades.", "Story"),
        ("Solicitar suporte.", "Bug"),
        ("Reportar bug", "Bug"),
        ("Solicitar suporte técnico", "Bug"),
        ("Outro tipo qualquer", "Bug"),  # Padrão
        ("", "Bug")  # Vazio
    ]
    
    print("=== TESTE DE MAPEAMENTO DE TIPOS ===\n")
    
    for tipo_solicitacao, expected_type in test_cases:
        result = determine_issue_type(tipo_solicitacao)
        status = "✅" if result['name'] == expected_type else "❌"
        
        print(f"{status} '{tipo_solicitacao}' → {result['name']} (ID: {result['id']})")
        print(f"   Label: {result['labels'][0]}")
        print()
    
    print("=== TESTE CONCLUÍDO ===")

if __name__ == "__main__":
    test_issue_type_mapping()