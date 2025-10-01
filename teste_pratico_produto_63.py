#!/usr/bin/env python3
"""
Teste prático conforme especificação do usuário:
Produto: Fachada ACM 100x100 (ID: 63)

ESTADO INICIAL:
- Chapa ACM 122x500: R$ 1.045,00 (inteira) → uso proporcional 1m² = R$ 171,31
- 2 pacotes de parafusos: R$ 20,00 cada = R$ 40,00 total
- 2 etapas VUZE: 00h 01m 49s cada, R$ 10,00/h → R$ 0,30 cada = R$ 0,60 total
- Custo total atual: R$ 211,91

ALTERAÇÕES A APLICAR:
- VUZE: R$ 10,00/h → R$ 15,00/h (+50%)
- Chapa inteira: R$ 1.045,00 → R$ 2.000,00 (+91,39%)
- Pacote parafusos: R$ 20,00 → R$ 25,00 (+25%)

CALCULAR: Novo preço sugerido
"""

import mysql.connector as mysql_conn
from decimal import Decimal
import json

# Configuração do banco
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'als32@#nss',
    'database': 'midnight'
}

def conectar_banco():
    return mysql_conn.connect(**DB_CONFIG)

def verificar_estado_inicial():
    """Verifica o estado inicial do produto 63"""
    print("🔍 VERIFICANDO ESTADO INICIAL DO PRODUTO 63")
    print("="*60)
    
    conn = conectar_banco()
    cursor = conn.cursor()
    
    try:
        # 1. Dados básicos do produto
        cursor.execute("""
            SELECT id, nome, codigo, preco, margem_lucro
            FROM produtos 
            WHERE id = 63
        """)
        produto = cursor.fetchone()
        if produto:
            print(f"Produto: {produto[1]} (Código: {produto[2]})")
            print(f"Preço atual: R$ {produto[3]:.2f}")
            print(f"Margem de lucro: {produto[4]:.1f}%")
        
        # 2. Máquina VUZE
        cursor.execute("""
            SELECT id, nome, hora_maquina 
            FROM maquinas 
            WHERE nome LIKE '%VUZE%'
        """)
        maquina = cursor.fetchone()
        if maquina:
            print(f"\nMáquina: {maquina[1]}")
            print(f"Hora/máquina atual: R$ {maquina[2]:.2f}")
        
        # 3. Materiais do produto com custos atuais
        cursor.execute("""
            SELECT DISTINCT pm.material_id, ie.nome,
                   (SELECT custo_unitario 
                    FROM entradas_estoque ee 
                    WHERE ee.item_id = pm.material_id 
                    AND ee.custo_unitario IS NOT NULL
                    ORDER BY ee.data_entrada DESC 
                    LIMIT 1) as custo_atual,
                   pm.quantidade_necessaria
            FROM produtos_materiais pm
            JOIN itens_estoque ie ON pm.material_id = ie.id
            WHERE pm.produto_id = 63
        """)
        materiais = cursor.fetchall()
        print(f"\nMateriais:")
        for material_id, nome, custo_atual, quantidade in materiais:
            print(f"  • {nome}: R$ {custo_atual:.2f} (qtd: {quantidade})")
        
        # 4. Etapas do produto
        cursor.execute("""
            SELECT pe.nome_etapa, pe.tempo_estimado, 
                   m.nome as nome_maquina, m.hora_maquina
            FROM produtos_etapas pe
            LEFT JOIN maquinas m ON pe.equipamento_id = m.id
            WHERE pe.produto_id = 63
        """)
        etapas = cursor.fetchall()
        print(f"\nEtapas:")
        for nome_etapa, tempo, nome_maq, custo_maq in etapas:
            if nome_maq:
                tempo_decimal = float(tempo)
                custo_etapa = tempo_decimal * float(custo_maq)
                # Converter tempo para hh:mm:ss
                horas = int(tempo_decimal)
                minutos = int((tempo_decimal - horas) * 60)
                segundos = int(((tempo_decimal - horas) * 60 - minutos) * 60)
                print(f"  • {nome_etapa}: {horas:02d}h {minutos:02d}m {segundos:02d}s × R$ {custo_maq:.2f} = R$ {custo_etapa:.2f}")
            else:
                print(f"  • {nome_etapa}: sem máquina")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
    finally:
        cursor.close()
        conn.close()

