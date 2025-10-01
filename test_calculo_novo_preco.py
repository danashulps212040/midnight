#!/usr/bin/env python3
"""
Teste rápido para calcular o novo preço do produto com alteração
da hora/máquina para R$ 11,00
"""

from database import Database
from datetime import timedelta

def calcular_novo_preco_produto():
    print("=== CÁLCULO DO NOVO PREÇO DO PRODUTO ===\n")
    
    try:
        db = Database()
        
        # 1. Buscar dados atuais do produto
        produto_id = 61  # "Produto teste 1"
        
        query_produto = """
            SELECT p.id, p.nome, p.preco, p.margem_lucro, p.custo_materiais, p.custo_etapas,
                   pe.tempo_estimado, pe.custo_estimado, pe.equipamento_id,
                   m.nome as maquina_nome, m.hora_maquina
            FROM produtos p
            LEFT JOIN produtos_etapas pe ON p.id = pe.produto_id AND pe.equipamento_tipo = 'maquina'
            LEFT JOIN maquinas m ON pe.equipamento_id = m.id
            WHERE p.id = %s
        """
        
        db.cursor.execute(query_produto, (produto_id,))
        produto = db.cursor.fetchone()
        
        if not produto:
            print("❌ Produto não encontrado!")
            return
        
        print(f"📦 Produto: {produto['nome']} (ID: {produto['id']})")
        print(f"💰 Preço atual: R$ {produto['preco']:.2f}")
        print(f"📊 Margem de lucro: {produto['margem_lucro']:.1f}%")
        print(f"🧱 Custo materiais: R$ {produto['custo_materiais'] or 0:.2f}")
        print(f"⚙️ Custo etapas atual: R$ {produto['custo_etapas'] or 0:.2f}")
        
        if produto['maquina_nome']:
            print(f"🔧 Máquina: {produto['maquina_nome']}")
            print(f"⏱️ Tempo estimado: {produto['tempo_estimado']}")
            print(f"💵 Custo/hora atual: R$ {produto['hora_maquina']:.2f}/hora")
        
        # 2. Calcular com novo valor da máquina
        novo_custo_hora = 11.00
        print(f"\n🔄 Alterando custo/hora para: R$ {novo_custo_hora:.2f}/hora")
        
        # Calcular novo custo da etapa
        if produto['tempo_estimado']:
            # Converter timedelta para horas decimais
            tempo_horas = produto['tempo_estimado'].total_seconds() / 3600
            novo_custo_etapa = novo_custo_hora * tempo_horas
            
            print(f"⏰ Tempo em horas: {tempo_horas:.4f}")
            print(f"💵 Novo custo da etapa: R$ {novo_custo_etapa:.2f}")
            
            # Calcular novo custo total
            custo_materiais = float(produto['custo_materiais'] or 0)
            novo_custo_total = custo_materiais + novo_custo_etapa
            
            # Calcular novo preço com margem
            margem = float(produto['margem_lucro'] or 0)
            novo_preco = novo_custo_total * (1 + margem / 100)
            
            print(f"\n📊 RESULTADO:")
            print(f"🧱 Custo materiais: R$ {custo_materiais:.2f}")
            print(f"⚙️ Novo custo etapas: R$ {novo_custo_etapa:.2f}")
            print(f"💰 Novo custo total: R$ {novo_custo_total:.2f}")
            print(f"📈 Margem aplicada: {margem:.1f}%")
            print(f"🎯 NOVO PREÇO: R$ {novo_preco:.2f}")
            
            # Comparar com preço atual
            diferenca = novo_preco - float(produto['preco'])
            variacao_percentual = (diferenca / float(produto['preco'])) * 100
            
            print(f"\n📉 COMPARAÇÃO:")
            print(f"📊 Preço atual: R$ {produto['preco']:.2f}")
            print(f"🎯 Novo preço: R$ {novo_preco:.2f}")
            print(f"📈 Diferença: R$ {diferenca:.2f}")
            print(f"📊 Variação: {variacao_percentual:.2f}%")
            
            if diferenca > 0:
                print(f"🔴 AUMENTO de R$ {diferenca:.2f}")
            else:
                print(f"🟢 REDUÇÃO de R$ {abs(diferenca):.2f}")
        
        # 3. Testar usando a função do sistema
        print(f"\n🧪 TESTE COM FUNÇÃO DO SISTEMA:")
        
        alteracoes_teste = {
            'materiais': [],
            'maquinas': [{
                'id': produto['equipamento_id'],
                'nome': produto['maquina_nome'],
                'custo_por_hora': novo_custo_hora,
                'custo_por_hora_anterior': float(produto['hora_maquina']),
                'variacao_percentual': ((novo_custo_hora - float(produto['hora_maquina'])) / float(produto['hora_maquina']) * 100)
            }]
        }
        
        resultado = db.calcular_impacto_alteracoes_precos(alteracoes_teste)
        
        if resultado['produtos_afetados']:
            produto_resultado = resultado['produtos_afetados'][0]
            print(f"✅ Sistema calculou:")
            print(f"   Preço atual: R$ {produto_resultado['preco_atual']:.2f}")
            print(f"   Novo preço: R$ {produto_resultado['novo_preco']:.2f}")
            print(f"   Variação: {produto_resultado['variacao_percentual']:.2f}%")
        else:
            print("❌ Sistema não detectou alteração (possível filtro muito restritivo)")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    calcular_novo_preco_produto()
