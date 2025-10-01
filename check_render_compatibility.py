#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Verificação de Compatibilidade para Render
Verifica se todos os arquivos necessários estão prontos para deploy
"""

import os
import sys
import json
from pathlib import Path

def check_file_exists(filepath, required=True):
    """Verifica se um arquivo existe"""
    exists = os.path.exists(filepath)
    status = "✅" if exists else ("❌" if required else "⚠️")
    req_text = "(obrigatório)" if required else "(opcional)"
    print(f"{status} {filepath} {req_text}")
    return exists

def check_requirements_txt():
    """Verifica se requirements.txt tem as dependências necessárias"""
    print("\n🔍 Verificando requirements.txt...")
    
    if not os.path.exists("requirements.txt"):
        print("❌ requirements.txt não encontrado!")
        return False
    
    with open("requirements.txt", "r") as f:
        content = f.read()
    
    required_deps = [
        "Flask",
        "psycopg2-binary", 
        "gunicorn",
        "Werkzeug"
    ]
    
    missing_deps = []
    for dep in required_deps:
        if dep.lower() not in content.lower():
            missing_deps.append(dep)
    
    if missing_deps:
        print(f"❌ Dependências faltando: {', '.join(missing_deps)}")
        return False
    else:
        print("✅ Todas as dependências necessárias estão presentes")
        return True

def check_database_files():
    """Verifica arquivos relacionados ao banco de dados"""
    print("\n🔍 Verificando arquivos do banco de dados...")
    
    has_mysql = check_file_exists("database.py", required=False)
    has_postgres = check_file_exists("database_render.py", required=True)
    has_migration = check_file_exists("migration_postgresql.sql", required=True)
    
    if has_mysql:
        print("ℹ️  database.py (MySQL) detectado - será usado em desenvolvimento")
    
    return has_postgres and has_migration

def check_flask_app():
    """Verifica se o arquivo Flask principal existe e está configurado"""
    print("\n🔍 Verificando aplicação Flask...")
    
    if not check_file_exists("flask_gui.py", required=True):
        return False
    
    # Verificar se tem import condicional do database
    with open("flask_gui.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    if "database_render" in content:
        print("✅ Import condicional do database configurado")
        return True
    else:
        print("⚠️  Import condicional não detectado - pode causar problemas")
        return False

def check_environment_config():
    """Verifica configuração de variáveis de ambiente"""
    print("\n🔍 Verificando configuração de ambiente...")
    
    has_env_example = check_file_exists(".env.example", required=False)
    has_gitignore = check_file_exists(".gitignore", required=False)
    
    if has_env_example:
        print("✅ Arquivo de exemplo de ambiente encontrado")
    
    return True

def check_render_compatibility():
    """Verifica compatibilidade específica do Render"""
    print("\n🔍 Verificando compatibilidade com Render...")
    
    issues = []
    
    # Verificar se não há dependências incompatíveis
    if os.path.exists("requirements.txt"):
        with open("requirements.txt", "r") as f:
            content = f.read().lower()
            
        # Dependências problemáticas no Render
        problematic = ["mysql-connector", "pymysql", "sqlite3"]
        for dep in problematic:
            if dep in content:
                issues.append(f"Dependência problemática: {dep}")
    
    if issues:
        for issue in issues:
            print(f"⚠️  {issue}")
        return False
    else:
        print("✅ Nenhum problema de compatibilidade detectado")
        return True

def generate_deployment_checklist():
    """Gera checklist para deploy no Render"""
    checklist = """
🚀 CHECKLIST PARA DEPLOY NO RENDER

📋 PRÉ-DEPLOY:
□ Criar conta no Render (render.com)
□ Criar repositório GitHub com os arquivos
□ Criar database PostgreSQL no Render
□ Executar migration_postgresql.sql no banco

📋 CONFIGURAÇÃO DO WEB SERVICE:
□ Environment: Python 3
□ Build Command: pip install -r requirements.txt
□ Start Command: gunicorn --bind 0.0.0.0:$PORT flask_gui:app

📋 VARIÁVEIS DE AMBIENTE:
□ DATABASE_URL (do PostgreSQL dashboard)
□ FLASK_ENV=production
□ SECRET_KEY (gere uma chave segura)
□ RENDER=true

📋 PÓS-DEPLOY:
□ Testar login (admin@midnight.com / admin123)
□ Verificar logs para erros
□ Testar PWA no iPad
□ Configurar domínio personalizado (opcional)

💡 COMANDOS ÚTEIS:
- Ver logs: Render Dashboard → Logs
- Restart: Settings → Manual Deploy
- Database: Dashboard → PostgreSQL → Connections
"""
    
    print(checklist)
    
    # Salvar checklist em arquivo
    with open("DEPLOY_CHECKLIST.md", "w", encoding="utf-8") as f:
        f.write(checklist)
    print("✅ Checklist salvo em DEPLOY_CHECKLIST.md")

def main():
    """Função principal de verificação"""
    print("🔍 VERIFICAÇÃO DE COMPATIBILIDADE PARA RENDER")
    print("=" * 50)
    
    checks = []
    
    # Verificações principais
    checks.append(("Arquivos necessários", check_database_files()))
    checks.append(("Requirements.txt", check_requirements_txt()))
    checks.append(("Aplicação Flask", check_flask_app()))
    checks.append(("Configuração ambiente", check_environment_config()))
    checks.append(("Compatibilidade Render", check_render_compatibility()))
    
    # Verificar arquivos adicionais
    print("\n🔍 Verificando arquivos adicionais...")
    check_file_exists("GUIA_MIGRACAO_RENDER.md", required=False)
    check_file_exists("github_uploader_gui.py", required=False)
    
    # Resumo final
    print("\n" + "=" * 50)
    print("📊 RESUMO DA VERIFICAÇÃO")
    
    passed = sum(1 for _, result in checks if result)
    total = len(checks)
    
    for name, result in checks:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{status} - {name}")
    
    print(f"\n🎯 RESULTADO: {passed}/{total} verificações passaram")
    
    if passed == total:
        print("✅ PRONTO PARA DEPLOY! 🚀")
        print("\n📋 Próximos passos:")
        print("1. Execute o GitHub Uploader para enviar os arquivos")
        print("2. Siga o GUIA_MIGRACAO_RENDER.md")
        print("3. Configure o PostgreSQL no Render")
        print("4. Crie o Web Service")
        
        generate_deployment_checklist()
    else:
        print("❌ CORRIJA OS PROBLEMAS ANTES DO DEPLOY")
        print("\n🔧 Ações necessárias:")
        for name, result in checks:
            if not result:
                print(f"- Corrigir: {name}")

if __name__ == "__main__":
    main()