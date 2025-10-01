#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de verificação pós-deploy
Testa todas as funcionalidades críticas da aplicação
"""

import requests
import json
import sys
from datetime import datetime

def test_health_check(base_url):
    """Testa se a aplicação está respondendo"""
    print("🏥 Testando health check...")
    
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        if response.status_code == 200:
            print("✅ Aplicação está respondendo")
            return True
        else:
            print(f"❌ Aplicação retornou status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao acessar aplicação: {e}")
        return False

def test_static_files(base_url):
    """Testa se arquivos estáticos estão sendo servidos"""
    print("📁 Testando arquivos estáticos...")
    
    static_files = [
        "/static/manifest.json",
        "/static/sw.js",
        "/static/style.css"
    ]
    
    success = True
    for file_path in static_files:
        try:
            response = requests.get(f"{base_url}{file_path}", timeout=10)
            if response.status_code == 200:
                print(f"✅ {file_path}")
            else:
                print(f"❌ {file_path} - Status {response.status_code}")
                success = False
        except Exception as e:
            print(f"❌ {file_path} - Erro: {e}")
            success = False
    
    return success

def test_pwa_manifest(base_url):
    """Testa se o manifest PWA está válido"""
    print("📱 Testando PWA manifest...")
    
    try:
        response = requests.get(f"{base_url}/static/manifest.json", timeout=10)
        if response.status_code == 200:
            manifest = response.json()
            required_fields = ["name", "short_name", "start_url", "display", "theme_color"]
            
            missing_fields = [field for field in required_fields if field not in manifest]
            if missing_fields:
                print(f"❌ Campos obrigatórios ausentes no manifest: {missing_fields}")
                return False
            else:
                print("✅ PWA manifest válido")
                return True
        else:
            print(f"❌ Manifest não acessível - Status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao verificar manifest: {e}")
        return False

def test_api_endpoints(base_url):
    """Testa endpoints críticos da API"""
    print("🔌 Testando endpoints da API...")
    
    # Endpoints que devem responder (mesmo que com erro de autenticação)
    endpoints = [
        "/api/produtos",
        "/api/usuarios", 
        "/api/clientes",
        "/api/estoque"
    ]
    
    success = True
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            # Aceitar 200 (OK) ou 401/403 (não autenticado) como válido
            if response.status_code in [200, 401, 403]:
                print(f"✅ {endpoint}")
            else:
                print(f"❌ {endpoint} - Status {response.status_code}")
                success = False
        except Exception as e:
            print(f"❌ {endpoint} - Erro: {e}")
            success = False
    
    return success

def test_database_connection(base_url):
    """Testa conexão com banco de dados via endpoint de health"""
    print("🗄️ Testando conexão com banco de dados...")
    
    try:
        # Tentar endpoint que testa conexão com banco
        response = requests.get(f"{base_url}/health/db", timeout=15)
        
        if response.status_code == 200:
            print("✅ Conexão com banco de dados OK")
            return True
        else:
            print(f"❌ Problema na conexão com banco - Status {response.status_code}")
            if response.text:
                print(f"   Detalhes: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar conexão com banco: {e}")
        return False

def test_performance(base_url):
    """Testa performance básica da aplicação"""
    print("⚡ Testando performance...")
    
    try:
        start_time = datetime.now()
        response = requests.get(base_url, timeout=30)
        end_time = datetime.now()
        
        response_time = (end_time - start_time).total_seconds()
        
        if response_time < 3.0:
            print(f"✅ Tempo de resposta OK: {response_time:.2f}s")
            return True
        elif response_time < 10.0:
            print(f"⚠️ Tempo de resposta lento: {response_time:.2f}s")
            return True
        else:
            print(f"❌ Tempo de resposta muito lento: {response_time:.2f}s")
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste de performance: {e}")
        return False

def generate_report(results, base_url):
    """Gera relatório final dos testes"""
    print("\n" + "="*50)
    print("📊 RELATÓRIO FINAL DE VERIFICAÇÃO")
    print("="*50)
    print(f"🌐 URL testada: {base_url}")
    print(f"🕐 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{test_name}: {status}")
    
    print(f"\n📈 Resultado Geral: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 TODOS OS TESTES PASSARAM! Aplicação está funcionando corretamente.")
        return True
    elif passed >= total * 0.8:  # 80% dos testes passaram
        print("⚠️ A maioria dos testes passou, mas há alguns problemas.")
        return True
    else:
        print("❌ MUITOS TESTES FALHARAM! Verificar problemas na aplicação.")
        return False

def main():
    """Função principal"""
    if len(sys.argv) != 2:
        print("Uso: python test_deploy.py <URL_DA_APLICACAO>")
        print("Exemplo: python test_deploy.py https://midnight-pdv-xxxx.onrender.com")
        sys.exit(1)
    
    base_url = sys.argv[1].rstrip('/')
    
    print("🔍 VERIFICAÇÃO PÓS-DEPLOY")
    print("="*50)
    print(f"🌐 Testando aplicação: {base_url}")
    print()
    
    # Executar testes
    results = {
        "Health Check": test_health_check(base_url),
        "Arquivos Estáticos": test_static_files(base_url), 
        "PWA Manifest": test_pwa_manifest(base_url),
        "Endpoints API": test_api_endpoints(base_url),
        "Conexão Banco": test_database_connection(base_url),
        "Performance": test_performance(base_url)
    }
    
    # Gerar relatório
    success = generate_report(results, base_url)
    
    # Exit code baseado no resultado
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()