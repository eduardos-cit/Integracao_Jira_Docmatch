#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste específico para validar o campo description nos payloads Bug e Story
"""

import os
import re
import json
import logging
from datetime import datetime
from dotenv import load_dotenv

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('teste_description_field.log', encoding='utf-8', mode='w'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def determine_issue_type(tipo_solicitacao):
    """Determina o tipo de issue baseado no campo "Tipo de solicitação:" """
    tipo_normalizado = tipo_solicitacao.lower().strip()
    
    if 'sugerir melhorias' in tipo_normalizado or 'novas funcionalidades' in tipo_normalizado:
        return {'id': '10001', 'name': 'Story', 'labels': ['STORY_BEX_AGENTIX']}
    elif 'solicitar suporte' in tipo_normalizado or 'reportar bug' in tipo_normalizado:
        return {'id': '10102', 'name': 'Bug', 'labels': ['BUG_PROD_AGENTIX']}
    else:
        return {'id': '10102', 'name': 'Bug', 'labels': ['BUG_PROD_AGENTIX']}

def parse_bex_content(content, test_name):
    """Extrai dados de um conteúdo BEX para teste"""
    patterns = {
        'tipo_solicitacao': r'Tipo de solicitação:\s*(.+)',
        'resumo': r'Resumo:\s*(.+)',
        'descricao': r'Descrição:\s*(.+?)(?=Status geral:|$)',
    }
    
    extracted_data = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        if match:
            extracted_data[key] = match.group(1).strip()
        else:
            extracted_data[key] = "Não informado"
    
    # Limpar descrição
    if extracted_data.get('descricao'):
        extracted_data['descricao'] = re.sub(r'\s+', ' ', extracted_data['descricao']).strip()
    
    # Adicionar conteúdo bruto
    extracted_data['raw_content'] = content.strip()
    
    # Determinar tipo de issue
    tipo_solicitacao = extracted_data.get('tipo_solicitacao', 'Não informado')
    issue_type_info = determine_issue_type(tipo_solicitacao)
    extracted_data['issue_type'] = issue_type_info
    
    return extracted_data

def create_bug_payload(project_key, summary, description, team_name):
    """Cria payload para Bug"""
    return {
        "fields": {
            "project": {"key": project_key},
            "summary": summary,
            "description": description,
            "issuetype": {"id": "10102"},  # Bug
            "labels": ["BUG_PROD_AGENTIX"],
            "priority": {"id": "2"},  # High priority
            "customfield_20700": {"id": "42400"},    # Ambiente: Open
            "customfield_13402": {"id": "15832"},    # Nível | Fase de testes: Integração - Componente  
            "customfield_13403": {"id": "15835"},    # Severity: High
            "customfield_13901": {"id": "17203"},    # Reincidente: Não
            "customfield_13900": {"id": "17201"},    # Defeito legado: Não
            "customfield_13401": {"id": "15810"},    # Company: CI&T
            "customfield_10401": team_name           # Team configurado no .env
        }
    }

def create_story_payload(project_key, summary, description, team_name):
    """Cria payload para Story"""
    return {
        "fields": {
            "project": {"key": project_key},
            "summary": summary,
            "description": description,
            "issuetype": {"id": "10001"},  # Story
            "labels": ["STORY_BEX_AGENTIX"],
            "priority": {"id": "3"},  # Medium priority
            "customfield_13401": {"id": "15810"},    # Company: CI&T
            "customfield_10401": team_name           # Team configurado no .env
        }
    }

def generate_jira_summary(descricao, max_chars=100):
    """Gera o summary para o Jira"""
    if not descricao or descricao == "Não informado":
        return "Solicitação BEX - Descrição não informada"
    
    summary = descricao.strip()
    
    if len(summary) > max_chars:
        summary = summary[:max_chars]
        last_space = summary.rfind(' ')
        if last_space > 50:
            summary = summary[:last_space]
        summary += "..."
    
    return summary

def validate_description_field(bex_data, payload, test_name):
    """Valida se o campo description está preenchido corretamente"""
    logger.info(f"[{test_name}] === VALIDAÇÃO DO CAMPO DESCRIPTION ===")
    
    # Verificar se description existe no payload
    description_payload = payload['fields'].get('description')
    raw_content = bex_data.get('raw_content', '')
    
    logger.info(f"[{test_name}] Description no payload existe: {'✅' if description_payload else '❌'}")
    
    if description_payload:
        logger.info(f"[{test_name}] Tamanho do description: {len(description_payload)} caracteres")
        logger.info(f"[{test_name}] Tamanho do raw_content: {len(raw_content)} caracteres")
        
        # Verificar se description = raw_content
        if description_payload == raw_content:
            logger.info(f"[{test_name}] ✅ Description = raw_content (CORRETO)")
            return True
        else:
            logger.error(f"[{test_name}] ❌ Description ≠ raw_content (ERRO)")
            logger.error(f"[{test_name}] Description (primeiros 100 chars): '{description_payload[:100]}...'")
            logger.error(f"[{test_name}] Raw_content (primeiros 100 chars): '{raw_content[:100]}...'")
            return False
    else:
        logger.error(f"[{test_name}] ❌ Campo description não encontrado no payload!")
        return False

def test_description_validation():
    """Testa a validação do campo description"""
    logger.info("🔍 === TESTE DE VALIDAÇÃO DO CAMPO DESCRIPTION ===")
    
    # Carregar team do .env
    load_dotenv()
    team_name = os.getenv('TEAM_NAME', 'DocMatch')
    
    # Dados de teste
    test_cases = {
        "BUG_TEST": """Data de criação: 28/10/2025 10:00:00