def aplicar_alteracoes():
    """Aplica as alterações especificadas"""
    print("\n" + "="*60)
    print("🔧 APLICANDO ALTERAÇÕES")
    print("="*60)
    
    conn = conectar_banco()
    cursor = conn.cursor()
    
    try:
        # 1. Alterar hora/máquina da VUZE: R$ 10,00 → R$ 15,00
        print("1. Alterando custo da máquina VUZE...")
        cursor.execute("""
            UPDATE maquinas 
            SET hora_maquina = 15.00 
            WHERE nome LIKE '%VUZE%'
        """)
        print("   ✓ VUZE: R$ 10,00/h → R$ 15,00/h (+50%)")
        
        # 2. Alterar custo da chapa: R$ 1.045,00 → R$ 2.000,00
        print("\n2. Alterando custo da chapa ACM...")
        cursor.execute("""
            SELECT pm.material_id 
            FROM produtos_materiais pm
            JOIN itens_estoque ie ON pm.material_id = ie.id
            WHERE pm.produto_id = 63 AND ie.nome LIKE '%ACM%'
        """)
        chapa_id = cursor.fetchone()
        if chapa_id:
            cursor.execute("""
                INSERT INTO entradas_estoque 
                (item_id, quantidade, custo_unitario, data_entrada, observacoes)
                VALUES (%s, 1, 2000.00, NOW(), 'Teste prático - alteração R$1045→R$2000')
            """, (chapa_id[0],))
            print("   ✓ Chapa ACM: R$ 1.045,00 → R$ 2.000,00 (+91,39%)")
        
        # 3. Alterar custo do parafuso: R$ 20,00 → R$ 25,00
        print("\n3. Alterando custo dos parafusos...")
        cursor.execute("""
            SELECT pm.material_id 
            FROM produtos_materiais pm
            JOIN itens_estoque ie ON pm.material_id = ie.id
            WHERE pm.produto_id = 63 AND ie.nome LIKE '%parafuso%'
        """)
        parafuso_id = cursor.fetchone()
        if parafuso_id:
            cursor.execute("""
                INSERT INTO entradas_estoque 
                (item_id, quantidade, custo_unitario, data_entrada, observacoes)
                VALUES (%s, 100, 25.00, NOW(), 'Teste prático - alteração R$20→R$25 (pacote)')
            """, (parafuso_id[0],))
            print("   ✓ Parafuso: R$ 20,00 → R$ 25,00 (+25%)")
        
        conn.commit()
        print("\n✅ Todas as alterações aplicadas com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro ao aplicar alterações: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

def calcular_novo_preco():
    """Calcula o novo preço usando a API"""
    print("\n" + "="*60)
    print("💰 CALCULANDO NOVO PREÇO")
    print("="*60)
    
    try:
        import sys
        import os
        sys.path.append('/Users/gabriel/Documents/Midnight/DEV23may2025')
        
        from flask_gui import obter_detalhes_calculo_produto, flask_app
        
        with flask_app.app_context():
            resultado = obter_detalhes_calculo_produto(63)
            
            if hasattr(resultado, 'get_json'):
                dados = resultado.get_json()
            else:
                dados = resultado
            
            # Extrair informações do cálculo
            produto = dados['produto']
            materiais = dados['materiais']
            custo_etapas = dados['custo_etapas']
            
            print("📊 DETALHAMENTO DO NOVO CÁLCULO:")
            print(f"Preço anterior: R$ {produto.get('preco_atual', 211.91):.2f}")
            print(f"Novo preço calculado: R$ {produto['preco']:.2f}")
            
            diferenca = produto['preco'] - produto.get('preco_atual', 211.91)
            variacao = (diferenca / produto.get('preco_atual', 211.91)) * 100
            print(f"Diferença: R$ {diferenca:+.2f}")
            print(f"Variação: {variacao:+.2f}%")
            
            print(f"\n🔧 CUSTOS DETALHADOS:")
            print(f"Etapas: R$ {custo_etapas:.2f}")
            print(f"Materiais: R$ {produto['custo_materiais']:.2f}")
            print(f"Total: R$ {produto['custo_total']:.2f}")
            
            print(f"\n📦 ANÁLISE DOS MATERIAIS:")
            for material in materiais:
                nome = material['nome']
                custo_novo = material['custo_unitario_novo']
                
                if 'ACM' in nome:
                    print(f"  • {nome}:")
                    print(f"    Custo inteiro: R$ {custo_novo:.2f}")
                    area_prop = material['area_utilizada'] / material['area_total']
                    custo_proporcional = custo_novo * area_prop
                    print(f"    Área utilizada: {material['area_utilizada']:.1f}m² de {material['area_total']:.1f}m² ({area_prop*100:.1f}%)")
                    print(f"    Custo proporcional: R$ {custo_proporcional:.2f}")
                elif 'parafuso' in nome.lower():
                    qtd_pacotes = material['quantidade_necessaria'] / (material['unidades_por_pacote'] or 1)
                    custo_total_parafusos = qtd_pacotes * custo_novo
                    print(f"  • {nome}:")
                    print(f"    Custo por pacote: R$ {custo_novo:.2f}")
                    print(f"    Quantidade: {material['quantidade_necessaria']} un = {qtd_pacotes:.0f} pacotes")
                    print(f"    Custo total: R$ {custo_total_parafusos:.2f}")
            
            print(f"\n🏭 ANÁLISE DAS ETAPAS:")
            conn = conectar_banco()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT pe.nome_etapa, pe.tempo_estimado, m.hora_maquina
                FROM produtos_etapas pe
                JOIN maquinas m ON pe.equipamento_id = m.id
                WHERE pe.produto_id = 63 AND m.nome LIKE '%VUZE%'
            """)
            etapas = cursor.fetchall()
            
            custo_total_etapas = 0
            for i, (nome_etapa, tempo, custo_hora) in enumerate(etapas, 1):
                tempo_decimal = float(tempo)
                custo_etapa = tempo_decimal * float(custo_hora)
                custo_total_etapas += custo_etapa
                
                # Converter para hh:mm:ss
                horas = int(tempo_decimal)
                minutos = int((tempo_decimal - horas) * 60)
                segundos = int(((tempo_decimal - horas) * 60 - minutos) * 60)
                
                print(f"  • Etapa {i}: {horas:02d}h {minutos:02d}m {segundos:02d}s × R$ {custo_hora:.2f} = R$ {custo_etapa:.2f}")
            
            print(f"  Total etapas: R$ {custo_total_etapas:.2f}")
            
            cursor.close()
            conn.close()
            
            return dados
            
    except Exception as e:
        print(f"❌ Erro no cálculo: {e}")
        import traceback
        traceback.print_exc()
        return None

def calcular_manualmente():
    """Calcula manualmente para validar"""
    print("\n" + "="*60)
    print("🧮 CÁLCULO MANUAL DE VALIDAÇÃO")
    print("="*60)
    
    # Valores após as alterações
    vuze_hora = 15.00  # R$/h
    chapa_inteira = 2000.00  # R$
    parafuso_pacote = 25.00  # R$/pacote
    
    # Especificações do produto
    area_chapa_total = 6.1  # m² (122cm × 500cm = 6.1m²)
    area_utilizada = 1.0  # m²
    qtd_parafusos = 2  # unidades (= 1 pacote, assumindo 100 unidades por pacote? Ou 2 pacotes?)
    tempo_etapa = 109/3600  # 1min 49s = 109s = 109/3600 h ≈ 0.030278h
    
    print("📏 ESPECIFICAÇÕES:")
    print(f"Chapa ACM 122×500: {area_chapa_total}m² total")
    print(f"Área utilizada: {area_utilizada}m²")
    print(f"Parafusos necessários: {qtd_parafusos} unidades")
    print(f"Tempo por etapa: {tempo_etapa:.6f}h (1min 49s)")
    
    print(f"\n💰 CUSTOS APÓS ALTERAÇÕES:")
    print(f"VUZE: R$ {vuze_hora:.2f}/h")
    print(f"Chapa inteira: R$ {chapa_inteira:.2f}")
    print(f"Pacote parafusos: R$ {parafuso_pacote:.2f}")
    
    print(f"\n🧮 CÁLCULO:")
    
    # 1. Custo da chapa (proporcional)
    custo_chapa_prop = chapa_inteira * (area_utilizada / area_chapa_total)
    print(f"1. Chapa (proporcional): R$ {chapa_inteira:.2f} × ({area_utilizada}/{area_chapa_total}) = R$ {custo_chapa_prop:.2f}")
    
    # 2. Custo dos parafusos (assumindo 2 pacotes baseado no valor original R$40,00 = 2×R$20,00)
    qtd_pacotes = 2  # Baseado no cenário original
    custo_parafusos = qtd_pacotes * parafuso_pacote
    print(f"2. Parafusos: {qtd_pacotes} pacotes × R$ {parafuso_pacote:.2f} = R$ {custo_parafusos:.2f}")
    
    # 3. Custo das etapas
    qtd_etapas = 2
    custo_por_etapa = tempo_etapa * vuze_hora
    custo_total_etapas = qtd_etapas * custo_por_etapa
    print(f"3. Etapas: {qtd_etapas} × ({tempo_etapa:.6f}h × R$ {vuze_hora:.2f}) = R$ {custo_total_etapas:.2f}")
    
    # Total
    custo_total = custo_chapa_prop + custo_parafusos + custo_total_etapas
    print(f"\n📊 RESUMO:")
    print(f"Materiais: R$ {custo_chapa_prop + custo_parafusos:.2f}")
    print(f"Etapas: R$ {custo_total_etapas:.2f}")
    print(f"TOTAL: R$ {custo_total:.2f}")
    
    # Comparação com valor original
    valor_original = 211.91
    diferenca = custo_total - valor_original
    variacao = (diferenca / valor_original) * 100
    
    print(f"\n📈 COMPARAÇÃO:")
    print(f"Valor original: R$ {valor_original:.2f}")
    print(f"Novo valor: R$ {custo_total:.2f}")
    print(f"Diferença: R$ {diferenca:+.2f}")
    print(f"Variação: {variacao:+.2f}%")

def main():
    print("🎯 TESTE PRÁTICO - PRODUTO 63 FACHADA ACM 100x100")
    print("="*70)
    
    # 1. Verificar estado inicial
    verificar_estado_inicial()
    
    # 2. Aplicar alterações
    aplicar_alteracoes()
    
    # 3. Calcular novo preço via API
    resultado_api = calcular_novo_preco()
    
    # 4. Calcular manualmente para validar
    calcular_manualmente()
    
    print("\n" + "="*70)
    print("🎉 TESTE PRÁTICO CONCLUÍDO!")
    print("="*70)
    
    if resultado_api:
        # Salvar resultado completo
        with open('/Users/gabriel/Documents/Midnight/DEV23may2025/resultado_teste_pratico_produto_63.json', 'w', encoding='utf-8') as f:
            json.dump(resultado_api, f, indent=2, ensure_ascii=False, default=str)
        print("📁 Resultado salvo em: resultado_teste_pratico_produto_63.json")

if __name__ == "__main__":
    main()
