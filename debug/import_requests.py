import requests
import json
import os
from dotenv import load_dotenv
from collections import defaultdict

# Carregar variáveis do arquivo .env
load_dotenv()

def get_jira_issues(jira_url, token, jql_query):
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }

    search_url = f"{jira_url}/rest/api/2/search"
    params = {
        'jql': jql_query,
        'fields': 'id,key,issuetype,status,summary,description,timetracking,assignee,reporter,updated,created,issuelinks,sprint',
        'maxResults': 50
    }

    response = requests.get(search_url, headers=headers, params=params, verify=False)

    if response.status_code == 200:
        issues = response.json().get('issues', [])
        return [
            {
                "key": issue['key'],
                "id": issue['id'],
                "issuetype": issue['fields']['issuetype']['name'],
                "status": issue['fields']['status']['name'],
                "summary": issue['fields']['summary'],
                "description": issue['fields'].get('description', ''),
                "original_estimation": issue['fields']['timetracking'].get('originalEstimate', 'N/A'),
                "story_points": issue['fields'].get('customfield_10004', 'N/A'),
                "sprints": issue['fields'].get('customfield_10100', 'N/A'),
                "assignee": issue['fields']['assignee']['displayName'] if issue['fields']['assignee'] else 'Unassigned',
                "reporter": issue['fields']['reporter']['displayName'],
                "updated": issue['fields']['updated'],
                "created": issue['fields']['created'],
                "test_plans": [],  # Inicializa lista para Test Plans
                "test_executions": []  # Inicializa lista para Test Executions
            }
            for issue in issues
        ]
    else:
        raise Exception(f"Failed to fetch issues: {response.status_code} - {response.text}")

def link_issues(issues):
    for issue in issues:
        # Verificar se há links de issues
        if 'issuelinks' in issue:
            for link in issue['issuelinks']:
                if link['type']['name'] == "Test Plan":
                    issue['test_plans'].append(link['outwardIssue']['key'])
                elif link['type']['name'] == "Test Execution":
                    issue['test_executions'].append(link['outwardIssue']['key'])
    return issues

def print_issues_by_issuetype(issues):
    grouped_issues = defaultdict(list)

    # Agrupar os problemas pela issuetype
    for issue in issues:
        grouped_issues[issue['issuetype']].append(issue['summary'])

    # Imprimir os problemas agrupados
    print("Relatório da Sprint:")
    for issuetype, descriptions in grouped_issues.items():
        print(f"\n{issuetype}:")
        for description in descriptions:
            print(description)

if __name__ == "__main__":
    jira_url = os.getenv("JIRA_URL")
    token = os.getenv("JIRA_TOKEN")

    # jql_query = "project = PLTFAT and issuetype in (story, 'Tech Solution', Bug, Incidente, Block) and sprint in (214375) ORDER BY issuetype ASC"
    jql_query = "issuekey = PLTFAT-12247"

    if not jira_url or not token:
        print("Verifique se JIRA_URL e JIRA_TOKEN estão definidos no arquivo .env.")
    else:
        try:
            issues_list = get_jira_issues(jira_url, token, jql_query)
            issues_list = link_issues(issues_list)  # Faz o link das issues
            if issues_list:
                print(f"\nSprints: {issues_list[0]['sprints']}")
            print_issues_by_issuetype(issues_list)  # Imprime os problemas agrupados
        except Exception as e:
            print(e)