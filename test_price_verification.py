#!/usr/bin/env python3
"""
Teste das funcionalidades de verificação de alterações de preços
Este script demonstra como o sistema detecta mudanças nos custos de 
materiais e máquinas e calcula o impacto nos preços dos produtos.
"""

import requests
import json
from datetime import datetime, timedelta

# Configurações do servidor
BASE_URL = "http://localhost:5000"

def test_price_verification_system():
    """
    Testa o sistema completo de verificação de alterações de preços
    """
    print("=== TESTE DO SISTEMA DE VERIFICAÇÃO DE ALTERAÇÕES DE PREÇOS ===\n")
    
    # 1. Verificar se há alterações de preços detectadas
    print("1. Verificando alterações de preços nos últimos 7 dias...")
    try:
        response = requests.post(f"{BASE_URL}/api/produtos/verificar-alteracoes-precos", 
                               json={"dias": 7})
        
        if response.status_code == 200:
            data = response.json()
            
            if data['alteracoes_detectadas']:
                print(f"✅ Alterações detectadas!")
                print(f"   - Produtos afetados: {data['resumo']['total_produtos']}")
                print(f"   - Materiais alterados: {data['resumo']['materiais_alterados']}")
                print(f"   - Máquinas alteradas: {data['resumo']['maquinas_alteradas']}")
                
                # Mostrar alguns produtos afetados
                produtos = data['produtos_afetados'][:3]  # Primeiros 3
                print("\n   Produtos mais impactados:")
                for produto in produtos:
                    variacao = produto['variacao_percentual']
                    sinal = "+" if variacao > 0 else ""
                    print(f"   - {produto['nome']}: R$ {produto['preco_atual']:.2f} → R$ {produto['novo_preco']:.2f} ({sinal}{variacao:.1f}%)")
                
            else:
                print("ℹ️  Nenhuma alteração significativa detectada nos últimos 7 dias")
                
        else:
            print(f"❌ Erro na verificação: {response.status_code}")
            print(f"   Resposta: {response.text}")
            
    except requests.RequestException as e:
        print(f"❌ Erro de conexão: {e}")
    
    print("\n" + "="*60 + "\n")
    
    # 2. Testar cálculo de novos preços
    print("2. Testando cálculo de novos preços com alterações simuladas...")
    
    # Simular alterações de materiais e máquinas
    materiais_alterados = [
        {
            "id": 1,
            "nome": "Aço Inox 304",
            "custo_anterior": 25.50,
            "custo_novo": 28.75,
            "variacao_percentual": 12.7
        },
        {
            "id": 2,
            "nome": "Tinta Acrílica Azul",
            "custo_anterior": 45.00,
            "custo_novo": 52.00,
            "variacao_percentual": 15.6
        }
    ]
    
    maquinas_alteradas = [
        {
            "id": 1,
            "nome": "Torno CNC",
            "custo_por_hora": 85.00,
            "metros_quadrados_por_hora": 2.5
        }
    ]
    
    try:
        response = requests.post(f"{BASE_URL}/api/produtos/calcular-novos-precos", 
                               json={
                                   "materiais_alterados": materiais_alterados,
                                   "maquinas_alteradas": maquinas_alteradas
                               })
        
        if response.status_code == 200:
            data = response.json()
            produtos_afetados = data['produtos_afetados']
            
            print(f"✅ Cálculo realizado com sucesso!")
            print(f"   Produtos recalculados: {len(produtos_afetados)}")
            
            # Categorizar por nível de impacto
            impacto_alto = [p for p in produtos_afetados if p['impacto'] == 'alto']
            impacto_medio = [p for p in produtos_afetados if p['impacto'] == 'medio']
            impacto_baixo = [p for p in produtos_afetados if p['impacto'] == 'baixo']
            
            print(f"\n   Impactos detectados:")
            print(f"   - Alto (>20%): {len(impacto_alto)} produtos")
            print(f"   - Médio (5-20%): {len(impacto_medio)} produtos")
            print(f"   - Baixo (<5%): {len(impacto_baixo)} produtos")
            
            # Mostrar produtos com maior impacto
            if impacto_alto:
                print(f"\n   Produtos com impacto ALTO:")
                for produto in impacto_alto[:3]:
                    print(f"   - {produto['nome']}: {produto['variacao_percentual']:+.1f}% ({produto['causa']})")
                    
        else:
            print(f"❌ Erro no cálculo: {response.status_code}")
            print(f"   Resposta: {response.text}")
            
    except requests.RequestException as e:
        print(f"❌ Erro de conexão: {e}")
    
    print("\n" + "="*60 + "\n")
    
    # 3. Testar listagem de produtos com custos detalhados
    print("3. Listando produtos com custos detalhados...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/produtos/listar")
        
        if response.status_code == 200:
            produtos = response.json()
            print(f"✅ {len(produtos)} produtos encontrados")
            
            # Mostrar alguns produtos com detalhes de custo
            print(f"\n   Primeiros 3 produtos:")
            for produto in produtos[:3]:
                custo_total = produto.get('custo_total', 0)
                custo_materiais = produto.get('custo_materiais', 0)
                custo_etapas = produto.get('custo_etapas', 0)
                preco = produto.get('preco', 0)
                margem = ((preco - custo_total) / custo_total * 100) if custo_total > 0 else 0
                
                print(f"   - {produto['nome']}:")
                print(f"     Materiais: R$ {custo_materiais:.2f} | Etapas: R$ {custo_etapas:.2f}")
                print(f"     Custo Total: R$ {custo_total:.2f} | Preço: R$ {preco:.2f} | Margem: {margem:.1f}%")
                
        else:
            print(f"❌ Erro na listagem: {response.status_code}")
            
    except requests.RequestException as e:
        print(f"❌ Erro de conexão: {e}")
    
    print("\n" + "="*60 + "\n")
    
    # 4. Testar recálculo de um produto específico
    print("4. Testando recálculo de produto específico...")
    
    try:
        # Assumindo que existe um produto com ID 1
        produto_id = 1
        response = requests.post(f"{BASE_URL}/api/produtos/{produto_id}/recalcular-preco")
        
        if response.status_code == 200:
            data = response.json()
            produto = data['produto']
            
            print(f"✅ Produto recalculado com sucesso!")
            print(f"   Produto: {produto['nome']}")
            print(f"   Preço anterior: R$ {produto['preco_anterior']:.2f}")
            print(f"   Preço atual: R$ {produto['preco']:.2f}")
            
            variacao = ((produto['preco'] - produto['preco_anterior']) / produto['preco_anterior'] * 100) if produto['preco_anterior'] > 0 else 0
            sinal = "+" if variacao > 0 else ""
            print(f"   Variação: {sinal}{variacao:.1f}%")
            
        elif response.status_code == 404:
            print(f"ℹ️  Produto ID {produto_id} não encontrado")
        else:
            print(f"❌ Erro no recálculo: {response.status_code}")
            
    except requests.RequestException as e:
        print(f"❌ Erro de conexão: {e}")
    
    print("\n" + "="*60)
    print("TESTE CONCLUÍDO")
    print("="*60)

