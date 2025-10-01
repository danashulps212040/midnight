#!/usr/bin/env python3
"""
Script para análise detalhada do produto e verificação de alterações reais
Adaptado para usar MySQL através da classe Database
"""

from database import Database
from datetime import datetime, timedelta
from decimal import Decimal

def buscar_produto_detalhes(produto_id=61):
    """Busca detalhes completos do produto"""
    db = Database()
    
    try:
        print(f"🔍 ANÁLISE DETALHADA DO PRODUTO ID: {produto_id}")
        print("=" * 80)
        
        # 1. Dados básicos do produto
        produto = db.buscar_produto_por_id(produto_id)
        if not produto or 'erro' in produto:
            print(f"❌ Produto {produto_id} não encontrado!")
            return
        
        print(f"📦 PRODUTO: {produto['nome']}")
        print(f"   Código: {produto['codigo']}")
        print(f"   Preço atual: R$ {produto['preco']}")
        print(f"   Margem: {produto.get('margem_lucro', 0)}%")
        print(f"   Custo materiais: R$ {produto.get('custo_materiais', 0)}")
        print(f"   Custo etapas: R$ {produto.get('custo_etapas', 0)}")
        print(f"   Data atualização: {produto.get('data_atualizacao', 'N/A')}")
        print()
        
        # 2. Materiais do produto
        print("🧱 MATERIAIS UTILIZADOS:")
        print("-" * 50)
        
        db.cursor.execute("""
            SELECT pm.*, ie.nome as material_nome, ie.custo_unitario_atual,
                   cat.nome as categoria_material, um.nome as unidade_medida,
                   ie.largura, ie.comprimento, ie.espessura, ie.volume
            FROM produtos_materiais pm
            JOIN itens_estoque ie ON pm.material_id = ie.id
            LEFT JOIN categoria_itens_estoque cat ON ie.categoria_id = cat.id
            LEFT JOIN unidades_medida um ON ie.unidade_medida_id = um.id
            WHERE pm.produto_id = %s
        """, (produto_id,))
        
        materiais = db.cursor.fetchall()
        
        if not materiais:
            print("   Nenhum material encontrado.")
        
        for material in materiais:
            print(f"   Material: {material['material_nome']}")
            print(f"   - ID: {material['material_id']}")
            print(f"   - Quantidade necessária: {material['quantidade']}")
            print(f"   - Preço unitário registrado no produto: R$ {material['preco_unitario']}")
            print(f"   - Preço total registrado: R$ {material['preco_total']}")
            print(f"   - Custo unitário ATUAL no estoque: R$ {material['custo_unitario_atual']}")
            print(f"   - Categoria: {material.get('categoria_material', 'N/A')}")
            print(f"   - Unidade: {material.get('unidade_medida', 'N/A')}")
            print(f"   - Dimensões: {material.get('largura', 'N/A')}x{material.get('comprimento', 'N/A')}x{material.get('espessura', 'N/A')}")
            print(f"   - Volume: {material.get('volume', 'N/A')}")
            print(f"   - Largura usada: {material.get('largura', 'N/A')}")
            print(f"   - Altura usada: {material.get('altura', 'N/A')}")
            print(f"   - Área utilizada: {material.get('area_utilizada', 'N/A')}")
            
            # Comparar preços
            preco_registrado = float(material['preco_unitario'] or 0)
            custo_atual = float(material['custo_unitario_atual'] or 0)
            diferenca = custo_atual - preco_registrado
            if diferenca != 0:
                print(f"   🚨 DIFERENÇA DE PREÇO: R$ {diferenca:.2f}")
            else:
                print(f"   ✅ PREÇO INALTERADO")
            print()
            
            # Verificar histórico de alterações do material nos últimos 7 dias
            print(f"   📊 HISTÓRICO DE CUSTOS (últimos 7 dias):")
            db.cursor.execute("""
                SELECT data_entrada, custo_unitario, quantidade
                FROM entradas_estoque
                WHERE item_id = %s AND data_entrada >= DATE_SUB(NOW(), INTERVAL 7 DAY)
                ORDER BY data_entrada DESC
            """, (material['material_id'],))
            
            entradas_recentes = db.cursor.fetchall()
            if entradas_recentes:
                for entrada in entradas_recentes:
                    print(f"     {entrada['data_entrada']}: R$ {entrada['custo_unitario']} (qtd: {entrada['quantidade']})")
            else:
                print("     Nenhuma entrada nos últimos 7 dias")
            print()
        
        # 3. Etapas do produto
        print("⚙️ ETAPAS DE PRODUÇÃO:")
        print("-" * 50)
        
        db.cursor.execute("""
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
        
        etapas = db.cursor.fetchall()
        
        if not etapas:
            print("   Nenhuma etapa encontrada.")
        
        for etapa in etapas:
            print(f"   Etapa: {etapa['nome']}")
            print(f"   - Tipo: {etapa['tipo']}")
            print(f"   - Equipamento: {etapa['equipamento_nome']} (ID: {etapa['equipamento_id']})")
            print(f"   - Tipo equipamento: {etapa['equipamento_tipo']}")
            print(f"   - Tempo estimado: {etapa['tempo_estimado']} horas")
            print(f"   - Custo registrado na etapa: R$ {etapa['custo_estimado'] or 'N/A'}")
            print(f"   - Custo hora ATUAL: R$ {etapa['custo_hora_atual'] or 'N/A'}")
            
            # Comparar custos se aplicável
            if etapa['custo_estimado'] and etapa['custo_hora_atual'] and etapa['tempo_estimado']:
                custo_registrado = float(etapa['custo_estimado'])
                custo_atual_calculado = float(etapa['custo_hora_atual']) * float(etapa['tempo_estimado'])
                diferenca = custo_atual_calculado - custo_registrado
                if abs(diferenca) > 0.01:  # Tolerância de 1 centavo
                    print(f"   🚨 DIFERENÇA DE CUSTO: R$ {diferenca:.2f}")
                else:
                    print(f"   ✅ CUSTO INALTERADO")
            print()
            
            # Verificar histórico de alterações de custo/hora nos últimos 7 dias
            if etapa['equipamento_tipo'] == 'maquina' and etapa['equipamento_id']:
                print(f"   📊 HISTÓRICO CUSTO/HORA MÁQUINA (últimos 7 dias):")
                db.cursor.execute("""
                    SELECT data_atualizacao, custo_hora
                    FROM maquinas_historico_custos
                    WHERE maquina_id = %s AND data_atualizacao >= DATE_SUB(NOW(), INTERVAL 7 DAY)
                    ORDER BY data_atualizacao DESC
                """, (etapa['equipamento_id'],))
                
                hist_maquina = db.cursor.fetchall()
                if hist_maquina:
                    for hist in hist_maquina:
                        print(f"     {hist['data_atualizacao']}: R$ {hist['custo_hora']}/hora")
                else:
                    print("     Nenhuma alteração no histórico nos últimos 7 dias")
                    
                    # Verificar a data da última alteração na tabela principal
                    db.cursor.execute("""
                        SELECT data_atualizacao, custo_hora
                        FROM maquinas
                        WHERE id = %s
                    """, (etapa['equipamento_id'],))
                    ultima = db.cursor.fetchone()
                    if ultima:
                        print(f"     Última alteração registrada: {ultima['data_atualizacao']} - R$ {ultima['custo_hora']}/hora")
            print()
        
        # 4. Verificar como o sistema detecta alterações
        print("🔍 VERIFICAÇÃO DE ALTERAÇÕES DO SISTEMA:")
        print("-" * 50)
        
        # Usar a mesma lógica do sistema para detectar alterações
        alteracoes = db.verificar_alteracoes_custos(7)  # últimos 7 dias
        
        if alteracoes:
            print("Materiais detectados como 'alterados' pelo sistema:")
            for mat in alteracoes.get('materiais', []):
                print(f"   - {mat['nome']} (ID: {mat['id']})")
            
            print("Máquinas detectadas como 'alteradas' pelo sistema:")
            for maq in alteracoes.get('maquinas', []):
                print(f"   - {maq['nome']} (ID: {maq['id']})")
            
            # Verificar impacto no produto específico
            print(f"\n🎯 IMPACTO NO PRODUTO {produto_id}:")
            resultado = db.calcular_impacto_alteracoes_precos(alteracoes)
            produtos_afetados = resultado.get('produtos_afetados', [])
            
            produto_encontrado = False
            for prod in produtos_afetados:
                if prod['id'] == produto_id:
                    produto_encontrado = True
                    print(f"   ✅ Produto DETECTADO como afetado")
                    print(f"   - Preço atual: R$ {prod['preco_atual']}")
                    print(f"   - Novo preço calculado: R$ {prod['novo_preco']}")
                    print(f"   - Variação: {prod['variacao_percentual']:.4f}%")
                    print(f"   - Impacto: {prod['impacto']}")
                    break
            
            if not produto_encontrado:
                print(f"   ❌ Produto NÃO detectado como afetado")
        else:
            print("   ✅ Nenhuma alteração detectada pelo sistema nos últimos 7 dias")
        
        print()
        
        # 5. Cálculo manual para verificação
        print("💰 CÁLCULO MANUAL DE VERIFICAÇÃO:")
        print("-" * 50)
        
        custo_total_materiais = 0
        custo_total_etapas = 0
        
        # Recalcular custo dos materiais usando valores ATUAIS
        print("   📦 Recálculo de materiais:")
        for material in materiais:
            custo_atual = float(material['custo_unitario_atual'] or 0)
            quantidade = float(material['quantidade'] or 0)
            custo_material = custo_atual * quantidade
            custo_total_materiais += custo_material
            print(f"     {material['material_nome']}: R$ {custo_atual} × {quantidade} = R$ {custo_material:.2f}")
        
        # Recalcular custo das etapas usando valores ATUAIS
        print("   ⚙️ Recálculo de etapas:")
        for etapa in etapas:
            if etapa['custo_hora_atual'] and etapa['tempo_estimado']:
                custo_hora = float(etapa['custo_hora_atual'])
                tempo = float(etapa['tempo_estimado'])
                custo_etapa = custo_hora * tempo
                custo_total_etapas += custo_etapa
                print(f"     {etapa['nome']}: R$ {custo_hora}/h × {tempo}h = R$ {custo_etapa:.2f}")
            elif etapa['custo_estimado']:
                custo_etapa = float(etapa['custo_estimado'])
                custo_total_etapas += custo_etapa
                print(f"     {etapa['nome']}: R$ {custo_etapa:.2f} (valor fixo registrado)")
        
        custo_total_novo = custo_total_materiais + custo_total_etapas
        margem = float(produto.get('margem_lucro', 0))
        preco_novo = custo_total_novo * (1 + margem / 100)
        preco_atual = float(produto['preco'])
        
        print(f"\n   📊 RESUMO:")
        print(f"   Custo materiais (valores atuais): R$ {custo_total_materiais:.2f}")
        print(f"   Custo etapas (valores atuais): R$ {custo_total_etapas:.2f}")
        print(f"   Custo total calculado: R$ {custo_total_novo:.2f}")
        print(f"   Preço com margem ({margem}%): R$ {preco_novo:.2f}")
        print(f"   Preço REGISTRADO no produto: R$ {preco_atual:.2f}")
        
        if preco_atual > 0:
            variacao = ((preco_novo - preco_atual) / preco_atual) * 100
            print(f"   Variação calculada: {variacao:.4f}%")
            
            if abs(variacao) < 1:
                print(f"   ✅ Variação INSIGNIFICANTE - produto NÃO deveria aparecer no modal")
            else:
                print(f"   ⚠️ Variação SIGNIFICATIVA - produto deveria aparecer no modal")
        else:
            print(f"   ⚠️ Preço atual é zero - não é possível calcular variação percentual")
        
    except Exception as e:
        print(f"❌ Erro durante análise: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

def verificar_funcao_backend():
    """Verifica como o backend está detectando alterações"""
    print("\n" + "=" * 80)
    print("🔍 VERIFICAÇÃO DA LÓGICA DO BACKEND")
    print("=" * 80)
    
    db = Database()
    
    try:
        # Simular exatamente o que a função verificar_alteracoes_custos faz
        print("Executando db.verificar_alteracoes_custos(7)...")
        alteracoes = db.verificar_alteracoes_custos(7)
        
        if alteracoes:
            print(f"\n📦 MATERIAIS 'ALTERADOS' detectados:")
            for mat in alteracoes.get('materiais', []):
                print(f"   - {mat['nome']} (ID: {mat['id']})")
                
                # Verificar por que este material foi considerado alterado
                db.cursor.execute("""
                    SELECT data_entrada, custo_unitario 
                    FROM entradas_estoque 
                    WHERE item_id = %s AND data_entrada >= DATE_SUB(NOW(), INTERVAL 7 DAY)
                    ORDER BY data_entrada DESC
                """, (mat['id'],))
                entradas = db.cursor.fetchall()
                
                print(f"     Entradas nos últimos 7 dias:")
                for entrada in entradas:
                    print(f"       {entrada['data_entrada']}: R$ {entrada['custo_unitario']}")
            
            print(f"\n⚙️ MÁQUINAS 'ALTERADAS' detectadas:")
            for maq in alteracoes.get('maquinas', []):
                print(f"   - {maq['nome']} (ID: {maq['id']})")
                
                # Verificar por que esta máquina foi considerada alterada
                db.cursor.execute("""
                    SELECT data_atualizacao, custo_hora
                    FROM maquinas
                    WHERE id = %s
                """, (maq['id'],))
                info_maquina = db.cursor.fetchone()
                
                if info_maquina:
                    print(f"     Data atualização: {info_maquina['data_atualizacao']}")
                    print(f"     Custo/hora atual: R$ {info_maquina['custo_hora']}")
            
            # Agora testar o impacto no produto
            print(f"\n🎯 CALCULANDO IMPACTO NO PRODUTO 61:")
            resultado = db.calcular_impacto_alteracoes_precos(alteracoes)
            produtos_afetados = resultado.get('produtos_afetados', [])
            
            print(f"Total de produtos afetados: {len(produtos_afetados)}")
            
            for produto in produtos_afetados:
                if produto['id'] == 61:
                    print(f"   📊 PRODUTO 61 ENCONTRADO:")
                    print(f"     - Nome: {produto['nome']}")
                    print(f"     - Preço atual: R$ {produto['preco_atual']}")
                    print(f"     - Novo preço: R$ {produto['novo_preco']}")
                    print(f"     - Variação: {produto['variacao_percentual']:.6f}%")
                    print(f"     - Diferença: R$ {produto['diferenca']}")
                    print(f"     - Impacto: {produto['impacto']}")
                    
                    if abs(produto['variacao_percentual']) < 1.0:
                        print(f"     ❌ PROBLEMA: Variação < 1% mas produto foi incluído!")
                    else:
                        print(f"     ✅ OK: Variação >= 1%")
                    break
            else:
                print(f"   ✅ Produto 61 não foi incluído nos afetados")
        else:
            print("   ✅ Nenhuma alteração detectada")
    
    except Exception as e:
        print(f"❌ Erro na verificação: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    print("🔍 ANÁLISE DETALHADA DO SISTEMA DE DETECÇÃO DE ALTERAÇÕES")
    print("=" * 80)
    
    buscar_produto_detalhes(61)
    verificar_funcao_backend()
    
    print(f"\n✅ Análise concluída!")
