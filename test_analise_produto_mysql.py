#!/usr/bin/env python3
"""
Script para análise detalhada do produto e verificação de alterações reais (MySQL)
"""

import mysql.connector
from mysql.connector import Error
from datetime import datetime, timedelta
from decimal import Decimal

def conectar_db():
    """Conecta ao banco de dados MySQL"""
    try:
        return mysql.connector.connect(
            host='localhost',
            user='root',
            password='als32@#nss',
            database='midnight'
        )
    except Error as e:
        print(f"❌ Erro ao conectar ao MySQL: {e}")
        return None

def buscar_produto_detalhes(produto_id=61):
    """Busca detalhes completos do produto"""
    conn = conectar_db()
    if not conn:
        return
        
    cursor = conn.cursor(dictionary=True)
    
    print(f"🔍 ANÁLISE DETALHADA DO PRODUTO ID: {produto_id}")
    print("=" * 80)
    
    try:
        # 1. Dados básicos do produto
        cursor.execute("""
            SELECT p.*, cp.nome as categoria_nome
            FROM produtos p
            LEFT JOIN categoria_produtos cp ON p.categoria_id = cp.id
            WHERE p.id = %s
        """, (produto_id,))
        
        produto = cursor.fetchone()
        if not produto:
            print(f"❌ Produto {produto_id} não encontrado!")
            return
        
        print(f"📦 PRODUTO: {produto['nome']}")
        print(f"   Código: {produto['codigo']}")
        print(f"   Preço atual: R$ {produto['preco']}")
        print(f"   Margem: {produto['margem_lucro']}%")
        print(f"   Custo materiais: R$ {produto['custo_materiais']}")
        print(f"   Custo etapas: R$ {produto['custo_etapas']}")
        print(f"   Data atualização: {produto['data_atualizacao']}")
        print()
        
        # 2. Materiais do produto
        print("🧱 MATERIAIS UTILIZADOS:")
        print("-" * 50)
        
        cursor.execute("""
            SELECT pm.*, ie.nome as material_nome, ie.custo_unitario_atual,
                   cat.nome as categoria_material, um.nome as unidade_medida,
                   ie.largura, ie.comprimento, ie.espessura, ie.volume
            FROM produtos_materiais pm
            JOIN itens_estoque ie ON pm.material_id = ie.id
            LEFT JOIN categoria_itens_estoque cat ON ie.categoria_id = cat.id
            LEFT JOIN unidades_medida um ON ie.unidade_medida_id = um.id
            WHERE pm.produto_id = %s
        """, (produto_id,))
        
        materiais = cursor.fetchall()
        
        for material in materiais:
            print(f"   Material: {material['material_nome']}")
            print(f"   - ID: {material['material_id']}")
            print(f"   - Quantidade necessária: {material['quantidade']}")
            print(f"   - Preço unitário registrado: R$ {material['preco_unitario']}")
            print(f"   - Preço total: R$ {material['preco_total']}")
            print(f"   - Custo unitário atual no estoque: R$ {material['custo_unitario_atual']}")
            print(f"   - Categoria: {material['categoria_material']}")
            print(f"   - Unidade: {material['unidade_medida']}")
            print(f"   - Dimensões: {material['largura']}x{material['comprimento']}x{material['espessura']}")
            print(f"   - Volume: {material['volume']}")
            print(f"   - Largura usada: {material['largura']}")
            print(f"   - Altura usada: {material['altura']}")
            print(f"   - Área utilizada: {material['area_utilizada']}")
            print()
            
            # Verificar histórico de alterações do material nos últimos 7 dias
            print(f"   📊 HISTÓRICO DE CUSTOS (últimos 7 dias):")
            cursor.execute("""
                SELECT data_entrada, custo_unitario, quantidade
                FROM entradas_estoque
                WHERE item_id = %s AND data_entrada >= DATE_SUB(NOW(), INTERVAL 7 DAY)
                ORDER BY data_entrada DESC
            """, (material['material_id'],))
            
            entradas_recentes = cursor.fetchall()
            if entradas_recentes:
                for entrada in entradas_recentes:
                    print(f"     {entrada['data_entrada']}: R$ {entrada['custo_unitario']} (qtd: {entrada['quantidade']})")
            else:
                print("     Nenhuma entrada nos últimos 7 dias")
            print()
        
        # 3. Etapas do produto
        print("⚙️ ETAPAS DE PRODUÇÃO:")
        print("-" * 50)
        
        cursor.execute("""
            SELECT pe.*, 
                   CASE 
                       WHEN pe.equipamento_tipo = 'maquina' THEN m.nome
                       WHEN pe.equipamento_tipo = 'ferramenta' THEN f.nome
                       ELSE 'Manual'
                   END as equipamento_nome,
                   CASE 
                       WHEN pe.equipamento_tipo = 'maquina' THEN m.custo_hora
                       WHEN pe.equipamento_tipo = 'ferramenta' THEN f.custo_hora
                       ELSE NULL
                   END as custo_hora_atual
            FROM produtos_etapas pe
            LEFT JOIN maquinas m ON pe.equipamento_id = m.id AND pe.equipamento_tipo = 'maquina'
            LEFT JOIN ferramentas f ON pe.equipamento_id = f.id AND pe.equipamento_tipo = 'ferramenta'
            WHERE pe.produto_id = %s
        """, (produto_id,))
        
        etapas = cursor.fetchall()
        
        for etapa in etapas:
            print(f"   Etapa: {etapa['nome']}")
            print(f"   - Tipo: {etapa['tipo']}")
            print(f"   - Equipamento: {etapa['equipamento_nome']} (ID: {etapa['equipamento_id']})")
            print(f"   - Tipo equipamento: {etapa['equipamento_tipo']}")
            print(f"   - Tempo estimado: {etapa['tempo_estimado']} horas")
            print(f"   - Custo registrado: R$ {etapa['custo_estimado'] or 'N/A'}")
            print(f"   - Custo hora atual: R$ {etapa['custo_hora_atual'] or 'N/A'}")
            print()
            
            # Verificar histórico de alterações de custo/hora nos últimos 7 dias
            if etapa['equipamento_tipo'] == 'maquina' and etapa['equipamento_id']:
                print(f"   📊 HISTÓRICO CUSTO/HORA MÁQUINA (últimos 7 dias):")
                cursor.execute("""
                    SELECT data_atualizacao, custo_hora
                    FROM maquinas
                    WHERE id = %s AND data_atualizacao >= DATE_SUB(NOW(), INTERVAL 7 DAY)
                    ORDER BY data_atualizacao DESC
                """, (etapa['equipamento_id'],))
                
                hist_maquina = cursor.fetchall()
                if hist_maquina:
                    for hist in hist_maquina:
                        print(f"     {hist['data_atualizacao']}: R$ {hist['custo_hora']}/hora")
                else:
                    print("     Nenhuma alteração nos últimos 7 dias")
                    
                    # Verificar a data da última alteração
                    cursor.execute("""
                        SELECT data_atualizacao, custo_hora
                        FROM maquinas
                        WHERE id = %s
                    """, (etapa['equipamento_id'],))
                    ultima = cursor.fetchone()
                    if ultima:
                        print(f"     Última alteração: {ultima['data_atualizacao']} - R$ {ultima['custo_hora']}/hora")
            print()
        
        # 4. Verificar se há alterações detectadas pelo sistema
        print("🔍 VERIFICAÇÃO DE ALTERAÇÕES DO SISTEMA:")
        print("-" * 50)
        
        # Simular a verificação de alterações como o sistema faz
        cursor.execute("""
            SELECT id, nome, custo_unitario_atual
            FROM itens_estoque 
            WHERE id IN (
                SELECT material_id FROM produtos_materiais WHERE produto_id = %s
            )
        """, (produto_id,))
        
        materiais_atuais = cursor.fetchall()
        print("Materiais que o sistema detectaria como 'alterados':")
        for mat in materiais_atuais:
            print(f"   - {mat['nome']} (ID: {mat['id']}) - Custo atual: R$ {mat['custo_unitario_atual']}")
        
        cursor.execute("""
            SELECT id, nome, custo_hora
            FROM maquinas 
            WHERE id IN (
                SELECT equipamento_id FROM produtos_etapas 
                WHERE produto_id = %s AND equipamento_tipo = 'maquina'
            )
        """, (produto_id,))
        
        maquinas_atuais = cursor.fetchall()
        print("Máquinas que o sistema detectaria como 'alteradas':")
        for maq in maquinas_atuais:
            print(f"   - {maq['nome']} (ID: {maq['id']}) - Custo/hora atual: R$ {maq['custo_hora']}")
        
        print()
        
        # 5. Calcular o custo real atual
        print("💰 CÁLCULO DE CUSTO ATUAL:")
        print("-" * 50)
        
        custo_total_materiais = 0
        custo_total_etapas = 0
        
        # Recalcular custo dos materiais
        for material in materiais:
            custo_material = float(material['custo_unitario_atual'] or 0) * float(material['quantidade'] or 0)
            custo_total_materiais += custo_material
            print(f"   Material {material['material_nome']}: R$ {material['custo_unitario_atual']} × {material['quantidade']} = R$ {custo_material:.2f}")
        
        # Recalcular custo das etapas
        for etapa in etapas:
            if etapa['custo_hora_atual'] and etapa['tempo_estimado']:
                custo_etapa = float(etapa['custo_hora_atual']) * float(etapa['tempo_estimado'])
                custo_total_etapas += custo_etapa
                print(f"   Etapa {etapa['nome']}: R$ {etapa['custo_hora_atual']}/h × {etapa['tempo_estimado']}h = R$ {custo_etapa:.2f}")
        
        custo_total_novo = custo_total_materiais + custo_total_etapas
        margem = float(produto['margem_lucro'] or 0)
        preco_novo = custo_total_novo * (1 + margem / 100)
        
        print(f"\n   📊 RESUMO:")
        print(f"   Custo materiais atual: R$ {custo_total_materiais:.2f}")
        print(f"   Custo etapas atual: R$ {custo_total_etapas:.2f}")
        print(f"   Custo total atual: R$ {custo_total_novo:.2f}")
        print(f"   Preço com margem ({margem}%): R$ {preco_novo:.2f}")
        print(f"   Preço registrado no produto: R$ {produto['preco']}")
        
        variacao = ((float(preco_novo) - float(produto['preco'])) / float(produto['preco'])) * 100
        print(f"   Variação real: {variacao:.4f}%")
        
        if abs(variacao) < 1:
            print(f"   ✅ Variação insignificante - produto NÃO deveria aparecer no modal")
        else:
            print(f"   ⚠️ Variação significativa - produto deveria aparecer no modal")
        
    except Error as e:
        print(f"❌ Erro na consulta: {e}")
    finally:
        cursor.close()
        conn.close()

