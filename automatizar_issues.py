#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para automatizar a criação de issues no Jira com base em arquivos .csv

Este script:
1. Lê o arquivo .csv de uma pasta local (configurada no .env)
2. Mapeia as colunas do CSV baseado no arquivo BulkCreate_configuration.txt
3. Cria issues no Jira em lote (bulk create) via API
4. Gera relatório com resultados do processamento
5. Move arquivos processados para a sub-pasta Processados

Configuração no .env:
- JIRA_URL: URL do Jira
- JIRA_TOKEN: Token de autenticação Bearer
- JIRA_PROJECT: Chave do projeto no Jira
- TEAM_NAME: Nome do time para atribuir às issues
- folder_path: Pasta onde estão os arquivos CSV

Data: 07/02/2026
"""

import os
import csv
import json
import requests
import shutil
import logging
import argparse
from datetime import datetime
from urllib3.exceptions import InsecureRequestWarning
from dotenv import load_dotenv

# Versão da API do Jira em uso
JIRA_API_VERSION = "2"  # Usar v2 para Jira Server/Data Center, v3 para Cloud

# Suprimir avisos de SSL para ambiente corporativo
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Configurar logging
# Garantir que a pasta logs existe
os.makedirs('logs', exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/automatizacao_issues.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def load_environment():
    """Carrega variáveis de ambiente do arquivo .env existente"""
    load_dotenv()
    
    jira_url = os.getenv('JIRA_URL')
    jira_token = os.getenv('JIRA_TOKEN')
    jira_project = os.getenv('JIRA_PROJECT')
    team_name = os.getenv('TEAM_NAME', 'DocMatch')
    folder_path = os.getenv('folder_path', 'issues')
    
    if not jira_url or not jira_token:
        logger.error("Variáveis JIRA_URL e JIRA_TOKEN devem estar definidas no arquivo .env")
        raise ValueError("Configuração do Jira não encontrada")
    
    if not jira_project:
        logger.error("Variável JIRA_PROJECT deve estar definida no arquivo .env")
        raise ValueError("Projeto do Jira não configurado")
    
    logger.info(f"Conectando ao Jira: {jira_url}")
    logger.info(f"Projeto: {jira_project}")
    logger.info(f"Team configurado: {team_name}")
    logger.info(f"Pasta CSV: {folder_path}")
    
    return jira_url, jira_token, jira_project, team_name, folder_path

def load_bulk_configuration():
    """
    Carrega configuração de mapeamento do arquivo BulkCreate_configuration.txt
    
    Returns:
        dict: Configuração de mapeamento ou None se houver erro
    """
    config_file = 'BulkCreate_configuration.txt'
    
    try:
        with open(config_file, 'r', encoding='utf-8') as file:
            config = json.load(file)
        
        logger.info(f"Configuração carregada de {config_file}")
        logger.info(f"Projeto configurado: {config['config.project']['project.key']}")
        
        return config
        
    except FileNotFoundError:
        logger.error(f"Arquivo {config_file} não encontrado")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Erro ao decodificar JSON de {config_file}: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Erro ao carregar configuração: {str(e)}")
        return None

def parse_csv_file(file_path, config):
    """
    Lê arquivo CSV e mapeia para estrutura de issues do Jira
    
    Args:
        file_path (str): Caminho para o arquivo .csv
        config (dict): Configuração de mapeamento
        
    Returns:
        list: Lista de issues mapeadas ou None se houver erro
    """
    try:
        issues = []
        field_mappings = config['config.field.mappings']
        project_key = config['config.project']['project.key']
        
        with open(file_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            
            for row_num, row in enumerate(csv_reader, start=2):  # linha 2 pois linha 1 é cabeçalho
                issue_data = {
                    'project': {'key': project_key},
                    'issuetype': {'name': row.get('Issue Type', 'Task')}
                }
                
                # Mapear campos do CSV para campos do Jira
                for csv_field, jira_mapping in field_mappings.items():
                    if csv_field in row and row[csv_field]:
                        value = row[csv_field].strip()
                        
                        if not value:  # Pular campos vazios
                            continue
                        
                        # Obter o nome do campo no Jira
                        jira_field = jira_mapping.get('jira.field')
                        custom_field = jira_mapping.get('existing.custom.field')
                        
                        if jira_field:
                            # Campos padrão do Jira
                            if jira_field == 'summary':
                                issue_data['summary'] = value
                            elif jira_field == 'description':
                                issue_data['description'] = value
                            elif jira_field == 'issuetype':
                                # Issue type precisa ser um objeto com 'name'
                                issue_data['issuetype'] = {'name': value}
                            elif jira_field == 'assignee':
                                issue_data['assignee'] = {'name': value}
                            elif jira_field == 'labels':
                                issue_data['labels'] = [label.strip() for label in value.split(',')]
                            elif jira_field == 'timeoriginalestimate':
                                # Se vier apenas número, assumir horas e acrescentar sufixo "h"
                                # Ex.: "8" -> "8h"
                                if value.isdigit():
                                    time_value = f"{int(value)}h"
                                else:
                                    # Se já estiver formatado (ex.: 1d 4h, 30m), usar diretamente
                                    time_value = value

                                issue_data['timetracking'] = {
                                    'originalEstimate': time_value,
                                    'remainingEstimate': time_value
                                }
                            elif jira_field == 'subtask-parent-id':
                                # Parent para subtasks
                                if value:
                                    issue_data['parent'] = {'key': value}
                            else:
                                issue_data[jira_field] = value
                        
                        elif custom_field:
                            # Campos customizados
                            field_key = f'customfield_{custom_field}'
                            
                            # Tratamento especial para campos específicos
                            if custom_field == '10401':  # Team
                                issue_data[field_key] = value
                            elif custom_field == '10100':  # Sprint
                                try:
                                    issue_data[field_key] = int(value)
                                except ValueError:
                                    issue_data[field_key] = value
                            elif custom_field == '10101':  # Epic Link
                                issue_data[field_key] = value
                            elif custom_field == '10500':  # Theme
                                # Campo Theme (customfield_10500) não enviado - não está disponível na tela do projeto
                                pass
                            else:
                                issue_data[field_key] = value
                
                # Garantir que Original Estimate sempre tenha um valor (padrão: 0h)
                if 'timetracking' not in issue_data:
                    issue_data['timetracking'] = {
                        'originalEstimate': '0h',
                        'remainingEstimate': '0h'
                    }
                
                # Validar campos obrigatórios
                if 'summary' not in issue_data:
                    logger.warning(f"Linha {row_num}: Issue sem Summary será ignorada")
                    continue
                
                issues.append(issue_data)
        
        logger.info(f"Arquivo {file_path}: {len(issues)} issues mapeadas")
        return issues
        
    except FileNotFoundError:
        logger.error(f"Arquivo {file_path} não encontrado")
        return None
    except Exception as e:
        logger.error(f"Erro ao processar arquivo {file_path}: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return None

def create_jira_issues_bulk(jira_url, token, issues_data, dry_run=False):
    """
    Cria múltiplas issues no Jira em uma única chamada (bulk create)
    
    API Reference:
    - POST /rest/api/2/issue/bulk (Jira Server/Data Center)
    - POST /rest/api/3/issue/bulk (Jira Cloud)
    
    Args:
        jira_url (str): URL base do Jira
        token (str): Token de autenticação
        issues_data (list): Lista de dicionários com dados das issues
        dry_run (bool): Se True, apenas mostra o JSON sem fazer a chamada API
        
    Returns:
        dict: Resultado da operação bulk create
    """
    try:
        if not issues_data:
            logger.warning("Nenhuma issue para criar")
            return {'status': 'error', 'message': 'Nenhuma issue para criar'}
        
        # Preparar payload para bulk create conforme documentação oficial
        # Estrutura: { "issueUpdates": [ { "fields": {...}, "update": {...} } ] }
        bulk_payload = {
            'issueUpdates': []
        }
        
        for issue_data in issues_data:
            # Cada item deve ter 'fields' e opcionalmente 'update'
            issue_update = {
                'fields': issue_data,
                'update': {}  # Pode conter operações adicionais
            }
            bulk_payload['issueUpdates'].append(issue_update)
        
        logger.info(f"Preparando criação em lote de {len(issues_data)} issues")
        logger.debug(f"Payload (primeiras 2 issues): {json.dumps(bulk_payload['issueUpdates'][:2], indent=2)}")
        
        # Salvar JSON em arquivo na pasta logs
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        json_type = 'test' if dry_run else 'prod'
        json_filename = f"logs/bulk_payload_{json_type}_{timestamp}.json"
        
        try:
            with open(json_filename, 'w', encoding='utf-8') as f:
                json.dump(bulk_payload, f, indent=2, ensure_ascii=False)
            logger.info(f"📄 JSON salvo em: {json_filename}")
        except Exception as e:
            logger.warning(f"⚠️  Não foi possível salvar JSON: {str(e)}")
        
        # Modo dry-run: apenas mostrar o JSON sem chamar a API
        if dry_run:
            logger.info("\n" + "="*70)
            logger.info("🔍 MODO DRY-RUN - JSON que seria enviado à API:")
            logger.info("="*70)
            print("\n" + json.dumps(bulk_payload, indent=2, ensure_ascii=False))
            logger.info("\n" + "="*70)
            logger.info(f"📊 Total de issues no payload: {len(bulk_payload['issueUpdates'])}")
            logger.info("⚠️  API NÃO FOI CHAMADA (modo dry-run)")
            logger.info("="*70)
            
            # Criar lista mock de issues para contagem correta no dry-run
            mock_issues = [{'key': f'DRY-RUN-{i+1}'} for i in range(len(bulk_payload['issueUpdates']))]
            
            return {
                'status': 'dry-run',
                'message': 'Dry-run executado com sucesso',
                'issues': mock_issues,
                'total_created': len(mock_issues),
                'total_errors': 0,
                'payload': bulk_payload
            }
        
        # Endpoint de bulk create (tentar v2 primeiro para Server/Data Center)
        create_url = f"{jira_url}/rest/api/2/issue/bulk"
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(create_url, headers=headers, json=bulk_payload, verify=False, timeout=60)
        
        # Status 201 Created indica sucesso
        if response.status_code == 201:
            result = response.json()
            issues_created = result.get('issues', [])
            errors = result.get('errors', [])
            
            logger.info(f"✓ Bulk create concluído: {len(issues_created)} issues criadas")
            
            if errors:
                logger.warning(f"⚠ Erros durante bulk create: {len(errors)} falhas")
                for i, error in enumerate(errors, 1):
                    if isinstance(error, dict):
                        logger.error(f"  Erro {i}: {error}")
                    else:
                        logger.error(f"  Erro {i}: {str(error)}")
            
            return {
                'status': 'success',
                'issues': issues_created,
                'errors': errors,
                'total_created': len(issues_created),
                'total_errors': len(errors)
            }
        else:
            logger.error(f"✗ Erro ao criar issues em lote: HTTP {response.status_code}")
            logger.error(f"Resposta: {response.text[:500]}...")
            
            # Tentar decodificar erro JSON
            try:
                error_detail = response.json()
                logger.error(f"Detalhes do erro: {json.dumps(error_detail, indent=2)}")
            except:
                pass
            
            return {
                'status': 'error',
                'message': f"Erro HTTP {response.status_code}: {response.text[:200]}"
            }
            
    except requests.exceptions.Timeout:
        logger.error("✗ Timeout ao criar issues - servidor demorou muito para responder")
        return {
            'status': 'error',
            'message': 'Timeout na requisição'
        }
    except Exception as e:
        logger.error(f"✗ Erro ao criar issues no Jira: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return {
            'status': 'error',
            'message': str(e)
        }

def process_csv_files(folder_path, jira_url, token, config, dry_run=False):
    """
    Processa todos os arquivos .csv da pasta especificada
    
    Args:
        folder_path (str): Caminho da pasta com arquivos .csv
        jira_url (str): URL base do Jira
        token (str): Token de autenticação
        config (dict): Configuração de mapeamento
        dry_run (bool): Se True, apenas mostra o JSON sem fazer a chamada API
        
    Returns:
        dict: Relatório do processamento
    """
    if not os.path.exists(folder_path):
        logger.error(f"Pasta não encontrada: {folder_path}")
        return {'error': 'Pasta não encontrada'}
    
    # Buscar todos os arquivos CSV na pasta
    all_csv_files = [f for f in os.listdir(folder_path) 
                     if f.endswith('.csv') and os.path.isfile(os.path.join(folder_path, f))]
    
    # Filtrar templates
    template_files = [f for f in all_csv_files if f.lower().startswith('template')]
    csv_files = [f for f in all_csv_files if not f.lower().startswith('template')]
    
    # Informar sobre templates ignorados
    if template_files:
        logger.info(f"📋 Arquivos template ignorados: {len(template_files)}")
        for tpl in template_files:
            logger.info(f"   ↳ {tpl}")
    
    if not csv_files:
        logger.warning(f"Nenhum arquivo .csv encontrado em {folder_path}")
        return {'error': 'Nenhum arquivo .csv encontrado'}
    
    logger.info(f"Encontrados {len(csv_files)} arquivos .csv para processar")
    
    results = {
        'processed_files': [],
        'created_issues': [],
        'failed_files': [],
        'total_files': len(csv_files),
        'total_issues_created': 0,
        'total_errors': 0
    }
    
    for csv_file in csv_files:
        file_path = os.path.join(folder_path, csv_file)
        logger.info(f"\n{'='*60}")
        logger.info(f"Processando arquivo: {csv_file}")
        logger.info(f"{'='*60}")
        
        # Parsear CSV e mapear para estrutura do Jira
        issues_data = parse_csv_file(file_path, config)
        
        if not issues_data:
            results['failed_files'].append({
                'file': csv_file,
                'error': 'Erro ao processar arquivo ou nenhuma issue válida encontrada'
            })
            results['total_errors'] += 1
            continue
        
        # Criar issues em lote no Jira
        bulk_result = create_jira_issues_bulk(jira_url, token, issues_data, dry_run=dry_run)
        
        if bulk_result['status'] in ['success', 'dry-run']:
            created_issues = bulk_result.get('issues', [])
            errors = bulk_result.get('errors', [])
            
            file_result = {
                'file': csv_file,
                'issues_created': len(created_issues),
                'errors': len(errors),
                'issue_keys': []
            }
            
            for issue in created_issues:
                issue_key = issue.get('key')
                issue_url = f"{jira_url}/browse/{issue_key}"
                file_result['issue_keys'].append({
                    'key': issue_key,
                    'url': issue_url
                })
                # Só logar issues reais, não mock do dry-run
                if not dry_run:
                    logger.info(f"✓ Issue criada: {issue_key}")
            
            if errors:
                file_result['error_details'] = errors
                logger.warning(f"⚠ {len(errors)} issues falharam")
            
            results['created_issues'].append(file_result)
            results['total_issues_created'] += len(created_issues)
            results['total_errors'] += len(errors)
            
            # Mover arquivo para Processados apenas se pelo menos 1 issue foi criada E não estiver em dry-run
            if len(created_issues) > 0 and not dry_run:
                move_to_processed(folder_path, csv_file)
            elif len(created_issues) == 0:
                # Apenas reportar erro se realmente não houver issues (não dry-run)
                logger.warning(f"Arquivo {csv_file} não será movido pois nenhuma issue foi criada")
                results['failed_files'].append({
                    'file': csv_file,
                    'error': 'Nenhuma issue criada com sucesso'
                })
        else:
            results['failed_files'].append({
                'file': csv_file,
                'error': bulk_result.get('message', 'Erro desconhecido')
            })
            results['total_errors'] += 1
        
        results['processed_files'].append(csv_file)
    
    return results

def move_to_processed(folder_path, csv_file):
    """
    Move arquivo processado para sub-pasta Processados
    
    Args:
        folder_path (str): Pasta original
        csv_file (str): Nome do arquivo
    """
    try:
        processed_folder = os.path.join(folder_path, "Processados")
        if not os.path.exists(processed_folder):
            os.makedirs(processed_folder)
            logger.info(f"Pasta Processados criada em {processed_folder}")
        
        source_path = os.path.join(folder_path, csv_file)
        
        # Adicionar "_prc" ao nome do arquivo
        name, ext = os.path.splitext(csv_file)
        new_filename = f"{name}_prc{ext}"
        dest_path = os.path.join(processed_folder, new_filename)
        
        # Se arquivo já existe, adiciona timestamp
        if os.path.exists(dest_path):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            dest_path = os.path.join(processed_folder, f"{name}_prc_{timestamp}{ext}")
        
        shutil.move(source_path, dest_path)
        logger.info(f"✓ Arquivo movido para Processados/ como: {new_filename}")
        
    except Exception as e:
        logger.error(f"Erro ao mover arquivo {csv_file}: {str(e)}")

def generate_report(results, output_path="issues/relatorio_processamento_csv.txt"):
    """
    Gera relatório detalhado do processamento
    
    Args:
        results (dict): Resultados do processamento
        output_path (str): Caminho do arquivo de relatório
    """
    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    report_content = f"""
{'='*70}
    RELATÓRIO DE PROCESSAMENTO CSV → JIRA
{'='*70}
Data/Hora: {timestamp}

