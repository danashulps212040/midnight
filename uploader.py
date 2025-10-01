#!/usr/bin/env python3
"""
GitHub Uploader Launcher
Escolha entre interface gráfica ou linha de comando
"""

import subprocess
import sys
import os

def main():
    print("🚀 GITHUB UPLOADER - MIDNIGHT PDV")
    print("=" * 50)
    print("\nEscolha a interface:")
    print("1. 📱 Interface Gráfica (GUI) - Recomendado")
    print("2. 💻 Linha de Comando (CLI)")
    print("3. ❌ Sair")
    
    while True:
        choice = input("\nDigite sua escolha (1-3): ").strip()
        
        if choice == '1':
            print("\n🚀 Iniciando interface gráfica...")
            try:
                subprocess.run([sys.executable, "github_uploader_gui.py"])
            except FileNotFoundError:
                print("❌ Arquivo github_uploader_gui.py não encontrado!")
                print("Execute o setup primeiro: python setup_uploader.py")
            except Exception as e:
                print(f"❌ Erro ao iniciar GUI: {e}")
            break
            
        elif choice == '2':
            print("\n💻 Iniciando linha de comando...")
            try:
                subprocess.run([sys.executable, "github_uploader.py"])
            except FileNotFoundError:
                print("❌ Arquivo github_uploader.py não encontrado!")
                print("Execute o setup primeiro: python setup_uploader.py")
            except Exception as e:
                print(f"❌ Erro ao iniciar CLI: {e}")
            break
            
        elif choice == '3':
            print("👋 Até logo!")
            break
            
        else:
            print("❌ Opção inválida! Digite 1, 2 ou 3.")

if __name__ == "__main__":
    main()