def verificar_funcao_backend():
    """Verifica como o backend está detectando alterações"""
    print("\n" + "=" * 80)
    print("🔍 VERIFICAÇÃO DA LÓGICA DO BACKEND")
    print("=" * 80)
    
    conn = conectar_db()
    if not conn:
        return
        
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Simular a query que o backend usa para detectar alterações
        dias_verificacao = 7
        
        print(f"Verificando alterações dos últimos {dias_verificacao} dias")
        
        # Query para materiais "alterados"
        cursor.execute("""
            SELECT DISTINCT ie.id, ie.nome, ie.custo_unitario_atual
            FROM itens_estoque ie
            INNER JOIN entradas_estoque ee ON ie.id = ee.item_id
            WHERE ee.data_entrada >= DATE_SUB(NOW(), INTERVAL %s DAY)
        """, (dias_verificacao,))
        
        materiais_alterados = cursor.fetchall()
        print(f"\n📦 MATERIAIS 'ALTERADOS' (com entradas nos últimos {dias_verificacao} dias):")
        for mat in materiais_alterados:
            print(f"   - {mat['nome']} (ID: {mat['id']}) - Custo: R$ {mat['custo_unitario_atual']}")
        
        # Query para máquinas "alteradas"
        cursor.execute("""
            SELECT id, nome, custo_hora, data_atualizacao
            FROM maquinas
            WHERE data_atualizacao >= DATE_SUB(NOW(), INTERVAL %s DAY)
        """, (dias_verificacao,))
        
        maquinas_alteradas = cursor.fetchall()
        print(f"\n⚙️ MÁQUINAS 'ALTERADAS' (atualizadas nos últimos {dias_verificacao} dias):")
        for maq in maquinas_alteradas:
            print(f"   - {maq['nome']} (ID: {maq['id']}) - Custo/hora: R$ {maq['custo_hora']} - Atualizada: {maq['data_atualizacao']}")
        
        # Verificar se o produto 61 usa algum desses materiais/máquinas
        print(f"\n🔍 PRODUTO 61 USA ESSES MATERIAIS/MÁQUINAS?")
        
        cursor.execute("""
            SELECT COUNT(*) as count FROM produtos_materiais pm
            JOIN itens_estoque ie ON pm.material_id = ie.id
            JOIN entradas_estoque ee ON ie.id = ee.item_id
            WHERE pm.produto_id = 61 AND ee.data_entrada >= DATE_SUB(NOW(), INTERVAL %s DAY)
        """, (dias_verificacao,))
        
        usa_materiais_alterados = cursor.fetchone()['count']
        print(f"   Usa materiais 'alterados': {'SIM' if usa_materiais_alterados > 0 else 'NÃO'} ({usa_materiais_alterados} materiais)")
        
        cursor.execute("""
            SELECT COUNT(*) as count FROM produtos_etapas pe
            JOIN maquinas m ON pe.equipamento_id = m.id AND pe.equipamento_tipo = 'maquina'
            WHERE pe.produto_id = 61 AND m.data_atualizacao >= DATE_SUB(NOW(), INTERVAL %s DAY)
        """, (dias_verificacao,))
        
        usa_maquinas_alteradas = cursor.fetchone()['count']
        print(f"   Usa máquinas 'alteradas': {'SIM' if usa_maquinas_alteradas > 0 else 'NÃO'} ({usa_maquinas_alteradas} máquinas)")
        
        if usa_materiais_alterados > 0 or usa_maquinas_alteradas > 0:
            print(f"\n   ⚠️ POR ISSO o sistema detecta o produto como 'afetado'!")
            print(f"   💡 SOLUÇÃO: Verificar se houve mudança REAL de preço/custo, não apenas entrada no estoque")
        
    except Error as e:
        print(f"❌ Erro na consulta: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("🔍 ANÁLISE DETALHADA DO SISTEMA DE DETECÇÃO DE ALTERAÇÕES")
    print("=" * 80)
    
    buscar_produto_detalhes(61)
    verificar_funcao_backend()
    
    print(f"\n✅ Análise concluída!")
