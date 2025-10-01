#!/usr/bin/env python3
"""
Script para testar alteração de custo de material
Simula nova entrada de estoque com custo diferente e verifica detecção no sistema
"""

import sqlite3
from datetime import datetime
import requests
import json

def conectar_bd():
    """Conecta ao banco de dados"""
    return sqlite3.connect('database.db')

def verificar_material_atual():
    """Verifica o estado atual do material chapa"""
    conn = conectar_bd()
    cursor = conn.cursor()
    
    print("=== ESTADO ATUAL DO MATERIAL ===")
    
    # Buscar informações do material chapa
    cursor.execute("""
        SELECT id, nome, codigo, categoria_id
        FROM itens_estoque 
        WHERE nome LIKE '%chapa%' OR codigo LIKE '%chapa%'
        ORDER BY id LIMIT 5
    """)
    
    materiais = cursor.fetchall()
    print("Materiais encontrados:")
    for material in materiais:
        print(f"  ID: {material[0]}, Nome: {material[1]}, Código: {material[2]}, Categoria: {material[3]}")
    
    if not materiais:
        print("ERRO: Nenhum material 'chapa' encontrado!")
        conn.close()
        return None
    
    # Vamos usar o primeiro material encontrado
    material_id = materiais[0][0]
    material_nome = materiais[0][1]
    
    print(f"\nUsando material: ID {material_id} - {material_nome}")
    
    # Verificar último custo registrado
    cursor.execute("""
        SELECT custo_unitario, data_entrada, id
        FROM entradas_estoque 
        WHERE item_id = ?
        ORDER BY data_entrada DESC, id DESC
        LIMIT 1
    """)
    
    ultima_entrada = cursor.fetchone()
    if ultima_entrada:
        print(f"Último custo registrado: R$ {ultima_entrada[0]:.2f}")
        print(f"Data da última entrada: {ultima_entrada[1]}")
        print(f"ID da entrada: {ultima_entrada[2]}")
    else:
        print("Nenhuma entrada de estoque encontrada para este material")
    
    conn.close()
    return material_id, material_nome

def criar_nova_entrada_material(material_id, novo_custo):
    """Cria nova entrada de estoque com novo custo"""
    conn = conectar_bd()
    cursor = conn.cursor()
    
    print(f"\n=== CRIANDO NOVA ENTRADA COM CUSTO R$ {novo_custo:.2f} ===")
    
    # Inserir nova entrada de estoque
    data_entrada = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    cursor.execute("""
        INSERT INTO entradas_estoque 
        (item_id, quantidade, custo_unitario, custo_total, data_entrada, responsavel, fornecedor, observacoes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        material_id,
        1.0,  # quantidade simbólica
        novo_custo,
        novo_custo,  # custo total = custo unitário * quantidade
        data_entrada,
        'Sistema Teste',
        'Fornecedor Teste',
        f'Teste de alteração de custo para R$ {novo_custo:.2f}'
    ))
    
    entrada_id = cursor.lastrowid
    conn.commit()
    
    print(f"Nova entrada criada com ID: {entrada_id}")
    print(f"Custo unitário: R$ {novo_custo:.2f}")
    print(f"Data: {data_entrada}")
    
    conn.close()
    return entrada_id

def verificar_deteccao_api():
    """Verifica se a API detecta a alteração de preço"""
    print("\n=== VERIFICANDO DETECÇÃO VIA API ===")
    
    try:
        # Produto ID 61 que sabemos ter chapa na composição
        produto_id = 61
        url = f'http://localhost:8000/api/produtos/{produto_id}/detalhes-calculo'
        
        print(f"Consultando: {url}")
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            print("Resposta da API:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            # Verificar se há detecção de variação
            if 'variacao_detectada' in data:
                print(f"\n✅ VARIAÇÃO DETECTADA: {data['variacao_detectada']}")
                if 'percentual_variacao' in data:
                    print(f"✅ PERCENTUAL DE VARIAÇÃO: {data['percentual_variacao']:.3f}%")
            else:
                print("\n❌ NENHUMA VARIAÇÃO DETECTADA")
                
        else:
            print(f"❌ Erro na API: {response.status_code}")
            print(response.text)
    
    except Exception as e:
        print(f"❌ Erro ao consultar API: {e}")

def verificar_deteccao_manual(material_id, produto_id=61):
    """Verifica detecção manual no banco de dados"""
    print("\n=== VERIFICAÇÃO MANUAL NO BANCO ===")
    
    conn = conectar_bd()
    cursor = conn.cursor()
    
    # Buscar último custo vs custo atual usado no cálculo
    cursor.execute("""
        SELECT custo_unitario, data_entrada 
        FROM entradas_estoque 
        WHERE item_id = ?
        ORDER BY data_entrada DESC, id DESC
        LIMIT 2
    """)
    
    entradas = cursor.fetchall()
    
    if len(entradas) >= 2:
        custo_atual = entradas[0][0]
        custo_anterior = entradas[1][0]
        
        print(f"Custo atual: R$ {custo_atual:.2f}")
        print(f"Custo anterior: R$ {custo_anterior:.2f}")
        
        if custo_atual != custo_anterior:
            variacao_percentual = ((custo_atual - custo_anterior) / custo_anterior) * 100
            print(f"Variação detectada: {variacao_percentual:.3f}%")
            
            if abs(variacao_percentual) > 0:
                print("✅ Sistema deveria detectar esta variação")
            else:
                print("❌ Variação muito pequena")
        else:
            print("❌ Nenhuma variação encontrada")
    else:
        print("❌ Não há entradas suficientes para comparação")
    
    conn.close()

def main():
    """Função principal do teste"""
    print("TESTE DE ALTERAÇÃO DE CUSTO DE MATERIAL")
    print("=" * 50)
    
    # 1. Verificar estado atual
    resultado = verificar_material_atual()
    if not resultado:
        return
    
    material_id, material_nome = resultado
    
    # 2. Criar nova entrada com custo R$ 1.030,00
    novo_custo = 1030.00
    entrada_id = criar_nova_entrada_material(material_id, novo_custo)
    
    # 3. Aguardar um momento para o sistema processar
    print("\nAguardando processamento...")
    import time
    time.sleep(2)
    
    # 4. Verificar detecção via API
    verificar_deteccao_api()
    
    # 5. Verificar detecção manual
    verificar_deteccao_manual(material_id)
    
    print("\n" + "=" * 50)
    print("TESTE CONCLUÍDO")
    print(f"Nova entrada de estoque criada: ID {entrada_id}")
    print(f"Material testado: {material_nome} (ID {material_id})")
    print(f"Novo custo: R$ {novo_custo:.2f}")
    print("\nVerifique o modal de atualização de preços no frontend para confirmar a detecção.")

if __name__ == "__main__":
    main()
