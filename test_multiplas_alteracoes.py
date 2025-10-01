#!/usr/bin/env python3
"""
Script para testar múltiplas alterações de preços no produto ID 62
Simula alterações em vários materiais e máquinas para verificar detecção completa
"""

import mysql.connector
from datetime import datetime
import requests
import json
import time

def conectar_bd():
    """Conecta ao banco de dados MySQL"""
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='als32@#nss',
        database='midnight'
    )

def verificar_estado_inicial():
    """Verifica o estado inicial do produto 62"""
    conn = conectar_bd()
    cursor = conn.cursor(dictionary=True)
    
    print("=" * 60)
    print("TESTE DE MÚLTIPLAS ALTERAÇÕES - PRODUTO ID 62")
    print("=" * 60)
    
    # Buscar informações do produto
    cursor.execute('SELECT * FROM produtos WHERE id = 62')
    produto = cursor.fetchone()
    
    print(f"Produto: {produto['nome']} (Código: {produto['codigo']})")
    print(f"Preço atual: R$ {produto['preco']:.2f}")
    print(f"Custo materiais: R$ {produto['custo_materiais']:.2f}")
    print(f"Custo etapas: R$ {produto['custo_etapas']:.2f}")
    
    # Buscar materiais
    cursor.execute('''
        SELECT pm.*, ie.nome as material_nome
        FROM produtos_materiais pm
        JOIN itens_estoque ie ON pm.material_id = ie.id
        WHERE pm.produto_id = 62
    ''')
    materiais = cursor.fetchall()
    
    print(f"\n=== MATERIAIS ATUAIS ({len(materiais)} itens) ===")
    for i, material in enumerate(materiais, 1):
        print(f"{i}. {material['material_nome']} (ID {material['material_id']})")
        print(f"   Quantidade: {material['quantidade_necessaria']}")
        print(f"   Custo unitário: R$ {material['custo_unitario']:.2f}")
        print(f"   Subtotal: R$ {material['subtotal']:.2f}")
    
    # Buscar etapas com máquinas
    cursor.execute('''
        SELECT pe.*, m.nome as maquina_nome, m.hora_maquina
        FROM produtos_etapas pe
        LEFT JOIN maquinas m ON pe.equipamento_id = m.id AND pe.equipamento_tipo = 'maquina'
        WHERE pe.produto_id = 62
    ''')
    etapas = cursor.fetchall()
    
    print(f"\n=== ETAPAS ATUAIS ({len(etapas)} itens) ===")
    for i, etapa in enumerate(etapas, 1):
        print(f"{i}. {etapa['nome']} ({etapa['equipamento_tipo']})")
        if etapa['maquina_nome']:
            print(f"   Máquina: {etapa['maquina_nome']} (ID {etapa['equipamento_id']})")
            print(f"   Valor/hora: R$ {etapa['hora_maquina']:.2f}")
        print(f"   Tempo: {etapa['tempo_estimado']}")
        print(f"   Custo: R$ {etapa['custo_estimado']:.2f}")
    
    conn.close()
    return produto, materiais, etapas

def simular_alteracao_material(material_id, novo_custo, nome_material):
    """Simula nova entrada de estoque para um material"""
    conn = conectar_bd()
    cursor = conn.cursor()
    
    print(f"\n📦 ALTERANDO MATERIAL: {nome_material}")
    print(f"   Novo custo: R$ {novo_custo:.2f}")
    
    # Verificar último custo
    cursor.execute('''
        SELECT custo_unitario FROM entradas_estoque 
        WHERE item_id = %s
        ORDER BY data_entrada DESC, id DESC
        LIMIT 1
    ''', (material_id,))
    
    ultimo_custo = cursor.fetchone()
    if ultimo_custo:
        custo_anterior = float(ultimo_custo[0])
        print(f"   Custo anterior: R$ {custo_anterior:.2f}")
        variacao = ((novo_custo - custo_anterior) / custo_anterior) * 100
        print(f"   Variação: {variacao:+.3f}%")
    
    # Inserir nova entrada
    cursor.execute('''
        INSERT INTO entradas_estoque 
        (item_id, quantidade, custo_unitario, data_entrada, fornecedor, observacoes)
        VALUES (%s, %s, %s, %s, %s, %s)
    ''', (
        material_id,
        1,
        novo_custo,
        datetime.now().date(),
        'Fornecedor Teste',
        f'Teste múltiplas alterações - novo custo R$ {novo_custo:.2f}'
    ))
    
    entrada_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    print(f"   ✅ Nova entrada criada: ID {entrada_id}")
    return entrada_id

def simular_alteracao_maquina(maquina_id, novo_valor_hora, nome_maquina):
    """Simula alteração do valor/hora de uma máquina"""
    conn = conectar_bd()
    cursor = conn.cursor()
    
    print(f"\n🔧 ALTERANDO MÁQUINA: {nome_maquina}")
    print(f"   Novo valor/hora: R$ {novo_valor_hora:.2f}")
    
    # Verificar valor atual
    cursor.execute('SELECT hora_maquina FROM maquinas WHERE id = %s', (maquina_id,))
    valor_atual = cursor.fetchone()
    if valor_atual:
        valor_anterior = float(valor_atual[0])
        print(f"   Valor anterior: R$ {valor_anterior:.2f}")
        variacao = ((novo_valor_hora - valor_anterior) / valor_anterior) * 100
        print(f"   Variação: {variacao:+.3f}%")
    
    # Registrar no histórico antes de alterar
    cursor.execute('''
        INSERT INTO historico_custos_maquinas 
        (maquina_id, hora_maquina_anterior, hora_maquina_nova, data_alteracao, usuario_responsavel, observacoes)
        VALUES (%s, %s, %s, %s, %s, %s)
    ''', (
        maquina_id,
        valor_anterior if valor_atual else 0,
        novo_valor_hora,
        datetime.now(),
        'Sistema Teste',
        f'Teste múltiplas alterações - novo valor R$ {novo_valor_hora:.2f}/h'
    ))
    
    # Atualizar valor na tabela maquinas
    cursor.execute('UPDATE maquinas SET hora_maquina = %s WHERE id = %s', (novo_valor_hora, maquina_id))
    
    historico_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    print(f"   ✅ Histórico registrado: ID {historico_id}")
    return historico_id