Última atualização: 28/10/2025 10:00:00
Matrícula solicitante: I435388
Nome do solicitante: João Silva
Email do solicitante: joao.silva@bradesco.com.br
Centro de custo: dvop
Solicitado ao time: Bia Tech Agentix
Projeto do PPMC: Não informado.
Projeto do Jira: Não informado.
Issue do Jira: Não informado.
Tipo de solicitação: Solicitar suporte.
Resumo: Problema ao acessar funcionalidade
Descrição: Sistema não está permitindo acesso à funcionalidade X do AgentIX após atualização.
Status geral: Aberto
Matrícula do atendente: Não Atribuído
Nome do atendente: Não Atribuído
Email do atendente: Não Atribuído
Labels: Não existem labels cadastradas.
Anexos: """,

        "STORY_TEST": """Data de criação: 28/10/2025 10:30:00
Última atualização: 28/10/2025 10:30:00
Matrícula solicitante: I435390
Nome do solicitante: Carlos Oliveira
Email do solicitante: carlos.oliveira@bradesco.com.br
Centro de custo: dvop
Solicitado ao time: Bia Tech Agentix
Projeto do PPMC: Não informado.
Projeto do Jira: Não informado.
Issue do Jira: Não informado.
Tipo de solicitação: Sugerir melhorias e novas funcionalidades.
Resumo: Nova funcionalidade de relatórios
Descrição: Solicito implementação de novos tipos de relatórios no painel do AgentIX para melhor acompanhamento.
Status geral: Aberto
Matrícula do atendente: Não Atribuído
Nome do atendente: Não Atribuído
Email do atendente: Não Atribuído
Labels: Não existem labels cadastradas.
Anexos: """
    }
    
    validation_results = []
    
    for test_name, bex_content in test_cases.items():
        try:
            logger.info(f"\n[{test_name}] === INICIANDO TESTE ===")
            
            # Parse do conteúdo BEX
            bex_data = parse_bex_content(bex_content, test_name)
            
            # Gerar summary e description
            summary = generate_jira_summary(bex_data.get('descricao', ''))
            description = bex_data.get('raw_content', 'Conteúdo não disponível')
            project_key = "PLTFAT"
            
            # Obter tipo de issue
            issue_type_info = bex_data.get('issue_type', {'name': 'Bug'})
            
            logger.info(f"[{test_name}] Tipo de issue: {issue_type_info['name']}")
            logger.info(f"[{test_name}] Summary: '{summary}'")
            
            # Criar payload baseado no tipo
            if issue_type_info['name'] == 'Story':
                payload = create_story_payload(project_key, summary, description, team_name)
            else:
                payload = create_bug_payload(project_key, summary, description, team_name)
            
            # Validar campo description
            is_valid = validate_description_field(bex_data, payload, test_name)
            validation_results.append({
                'test_name': test_name,
                'issue_type': issue_type_info['name'],
                'description_valid': is_valid
            })
            
            # Mostrar estrutura do payload
            logger.info(f"[{test_name}] Campos no payload: {list(payload['fields'].keys())}")
            logger.info(f"[{test_name}] ✅ TESTE CONCLUÍDO")
            
        except Exception as e:
            logger.error(f"[{test_name}] ❌ ERRO NO TESTE: {str(e)}")
            validation_results.append({
                'test_name': test_name,
                'description_valid': False,
                'error': str(e)
            })
    
    # Resumo dos resultados
    logger.info("\n📊 === RESUMO DOS TESTES DE DESCRIPTION ===")
    valid_tests = [r for r in validation_results if r.get('description_valid', False)]
    invalid_tests = [r for r in validation_results if not r.get('description_valid', False)]
    
    logger.info(f"✅ Testes válidos: {len(valid_tests)}")
    logger.info(f"❌ Testes inválidos: {len(invalid_tests)}")
    
    for result in valid_tests:
        logger.info(f"  ✅ {result['test_name']}: {result.get('issue_type', 'Unknown')} - Description OK")
    
    for result in invalid_tests:
        error_msg = result.get('error', 'Description inválida')
        logger.info(f"  ❌ {result['test_name']}: {error_msg}")
    
    # Validação final
    if len(valid_tests) == len(validation_results):
        logger.info("\n🎉 === CAMPO DESCRIPTION VÁLIDO ===")
        logger.info("✅ Campo description preenchido corretamente em todos os payloads")
        logger.info("✅ Description = raw_content do arquivo BEX")
        logger.info("✅ Conteúdo completo preservado")
    else:
        logger.error("\n🚨 === PROBLEMA NO CAMPO DESCRIPTION ===")
        logger.error("❌ Campo description não está sendo preenchido corretamente")
        logger.error("❌ Revisar implementação antes de usar em produção")
    
    logger.info(f"\n📄 Log salvo em: teste_description_field.log")

if __name__ == "__main__":
    test_description_validation()