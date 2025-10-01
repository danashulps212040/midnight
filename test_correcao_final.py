#!/usr/bin/env python3
"""
Script para testar se a correção do filtro está funcionando
"""

from database import Database

def testar_correcao_filtro():
    """Testa o filtro corrigido"""
    
    print("🔧 TESTE DA CORREÇÃO DO FILTRO")
    print("=" * 50)
    
    db = Database()
    
    try:
        # 1. Testar a rota que estava funcionando corretamente
        print("1️⃣ Testando verificar_alteracoes_precos:")
        alteracoes = db.verificar_alteracoes_custos(7)
        
        if alteracoes:
            resultado = db.calcular_impacto_alteracoes_precos(alteracoes)
            produtos_afetados = resultado.get('produtos_afetados', [])
            print(f"   Total de produtos afetados: {len(produtos_afetados)}")
            
            produto_61_encontrado = False
            for produto in produtos_afetados:
                if produto['id'] == 61:
                    produto_61_encontrado = True
                    print(f"   ❌ PROBLEMA: Produto 61 ainda aparece!")
                    print(f"      Variação: {produto['variacao_percentual']:.6f}%")
                    break
            
            if not produto_61_encontrado:
                print(f"   ✅ CORRETO: Produto 61 não aparece (filtro backend funciona)")
        else:
            print("   ✅ Nenhuma alteração detectada")
        
        # 2. Testar chamada para detalhes-calculo (simular frontend)
        print("\n2️⃣ Testando detalhes-calculo do produto 61:")
        
        # Buscar produto
        produto = db.buscar_produto_por_id(61)
        print(f"   Produto: {produto['nome']}")
        print(f"   Preço atual: R$ {produto['preco']}")
        
        # Simular chamada para detalhes
        print("   📊 Verificando se há diferenças nos cálculos detalhados...")
        
        # Verificar materiais
        db.cursor.execute("""
            SELECT pm.*, ie.nome as material_nome, ie.custo_atual
            FROM produtos_materiais pm
            JOIN itens_estoque ie ON pm.material_id = ie.id
            WHERE pm.produto_id = 61
        """, ())
        materiais = db.cursor.fetchall()
        
        for material in materiais:
            preco_registrado = float(material['custo_unitario'] or 0)  # Corrigido nome da coluna
            custo_atual = float(material['custo_atual'] or 0) 
            diferenca = abs(custo_atual - preco_registrado)
            print(f"   Material {material['material_nome']}: diferença R$ {diferenca:.2f}")
            print(f"     - Custo registrado no produto: R$ {preco_registrado}")
            print(f"     - Custo atual no estoque: R$ {custo_atual}")
            
        # Verificar etapas
        db.cursor.execute("""
            SELECT pe.*, m.nome as maquina_nome, m.hora_maquina
            FROM produtos_etapas pe
            JOIN maquinas m ON pe.equipamento_id = m.id AND pe.equipamento_tipo = 'maquina'
            WHERE pe.produto_id = 61
        """, ())
        etapas = db.cursor.fetchall()
        
        for etapa in etapas:
            custo_registrado = float(etapa['custo_estimado'] or 0)
            tempo_horas = etapa['tempo_estimado'].total_seconds() / 3600
            custo_atual = float(etapa['hora_maquina']) * tempo_horas
            diferenca = abs(custo_atual - custo_registrado)
            print(f"   Etapa {etapa['nome']}: diferença R$ {diferenca:.2f}")
            
        print("\n3️⃣ RESULTADO ESPERADO:")
        print("   ✅ Backend: Produto 61 NÃO deve aparecer (variação < 1%)")
        print("   ✅ Frontend: Após correção, também NÃO deve aparecer")
        print("   💡 Teste manual: Acesse o sistema e clique em 'Verificar alterações'")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    testar_correcao_filtro()
