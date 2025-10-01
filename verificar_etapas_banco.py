#!/usr/bin/env python3
"""
Teste direto no banco para verificar se os tipos de etapa estão sendo salvos.
"""

from database import Database

def verificar_etapas_no_banco():
    """Verifica as etapas salvas no banco e seus tipos."""
    
    print("=== VERIFICAÇÃO: Etapas no banco de dados ===")
    
    try:
        db = Database()
        
        # Consultar diretamente as etapas na tabela
        query = """
        SELECT pe.id, pe.produto_id, pe.nome, pe.tipo, pe.equipamento_tipo, 
               pe.equipamento_id, pe.equipamento_nome, pe.tempo_estimado, pe.custo_estimado,
               p.nome as produto_nome
        FROM produtos_etapas pe
        LEFT JOIN produtos p ON pe.produto_id = p.id
        ORDER BY pe.produto_id, pe.id
        """
        
        db.cursor.execute(query)
        etapas = db.cursor.fetchall()
        
        if etapas:
            print(f"\n📋 Encontradas {len(etapas)} etapas no banco:")
            print("-" * 100)
            
            for etapa in etapas:
                print(f"ID: {etapa[0]:<3} | Produto: {etapa[9]:<25} | Etapa: {etapa[2]:<20}")
                print(f"      Tipo: '{etapa[3]}' | Equipamento Tipo: '{etapa[4]}' | Equipamento: {etapa[6] or 'N/A'}")
                print(f"      Tempo: {etapa[7]} | Custo: R$ {etapa[8] or 0}")
                print("-" * 100)
        else:
            print("\n📭 Nenhuma etapa encontrada no banco.")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro ao consultar banco: {e}")
        return False

if __name__ == "__main__":
    verificar_etapas_no_banco()
