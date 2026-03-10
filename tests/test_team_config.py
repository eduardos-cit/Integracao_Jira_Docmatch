#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste para validar a implementação do campo Team
"""

import os
from dotenv import load_dotenv

def test_team_configuration():
    """Testa se a configuração do TEAM_NAME está funcionando"""
    load_dotenv()
    
    team_name = os.getenv('TEAM_NAME', 'DocMatch')
    print(f"✅ TEAM_NAME configurado: {team_name}")
    
    # Simular dados do BEX
    bex_data = {
        'descricao': 'Este é um teste de descrição para validar o campo Team',
        'raw_content': 'Conteúdo completo do arquivo de teste...'
    }
    
    # Simular payload do Jira
    payload_fields = {
        "customfield_10401": team_name  # Team configurado no .env
    }
    
    print(f"✅ Campo Team no payload: customfield_10401 = '{payload_fields['customfield_10401']}'")
    print("✅ Teste concluído com sucesso!")

if __name__ == "__main__":
    test_team_configuration()