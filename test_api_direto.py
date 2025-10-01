#!/usr/bin/env python3
"""
Script para testar a API de detalhes de cálculo do produto 63 diretamente
"""

import sys
import os
sys.path.append('/Users/gabriel/Documents/Midnight/DEV23may2025')

from flask_gui import obter_detalhes_calculo_produto
import json

def testar_api_diretamente():
    """Testa a função da API diretamente sem passar pelo servidor Flask"""
    print("=== TESTE DIRETO DA API ===")
    
    try:
        # Simular contexto Flask mínimo
        class MockRequest:
            def __init__(self):
                self.method = 'GET'
        
        # Importar Flask app para contexto
        from flask_gui import flask_app
        
        with flask_app.app_context():
            # Chamar função diretamente
            resultado = obter_detalhes_calculo_produto(63)
            
            # Verificar se é uma resposta Flask
            if hasattr(resultado, 'get_json'):
                dados = resultado.get_json()
                status_code = resultado.status_code
            else:
                dados = resultado
                status_code = 200
            
            print(f"Status Code: {status_code}")
            print("Resposta:")
            print(json.dumps(dados, indent=2, ensure_ascii=False, default=str))
            
            # Salvar resposta
            with open('/Users/gabriel/Documents/Midnight/DEV23may2025/resposta_produto_63_direto.json', 'w', encoding='utf-8') as f:
                json.dump(dados, f, indent=2, ensure_ascii=False, default=str)
            
            print(f"\n✓ Resposta salva em: resposta_produto_63_direto.json")
            
            return dados
            
    except Exception as e:
        print(f"❌ Erro ao testar API diretamente: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    testar_api_diretamente()
