"""
Script Unificado de Geração de Relatórios Jira
==============================================
Gera simultaneamente relatórios de Sprint Review e Geral do Projeto
com uma única conexão ao Jira, otimizando tempo e recursos.

Autor: Equipe de Automação Jira
Versão: 2.0
Data: Fevereiro 2026
"""

from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta
from dateutil import parser
import os
import json
import argparse

# Importar funções utilitárias compartilhadas
from jira_utils import (
    get_jira_issues,
    find_current_sprint_info,
    filter_sprint_issues,
    group_issues_by_status,
    calculate_metrics,
    calculate_lead_time,
    print_summary,
    generate_html_report,
    generate_html_report_sprint_v2,
    save_issues_to_csv
)

# Carregar variáveis do arquivo .env
load_dotenv()

def main(save_csv=False):
    """
    Função principal que coordena a geração de ambos os relatórios
    
    Args:
        save_csv (bool): Se True, salva dados brutos em CSV na pasta logs
    """
    print("=" * 70)
    print("GERADOR UNIFICADO DE RELATÓRIOS JIRA")
    print("Gerando relatórios: Sprint Review + Geral do Projeto")
    print("=" * 70)
    print()
    
    # Configuração
    jira_url = os.getenv("JIRA_URL")
    token = os.getenv("JIRA_TOKEN")
    project = os.getenv("JIRA_PROJECT")
    team = os.getenv("TEAM_NAME")
    
    if not jira_url or not token:
        print("❌ Erro: JIRA_URL e JIRA_TOKEN devem estar configurados no arquivo .env")
        return
    
    # 1. Buscar TODAS as issues do projeto (uma única conexão)
    print("\n📡 ETAPA 1: Conectando ao Jira e buscando dados...")
    all_project_issues = get_jira_issues(jira_url, token, project=project, team=team, filter_open_sprints=False)
    
    if not all_project_issues:
        print("❌ Nenhuma issue encontrada. Verifique a query JQL e suas permissões.")
        return
    
    # 2. Identificar sprint ativa
    print("\n📅 ETAPA 2: Identificando sprint ativa...")
    sprint_info = find_current_sprint_info(jira_url, token, project, all_project_issues)
    
    if sprint_info:
        print(f"✓ Sprint ativa encontrada: {sprint_info.get('name')} (ID: {sprint_info.get('id')})")
        if 'startDate' in sprint_info:
            start = parser.parse(sprint_info['startDate']).strftime('%d/%m/%Y')
            print(f"  Data de início: {start}")
        if 'endDate' in sprint_info:
            end = parser.parse(sprint_info['endDate']).strftime('%d/%m/%Y')
            print(f"  Data de fim: {end}")
    else:
        print("⚠ Nenhuma sprint ativa encontrada. Relatórios serão gerados sem informações de sprint.")
    
    # 3. Filtrar issues da sprint
    print("\n🔍 ETAPA 3: Filtrando issues da sprint ativa...")
    sprint_issues = filter_sprint_issues(all_project_issues, sprint_info) if sprint_info else []
    
    # 4. Gerar RELATÓRIO DA SPRINT REVIEW
    if sprint_issues:
        print("\n📊 ETAPA 4: Gerando Relatório de Sprint Review...")
        
        # Salvar dados brutos da sprint em CSV se solicitado
        if save_csv:
            save_issues_to_csv(sprint_issues, report_type='sprint')
        
        grouped_sprint = group_issues_by_status(sprint_issues, sprint_info)
        metrics_sprint = calculate_metrics(sprint_issues, grouped_sprint, report_type='sprint')
        
        print_summary(grouped_sprint, report_type='sprint')
        
        sprint_report_file_v1 = generate_html_report(
            grouped_sprint, 
            metrics_sprint, 
            jira_url, 
            sprint_info, 
            report_type='sprint'
        )

        sprint_report_file_v2 = generate_html_report_sprint_v2(
            grouped_sprint,
            metrics_sprint,
            jira_url,
            sprint_info
        )
        
        print(f"\n✅ Relatório de Sprint Review v1 (comparação): {sprint_report_file_v1}")
        print(f"✅ Relatório de Sprint Review v2 (novo): {sprint_report_file_v2}")
    else:
        print("\n⚠ Sem issues na sprint ativa. Relatório de Sprint Review não será gerado.")
    
    # 5. Gerar RELATÓRIO GERAL DO PROJETO
    print("\n📊 ETAPA 5: Gerando Relatório Geral do Projeto...")
    
    # Salvar dados brutos gerais em CSV se solicitado
    if save_csv:
        save_issues_to_csv(all_project_issues, report_type='completo')
    
    grouped_geral = group_issues_by_status(all_project_issues, sprint_info)
    metrics_geral = calculate_metrics(all_project_issues, grouped_geral, report_type='geral')
    
    print_summary(grouped_geral, report_type='geral')
    
    geral_report_file = generate_html_report(
        grouped_geral, 
        metrics_geral, 
        jira_url, 
        sprint_info, 
        report_type='geral'
    )
    
    print(f"\n✅ Relatório Geral do Projeto: {geral_report_file}")
    
    # 6. Resumo final
    print("\n" + "=" * 70)
    print("✅ GERAÇÃO CONCLUÍDA COM SUCESSO!")
    print("=" * 70)
    print(f"\n📋 Resumo:")
    print(f"  • Total de issues no projeto: {len(all_project_issues)}")
    print(f"  • Issues na sprint ativa: {len(sprint_issues)}")
    total_reports = 3 if sprint_issues else 1
    print(f"  • Relatórios gerados: {total_reports}")
    print(f"\n💡 Otimização: Uma única conexão ao Jira gerou ambos os relatórios!")
    print()


if __name__ == "__main__":
    # Configurar argumentos de linha de comando
    arg_parser = argparse.ArgumentParser(description='Gerar relatórios completos (Sprint Review + Geral) do Jira')
    arg_parser.add_argument('--save-csv', action='store_true',
                        help='Salvar dados brutos em formato CSV na pasta logs')
    args = arg_parser.parse_args()
    
    main(save_csv=args.save_csv)
