#!/usr/bin/env python3
"""
Script de teste para verificar as APIs de atualização de preços
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_verificar_mudancas_custos():
    """Testa a API de verificação de mudanças de custos"""
    print("🧪 Testando API: /api/produtos/verificar-mudancas-custos")
    
    url = f"{BASE_URL}/api/produtos/verificar-mudancas-custos"
    data = {
        "materiais_ids": [1, 2, 3],
        "maquinas_ids": [1, 2]
    }
    
    try:
        response = requests.post(url, json=data, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def test_calcular_novos_precos():
    """Testa a API de cálculo de novos preços"""
    print("\n🧪 Testando API: /api/produtos/calcular-novos-precos")
    
    url = f"{BASE_URL}/api/produtos/calcular-novos-precos"
    data = {
        "produtos_ids": [1, 2, 3]
    }
    
    try:
        response = requests.post(url, json=data, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def test_simular_mudancas():
    """Testa a API de simulação"""
    print("\n🧪 Testando API: /api/produtos/simular-mudancas")
    
    url = f"{BASE_URL}/api/produtos/simular-mudancas"
    
    try:
        response = requests.get(url, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def test_atualizar_precos():
    """Testa a API de atualização de preços"""
    print("\n🧪 Testando API: /api/produtos/atualizar-precos")
    
    url = f"{BASE_URL}/api/produtos/atualizar-precos"
    data = {
        "produtos": [
            {
                "id": 1,
                "novo_preco": 150.75,
                "custo_materiais": 80.50,
                "custo_etapas": 45.25
            }
        ]
    }
    
    try:
        response = requests.post(url, json=data, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def test_server_connectivity():
    """Testa se o servidor está rodando"""
    print("🔌 Testando conectividade com o servidor...")
    
    try:
        response = requests.get(f"{BASE_URL}/dashboard", timeout=5)
        if response.status_code == 200:
            print("✅ Servidor está respondendo")
            return True
        else:
            print(f"⚠️ Servidor responde mas com status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Servidor não está respondendo: {e}")
        return False

def main():
    """Executa todos os testes"""
    print("=" * 60)
    print("🚀 TESTE DAS APIs DE ATUALIZAÇÃO DE PREÇOS")
    print("=" * 60)
    
    # Testar conectividade primeiro
    if not test_server_connectivity():
        print("\n❌ Não é possível continuar sem conexão com o servidor.")
        print("💡 Certifique-se de que o Flask está rodando na porta 5000")
        return
    
    # Lista de testes
    tests = [
        ("Simulação de mudanças", test_simular_mudancas),
        ("Verificar mudanças de custos", test_verificar_mudancas_custos),
        ("Calcular novos preços", test_calcular_novos_precos),
        ("Atualizar preços", test_atualizar_precos)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*40}")
        success = test_func()
        results.append((test_name, success))
    
    # Resumo dos resultados
    print(f"\n{'='*60}")
    print("📊 RESUMO DOS TESTES:")
    print(f"{'='*60}")
    
    passed = 0
    for test_name, success in results:
        status = "✅ PASSOU" if success else "❌ FALHOU"
        print(f"{test_name}: {status}")
        if success:
            passed += 1
    
    print(f"\n🎯 Resultado: {passed}/{len(results)} testes passaram")
    
    if passed == len(results):
        print("🎉 Todos os testes passaram! Sistema pronto para uso.")
    else:
        print("⚠️ Alguns testes falharam. Verifique os logs acima.")

if __name__ == "__main__":
    main()
