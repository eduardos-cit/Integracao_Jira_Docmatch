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
    generate_html_report_sprint_v2,
    link_issues,
    save_issues_to_csv
)

# Suprimir avisos de SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Carregar variáveis do arquivo .env
load_dotenv()

if __name__ == "__main__":
    # Configurar argumentos de linha de comando
    arg_parser = argparse.ArgumentParser(description='Gerar relatório de Sprint Review do Jira')
    arg_parser.add_argument('--save-csv', action='store_true', 
                        help='Salvar dados brutos em formato CSV na pasta logs')
    args = arg_parser.parse_args()
    
    jira_url = os.getenv("JIRA_URL")
    token = os.getenv("JIRA_TOKEN")
    project = os.getenv("JIRA_PROJECT")
    team = os.getenv("TEAM_NAME")

    if not jira_url or not token:
        print("Verifique se JIRA_URL e JIRA_TOKEN estão definidos no arquivo .env.")
    else:
        try:
            print("Buscando issues do Jira...")
            issues_list = get_jira_issues(jira_url, token, project=project, team=team, filter_open_sprints=True)
            issues_list = link_issues(issues_list)  # Faz o link das issues
            
            # Salvar dados brutos em CSV se solicitado
            if args.save_csv:
                save_issues_to_csv(issues_list, report_type='sprint')
            
            # Buscar informações da sprint dinamicamente
            sprint_info = find_current_sprint_info(jira_url, token, project, issues_list)
            
            if sprint_info:
                if 'startDate' in sprint_info:
                    start_date = parser.parse(sprint_info['startDate']).strftime('%d/%m/%Y')
                    print(f"Data de início da sprint: {start_date}")
                if 'endDate' in sprint_info:
                    end_date = parser.parse(sprint_info['endDate']).strftime('%d/%m/%Y')
                    print(f"Data de fim da sprint: {end_date}")
            else:
                print("Usando período padrão da sprint (02/02/2026 a 15/02/2026)")
            
            # Agrupar issues por status considerando período da sprint
            grouped_issues = group_issues_by_status(issues_list, sprint_info)
            
            # Calcular métricas ágeis
            metrics = calculate_metrics(issues_list, grouped_issues, report_type='sprint')
            
            # Imprimir relatório no console
            print_summary(grouped_issues, report_type='sprint')
            
            # Gerar relatório HTML v1 (atual) e v2 (nova versão com métricas avançadas)
            html_file_v1 = generate_html_report(grouped_issues, metrics, jira_url, sprint_info, report_type='sprint')
            html_file_v2 = generate_html_report_sprint_v2(grouped_issues, metrics, jira_url, sprint_info)
            
            print(f"\nTotal de issues encontradas: {len(issues_list)}")
            print(f"Relatório HTML v1 (comparação) salvo em: {html_file_v1}")
            print(f"Relatório HTML v2 (novo) salvo em: {html_file_v2}")
            
        except Exception as e:
            print(f"Erro: {e}")
