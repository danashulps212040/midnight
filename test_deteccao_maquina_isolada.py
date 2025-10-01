#!/usr/bin/env python3
"""
Teste específico para verificar se alterações no custo por hora de máquinas
estão sendo detectadas corretamente pelo sistema.
"""

import requests
import json
from database import Database
from datetime import datetime, timedelta

def testar_deteccao_alteracao_maquina():
    """
    Teste isolado de detecção de alteração em máquina específica
    """
    print("=== TESTE DE DETECÇÃO DE ALTERAÇÃO EM MÁQUINA ===\n")
    
    try:
        db = Database()
        
        # 1. Escolher uma máquina específica para teste
        print("1. Selecionando máquina para teste:")
        
        query_maquina = """
            SELECT m.id, m.nome, m.hora_maquina, m.data_atualizacao,
                   COUNT(pe.produto_id) as produtos_usando
            FROM maquinas m
            LEFT JOIN produtos_etapas pe ON m.id = pe.equipamento_id 
                                         AND pe.equipamento_tipo = 'maquina'
            WHERE m.hora_maquina > 0
            GROUP BY m.id, m.nome, m.hora_maquina, m.data_atualizacao
            HAVING produtos_usando > 0
            ORDER BY produtos_usando DESC
            LIMIT 1
        """
        
        db.cursor.execute(query_maquina)
        maquina = db.cursor.fetchone()
        
        if not maquina:
            print("❌ Nenhuma máquina encontrada com produtos associados!")
            return
        
        print(f"   ✅ Máquina selecionada: {maquina['nome']} (ID: {maquina['id']})")
        print(f"   💰 Custo atual: R$ {maquina['hora_maquina']}/hora")
        print(f"   📦 Produtos usando: {maquina['produtos_usando']}")
        print(f"   📅 Última atualização: {maquina['data_atualizacao']}")
        
        # 2. Verificar produtos que usam esta máquina
        print("\n2. Produtos que usam esta máquina:")
        
        query_produtos = """
            SELECT DISTINCT p.id, p.nome, p.preco, p.margem_lucro,
                   pe.tempo_estimado, pe.custo_estimado
            FROM produtos p
            INNER JOIN produtos_etapas pe ON p.id = pe.produto_id
            WHERE pe.equipamento_id = %s AND pe.equipamento_tipo = 'maquina'
            LIMIT 3
        """
        
        db.cursor.execute(query_produtos, (maquina['id'],))
        produtos = db.cursor.fetchall()
        
        for produto in produtos:
            print(f"   - {produto['nome']} (ID: {produto['id']})")
            print(f"     Preço atual: R$ {produto['preco']}")
            print(f"     Tempo na máquina: {produto['tempo_estimado']}")
            print(f"     Custo etapa: R$ {produto['custo_estimado']}")
        
        # 3. Simular alteração de preço na máquina
        print(f"\n3. Simulando alteração no custo da máquina:")
        
        custo_atual = float(maquina['hora_maquina'])
        custo_novo = round(custo_atual * 1.10, 2)  # Aumento de 10%
        
        print(f"   Custo anterior: R$ {custo_atual}/hora")
        print(f"   Custo novo: R$ {custo_novo}/hora")
        print(f"   Variação: +{((custo_novo - custo_atual) / custo_atual * 100):.2f}%")
        
        # 4. Testar detecção via API de simulação
        print("\n4. Testando detecção via API:")
        
        response = requests.get('http://localhost:8000/api/produtos/simular-mudancas')
        
        if response.status_code == 200:
            data = response.json()
            
            produtos_afetados = data.get('produtos_afetados', [])
            maquinas_alteradas = data.get('maquinas_alteradas', [])
            
            # Verificar se maquinas_alteradas é um inteiro (contagem) ou lista
            if isinstance(maquinas_alteradas, int):
                count_maquinas = maquinas_alteradas
                maquinas_alteradas = []
            else:
                count_maquinas = len(maquinas_alteradas) if maquinas_alteradas else 0
            
            print(f"   ✅ API respondeu com sucesso!")
            print(f"   📊 Produtos afetados: {len(produtos_afetados)}")
            print(f"   ⚙️ Máquinas alteradas: {count_maquinas}")
            
            # Debug: mostrar estrutura completa da resposta
            print(f"   🔍 Debug - estrutura da resposta:")
            for key, value in data.items():
                if key != 'produtos_afetados':
                    print(f"     {key}: {value} (tipo: {type(value)})")
            
            # Verificar se nossa máquina está nas alterações
            maquina_encontrada = False
            if maquinas_alteradas:  # Se for lista
                for maq_alt in maquinas_alteradas:
                    if maq_alt.get('id') == maquina['id']:
                        maquina_encontrada = True
                        print(f"   ✅ Máquina {maquina['nome']} encontrada nas alterações!")
                        print(f"   💰 Custo simulado: R$ {maq_alt['custo_por_hora']}/hora")
                        break
            
            if not maquina_encontrada:
                print(f"   ⚠️ Máquina {maquina['nome']} NÃO foi incluída nas alterações")
            
            # Verificar se produtos afetados incluem os que usam nossa máquina
            produtos_encontrados = 0
            for produto_id in [p['id'] for p in produtos]:
                for prod_afetado in produtos_afetados:
                    if prod_afetado['id'] == produto_id:
                        produtos_encontrados += 1
                        print(f"   ✅ Produto {prod_afetado['nome']} detectado como afetado!")
                        print(f"     Preço: R$ {prod_afetado['preco_atual']:.2f} → R$ {prod_afetado['novo_preco']:.2f}")
                        print(f"     Variação: {prod_afetado['variacao_percentual']:.2f}%")
                        break
            
            print(f"   📦 Produtos detectados: {produtos_encontrados}/{len(produtos)}")
            
        else:
            print(f"   ❌ Erro na API: {response.status_code}")
            print(f"   📄 Resposta: {response.text}")
        
        # 5. Testar detecção via verificação de alterações reais
        print("\n5. Testando verificação de alterações reais:")
        
        response = requests.post(
            'http://localhost:8000/api/produtos/verificar-alteracoes-precos',
            json={'dias': 7}
        )
        
        if response.status_code == 200:
            data = response.json()
            
            alteracoes_detectadas = data.get('alteracoes_detectadas', False)
            produtos_afetados = data.get('produtos_afetados', [])
            
            print(f"   ✅ API de verificação respondeu!")
            print(f"   🔍 Alterações detectadas: {alteracoes_detectadas}")
            print(f"   📊 Produtos afetados: {len(produtos_afetados)}")
            
            if produtos_afetados:
                print("   📦 Produtos encontrados:")
                for produto in produtos_afetados[:3]:
                    print(f"     - {produto['nome']}: R$ {produto['preco_atual']:.2f} → R$ {produto['novo_preco']:.2f}")
        else:
            print(f"   ❌ Erro na API: {response.status_code}")
        
        # 6. Teste direto no banco - calcular impacto
        print("\n6. Teste direto do cálculo de impacto:")
        
        alteracoes_teste = {
            'materiais': [],
            'maquinas': [{
                'id': maquina['id'],
                'nome': maquina['nome'],
                'custo_por_hora': custo_novo,
                'custo_por_hora_anterior': custo_atual,
                'variacao_percentual': ((custo_novo - custo_atual) / custo_atual * 100)
            }]
        }
        
        resultado = db.calcular_impacto_alteracoes_precos(alteracoes_teste)
        
        print(f"   📊 Produtos afetados pelo cálculo direto: {len(resultado['produtos_afetados'])}")
        
        if resultado['produtos_afetados']:
            print("   📦 Detalhes dos produtos afetados:")
            for produto in resultado['produtos_afetados'][:3]:
                print(f"     - {produto['nome']}")
                print(f"       Preço: R$ {produto['preco_atual']:.2f} → R$ {produto['novo_preco']:.2f}")
                print(f"       Variação: {produto['variacao_percentual']:.2f}%")
                print(f"       Causa: {produto['causa']}")
        else:
            print("   ⚠️ Nenhum produto foi detectado como afetado")
            print("   🔍 Verificando possíveis problemas:")
            
            # Debug: verificar se há produtos com variação mas abaixo do limiar
            for produto in produtos:
                # Calcular manualmente o que seria o novo custo
                if produto['tempo_estimado']:
                    tempo_horas = produto['tempo_estimado'].total_seconds() / 3600
                    custo_atual_etapa = float(produto['custo_estimado'] or 0)
                    custo_novo_etapa = custo_novo * tempo_horas
                    diferenca = custo_novo_etapa - custo_atual_etapa
                    
                    if abs(diferenca) > 0.01:  # Diferença maior que 1 centavo
                        print(f"     - {produto['nome']}: diferença de R$ {diferenca:.2f} na etapa")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Erro durante teste: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    testar_deteccao_alteracao_maquina()
