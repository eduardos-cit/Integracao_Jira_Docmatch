#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste para função move_to_processed()

Testa se arquivos são movidos corretamente para a sub-pasta Processados
"""

import sys
import os
import shutil
from datetime import datetime

# Adicionar diretório pai ao path para importar o módulo
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from automatizar_issues import move_to_processed

def test_move_to_processed():
    """Testa movimentação de arquivos para pasta Processados"""
    print("="*60)
    print("TESTE: move_to_processed()")
    print("="*60)
    
    test_folder = "test_temp_folder"
    test_file = "test_file.csv"
    
    try:
        # Criar estrutura de teste
        print("\n📁 Criando estrutura de teste...")
        
        if not os.path.exists(test_folder):
            os.makedirs(test_folder)
        
        test_file_path = os.path.join(test_folder, test_file)
        
        # Criar arquivo de teste
        with open(test_file_path, 'w', encoding='utf-8') as f:
            f.write("Issue Type,Summary\n")
            f.write("Task,Teste de movimentação\n")
        
        print(f"  ✓ Arquivo criado: {test_file_path}")
        
        # Verificar que arquivo existe antes do teste
        assert os.path.exists(test_file_path), "Arquivo de teste não foi criado"
        
        # Executar função de movimentação
        print(f"\n📦 Movendo arquivo para Processados...")
        move_to_processed(test_folder, test_file)
        
        # Verificar resultados
        processed_folder = os.path.join(test_folder, "Processados")
        processed_file_path = os.path.join(processed_folder, test_file)
        
        # Verificar que pasta Processados foi criada
        assert os.path.exists(processed_folder), "Pasta Processados não foi criada"
        print(f"  ✓ Pasta Processados existe: {processed_folder}")
        
        # Verificar que arquivo foi movido
        assert os.path.exists(processed_file_path), "Arquivo não foi movido"
        print(f"  ✓ Arquivo movido: {processed_file_path}")
        
        # Verificar que arquivo original não existe mais
        assert not os.path.exists(test_file_path), "Arquivo original ainda existe"
        print(f"  ✓ Arquivo original removido")
        
        # Testar movimentação de arquivo duplicado (com timestamp)
        print(f"\n📦 Testando movimentação de arquivo duplicado...")
        
        # Criar outro arquivo com mesmo nome
        with open(test_file_path, 'w', encoding='utf-8') as f:
            f.write("Issue Type,Summary\n")
            f.write("Task,Teste de movimentação duplicado\n")
        
        move_to_processed(test_folder, test_file)
        
        # Verificar que existem 2 arquivos na pasta Processados
        files_in_processed = os.listdir(processed_folder)
        assert len(files_in_processed) >= 2, "Arquivo duplicado não foi criado com timestamp"
        print(f"  ✓ Arquivo duplicado movido com timestamp")
        print(f"  Arquivos em Processados: {files_in_processed}")
        
        print("\n✅ TESTE PASSOU - Arquivos movidos corretamente")
        return True
        
    except Exception as e:
        print(f"\n❌ TESTE FALHOU - Erro: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return False
        
    finally:
        # Limpar estrutura de teste
        print(f"\n🧹 Limpando arquivos de teste...")
        if os.path.exists(test_folder):
            shutil.rmtree(test_folder)
            print(f"  ✓ Pasta de teste removida: {test_folder}")

if __name__ == "__main__":
    success = test_move_to_processed()
    sys.exit(0 if success else 1)
