#!/usr/bin/env python3
"""
Teste de integração entre frontend e backend para verificação de alterações de preços
"""

import requests
import json

def test_verificar_alteracoes_precos():
    """
    Testa a API /api/produtos/verificar-alteracoes-precos
    """
    url = 'http://localhost:5000/api/produtos/verificar-alteracoes-precos'
    
    payload = {
        'dias': 7
    }
    
    try:
        print("🧪 Testando API de verificação de alterações de preços...")
        print(f"URL: {url}")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        print("-" * 60)
        
        response = requests.post(url, json=payload)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Resposta recebida com sucesso!")
            print(f"📊 Estrutura da resposta:")
            print(f"- alteracoes_detectadas: {data.get('alteracoes_detectadas')}")
            print(f"- produtos_afetados: {type(data.get('produtos_afetados'))} com {len(data.get('produtos_afetados', []))} itens")
            
            if data.get('resumo'):
                resumo = data['resumo']
                print(f"- resumo.total_produtos: {resumo.get('total_produtos')}")
                print(f"- resumo.materiais_alterados: {resumo.get('materiais_alterados')}")
                print(f"- resumo.maquinas_alteradas: {resumo.get('maquinas_alteradas')}")
            
            # Verificar se produtos_afetados é um array válido
            produtos_afetados = data.get('produtos_afetados', [])
            if isinstance(produtos_afetados, list):
                print("✅ produtos_afetados é um array válido")
                
                if produtos_afetados:
                    print(f"\n📋 Primeiro produto afetado:")
                    primeiro_produto = produtos_afetados[0]
                    for key, value in primeiro_produto.items():
                        print(f"  - {key}: {value}")
                        
                    print(f"\n🔍 Teste .map() simulado:")
                    try:
                        # Simular o que o frontend faria
                        produtos_processados = []
                        for produto in produtos_afetados:
                            produtos_processados.append({
                                'id': produto.get('id'),
                                'nome': produto.get('nome'),
                                'categoria': produto.get('categoria', 'Sem categoria'),
                                'preco_atual': produto.get('preco_atual'),
                                'novo_preco': produto.get('novo_preco'),
                                'variacao_percentual': produto.get('variacao_percentual'),
                                'impacto': produto.get('impacto'),
                                'causa': produto.get('causa'),
                                'materiais_alterados': produto.get('materiais_alterados', []),
                                'maquinas_alteradas': produto.get('maquinas_alteradas', []),
                                'selecionado': False
                            })
                        print(f"✅ Processamento .map() simulado bem-sucedido! {len(produtos_processados)} produtos processados")
                    except Exception as e:
                        print(f"❌ Erro no processamento .map() simulado: {e}")
                else:
                    print("ℹ️ Nenhum produto afetado encontrado")
            else:
                print(f"❌ produtos_afetados não é um array! Tipo: {type(produtos_afetados)}")
                print(f"Valor: {produtos_afetados}")
            
            print(f"\n📄 Resposta completa:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
        else:
            print(f"❌ Erro na requisição: {response.status_code}")
            print(f"Resposta: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Erro de conexão. Certifique-se de que o servidor Flask está rodando na porta 5000")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

if __name__ == "__main__":
    test_verificar_alteracoes_precos()
