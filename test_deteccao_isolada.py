#!/usr/bin/env python3
"""
Teste para verificar se o sistema detecta corretamente oscilações isoladas:
- APENAS em materiais (sem mudanças em máquinas)
- APENAS em máquinas (sem mudanças em materiais)
- Em ambos (cenário já testado)

Este teste valida se o sistema de atualização de preços funciona para todos os casos.
"""

import requests
import json
from datetime import datetime, timedelta
from database import Database

BASE_URL = "http://localhost:8000"

def simular_alteracao_apenas_material():
    """
    Simula uma alteração APENAS em material, sem alterar máquinas
    """
    print("\n" + "="*60)
    print("🧪 TESTE 1: ALTERAÇÃO APENAS EM MATERIAL")
    print("="*60)
    
    try:
        # Simular mudança apenas em materiais
        dados = {
            "materiais_ids": [99],  # ID do material que afeta o produto (Chapa ACM)
            "maquinas_ids": []        # Nenhuma máquina alterada
        }
        
        print(f"📋 Enviando dados: {dados}")
        
        response = requests.post(
            f"{BASE_URL}/api/produtos/verificar-mudancas-custos",
            json=dados,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"📡 Status da resposta: {response.status_code}")
        
        if response.status_code == 200:
            resultado = response.json()
            
            print(f"✅ Status: {resultado['status']}")
            print(f"📊 Produtos afetados: {resultado['total_produtos']}")
            print(f"🔧 Materiais alterados: {len(resultado['materiais_alterados'])}")
            print(f"⚙️ Máquinas alteradas: {len(resultado['maquinas_alteradas'])}")
            
            if resultado['total_produtos'] > 0:
                print("✅ SUCESSO: Sistema detectou produtos afetados por alteração APENAS em materiais")
                
                # Mostrar alguns produtos afetados
                print("\n📦 Produtos afetados:")
                for i, produto in enumerate(resultado['produtos_afetados']):
                    if i >= 3:  # Mostrar apenas os primeiros 3
                        break
                    print(f"   - {produto['nome']}: R$ {produto['preco_atual']:.2f} → R$ {produto['novo_preco']:.2f}")
                
                return True
            else:
                print("❌ FALHA: Sistema NÃO detectou produtos afetados por alteração em materiais")
                return False
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
            print(f"📄 Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def simular_alteracao_apenas_maquina():
    """
    Simula uma alteração APENAS em máquina, sem alterar materiais
    """
    print("\n" + "="*60)
    print("🧪 TESTE 2: ALTERAÇÃO APENAS EM MÁQUINA")
    print("="*60)
    
    try:
        # Simular mudança apenas em máquinas
        dados = {
            "materiais_ids": [],      # Nenhum material alterado
            "maquinas_ids": [9]    # ID da máquina que afeta o produto (Router VUZE)
        }
        
        print(f"📋 Enviando dados: {dados}")
        
        response = requests.post(
            f"{BASE_URL}/api/produtos/verificar-mudancas-custos",
            json=dados,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"📡 Status da resposta: {response.status_code}")
        
        if response.status_code == 200:
            resultado = response.json()
            
            print(f"✅ Status: {resultado['status']}")
            print(f"📊 Produtos afetados: {resultado['total_produtos']}")
            print(f"🔧 Materiais alterados: {len(resultado['materiais_alterados'])}")
            print(f"⚙️ Máquinas alteradas: {len(resultado['maquinas_alteradas'])}")
            
            if resultado['total_produtos'] > 0:
                print("✅ SUCESSO: Sistema detectou produtos afetados por alteração APENAS em máquinas")
                
                # Mostrar alguns produtos afetados
                print("\n📦 Produtos afetados:")
                for i, produto in enumerate(resultado['produtos_afetados']):
                    if i >= 3:  # Mostrar apenas os primeiros 3
                        break
                    print(f"   - {produto['nome']}: R$ {produto['preco_atual']:.2f} → R$ {produto['novo_preco']:.2f}")
                
                return True
            else:
                print("❌ FALHA: Sistema NÃO detectou produtos afetados por alteração em máquinas")
                return False
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
            print(f"📄 Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def simular_alteracao_ambos():
    """
    Simula alterações em AMBOS materiais e máquinas (cenário já testado)
    """
    print("\n" + "="*60)
    print("🧪 TESTE 3: ALTERAÇÃO EM MATERIAIS E MÁQUINAS")
    print("="*60)
    
    try:
        # Simular mudança em ambos
        dados = {
            "materiais_ids": [99],  # ID do material que afeta o produto
            "maquinas_ids": [9]    # ID da máquina que afeta o produto
        }
        
        print(f"📋 Enviando dados: {dados}")
        
        response = requests.post(
            f"{BASE_URL}/api/produtos/verificar-mudancas-custos",
            json=dados,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"📡 Status da resposta: {response.status_code}")
        
        if response.status_code == 200:
            resultado = response.json()
            
            print(f"✅ Status: {resultado['status']}")
            print(f"📊 Produtos afetados: {resultado['total_produtos']}")
            print(f"🔧 Materiais alterados: {len(resultado['materiais_alterados'])}")
            print(f"⚙️ Máquinas alteradas: {len(resultado['maquinas_alteradas'])}")
            
            if resultado['total_produtos'] > 0:
                print("✅ SUCESSO: Sistema detectou produtos afetados por alteração em AMBOS materiais e máquinas")
                
                # Mostrar alguns produtos afetados
                print("\n📦 Produtos afetados:")
                for i, produto in enumerate(resultado['produtos_afetados']):
                    if i >= 3:  # Mostrar apenas os primeiros 3
                        break
                    print(f"   - {produto['nome']}: R$ {produto['preco_atual']:.2f} → R$ {produto['novo_preco']:.2f}")
                
                return True
            else:
                print("❌ FALHA: Sistema NÃO detectou produtos afetados por alteração mista")
                return False
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
            print(f"📄 Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def testar_api_verificacao_alteracoes_precos():
    """
    Testa a API principal de verificação de alterações de preços
    """
    print("\n" + "="*60)
    print("🧪 TESTE 4: API VERIFICAÇÃO ALTERAÇÕES (7 DIAS)")
    print("="*60)
    
    try:
        dados = {"dias": 7}
        
        response = requests.post(
            f"{BASE_URL}/api/produtos/verificar-alteracoes-precos",
            json=dados,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"📡 Status da resposta: {response.status_code}")
        
        if response.status_code == 200:
            resultado = response.json()
            
            print(f"🔍 Alterações detectadas: {resultado['alteracoes_detectadas']}")
            
            if resultado['alteracoes_detectadas']:
                print(f"📊 Total de produtos afetados: {resultado['resumo']['total_produtos']}")
                print(f"🔧 Materiais alterados: {resultado['resumo']['materiais_alterados']}")
                print(f"⚙️ Máquinas alteradas: {resultado['resumo']['maquinas_alteradas']}")
                
                # Mostrar alguns produtos afetados
                if resultado['produtos_afetados']:
                    print("\n📦 Produtos afetados:")
                    for i, produto in enumerate(resultado['produtos_afetados']):
                        if i >= 3:  # Mostrar apenas os primeiros 3
                            break
                        print(f"   - {produto['nome']}: R$ {produto['preco_atual']:.2f} → R$ {produto['novo_preco']:.2f}")
                
                return True
            else:
                print("ℹ️ Nenhuma alteração detectada nos últimos 7 dias")
                return True  # Isso é válido
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
            print(f"📄 Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def verificar_dados_sistema():
    """
    Verifica se existem dados suficientes no sistema para os testes
    """
    print("\n" + "="*60)
    print("🔍 VERIFICAÇÃO DOS DADOS DO SISTEMA")
    print("="*60)
    
    try:
        db = Database()
        
        # Verificar materiais disponíveis
        db.cursor.execute("SELECT COUNT(*) as total FROM itens_estoque WHERE custo_atual > 0 OR custo_medio > 0")
        materiais_count = db.cursor.fetchone()['total']
        print(f"🔧 Materiais disponíveis: {materiais_count}")
        
        # Verificar máquinas disponíveis
        db.cursor.execute("SELECT COUNT(*) as total FROM maquinas WHERE hora_maquina > 0")
        maquinas_count = db.cursor.fetchone()['total']
        print(f"⚙️ Máquinas disponíveis: {maquinas_count}")
        
        # Verificar produtos disponíveis
        db.cursor.execute("SELECT COUNT(*) as total FROM produtos")
        produtos_count = db.cursor.fetchone()['total']
        print(f"📦 Produtos disponíveis: {produtos_count}")
        
        # Verificar produtos com materiais
        db.cursor.execute("""
            SELECT COUNT(DISTINCT p.id) as total 
            FROM produtos p 
            INNER JOIN produtos_materiais pm ON p.id = pm.produto_id
        """)
        produtos_com_materiais = db.cursor.fetchone()['total']
        print(f"📋 Produtos com materiais: {produtos_com_materiais}")
        
        # Verificar produtos com etapas
        db.cursor.execute("""
            SELECT COUNT(DISTINCT p.id) as total 
            FROM produtos p 
            INNER JOIN produtos_etapas pe ON p.id = pe.produto_id
        """)
        produtos_com_etapas = db.cursor.fetchone()['total']
        print(f"⚙️ Produtos com etapas: {produtos_com_etapas}")
        
        db.close()
        
        # Verificar se há dados suficientes
        if materiais_count > 0 and maquinas_count > 0 and produtos_count > 0:
            print("✅ Sistema possui dados suficientes para os testes")
            return True
        else:
            print("❌ Sistema não possui dados suficientes para os testes")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao verificar dados: {e}")
        return False

def main():
    """
    Executa todos os testes de detecção isolada
    """
    print("🚀 TESTE DE DETECÇÃO DE OSCILAÇÕES ISOLADAS")
    print("=" * 80)
    print(f"📅 Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Servidor: {BASE_URL}")
    
    # Verificar se o servidor está rodando
    try:
        response = requests.get(f"{BASE_URL}/dashboard", timeout=5)
        if response.status_code != 200:
            print("❌ Servidor Flask não está respondendo corretamente")
            return
    except:
        print("❌ Não foi possível conectar ao servidor Flask")
        print("   Certifique-se de que o servidor está rodando na porta 8000")
        return
    
    print("✅ Servidor Flask está rodando")
    
    # Verificar dados do sistema
    if not verificar_dados_sistema():
        print("❌ Teste cancelado devido à falta de dados no sistema")
        return
    
    # Executar todos os testes
    resultados = []
    
    print("\n" + "🔬 INICIANDO TESTES DE DETECÇÃO" + "\n")
    
    # Teste 1: Apenas materiais
    resultado1 = simular_alteracao_apenas_material()
    resultados.append(("Alteração apenas em materiais", resultado1))
    
    # Teste 2: Apenas máquinas
    resultado2 = simular_alteracao_apenas_maquina()
    resultados.append(("Alteração apenas em máquinas", resultado2))
    
    # Teste 3: Ambos (materiais e máquinas)
    resultado3 = simular_alteracao_ambos()
    resultados.append(("Alteração em materiais e máquinas", resultado3))
    
    # Teste 4: API principal de verificação
    resultado4 = testar_api_verificacao_alteracoes_precos()
    resultados.append(("API verificação alterações (7 dias)", resultado4))
    
    # Resumo dos resultados
    print("\n" + "="*80)
    print("📊 RESUMO DOS RESULTADOS")
    print("="*80)
    
    sucessos = 0
    for nome, sucesso in resultados:
        status = "✅ PASSOU" if sucesso else "❌ FALHOU"
        print(f"{status} - {nome}")
        if sucesso:
            sucessos += 1
    
    print(f"\n📈 Taxa de sucesso: {sucessos}/{len(resultados)} ({sucessos/len(resultados)*100:.1f}%)")
    
    # Conclusão
    if sucessos == len(resultados):
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("✅ O sistema detecta corretamente oscilações isoladas em materiais OU máquinas")
    elif sucessos >= len(resultados) - 1:
        print("\n⚠️ QUASE TODOS OS TESTES PASSARAM")
        print("🔧 O sistema funciona na maioria dos casos, mas pode precisar de ajustes menores")
    else:
        print("\n❌ VÁRIOS TESTES FALHARAM")
        print("🔧 O sistema precisa de correções na lógica de detecção")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    main()
