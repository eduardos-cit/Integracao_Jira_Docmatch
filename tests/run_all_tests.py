#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Executor de todos os testes

Executa todos os scripts de teste e gera relatório consolidado
"""

import sys
import os
import subprocess
from datetime import datetime

def run_test(test_file, test_name):
    """
    Executa um teste individual
    
    Args:
        test_file (str): Caminho do arquivo de teste
        test_name (str): Nome descritivo do teste
        
    Returns:
        tuple: (sucesso, tempo_execução)
    """
    print(f"\n{'='*70}")
    print(f"Executando: {test_name}")
    print(f"{'='*70}")
    
    start_time = datetime.now()
    
    # Define working directory como a raiz do projeto (diretório pai de tests/)
    tests_dir = os.path.dirname(__file__) or '.'
    project_root = os.path.abspath(os.path.join(tests_dir, '..'))
    
    try:
        result = subprocess.run(
            [sys.executable, test_file],
            capture_output=False,
            text=True,
            cwd=project_root
        )
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        success = result.returncode == 0
        return success, duration
        
    except Exception as e:
        print(f"❌ Erro ao executar teste: {str(e)}")
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        return False, duration

def main():
    """Executa todos os testes"""
    print("\n" + "="*70)
    print("  SUITE DE TESTES - AUTOMATIZAÇÃO JIRA")
    print("="*70)
    print(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    tests_dir = os.path.dirname(__file__) or '.'
    
    tests = [
        ("test_load_environment.py", "Teste 1: Carregamento de Variáveis de Ambiente"),
        ("test_load_bulk_configuration.py", "Teste 2: Carregamento de Configuração"),
        ("test_parse_csv.py", "Teste 3: Parsing de CSV"),
        ("test_move_to_processed.py", "Teste 4: Movimentação de Arquivos"),
        ("test_jira_connection.py", "Teste 5: Conexão com API Jira"),
        ("test_bulk_create_api.py", "Teste 6: Validação Bulk Create API"),
    ]
    
    results = []
    total_duration = 0
    
    for test_file, test_name in tests:
        test_path = os.path.join(tests_dir, test_file)
        
        if not os.path.exists(test_path):
            print(f"\n⚠️  Arquivo de teste não encontrado: {test_file}")
            results.append((test_name, False, 0))
            continue
        
        success, duration = run_test(test_path, test_name)
        results.append((test_name, success, duration))
        total_duration += duration
    
    # Relatório Final
    print("\n" + "="*70)
    print("  RELATÓRIO FINAL")
    print("="*70)
    
    passed = sum(1 for _, success, _ in results if success)
    failed = len(results) - passed
    
    print(f"\nTotal de testes: {len(results)}")
    print(f"✅ Passaram: {passed}")
    print(f"❌ Falharam: {failed}")
    print(f"⏱️  Tempo total: {total_duration:.2f}s")
    
    print("\nDetalhes:")
    for test_name, success, duration in results:
        status = "✅ PASSOU" if success else "❌ FALHOU"
        print(f"  {status} - {test_name} ({duration:.2f}s)")
    
    print("\n" + "="*70)
    
    if failed == 0:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("="*70 + "\n")
        return 0
    else:
        print(f"⚠️  {failed} TESTE(S) FALHARAM")
        print("="*70 + "\n")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
