#!/usr/bin/env python3
"""
Script para análise detalhada do produto e verificação de alterações reais
"""

from database import Database
from datetime import datetime, timedelta
from decimal import Decimal

def buscar_produto_detalhes(produto_id=61):
    """Busca detalhes completos do produto"""
    db = Database()
    cursor = db.cursor
    
    print(f"🔍 ANÁLISE DETALHADA DO PRODUTO ID: {produto_id}")
    print("=" * 80)
    
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
        db.close()
        return
    
    # Converter para dict
    produto_dict = produto
    
    print(f"📦 PRODUTO: {produto_dict['nome']}")
    print(f"   Código: {produto_dict['codigo']}")
    print(f"   Preço atual: R$ {produto_dict['preco']}")
    print(f"   Margem: {produto_dict['margem_lucro']}%")
    print(f"   Custo materiais: R$ {produto_dict['custo_materiais']}")
    print(f"   Custo etapas: R$ {produto_dict['custo_etapas']}")
    print(f"   Data atualização: {produto_dict['data_atualizacao']}")
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
        print(f"   - Categoria: {material.get('categoria_material', 'N/A')}")
        print(f"   - Unidade: {material.get('unidade_medida', 'N/A')}")
        print(f"   - Dimensões: {material.get('largura', 'N/A')}x{material.get('comprimento', 'N/A')}x{material.get('espessura', 'N/A')}")
        print(f"   - Volume: {material.get('volume', 'N/A')}")
        print(f"   - Largura usada: {material.get('largura', 'N/A')}")
        print(f"   - Altura usada: {material.get('altura', 'N/A')}")
        print(f"   - Área utilizada: {material.get('area_utilizada', 'N/A')}")
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
        WHERE pe.produto_id = ?
    """, (produto_id,))
    
    etapas = cursor.fetchall()
    colunas_etap = [desc[0] for desc in cursor.description]
    
    for etapa in etapas:
        etap_dict = dict(zip(colunas_etap, etapa))
        print(f"   Etapa: {etap_dict['nome']}")
        print(f"   - Tipo: {etap_dict['tipo']}")
        print(f"   - Equipamento: {etap_dict['equipamento_nome']} (ID: {etap_dict['equipamento_id']})")
        print(f"   - Tipo equipamento: {etap_dict['equipamento_tipo']}")
        print(f"   - Tempo estimado: {etap_dict['tempo_estimado']} horas")
        print(f"   - Custo registrado: R$ {etap_dict['custo_estimado'] or 'N/A'}")
        print(f"   - Custo hora atual: R$ {etap_dict['custo_hora_atual'] or 'N/A'}")
        print()
        
        # Verificar histórico de alterações de custo/hora nos últimos 7 dias
        if etap_dict['equipamento_tipo'] == 'maquina' and etap_dict['equipamento_id']:
            print(f"   📊 HISTÓRICO CUSTO/HORA MÁQUINA (últimos 7 dias):")
            cursor.execute("""
                SELECT data_atualizacao, custo_hora
                FROM maquinas
                WHERE id = ? AND data_atualizacao >= date('now', '-7 days')
                ORDER BY data_atualizacao DESC
            """, (etap_dict['equipamento_id'],))
            
            hist_maquina = cursor.fetchall()
            if hist_maquina:
                for hist in hist_maquina:
                    print(f"     {hist[0]}: R$ {hist[1]}/hora")
            else:
                print("     Nenhuma alteração nos últimos 7 dias")
                
                # Verificar a data da última alteração
                cursor.execute("""
                    SELECT data_atualizacao, custo_hora
                    FROM maquinas
                    WHERE id = ?
                """, (etap_dict['equipamento_id'],))
                ultima = cursor.fetchone()
                if ultima:
                    print(f"     Última alteração: {ultima[0]} - R$ {ultima[1]}/hora")
        print()
    
    # 4. Verificar se há alterações detectadas pelo sistema
    print("🔍 VERIFICAÇÃO DE ALTERAÇÕES DO SISTEMA:")
    print("-" * 50)
    
    # Simular a verificação de alterações como o sistema faz
    cursor.execute("""
        SELECT id, nome, custo_unitario_atual
        FROM itens_estoque 
        WHERE id IN (
            SELECT material_id FROM produtos_materiais WHERE produto_id = ?
        )
    """, (produto_id,))
    
    materiais_atuais = cursor.fetchall()
    print("Materiais que o sistema detectaria como 'alterados':")
    for mat in materiais_atuais:
        print(f"   - {mat[1]} (ID: {mat[0]}) - Custo atual: R$ {mat[2]}")
    
    cursor.execute("""
        SELECT id, nome, custo_hora
        FROM maquinas 
        WHERE id IN (
            SELECT equipamento_id FROM produtos_etapas 
            WHERE produto_id = ? AND equipamento_tipo = 'maquina'
        )
    """, (produto_id,))
    
    maquinas_atuais = cursor.fetchall()
    print("Máquinas que o sistema detectaria como 'alteradas':")
    for maq in maquinas_atuais:
        print(f"   - {maq[1]} (ID: {maq[0]}) - Custo/hora atual: R$ {maq[2]}")
    
    print()
    
    # 5. Calcular o custo real atual
    print("💰 CÁLCULO DE CUSTO ATUAL:")
    print("-" * 50)
    
    custo_total_materiais = 0
    custo_total_etapas = 0
    
    # Recalcular custo dos materiais
    for material in materiais:
        mat_dict = dict(zip(colunas_mat, material))
        custo_material = float(mat_dict['custo_unitario_atual'] or 0) * float(mat_dict['quantidade'] or 0)
        custo_total_materiais += custo_material
        print(f"   Material {mat_dict['material_nome']}: R$ {mat_dict['custo_unitario_atual']} × {mat_dict['quantidade']} = R$ {custo_material:.2f}")
    
    # Recalcular custo das etapas
    for etapa in etapas:
        etap_dict = dict(zip(colunas_etap, etapa))
        if etap_dict['custo_hora_atual'] and etap_dict['tempo_estimado']:
            custo_etapa = float(etap_dict['custo_hora_atual']) * float(etap_dict['tempo_estimado'])
            custo_total_etapas += custo_etapa
            print(f"   Etapa {etap_dict['nome']}: R$ {etap_dict['custo_hora_atual']}/h × {etap_dict['tempo_estimado']}h = R$ {custo_etapa:.2f}")
    
    custo_total_novo = custo_total_materiais + custo_total_etapas
    margem = float(produto_dict['margem_lucro'] or 0)
    preco_novo = custo_total_novo * (1 + margem / 100)
    
    print(f"\n   📊 RESUMO:")
    print(f"   Custo materiais atual: R$ {custo_total_materiais:.2f}")
    print(f"   Custo etapas atual: R$ {custo_total_etapas:.2f}")
    print(f"   Custo total atual: R$ {custo_total_novo:.2f}")
    print(f"   Preço com margem ({margem}%): R$ {preco_novo:.2f}")
    print(f"   Preço registrado no produto: R$ {produto_dict['preco']}")
    
    variacao = ((float(preco_novo) - float(produto_dict['preco'])) / float(produto_dict['preco'])) * 100
    print(f"   Variação real: {variacao:.4f}%")
    
    if abs(variacao) < 1:
        print(f"   ✅ Variação insignificante - produto NÃO deveria aparecer no modal")
    else:
        print(f"   ⚠️ Variação significativa - produto deveria aparecer no modal")
    
    conn.close()

def verificar_funcao_backend():
    """Verifica como o backend está detectando alterações"""
    print("\n" + "=" * 80)
    print("🔍 VERIFICAÇÃO DA LÓGICA DO BACKEND")
    print("=" * 80)
    
    conn = conectar_db()
    cursor = conn.cursor()
    
    # Simular a query que o backend usa para detectar alterações
    dias_verificacao = 7
    data_limite = (datetime.now() - timedelta(days=dias_verificacao)).strftime('%Y-%m-%d')
    
    print(f"Data limite para verificação: {data_limite}")
    
    # Query para materiais "alterados"
    cursor.execute("""
        SELECT DISTINCT ie.id, ie.nome, ie.custo_unitario_atual
        FROM itens_estoque ie
        INNER JOIN entradas_estoque ee ON ie.id = ee.item_id
        WHERE ee.data_entrada >= ?
    """, (data_limite,))
    
    materiais_alterados = cursor.fetchall()
    print(f"\n📦 MATERIAIS 'ALTERADOS' (com entradas desde {data_limite}):")
    for mat in materiais_alterados:
        print(f"   - {mat[1]} (ID: {mat[0]}) - Custo: R$ {mat[2]}")
    
    # Query para máquinas "alteradas"
    cursor.execute("""
        SELECT id, nome, custo_hora, data_atualizacao
        FROM maquinas
        WHERE data_atualizacao >= ?
    """, (data_limite,))
    
    maquinas_alteradas = cursor.fetchall()
    print(f"\n⚙️ MÁQUINAS 'ALTERADAS' (atualizadas desde {data_limite}):")
    for maq in maquinas_alteradas:
        print(f"   - {maq[1]} (ID: {maq[0]}) - Custo/hora: R$ {maq[2]} - Atualizada: {maq[3]}")
    
    # Verificar se o produto 61 usa algum desses materiais/máquinas
    print(f"\n🔍 PRODUTO 61 USA ESSES MATERIAIS/MÁQUINAS?")
    
    cursor.execute("""
        SELECT COUNT(*) FROM produtos_materiais pm
        JOIN itens_estoque ie ON pm.material_id = ie.id
        JOIN entradas_estoque ee ON ie.id = ee.item_id
        WHERE pm.produto_id = 61 AND ee.data_entrada >= ?
    """, (data_limite,))
    
    usa_materiais_alterados = cursor.fetchone()[0]
    print(f"   Usa materiais 'alterados': {'SIM' if usa_materiais_alterados > 0 else 'NÃO'} ({usa_materiais_alterados} materiais)")
    
    cursor.execute("""
        SELECT COUNT(*) FROM produtos_etapas pe
        JOIN maquinas m ON pe.equipamento_id = m.id AND pe.equipamento_tipo = 'maquina'
        WHERE pe.produto_id = 61 AND m.data_atualizacao >= ?
    """, (data_limite,))
    
    usa_maquinas_alteradas = cursor.fetchone()[0]
    print(f"   Usa máquinas 'alteradas': {'SIM' if usa_maquinas_alteradas > 0 else 'NÃO'} ({usa_maquinas_alteradas} máquinas)")
    
    if usa_materiais_alterados > 0 or usa_maquinas_alteradas > 0:
        print(f"\n   ⚠️ POR ISSO o sistema detecta o produto como 'afetado'!")
        print(f"   💡 SOLUÇÃO: Verificar se houve mudança REAL de preço/custo, não apenas entrada no estoque")
    
    conn.close()

if __name__ == "__main__":
    print("🔍 ANÁLISE DETALHADA DO SISTEMA DE DETECÇÃO DE ALTERAÇÕES")
    print("=" * 80)
    
    buscar_produto_detalhes(61)
    verificar_funcao_backend()
    
    print(f"\n✅ Análise concluída!")
