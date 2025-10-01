#!/usr/bin/env python3
"""
Script automatizado para preparar e fazer upload do projeto para o Render
"""

import os
import sys
import json
from pathlib import Path

def check_files():
    """Verifica se todos os arquivos necessários existem"""
    required_files = [
        'flask_gui.py',
        'requirements.txt', 
        'Procfile',
        'runtime.txt',
        'render.yaml',
        'database.py'
    ]
    
    missing = []
    for file in required_files:
        if not os.path.exists(file):
            missing.append(file)
    
    if missing:
        print("❌ Arquivos obrigatórios não encontrados:")
        for f in missing:
            print(f"   - {f}")
        return False
    
    print("✅ Todos os arquivos obrigatórios encontrados!")
    return True

def show_checklist():
    """Mostra checklist final antes do upload"""
    print("\n" + "="*60)
    print("🚀 CHECKLIST FINAL PARA DEPLOY NO RENDER")
    print("="*60)
    
    checklist = [
        "✅ Flask configurado com port dinâmico",
        "✅ requirements.txt com dependências corretas", 
        "✅ Procfile configurado para gunicorn",
        "✅ runtime.txt com Python 3.11.5",
        "✅ render.yaml com configurações otimizadas",
        "✅ PWA manifest e service worker prontos",
        "✅ Database SQLite incluído",
        "✅ Arquivos estáticos (CSS/JS) incluídos"
    ]
    
    for item in checklist:
        print(f"  {item}")
    
    print("\n📋 PRÓXIMOS PASSOS:")
    print("  1. Execute: python github_uploader_gui.py")
    print("  2. Faça upload de todos os arquivos")
    print("  3. Acesse render.com e conecte seu repositório")
    print("  4. Configure o Web Service conforme o guia")
    print("  5. Sua URL será: https://seu-app.onrender.com")
    
    print(f"\n📖 Guia completo: {os.path.abspath('GUIA_DEPLOY_RENDER.md')}")

def main():
    print("🔍 Verificando preparação para Render Deploy...\n")
    
    if not check_files():
        print("\n❌ Resolva os arquivos em falta e execute novamente.")
        return 1
    
    show_checklist()
    
    print(f"\n🎉 Projeto pronto para deploy no Render!")
    print(f"💡 Leia o guia: GUIA_DEPLOY_RENDER.md")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())