def test_price_update_simulation():
    """
    Simula o fluxo completo de detecção e aplicação de atualizações de preços
    """
    print("\n=== SIMULAÇÃO DE ATUALIZAÇÃO DE PREÇOS ===\n")
    
    # Simular produtos que precisam de atualização
    produtos_para_atualizar = [
        {
            "id": 1,
            "novo_preco": 125.75,
            "preco_anterior": 115.50
        },
        {
            "id": 2,
            "novo_preco": 89.90,
            "preco_anterior": 82.30
        }
    ]
    
    try:
        response = requests.post(f"{BASE_URL}/api/produtos/atualizar-precos",
                               json={"produtos": produtos_para_atualizar})
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Atualização realizada com sucesso!")
            print(f"   Produtos atualizados: {data['atualizados']}")
            
            if data['erros']:
                print(f"   Erros encontrados: {len(data['erros'])}")
                for erro in data['erros']:
                    print(f"   - {erro}")
        else:
            print(f"❌ Erro na atualização: {response.status_code}")
            print(f"   Resposta: {response.text}")
            
    except requests.RequestException as e:
        print(f"❌ Erro de conexão: {e}")

if __name__ == "__main__":
    print(f"Iniciando testes em {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Servidor: {BASE_URL}")
    print()
    
    # Verificar se o servidor está rodando
    try:
        response = requests.get(f"{BASE_URL}/dashboard")
        if response.status_code == 200:
            print("✅ Servidor Flask está rodando")
        else:
            print("⚠️  Servidor responde mas pode haver problemas")
    except requests.RequestException:
        print("❌ Servidor Flask não está rodando")
        print("   Execute 'python flask_gui.py' primeiro")
        exit(1)
    
    print()
    
    # Executar testes
    test_price_verification_system()
    test_price_update_simulation()
    
    print(f"\nTestes finalizados em {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
