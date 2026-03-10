#!/usr/bin/env python3
"""
Script de teste para validar o cálculo do lead time com os novos status iniciais
"""

from datetime import datetime, timezone
from dateutil import parser

def calculate_lead_time_test(issue):
    """
    Versão de teste da função calculate_lead_time
    """
    try:
        # Definir status inicial baseado no tipo da issue
        issue_type = issue['issuetype'].upper()
        if issue_type == 'BUG':
            initial_status = 'NOVO'
        elif issue_type == 'STORY':
            initial_status = 'PRODUCT BACKLOG'
        elif issue_type in ['TECH SOLUTION', 'INCIDENTE']:
            initial_status = 'BACKLOG'
        else:
            # Fallback para tipos não mapeados - usar data de criação
            initial_status = None
        
        print(f"\nTesting {issue['key']} ({issue_type}):")
        print(f"  Status inicial mapeado: {initial_status}")
        
        # Procurar pela data de saída do status inicial
        start_date = None
        
        if initial_status and 'changelog' in issue and 'histories' in issue['changelog']:
            for history in issue['changelog']['histories']:
                history_date = parser.parse(history['created'])
                for item in history.get('items', []):
                    if item.get('field') == 'status':
                        from_status = item.get('fromString', '').upper()
                        to_status = item.get('toString', '').upper()
                        
                        # Encontrou saída do status inicial
                        if from_status == initial_status and to_status != initial_status:
                            if start_date is None or history_date < start_date:
                                start_date = history_date
                                print(f"  ✓ Encontrou saída de '{initial_status}' para '{to_status}' em {history_date.strftime('%d/%m/%Y %H:%M')}")
                            break
        
        # Se não encontrou data de saída do status inicial, usar data de criação
        if start_date is None:
            start_date = parser.parse(issue['created'])
            if start_date.tzinfo is None:
                start_date = start_date.replace(tzinfo=timezone.utc)
            print(f"  → Usando data de criação como fallback: {start_date.strftime('%d/%m/%Y %H:%M')}")
        
        # Procurar pela última transição para produção ou finalização
        last_production_date = None
        
        if 'changelog' in issue and 'histories' in issue['changelog']:
            for history in issue['changelog']['histories']:
                history_date = parser.parse(history['created'])
                for item in history.get('items', []):
                    if item.get('field') == 'status':
                        to_status = item.get('toString', '').upper()
                        if to_status in ['EM PRODUÇÃO', 'ATIVADA', 'FINALIZADO', 'FECHADO']:
                            last_production_date = history_date
                            print(f"  ✓ Chegou em produção/finalizado: {to_status} em {history_date.strftime('%d/%m/%Y %H:%M')}")
        
        if last_production_date:
            lead_time = (last_production_date - start_date).days
            print(f"  Lead Time: {lead_time} dias (de {start_date.strftime('%d/%m/%Y')} até {last_production_date.strftime('%d/%m/%Y')})")
            return max(lead_time, 0)  # Evitar valores negativos
        else:
            # Se não chegou em produção, calcular até agora
            current_date = datetime.now(timezone.utc)
            lead_time = (current_date - start_date).days
            print(f"  Lead Time atual: {lead_time} dias (de {start_date.strftime('%d/%m/%Y')} até hoje)")
            return max(lead_time, 0)
            
    except Exception as e:
        print(f"  Erro ao calcular lead time: {e}")
        return 0

# Exemplos de teste (simulando dados do Jira)
test_issues = [
    {
        'key': 'PLTFAT-12345',
        'issuetype': 'Bug',
        'created': '2025-10-01T09:00:00.000-0300',
        'changelog': {
            'histories': [
                {
                    'created': '2025-10-02T10:30:00.000-0300',
                    'items': [
                        {
                            'field': 'status',
                            'fromString': 'Novo',
                            'toString': 'Em Desenvolvimento'
                        }
                    ]
                },
                {
                    'created': '2025-10-10T15:45:00.000-0300',
                    'items': [
                        {
                            'field': 'status',
                            'fromString': 'Em Teste',
                            'toString': 'Fechado'
                        }
                    ]
                }
            ]
        }
    },
    {
        'key': 'PLTFAT-67890', 
        'issuetype': 'Story',
        'created': '2025-09-15T08:00:00.000-0300',
        'changelog': {
            'histories': [
                {
                    'created': '2025-09-20T14:00:00.000-0300',
                    'items': [
                        {
                            'field': 'status',
                            'fromString': 'Product Backlog',
                            'toString': 'Pronto para Desenvolvimento'
                        }
                    ]
                },
                {
                    'created': '2025-10-05T16:30:00.000-0300',
                    'items': [
                        {
                            'field': 'status',
                            'fromString': 'Testada',
                            'toString': 'Em Produção'
                        }
                    ]
                }
            ]
        }
    }
]

if __name__ == "__main__":
    print("=== TESTE DE CÁLCULO DE LEAD TIME ===")
    print("Status iniciais por tipo:")
    print("- Bug: NOVO")
    print("- Story: PRODUCT BACKLOG") 
    print("- Tech Solution: BACKLOG")
    print("- Incidente: BACKLOG")
    
    for issue in test_issues:
        lead_time = calculate_lead_time_test(issue)
        print(f"  Resultado final: {lead_time} dias")
    
    print("\n=== TESTE CONCLUÍDO ===")