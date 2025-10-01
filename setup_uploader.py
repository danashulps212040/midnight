#!/usr/bin/env python3
"""
Instalador de dependências para GitHub Uploader
"""

import subprocess
import sys
import os

def install_requirements():
    """Instala as dependências necessárias"""
    
    requirements = [
        'requests>=2.28.0',
        'pathlib',  # Geralmente já incluído no Python 3.4+
    ]
    
    print("🔧 INSTALANDO DEPENDÊNCIAS...")
    print("=" * 40)
    
    for package in requirements:
        try:
            print(f"📦 Instalando {package}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print(f"✅ {package} instalado com sucesso")
        except subprocess.CalledProcessError as e:
            print(f"❌ Erro ao instalar {package}: {e}")
            return False
    
    return True

def create_requirements_txt():
    """Cria arquivo requirements.txt"""
    requirements_content = """# Dependências do GitHub Uploader
requests>=2.28.0
pathlib2>=2.3.0; python_version < '3.4'

# Dependências do Flask PDV (caso necessário na nuvem)
Flask>=2.3.0
Flask-CORS>=4.0.0
sqlite3
"""
    
    with open('requirements.txt', 'w', encoding='utf-8') as f:
        f.write(requirements_content)
    
    print("✅ Arquivo requirements.txt criado")

def main():
    print("🚀 SETUP DO GITHUB UPLOADER")
    print("=" * 40)
    
    # Verificar Python
    if sys.version_info < (3, 6):
        print("❌ Python 3.6+ é necessário")
        sys.exit(1)
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    
    # Instalar dependências
    if install_requirements():
        print("\n✅ SETUP CONCLUÍDO!")
        print("\n🎯 PRÓXIMOS PASSOS:")
        print("📱 Interface Gráfica (Recomendado):")
        print("   python github_uploader_gui.py")
        print("\n💻 Interface de Linha de Comando:")
        print("   python github_uploader.py")
        print("\n🔧 Configure suas credenciais do GitHub e faça o upload!")
        
        # Criar requirements.txt
        create_requirements_txt()
        
    else:
        print("\n❌ Erro no setup. Verifique as mensagens acima.")

if __name__ == "__main__":
    main()