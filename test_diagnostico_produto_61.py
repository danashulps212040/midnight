#!/usr/bin/env python3
"""
Script simplificado para verificar por que o produto 61 aparece no modal
"""

from database import Database
from datetime import datetime, timedelta

def verificar_problema_produto_61():
    """Verifica especificamente por que o produto 61 está aparecendo no modal"""
    
    print("🔍 DIAGNÓSTICO: Por que produto 61 aparece no modal?")
    print("=" * 60)
    
    db = Database()
    
    try:
        # 1. Buscar o produto
        produto = db.buscar_produto_por_id(61)
        print(f"📦 Produto: {produto['nome']}")
        print(f"   Preço atual: R$ {produto['preco']}")
        print()
        
        # 2. Verificar alterações detectadas pelo sistema
        alteracoes = db.verificar_alteracoes_custos(7)
        print(f"🔍 Alterações detectadas nos últimos 7 dias:")
        print(f"   Materiais: {len(alteracoes.get('materiais', []))}")
        print(f"   Máquinas: {len(alteracoes.get('maquinas', []))}")
        print()
        
        # 3. Listar máquinas alteradas
        if alteracoes and alteracoes.get('maquinas'):
            print("⚙️ Máquinas detectadas como alteradas:")
            for maq in alteracoes['maquinas']:
                print(f"   - {maq['nome']} (ID: {maq['id']})")
                
                # Verificar quando foi alterada
                db.cursor.execute("""
                    SELECT data_atualizacao, hora_maquina 
                    FROM maquinas 
                    WHERE id = %s
                """, (maq['id'],))
                info = db.cursor.fetchone()
                print(f"     Última atualização: {info['data_atualizacao']}")
                print(f"     Custo/hora atual: R$ {info['hora_maquina']}")
            print()
        
        # 4. Verificar se o produto usa essas máquinas
        print("🔗 Verificando se produto 61 usa essas máquinas:")
        db.cursor.execute("""
            SELECT pe.*, m.nome as maquina_nome, m.hora_maquina
            FROM produtos_etapas pe
            JOIN maquinas m ON pe.equipamento_id = m.id AND pe.equipamento_tipo = 'maquina'
            WHERE pe.produto_id = 61
        """, ())
        
        etapas_maquinas = db.cursor.fetchall()
        
        if etapas_maquinas:
            print("   ✅ SIM, o produto usa máquinas:")
            for etapa in etapas_maquinas:
                print(f"     - Etapa: {etapa['nome']}")
                print(f"       Máquina: {etapa['maquina_nome']} (ID: {etapa['equipamento_id']})")
                print(f"       Tempo: {etapa['tempo_estimado']} horas")
                print(f"       Custo registrado: R$ {etapa['custo_estimado']}")
                print(f"       Custo atual da máquina: R$ {etapa['hora_maquina']}/hora")
                
                # Calcular se há diferença real
                if etapa['tempo_estimado'] and etapa['hora_maquina']:
                    # Converter timedelta para horas
                    tempo_horas = etapa['tempo_estimado'].total_seconds() / 3600
                    custo_atual = float(etapa['hora_maquina']) * tempo_horas
                    custo_registrado = float(etapa['custo_estimado'] or 0)
                    diferenca = custo_atual - custo_registrado
                    print(f"       Tempo em horas: {tempo_horas:.4f}")
                    print(f"       Custo atual calculado: R$ {custo_atual:.2f}")
                    print(f"       Diferença: R$ {diferenca:.2f}")
                    
                    if abs(diferenca) < 0.01:
                        print(f"       ✅ SEM DIFERENÇA REAL!")
                    else:
                        print(f"       🚨 DIFERENÇA REAL ENCONTRADA!")
                print()
        else:
            print("   ❌ NÃO, o produto não usa máquinas")
        
        # 5. Calcular impacto real
        print("💰 Calculando impacto real no preço:")
        
        if alteracoes:
            resultado = db.calcular_impacto_alteracoes_precos(alteracoes)
            produtos_afetados = resultado.get('produtos_afetados', [])
            
            produto_encontrado = None
            for prod in produtos_afetados:
                if prod['id'] == 61:
                    produto_encontrado = prod
                    break
            
            if produto_encontrado:
                print(f"   🎯 Produto 61 FOI INCLUÍDO:")
                print(f"     Preço atual: R$ {produto_encontrado['preco_atual']}")
                print(f"     Novo preço: R$ {produto_encontrado['novo_preco']}")
                print(f"     Variação: {produto_encontrado['variacao_percentual']:.6f}%")
                print(f"     Diferença: R$ {produto_encontrado['diferenca']}")
                
                # AQUI ESTÁ O PROBLEMA!
                if abs(produto_encontrado['variacao_percentual']) < 1.0:
                    print(f"   ❌ PROBLEMA IDENTIFICADO:")
                    print(f"      Variação {produto_encontrado['variacao_percentual']:.6f}% < 1%")
                    print(f"      MAS o produto foi incluído mesmo assim!")
                    print(f"      CAUSA: O filtro no backend NÃO está funcionando!")
                else:
                    print(f"   ✅ Variação >= 1%, inclusão justificada")
            else:
                print(f"   ✅ Produto 61 NÃO foi incluído (correto)")
        
        # 6. Verificar por que a data_atualizacao das máquinas é recente
        print("\n🕐 Verificando por que máquinas têm data_atualizacao recente:")
        
        if alteracoes and alteracoes.get('maquinas'):
            for maq in alteracoes['maquinas']:
                print(f"   Máquina: {maq['nome']}")
                
                # Verificar histórico se existe
                db.cursor.execute("""
                    SELECT * FROM historico_custos_maquinas 
                    WHERE maquina_id = %s 
                    ORDER BY data_alteracao DESC 
                    LIMIT 3
                """, (maq['id'],))
                historico = db.cursor.fetchall()
                
                if historico:
                    print(f"     Histórico de alterações:")
                    for h in historico:
                        print(f"       {h['data_alteracao']}: R$ {h['custo_anterior']} → R$ {h['custo_novo']}")
                else:
                    print(f"     Sem histórico de alterações registrado")
                    print(f"     PROVÁVEL CAUSA: Máquina foi criada/editada recentemente")
                    print(f"     mas o custo não mudou realmente")
    
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    verificar_problema_produto_61()