def verificar_deteccao_api():
    """Verifica se a API detecta todas as alterações"""
    print(f"\n🔍 VERIFICANDO DETECÇÃO VIA API...")
    
    try:
        url = 'http://localhost:8000/api/produtos/62/detalhes-calculo'
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            
            print("✅ API respondeu com sucesso!")
            print(f"   Custo etapas: R$ {data['custo_etapas']:.2f}")
            
            # Verificar materiais
            materiais = data.get('materiais', [])
            materiais_alterados = 0
            for material in materiais:
                print(f"\n📦 Material: {material['nome']}")
                print(f"   Custo atual: R$ {material['custo_unitario']:.2f}")
                
                if material.get('custo_unitario_novo'):
                    print(f"   🚨 ALTERAÇÃO DETECTADA!")
                    print(f"   Custo novo: R$ {material['custo_unitario_novo']:.2f}")
                    variacao = ((material['custo_unitario_novo'] - material['custo_unitario']) / material['custo_unitario']) * 100
                    print(f"   Variação: {variacao:+.3f}%")
                    materiais_alterados += 1
                else:
                    print(f"   ❌ Nenhuma alteração detectada")
            
            # Mostrar novo custo total
            print(f"\n💰 RESUMO DOS CUSTOS:")
            print(f"   Custo materiais: R$ {data['produto']['custo_materiais']:.2f}")
            print(f"   Custo etapas: R$ {data['custo_etapas']:.2f}")
            print(f"   Custo total: R$ {data['produto']['custo_total']:.2f}")
            print(f"   Preço atual produto: R$ {data['produto']['preco_atual']:.2f}")
            
            print(f"\n📊 ESTATÍSTICAS:")
            print(f"   Materiais com alteração detectada: {materiais_alterados}/{len(materiais)}")
            
            return data
        else:
            print(f"❌ Erro na API: {response.status_code}")
            print(response.text)
            return None
    
    except Exception as e:
        print(f"❌ Erro ao consultar API: {e}")
        return None

def main():
    """Função principal do teste"""
    
    # 1. Verificar estado inicial
    produto, materiais, etapas = verificar_estado_inicial()
    
    print(f"\n" + "=" * 60)
    print("INICIANDO SIMULAÇÃO DE MÚLTIPLAS ALTERAÇÕES")
    print("=" * 60)
    
    # 2. Simular alterações nos materiais
    alteracoes_materiais = []
    
    # Material 1: Chapa de ACM (ID 99) - Reduzir preço
    if len(materiais) >= 1:
        material1 = materiais[0]
        entrada_id1 = simular_alteracao_material(
            material1['material_id'], 
            800.00,  # Redução significativa para R$ 800
            material1['material_nome']
        )
        alteracoes_materiais.append(entrada_id1)
    
    # Material 2: Parafuso (ID 98) - Aumentar preço  
    if len(materiais) >= 2:
        material2 = materiais[1]
        entrada_id2 = simular_alteracao_material(
            material2['material_id'],
            30.00,  # Aumento para R$ 30
            material2['material_nome']
        )
        alteracoes_materiais.append(entrada_id2)
    
    # 3. Simular alterações nas máquinas
    alteracoes_maquinas = []
    
    # Máquina: Router VUZE (ID 9) - Aumentar valor/hora
    if len(etapas) >= 1 and etapas[0]['equipamento_tipo'] == 'maquina':
        etapa1 = etapas[0]
        historico_id1 = simular_alteracao_maquina(
            etapa1['equipamento_id'],
            20.00,  # Aumento mais significativo para R$ 20
            etapa1['maquina_nome']
        )
        alteracoes_maquinas.append(historico_id1)
    
    # 4. Aguardar processamento
    print(f"\n⏳ Aguardando processamento das alterações...")
    time.sleep(3)
    
    # 5. Verificar detecção via API
    print(f"\n" + "=" * 60)
    print("VERIFICANDO DETECÇÃO DAS ALTERAÇÕES")
    print("=" * 60)
    
    resultado_api = verificar_deteccao_api()
    
    # 6. Resumo final
    print(f"\n" + "=" * 60)
    print("RESUMO DO TESTE")
    print("=" * 60)
    print(f"Produto testado: {produto['nome']} (ID 62)")
    print(f"Alterações em materiais: {len(alteracoes_materiais)}")
    print(f"Alterações em máquinas: {len(alteracoes_maquinas)}")
    
    if resultado_api:
        print(f"✅ API funcionou corretamente")
        print(f"🔍 Verifique o modal de atualização de preços no frontend para ver todas as alterações!")
    else:
        print(f"❌ Problemas na API - verifique logs")
    
    print(f"\n" + "=" * 60)

if __name__ == "__main__":
    main()
