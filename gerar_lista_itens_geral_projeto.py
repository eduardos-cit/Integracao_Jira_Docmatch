from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta
from dateutil import parser
import os
import json
import urllib3
import argparse

# Importar funções utilitárias compartilhadas
from jira_utils import (
    get_jira_issues,
    find_current_sprint_info,
    filter_sprint_issues,
    group_issues_by_status,
    calculate_metrics,
    calculate_lead_time,
    calculate_age_since_backlog,
    print_summary,
    generate_html_report,
    link_issues,
    filter_issues_by_date,
    save_issues_to_csv
)

# Suprimir avisos de SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Carregar variáveis do arquivo .env
load_dotenv()

if __name__ == "__main__":
    # Configurar argumentos de linha de comando
    arg_parser = argparse.ArgumentParser(description='Gerar relatório geral do projeto do Jira')
    arg_parser.add_argument('data_inicio', nargs='?', default=None,
                        help='Data de início para filtro (formato: DD/MM/YYYY ou YYYY-MM-DD)')
    arg_parser.add_argument('data_fim', nargs='?', default=None,
                        help='Data de fim para filtro (formato: DD/MM/YYYY ou YYYY-MM-DD)')
    arg_parser.add_argument('--save-csv', action='store_true',
                        help='Salvar dados brutos em formato CSV na pasta logs')
    args = arg_parser.parse_args()
    
    jira_url = os.getenv("JIRA_URL")
    token = os.getenv("JIRA_TOKEN")
    project = os.getenv("JIRA_PROJECT")
    team = os.getenv("TEAM_NAME")
    
    # Processar parâmetros de data opcionais
    filter_start_date = args.data_inicio
    filter_end_date = args.data_fim
    
    if filter_start_date:
        print(f"Parâmetro de data início recebido: {filter_start_date}")
    
    if filter_end_date:
        print(f"Parâmetro de data fim recebido: {filter_end_date}")
    
    if not filter_start_date and not filter_end_date:
        print("Nenhum filtro de data especificado. Gerando relatório com todas as issues.")

    if not jira_url or not token:
        print("Verifique se JIRA_URL e JIRA_TOKEN estão definidos no arquivo .env.")
    else:
        try:
            print("Buscando issues do Jira...")
            issues_list = get_jira_issues(jira_url, token, project=project, team=team, filter_open_sprints=False)
            issues_list = link_issues(issues_list)  # Faz o link das issues
            
            # Aplicar filtro de datas se especificado
            if filter_start_date or filter_end_date:
                issues_list = filter_issues_by_date(issues_list, filter_start_date, filter_end_date)
            
            # Salvar dados brutos em CSV se solicitado
            if args.save_csv:
                save_issues_to_csv(issues_list, report_type='geral')
            
            # Buscar informações da sprint dinamicamente
            sprint_info = find_current_sprint_info(jira_url, token, project, issues_list)
            
            if sprint_info:
                if 'startDate' in sprint_info:
                    sprint_start = parser.parse(sprint_info['startDate']).strftime('%d/%m/%Y')
                    print(f"Data de início da sprint: {sprint_start}")
                if 'endDate' in sprint_info:
                    sprint_end = parser.parse(sprint_info['endDate']).strftime('%d/%m/%Y')
                    print(f"Data de fim da sprint: {sprint_end}")
            else:
                print("Usando período padrão da sprint (02/02/2026 a 15/02/2026)")
            
            # Agrupar issues por status considerando período da sprint
            grouped_issues = group_issues_by_status(issues_list, sprint_info)
            
            # Calcular métricas ágeis
            metrics = calculate_metrics(issues_list, grouped_issues, report_type='geral')
            
            # Imprimir relatório no console
            print_summary(grouped_issues, report_type='geral')
            
            # Gerar relatório HTML com métricas (incluindo datas de filtro)
            html_file = generate_html_report(grouped_issues, metrics, jira_url, sprint_info, 
                                            report_type='geral', 
                                            filter_start_date=filter_start_date, 
                                            filter_end_date=filter_end_date)
            
            print(f"\nTotal de issues encontradas: {len(issues_list)}")
            print(f"Relatório HTML salvo em: {html_file}")
            
        except Exception as e:
            print(f"Erro: {e}")
