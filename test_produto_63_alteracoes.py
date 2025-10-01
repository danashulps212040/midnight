#!/usr/bin/env python3
"""
Script para alterar custos específicos do produto id 63:
- Máquina VUZE: alterar custo para 18.00 (era 15.00)
- Material chapa: alterar custo para 12.50 (variação de +25%)
- Material parafuso: alterar custo para 0.18 (variação de +20%)
"""

import mysql.connector as mysql_conn
from decimal import Decimal
import requests
import json
from datetime import datetime

# Configuração do banco
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'als32@#nss',
    'database': 'midnight'
}

def conectar_banco():
    return mysql_conn.connect(**DB_CONFIG)

def alterar_custo_maquina_vuze():
    """Altera o custo da máquina VUZE para R$ 18.00"""
    print("=== ALTERANDO CUSTO DA MÁQUINA VUZE ===")
    
    conn = conectar_banco()
    cursor = conn.cursor()
    
    try:
        # Buscar máquina VUZE apenas pelo nome
        cursor.execute("""
            SELECT id, nome, hora_maquina 
            FROM maquinas 
            WHERE nome LIKE '%VUZE%' OR nome LIKE '%vuze%'
            LIMIT 1
        """)
        
        maquina = cursor.fetchone()
        if not maquina:
            print("❌ Máquina VUZE não encontrada")
            return False
        
        maquina_id, nome, custo_atual = maquina
        print(f"✓ Máquina encontrada: ID {maquina_id} - {nome}")
        print(f"  Custo atual: R$ {custo_atual}")
        
        # Alterar custo para R$ 18.00
        novo_custo = Decimal('18.00')
        cursor.execute("""
            UPDATE maquinas 
            SET hora_maquina = %s 
            WHERE id = %s
        """, (novo_custo, maquina_id))
        
        conn.commit()
        print(f"✓ Custo alterado para: R$ {novo_custo}")
        
        # Verificar alteração
        cursor.execute("SELECT hora_maquina FROM maquinas WHERE id = %s", (maquina_id,))
        custo_verificado = cursor.fetchone()[0]
        print(f"✓ Verificação: R$ {custo_verificado}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao alterar custo da máquina: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

def alterar_custos_materiais():
    """Altera custos de materiais do produto 63"""
    print("\n=== ALTERANDO CUSTOS DE MATERIAIS ===")
    
    conn = conectar_banco()
    cursor = conn.cursor()
    
    try:
        # Buscar materiais do produto 63
        cursor.execute("""
            SELECT DISTINCT pm.material_id, ie.nome
            FROM produtos_materiais pm
            JOIN itens_estoque ie ON pm.material_id = ie.id
            WHERE pm.produto_id = 63
        """)
        
        materiais = cursor.fetchall()
        if not materiais:
            print("❌ Nenhum material encontrado para produto 63")
            return False
        
        print(f"✓ {len(materiais)} materiais encontrados:")
        for material_id, nome in materiais:
            print(f"  - ID {material_id}: {nome}")
        
        # Definir alterações específicas
        alteracoes = {
            'chapa': {'novo_custo': Decimal('12.50'), 'variacao': '+25%'},
            'parafuso': {'novo_custo': Decimal('0.18'), 'variacao': '+20%'}
        }
        
        alteracoes_realizadas = 0
        
        for material_id, nome in materiais:
            nome_lower = nome.lower()
            
            # Verificar se é um dos materiais que queremos alterar
            alteracao_info = None
            for palavra_chave, info in alteracoes.items():
                if palavra_chave in nome_lower:
                    alteracao_info = info
                    break
            
            if not alteracao_info:
                continue
            
            # Obter custo atual
            cursor.execute("""
                SELECT custo_unitario 
                FROM entradas_estoque 
                WHERE item_id = %s AND custo_unitario IS NOT NULL
                ORDER BY data_entrada DESC 
                LIMIT 1
            """, (material_id,))
            
            resultado = cursor.fetchone()
            custo_atual = resultado[0] if resultado else Decimal('10.00')
            
            print(f"\n--- Material: {nome} ---")
            print(f"  Custo atual: R$ {custo_atual}")
            print(f"  Novo custo: R$ {alteracao_info['novo_custo']} ({alteracao_info['variacao']})")
            
            # Criar nova entrada com custo alterado
            cursor.execute("""
                INSERT INTO entradas_estoque 
                (item_id, quantidade, custo_unitario, data_entrada, observacoes)
                VALUES (%s, 1, %s, NOW(), %s)
            """, (
                material_id, 
                alteracao_info['novo_custo'],
                f"Teste produto 63 - {alteracao_info['variacao']} - {datetime.now().strftime('%H:%M:%S')}"
            ))
            
            alteracoes_realizadas += 1
            print(f"✓ Entrada criada com novo custo")
        
        conn.commit()
        print(f"\n✓ {alteracoes_realizadas} alterações de materiais realizadas")
        return alteracoes_realizadas > 0
        
    except Exception as e:
        print(f"❌ Erro ao alterar custos de materiais: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

def consultar_detalhes_calculo():
    """Consulta a API para obter detalhes do cálculo do produto 63"""
    print("\n=== CONSULTANDO DETALHES DE CÁLCULO ===")
    
    try:
        url = "http://localhost:5000/api/produtos/63/detalhes-calculo"
        response = requests.get(url)
        
        if response.status_code == 200:
            dados = response.json()
            
            print("✓ Resposta da API obtida com sucesso")
            print("\n--- RESUMO DO CÁLCULO ---")
            
            if 'resumo' in dados:
                resumo = dados['resumo']
                print(f"Produto ID: {resumo.get('produto_id')}")
                print(f"Nome: {resumo.get('nome_produto')}")
                print(f"Preço atual: R$ {resumo.get('preco_atual', 'N/A')}")
                print(f"Novo preço sugerido: R$ {resumo.get('novo_preco_sugerido', 'N/A')}")
                
                if 'variacao_percentual' in resumo:
                    variacao = resumo['variacao_percentual']
                    print(f"Variação: {variacao:+.3f}%")
            
            if 'alteracoes_detectadas' in dados:
                alteracoes = dados['alteracoes_detectadas']
                print(f"\n--- ALTERAÇÕES DETECTADAS ---")
                print(f"Materiais alterados: {len(alteracoes.get('materiais', []))}")
                print(f"Etapas alteradas: {len(alteracoes.get('etapas', []))}")
                
                # Detalhar materiais alterados
                if alteracoes.get('materiais'):
                    print("\nMateriais:")
                    for material in alteracoes['materiais']:
                        print(f"  - {material.get('nome')}: R$ {material.get('custo_anterior')} → R$ {material.get('custo_atual')} ({material.get('variacao_percentual', 0):+.3f}%)")
                
                # Detalhar etapas alteradas
                if alteracoes.get('etapas'):
                    print("\nEtapas:")
                    for etapa in alteracoes['etapas']:
                        print(f"  - {etapa.get('nome_etapa')}: R$ {etapa.get('custo_anterior')} → R$ {etapa.get('custo_atual')} ({etapa.get('variacao_percentual', 0):+.3f}%)")
            
            # Salvar resposta completa em arquivo para análise
            with open('/Users/gabriel/Documents/Midnight/DEV23may2025/resposta_produto_63.json', 'w', encoding='utf-8') as f:
                json.dump(dados, f, indent=2, ensure_ascii=False, default=str)
            print(f"\n✓ Resposta completa salva em: resposta_produto_63.json")
            
            return dados
            
        else:
            print(f"❌ Erro na API: {response.status_code}")
            print(f"Resposta: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Erro ao consultar API: {e}")
        return None

def main():
    print("TESTE PRODUTO 63 - ALTERAÇÕES DE CUSTOS")
    print("="*50)
    
    # 1. Alterar custo da máquina VUZE
    if not alterar_custo_maquina_vuze():
        print("❌ Falha ao alterar custo da máquina")
        return
    
    # 2. Alterar custos de materiais
    if not alterar_custos_materiais():
        print("❌ Falha ao alterar custos de materiais")
        return
    
    # 3. Aguardar um momento para que as alterações sejam processadas
    import time
    print("\n⏳ Aguardando processamento das alterações...")
    time.sleep(2)
    
    # 4. Consultar detalhes do cálculo
    resultado = consultar_detalhes_calculo()
    
    if resultado:
        print("\n🎉 TESTE CONCLUÍDO COM SUCESSO!")
    else:
        print("\n❌ Falha ao obter detalhes do cálculo")

if __name__ == "__main__":
    main()