{'='*70}
RESUMO
{'='*70}
Total de arquivos processados: {results.get('total_files', 0)}
Total de issues criadas: {results.get('total_issues_created', 0)}
Total de erros: {results.get('total_errors', 0)}

{'='*70}
ISSUES CRIADAS COM SUCESSO
{'='*70}
"""
    
    for created in results.get('created_issues', []):
        report_content += f"""
Arquivo: {created['file']}
Issues criadas: {created['issues_created']}
Erros durante criação: {created['errors']}

Issue Keys:
"""
        for issue in created['issue_keys']:
            report_content += f"  - {issue['key']}: {issue['url']}\n"
        
        if 'error_details' in created and created['error_details']:
            report_content += "\nDetalhes dos erros:\n"
            for error in created['error_details']:
                report_content += f"  - {error}\n"
        
        report_content += "\n" + "-"*70 + "\n"
    
    if results.get('failed_files'):
        report_content += f"\n{'='*70}\nFALHAS NO PROCESSAMENTO\n{'='*70}\n"
        for failed in results.get('failed_files', []):
            report_content += f"""
Arquivo: {failed['file']}
Erro: {failed['error']}
{'-'*70}
"""
    
    try:
        # Garantir que o diretório existe
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(report_content)
        logger.info(f"\n📄 Relatório salvo em: {output_path}")
    except Exception as e:
        logger.error(f"Erro ao salvar relatório: {str(e)}")

def main():
    """Função principal do script"""
    try:
        # Processar argumentos de linha de comando
        parser = argparse.ArgumentParser(
            description='Automatização de criação de issues no Jira a partir de arquivos CSV',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Exemplos de uso:
  python automatizar_issues.py              # Execução normal (cria issues no Jira)
  python automatizar_issues.py --dry-run    # Modo teste (apenas mostra o JSON)
"""
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Modo teste: mostra o JSON que seria enviado sem chamar a API do Jira'
        )
        args = parser.parse_args()
        
        logger.info("\n" + "="*70)
        if args.dry_run:
            logger.info("    AUTOMATIZAÇÃO CSV → JIRA (MODO DRY-RUN)")
        else:
            logger.info("    AUTOMATIZAÇÃO CSV → JIRA")
        logger.info("="*70)
        
        if args.dry_run:
            logger.info("⚠️  MODO DRY-RUN ATIVO: API não será chamada, apenas JSON será exibido")
        
        # Carregar configurações do .env
        jira_url, jira_token, jira_project, team_name, folder_path = load_environment()
        
        # Carregar configuração de mapeamento
        config = load_bulk_configuration()
        if not config:
            logger.error("Não foi possível carregar configuração de mapeamento")
            return
        
        # Processar arquivos CSV
        logger.info(f"\nProcessando arquivos da pasta: {folder_path}")
        results = process_csv_files(folder_path, jira_url, jira_token, config, dry_run=args.dry_run)
        
        if 'error' in results:
            logger.error(f"Erro no processamento: {results['error']}")
            return
        
        # Gerar relatório
        generate_report(results, output_path="issues/relatorio_processamento_csv.txt")
        
        # Resumo final
        logger.info("\n" + "="*70)
        logger.info("    PROCESSAMENTO CONCLUÍDO")
        logger.info("="*70)
        logger.info(f"Total de arquivos: {results['total_files']}")
        logger.info(f"Issues criadas: {results['total_issues_created']}")
        logger.info(f"Erros: {results['total_errors']}")
        
        print(f"\n{'='*70}")
        if args.dry_run:
            print(f"🔍 Dry-run concluído!")
            print(f"📊 Issues que seriam criadas: {results['total_issues_created']}")
            print(f"⚠️  Nenhuma issue foi criada (modo teste)")
        else:
            print(f"✅ Processamento concluído!")
            print(f"📊 Total de issues criadas: {results['total_issues_created']}")
            print(f"❌ Total de erros: {results['total_errors']}")
            print(f"📄 Relatório salvo: issues/relatorio_processamento_csv.txt")
        print(f"{'='*70}\n")
        
    except KeyboardInterrupt:
        logger.info("\n⚠ Processamento interrompido pelo usuário")
    except Exception as e:
        logger.error(f"\n❌ Erro geral no processamento: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    main()