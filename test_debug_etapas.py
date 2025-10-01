#!/usr/bin/env python3
"""
Script para testar diretamente o banco de dados e verificar o cálculo
"""

import sys
import os

# Adicionar o diretório atual ao path para importar database
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import Database

def test_alteracoes_maquinas():
    """
    Testa as consultas de alterações de máquinas
    """
    try:
        db = Database()
        
        print("🔍 Verificando histórico de alterações de máquinas...")
        
        # Verificar se há registros no histórico
        query_historico = """
            SELECT hm.*, m.nome
            FROM historico_custos_maquinas hm
            INNER JOIN maquinas m ON hm.maquina_id = m.id
            ORDER BY hm.data_alteracao DESC
            LIMIT 5
        """
        db.cursor.execute(query_historico)
        historico = db.cursor.fetchall()
        
        print(f"📊 Registros no histórico: {len(historico)}")
        for reg in historico:
            print(f"  - Máquina: {reg['nome']} (ID: {reg['maquina_id']})")
            print(f"    Valor anterior: R$ {reg['hora_maquina_anterior']:.2f}")
            print(f"    Valor novo: R$ {reg['hora_maquina_nova']:.2f}")
            print(f"    Data: {reg['data_alteracao']}")
            print()
        
        # Testar a consulta específica usada na API
        query_alteracoes = """
            SELECT hm.maquina_id, MAX(hm.hora_maquina_nova) as valor_hora_mais_recente,
                   m.hora_maquina as valor_hora_atual
            FROM historico_custos_maquinas hm
            INNER JOIN maquinas m ON hm.maquina_id = m.id
            WHERE hm.data_alteracao >= (NOW() - INTERVAL 7 DAY)
            GROUP BY hm.maquina_id, m.hora_maquina
        """
        db.cursor.execute(query_alteracoes)
        alteracoes = db.cursor.fetchall()
        
        print(f"🔧 Alterações detectadas (últimos 7 dias): {len(alteracoes)}")
        alteracoes_dict = {}
        for alt in alteracoes:
            alteracoes_dict[alt['maquina_id']] = alt
            print(f"  - Máquina ID {alt['maquina_id']}:")
            print(f"    Valor mais recente: R$ {alt['valor_hora_mais_recente']:.2f}")
            print(f"    Valor atual: R$ {alt['valor_hora_atual']:.2f}")
            print()
        
        # Buscar etapas do produto 40
        produto_id = 40
        query_etapas = """
            SELECT pe.equipamento_id, pe.equipamento_tipo, pe.custo_estimado, pe.tempo_estimado,
                   m.hora_maquina, m.nome as maquina_nome
            FROM produtos_etapas pe
            LEFT JOIN maquinas m ON pe.equipamento_id = m.id AND pe.equipamento_tipo = 'maquina'
            WHERE pe.produto_id = %s
        """
        db.cursor.execute(query_etapas, (produto_id,))
        etapas = db.cursor.fetchall()
        
        print(f"⚙️ Etapas do produto {produto_id}: {len(etapas)}")
        
        custo_etapas_total = 0
        for etapa in etapas:
            print(f"  - Etapa: {etapa.get('equipamento_tipo', 'N/A')}")
            print(f"    Equipamento ID: {etapa.get('equipamento_id')}")
            print(f"    Máquina: {etapa.get('maquina_nome')}")
            print(f"    Custo estimado: R$ {float(etapa.get('custo_estimado') or 0):.2f}")
            print(f"    Tempo estimado: {etapa.get('tempo_estimado')}")
            print(f"    Hora máquina atual: R$ {float(etapa.get('hora_maquina') or 0):.2f}")
            
            if etapa['equipamento_tipo'] == 'maquina' and etapa['equipamento_id']:
                # Calcular como na API
                tempo_horas = 0
                if etapa['tempo_estimado']:
                    tempo_str = str(etapa['tempo_estimado'])
                    if ':' in tempo_str:
                        partes = tempo_str.split(':')
                        horas = float(partes[0]) if len(partes) > 0 else 0
                        minutos = float(partes[1]) if len(partes) > 1 else 0
                        segundos = float(partes[2]) if len(partes) > 2 else 0
                        tempo_horas = horas + (minutos / 60.0) + (segundos / 3600.0)
                    else:
                        tempo_horas = float(tempo_str)
                
                # Verificar se há alteração
                alteracao_maquina = alteracoes_dict.get(etapa['equipamento_id'])
                if alteracao_maquina:
                    valor_hora = float(alteracao_maquina['valor_hora_mais_recente'])
                    print(f"    ✅ USANDO VALOR ALTERADO: R$ {valor_hora:.2f}/h")
                else:
                    valor_hora = float(etapa['hora_maquina'] or 0)
                    print(f"    ⚠️ USANDO VALOR ATUAL: R$ {valor_hora:.2f}/h")
                
                custo_etapa = tempo_horas * valor_hora
                custo_etapas_total += custo_etapa
                print(f"    💰 Cálculo: {tempo_horas:.6f}h × R$ {valor_hora:.2f} = R$ {custo_etapa:.2f}")
            
            elif etapa['custo_estimado'] and etapa['custo_estimado'] > 0:
                custo_estimado = float(etapa['custo_estimado'])
                custo_etapas_total += custo_estimado
                print(f"    💰 Usando custo estimado: R$ {custo_estimado:.2f}")
            
            print()
        
        print(f"💰 CUSTO TOTAL DAS ETAPAS: R$ {custo_etapas_total:.2f}")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_alteracoes_maquinas()
