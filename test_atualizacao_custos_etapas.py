#!/usr/bin/env python3
"""
Script para testar a atualização dos custos das etapas quando o preço é atualizado
"""

import requests
import json
from database import Database

def testar_atualizacao_custos_etapas():
    """
    Testa se os custos das etapas são atualizados corretamente na tabela produtos_etapas
    """
    try:
        produto_id = 41
        
        print("🧪 Teste de Atualização de Custos das Etapas")
        print("=" * 60)
        
        # 1. Verificar estado inicial
        print("1️⃣ Verificando estado inicial...")
        db = Database()
        
        # Buscar custo atual das etapas na tabela
        query_etapas_antes = """
            SELECT pe.id, pe.nome, pe.custo_estimado, pe.tempo_estimado, pe.equipamento_id,
                   m.hora_maquina, m.nome as maquina_nome
            FROM produtos_etapas pe
            LEFT JOIN maquinas m ON pe.equipamento_id = m.id AND pe.equipamento_tipo = 'maquina'
            WHERE pe.produto_id = %s
        """
        db.cursor.execute(query_etapas_antes, (produto_id,))
        etapas_antes = db.cursor.fetchall()
        
        print(f"📋 Etapas antes da atualização:")
        for etapa in etapas_antes:
            print(f"  - {etapa['nome']}: R$ {float(etapa['custo_estimado'] or 0):.2f}")
            print(f"    Máquina: {etapa['maquina_nome']} (R$ {float(etapa['hora_maquina'] or 0):.2f}/h)")
            print(f"    Tempo: {etapa['tempo_estimado']}")
        
        # Buscar preço atual do produto
        query_produto = "SELECT preco FROM produtos WHERE id = %s"
        db.cursor.execute(query_produto, (produto_id,))
        resultado = db.cursor.fetchone()
        preco_atual = float(resultado['preco']) if resultado else 0
        print(f"💰 Preço atual do produto: R$ {preco_atual:.2f}")
        
        db.close()
        
        # 2. Simular atualização de preços via API
        print("\n2️⃣ Simulando atualização de preços...")
        
        # Calcular novo preço (exemplo: R$ 328.32 conforme seu cenário)
        novo_preco = 328.32
        
        # Dados para simular atualização de preços
        dados_atualizacao = {
            "produtos": [
                {
                    "id": produto_id,
                    "preco_anterior": preco_atual,
                    "novo_preco": novo_preco
                }
            ]
        }
        
        # Chamar API de atualização
        url_atualizacao = 'http://localhost:8000/api/produtos/atualizar-precos'
        response = requests.post(
            url_atualizacao,
            headers={'Content-Type': 'application/json'},
            data=json.dumps(dados_atualizacao)
        )
        
        print(f"📡 Resposta da API de atualização: {response.status_code}")
        if response.status_code == 200:
            resposta = response.json()
            print(f"✅ {resposta.get('atualizados', 0)} produto(s) atualizado(s)")
            if resposta.get('erros'):
                print(f"❌ Erros: {resposta['erros']}")
        else:
            print(f"❌ Erro na atualização: {response.text}")
            return
        
        # 3. Verificar estado após atualização
        print("\n3️⃣ Verificando estado após atualização...")
        
        db = Database()
        
        # Buscar custos das etapas após atualização
        db.cursor.execute(query_etapas_antes, (produto_id,))
        etapas_depois = db.cursor.fetchall()
        
        print(f"📋 Etapas após a atualização:")
        for etapa in etapas_depois:
            print(f"  - {etapa['nome']}: R$ {float(etapa['custo_estimado'] or 0):.2f}")
            print(f"    Máquina: {etapa['maquina_nome']} (R$ {float(etapa['hora_maquina'] or 0):.2f}/h)")
            print(f"    Tempo: {etapa['tempo_estimado']}")
        
        # Verificar se preço do produto foi atualizado
        db.cursor.execute(query_produto, (produto_id,))
        resultado = db.cursor.fetchone()
        preco_final = float(resultado['preco']) if resultado else 0
        print(f"💰 Preço final do produto: R$ {preco_final:.2f}")
        
        db.close()
        
        # 4. Comparar resultados
        print("\n4️⃣ Análise dos resultados:")
        print("=" * 40)
        
        custos_mudaram = False
        for antes, depois in zip(etapas_antes, etapas_depois):
            custo_antes = float(antes['custo_estimado'] or 0)
            custo_depois = float(depois['custo_estimado'] or 0)
            
            if abs(custo_antes - custo_depois) > 0.01:  # Diferença significativa
                print(f"✅ Etapa '{antes['nome']}': R$ {custo_antes:.2f} → R$ {custo_depois:.2f}")
                custos_mudaram = True
            else:
                print(f"⚠️ Etapa '{antes['nome']}': R$ {custo_antes:.2f} (não alterado)")
        
        if abs(preco_atual - preco_final) > 0.01:
            print(f"✅ Preço do produto: R$ {preco_atual:.2f} → R$ {preco_final:.2f}")
        else:
            print(f"⚠️ Preço do produto: R$ {preco_atual:.2f} (não alterado)")
        
        print("\n" + "=" * 60)
        if custos_mudaram:
            print("✅ SUCESSO: Os custos das etapas foram atualizados na tabela produtos_etapas!")
        else:
            print("❌ PROBLEMA: Os custos das etapas NÃO foram atualizados na tabela produtos_etapas!")
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    testar_atualizacao_custos_etapas()
