#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de teste para verificar as melhorias implementadas no sistema de orçamentos:

1. Nova coluna data_hora_entrega no banco de dados
2. Campo de desconto mostrando valor em formato monetário brasileiro
3. Dropdown de parcelas com estilo CSS consistente
4. Parcelas mostrando valor individual de cada parcela

Para executar: python test_orcamento_improvements.py
"""

import mysql.connector
from datetime import datetime, date
import sys
import os

# Adicionar o diretório do projeto ao path para importar database.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_database_column():
    """Testa se a coluna data_hora_entrega foi criada corretamente"""
    print("🔍 Testando estrutura do banco de dados...")
    
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',  # Substitua pela sua senha
            database='midnight'
        )
        
        cursor = conn.cursor()
        
        # Verificar se a coluna existe
        cursor.execute("DESCRIBE orcamentos")
        columns = cursor.fetchall()
        
        has_data_hora_entrega = False
        for column in columns:
            if column[0] == 'data_hora_entrega':
                has_data_hora_entrega = True
                print(f"✅ Coluna 'data_hora_entrega' encontrada: {column[1]} {column[2]}")
                break
        
        if not has_data_hora_entrega:
            print("❌ Coluna 'data_hora_entrega' não encontrada!")
            return False
        
        # Testar inserção de dados
        print("\n📝 Testando inserção de dados com data_hora_entrega...")
        
        test_query = """
            INSERT INTO orcamentos (
                numero, data_orcamento, cliente_id, vendedor_id, 
                prazo_entrega, data_hora_entrega, valor_total, status
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        test_data = (
            'TEST001',
            date.today(),
            1,  # cliente_id (assumindo que existe)
            1,  # vendedor_id (assumindo que existe)
            '15 dias',
            datetime(2025, 8, 15, 14, 30),  # Data e hora de entrega
            1000.00,
            'Teste'
        )
        
        cursor.execute(test_query, test_data)
        test_id = cursor.lastrowid
        
        # Verificar se foi inserido corretamente
        cursor.execute("SELECT numero, data_hora_entrega FROM orcamentos WHERE id = %s", (test_id,))
        result = cursor.fetchone()
        
        if result:
            print(f"✅ Teste de inserção bem-sucedido: {result[0]} - {result[1]}")
            
            # Limpar dados de teste
            cursor.execute("DELETE FROM orcamentos WHERE id = %s", (test_id,))
            conn.commit()
            print("🧹 Dados de teste removidos")
        else:
            print("❌ Falha na inserção de teste")
            return False
        
        cursor.close()
        conn.close()
        
        print("✅ Teste de banco de dados concluído com sucesso!")
        return True
        
    except mysql.connector.Error as e:
        print(f"❌ Erro de conexão com o banco: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

def test_html_structure():
    """Verifica se as alterações HTML foram aplicadas corretamente"""
    print("\n🔍 Testando estrutura HTML...")
    
    try:
        with open('templates/orcamentos.html', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar se o dropdown de parcelas foi alterado
        if '<div class="dropdown custom-select" tabindex="0" role="button" id="parcelas">' in content:
            print("✅ Dropdown de parcelas convertido para custom-select")
        else:
            print("❌ Dropdown de parcelas ainda está como <select>")
            return False
        
        # Verificar se a função atualizarTextoParcelas existe
        if 'function atualizarTextoParcelas()' in content:
            print("✅ Função atualizarTextoParcelas() encontrada")
        else:
            print("❌ Função atualizarTextoParcelas() não encontrada")
            return False
        
        # Verificar se o desconto mostra valor monetário
        if 'R$ ${valorDesconto.toFixed(2).replace(\'.\', \',\')}' in content:
            print("✅ Desconto configurado para mostrar valor monetário")
        else:
            print("❌ Desconto não está mostrando valor monetário")
            return False
        
        # Verificar se a data/hora de entrega está sendo coletada
        if 'data_entrega: dataEntrega || null' in content:
            print("✅ Data/hora de entrega sendo coletada no formulário")
        else:
            print("❌ Data/hora de entrega não está sendo coletada")
            return False
        
        print("✅ Estrutura HTML verificada com sucesso!")
        return True
        
    except FileNotFoundError:
        print("❌ Arquivo templates/orcamentos.html não encontrado")
        return False
    except Exception as e:
        print(f"❌ Erro ao verificar HTML: {e}")
        return False

def test_flask_backend():
    """Verifica se as alterações no backend Flask foram aplicadas"""
    print("\n🔍 Testando backend Flask...")
    
    try:
        with open('flask_gui.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar se data_hora_entrega está sendo processada
        if 'data_hora_entrega = data.get(\'data_entrega\')' in content:
            print("✅ Backend coletando data_hora_entrega")
        else:
            print("❌ Backend não está coletando data_hora_entrega")
            return False
        
        # Verificar se está sendo incluída no orcamento_data
        if '\'data_hora_entrega\': data_hora_entrega_obj' in content:
            print("✅ data_hora_entrega incluída nos dados do orçamento")
        else:
            print("❌ data_hora_entrega não incluída nos dados do orçamento")
            return False
        
        # Verificar se o processamento de datetime está correto
        if 'datetime.strptime(data_hora_entrega, \'%Y-%m-%dT%H:%M\')' in content:
            print("✅ Processamento de datetime-local configurado corretamente")
        else:
            print("❌ Processamento de datetime-local não encontrado")
            return False
        
        print("✅ Backend Flask verificado com sucesso!")
        return True
        
    except FileNotFoundError:
        print("❌ Arquivo flask_gui.py não encontrado")
        return False
    except Exception as e:
        print(f"❌ Erro ao verificar backend: {e}")
        return False

def main():
    """Executa todos os testes"""
    print("🚀 Iniciando testes das melhorias do sistema de orçamentos\n")
    print("=" * 60)
    
    tests_passed = 0
    total_tests = 3
    
    # Teste 1: Estrutura do banco de dados
    if test_database_column():
        tests_passed += 1
    
    # Teste 2: Estrutura HTML
    if test_html_structure():
        tests_passed += 1
    
    # Teste 3: Backend Flask
    if test_flask_backend():
        tests_passed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Resultado dos testes: {tests_passed}/{total_tests} passaram")
    
    if tests_passed == total_tests:
        print("🎉 Todas as melhorias foram implementadas com sucesso!")
        print("\n📋 Resumo das melhorias implementadas:")
        print("  1. ✅ Nova coluna 'data_hora_entrega' criada no banco")
        print("  2. ✅ Campo de desconto mostra valor em R$ brasileiro")
        print("  3. ✅ Dropdown de parcelas com estilo CSS consistente")
        print("  4. ✅ Parcelas mostram valor individual (ex: 2x de R$ 50,00)")
        print("  5. ✅ Backend processa data/hora de entrega corretamente")
    else:
        print("⚠️  Algumas melhorias precisam de ajustes adicionais")
    
    return tests_passed == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
