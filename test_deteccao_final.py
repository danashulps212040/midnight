#!/usr/bin/env python3
"""
Teste final: Verificar se o sistema de detecção de alterações 
está funcionando corretamente através da API de verificação
"""

import sys
import os
sys.path.append('/Users/gabriel/Documents/Midnight/DEV23may2025')

from flask_gui import verificar_alteracoes_precos
import json

def testar_deteccao_alteracoes():
    """Testa o sistema de detecção de alterações"""
    print("🔍 TESTE DE DETECÇÃO DE ALTERAÇÕES")
    print("="*50)
    
    try:
        from flask_gui import flask_app
        
        with flask_app.app_context():
            # Chamar função de verificação
            resultado = verificar_alteracoes_precos()
            
            # Verificar se é uma resposta Flask
            if hasattr(resultado, 'get_json'):
                dados = resultado.get_json()
                status_code = resultado.status_code
            else:
                dados = resultado
                status_code = 200
            
            print(f"Status Code: {status_code}")
            print()
            
            if 'produtos_alterados' in dados:
                produtos_alterados = dados['produtos_alterados']
                
                print(f"📊 PRODUTOS COM ALTERAÇÕES DETECTADAS: {len(produtos_alterados)}")
                print()
                
                # Verificar se produto 63 foi detectado
                produto_63_encontrado = False
                
                for produto in produtos_alterados:
                    if produto.get('produto_id') == 63:
                        produto_63_encontrado = True
                        print(f"✅ PRODUTO 63 DETECTADO:")
                        print(f"   Nome: {produto.get('nome_produto')}")
                        print(f"   Preço atual: R$ {produto.get('preco_atual', 0):.2f}")
                        print(f"   Novo preço: R$ {produto.get('novo_preco_sugerido', 0):.2f}")
                        print(f"   Variação: {produto.get('variacao_percentual', 0):+.3f}%")
                        
                        alteracoes = produto.get('alteracoes_detectadas', {})
                        materiais = alteracoes.get('materiais', [])
                        etapas = alteracoes.get('etapas', [])
                        
                        print(f"   Materiais alterados: {len(materiais)}")
                        print(f"   Etapas alteradas: {len(etapas)}")
                        
                        if materiais:
                            print("\n   📦 Materiais:")
                            for material in materiais:
                                var_pct = material.get('variacao_percentual', 0)
                                print(f"      • {material.get('nome')}: {var_pct:+.1f}%")
                        
                        if etapas:
                            print("\n   🏭 Etapas:")
                            for etapa in etapas:
                                var_pct = etapa.get('variacao_percentual', 0)
                                print(f"      • {etapa.get('nome_etapa')}: {var_pct:+.1f}%")
                        
                        break
                
                if not produto_63_encontrado:
                    print("❌ PRODUTO 63 NÃO FOI DETECTADO")
                    print("   Verificando outros produtos encontrados:")
                    for produto in produtos_alterados[:3]:  # Mostrar até 3 produtos
                        print(f"   • Produto {produto.get('produto_id')}: {produto.get('nome_produto')}")
                
            else:
                print("❌ Nenhuma alteração detectada")
                print("Resposta completa:")
                print(json.dumps(dados, indent=2, ensure_ascii=False, default=str))
            
            # Salvar resposta completa
            with open('/Users/gabriel/Documents/Midnight/DEV23may2025/deteccao_alteracoes_resultado.json', 'w', encoding='utf-8') as f:
                json.dump(dados, f, indent=2, ensure_ascii=False, default=str)
            
            print(f"\n✓ Resposta completa salva em: deteccao_alteracoes_resultado.json")
            
            return dados
            
    except Exception as e:
        print(f"❌ Erro ao testar detecção: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    testar_deteccao_alteracoes()
