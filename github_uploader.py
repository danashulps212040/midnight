#!/usr/bin/env python3
"""
GitHub Uploader - App para upload automático de arquivos para repositório GitHub
Desenvolvido para o projeto Midnight PDV
"""

import os
import sys
import json
import subprocess
import shutil
from pathlib import Path
from datetime import datetime
import requests
import base64

class GitHubUploader:
    def __init__(self):
        self.project_dir = Path(__file__).parent
        self.config_file = self.project_dir / "github_config.json"
        self.gitignore_file = self.project_dir / ".gitignore"
        self.config = {}
        
    def load_config(self):
        """Carrega configuração do GitHub"""
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            print("✅ Configuração carregada do github_config.json")
        else:
            print("⚠️ Arquivo de configuração não encontrado. Criando novo...")
            self.setup_config()
    
    def setup_config(self):
        """Configura credenciais e repositório do GitHub"""
        print("\n🔧 CONFIGURAÇÃO DO GITHUB")
        print("=" * 50)
        
        # Solicitar dados
        username = input("👤 GitHub Username: ").strip()
        repo_name = input("📁 Nome do Repositório: ").strip()
        token = input("🔐 GitHub Token (Personal Access Token): ").strip()
        branch = input("🌿 Branch (padrão: main): ").strip() or "main"
        
        self.config = {
            "github_username": username,
            "repository_name": repo_name,
            "github_token": token,
            "branch": branch,
            "api_url": f"https://api.github.com/repos/{username}/{repo_name}",
            "last_upload": None
        }
        
        # Salvar configuração
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=4, ensure_ascii=False)
        
        print(f"✅ Configuração salva em {self.config_file}")
        
        # Criar .gitignore se não existir
        self.create_gitignore()
    
    def create_gitignore(self):
        """Cria arquivo .gitignore com exclusões padrão"""
        gitignore_content = """# GitHub Uploader
github_config.json
github_uploader.log

# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.env

# Database
*.db
*.sqlite
*.sqlite3

# Logs
*.log
nohup.out

# OS
.DS_Store
Thumbs.db

# IDE
.vscode/
.idea/
*.swp
*.swo

# Temporary files
*.tmp
*.temp
*~

# Large files
*.mp4
*.avi
*.mov
*.mkv
"""
        
        if not self.gitignore_file.exists():
            with open(self.gitignore_file, 'w', encoding='utf-8') as f:
                f.write(gitignore_content)
            print(f"✅ Criado {self.gitignore_file}")
    
    def get_files_to_upload(self):
        """Obtém lista de arquivos para upload respeitando .gitignore"""
        files_to_upload = []
        gitignore_patterns = self.load_gitignore_patterns()
        
        for root, dirs, files in os.walk(self.project_dir):
            # Filtrar diretórios
            dirs[:] = [d for d in dirs if not self.should_ignore(d, gitignore_patterns)]
            
            for file in files:
                file_path = Path(root) / file
                relative_path = file_path.relative_to(self.project_dir)
                
                # Verificar se deve ignorar
                if not self.should_ignore(str(relative_path), gitignore_patterns):
                    files_to_upload.append(relative_path)
        
        return files_to_upload
    
    def load_gitignore_patterns(self):
        """Carrega padrões do .gitignore"""
        patterns = [
            # Padrões padrão
            '__pycache__',
            '*.pyc',
            '.git',
            'github_config.json',
            'github_uploader.log'
        ]
        
        if self.gitignore_file.exists():
            with open(self.gitignore_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        patterns.append(line)
        
        return patterns
    
    def should_ignore(self, path, patterns):
        """Verifica se arquivo deve ser ignorado"""
        for pattern in patterns:
            if pattern in path or path.endswith(pattern.replace('*', '')):
                return True
        return False
    
    def upload_file_to_github(self, file_path):
        """Faz upload de um arquivo para o GitHub"""
        try:
            # Ler conteúdo do arquivo
            full_path = self.project_dir / file_path
            
            if full_path.stat().st_size > 25 * 1024 * 1024:  # 25MB limit
                print(f"⚠️ Arquivo muito grande (>25MB): {file_path}")
                return False
            
            with open(full_path, 'rb') as f:
                content = f.read()
            
            # Codificar em base64
            content_encoded = base64.b64encode(content).decode('utf-8')
            
            # Preparar dados para API
            url = f"{self.config['api_url']}/contents/{file_path}"
            
            headers = {
                'Authorization': f"token {self.config['github_token']}",
                'Accept': 'application/vnd.github.v3+json',
                'Content-Type': 'application/json'
            }
            
            # Verificar se arquivo já existe
            response = requests.get(url, headers=headers)
            sha = None
            if response.status_code == 200:
                sha = response.json().get('sha')
            
            # Dados do commit
            data = {
                'message': f'Upload: {file_path} - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
                'content': content_encoded,
                'branch': self.config['branch']
            }
            
            if sha:
                data['sha'] = sha
            
            # Fazer upload
            response = requests.put(url, headers=headers, json=data)
            
            if response.status_code in [200, 201]:
                print(f"✅ Upload: {file_path}")
                return True
            else:
                print(f"❌ Erro no upload de {file_path}: {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao processar {file_path}: {str(e)}")
            return False
    
    def upload_all_files(self):
        """Faz upload de todos os arquivos"""
        files = self.get_files_to_upload()
        
        print(f"\n📁 ARQUIVOS ENCONTRADOS: {len(files)}")
        print("=" * 50)
        
        # Mostrar prévia
        for i, file in enumerate(files[:10]):
            print(f"   {i+1:3d}. {file}")
        
        if len(files) > 10:
            print(f"   ... e mais {len(files) - 10} arquivos")
        
        # Confirmar
        print("\n🚀 INICIAR UPLOAD?")
        confirm = input("Digite 'sim' para continuar: ").lower()
        
        if confirm != 'sim':
            print("❌ Upload cancelado")
            return
        
        # Upload
        print(f"\n📤 UPLOADING PARA: {self.config['github_username']}/{self.config['repository_name']}")
        print("=" * 70)
        
        success_count = 0
        error_count = 0
        
        for i, file in enumerate(files):
            print(f"[{i+1:3d}/{len(files)}] ", end="")
            
            if self.upload_file_to_github(file):
                success_count += 1
            else:
                error_count += 1
        
        # Resultado final
        print("\n" + "=" * 70)
        print(f"✅ UPLOADS CONCLUÍDOS: {success_count}")
        print(f"❌ UPLOADS COM ERRO: {error_count}")
        print(f"📊 TOTAL: {len(files)} arquivos")
        
        # Atualizar configuração
        self.config['last_upload'] = datetime.now().isoformat()
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=4, ensure_ascii=False)
    
    def show_status(self):
        """Mostra status do repositório"""
        print("\n📊 STATUS DO REPOSITÓRIO")
        print("=" * 50)
        print(f"👤 Username: {self.config.get('github_username', 'N/A')}")
        print(f"📁 Repositório: {self.config.get('repository_name', 'N/A')}")
        print(f"🌿 Branch: {self.config.get('branch', 'N/A')}")
        print(f"🕒 Último upload: {self.config.get('last_upload', 'Nunca')}")
        
        files = self.get_files_to_upload()
        print(f"📄 Arquivos para upload: {len(files)}")
    
    def run(self):
        """Executa o aplicativo"""
        print("🚀 GITHUB UPLOADER - MIDNIGHT PDV")
        print("=" * 50)
        
        # Carregar configuração
        self.load_config()
        
        while True:
            print("\n🎯 OPÇÕES:")
            print("1. 📤 Upload de todos os arquivos")
            print("2. 📊 Ver status do repositório")
            print("3. 🔧 Reconfigurar GitHub")
            print("4. 📄 Ver arquivos para upload")
            print("5. ❌ Sair")
            
            choice = input("\nEscolha uma opção: ").strip()
            
            if choice == '1':
                self.upload_all_files()
            elif choice == '2':
                self.show_status()
            elif choice == '3':
                self.setup_config()
            elif choice == '4':
                files = self.get_files_to_upload()
                print(f"\n📄 ARQUIVOS PARA UPLOAD ({len(files)}):")
                for i, file in enumerate(files):
                    print(f"   {i+1:3d}. {file}")
            elif choice == '5':
                print("👋 Até logo!")
                break
            else:
                print("❌ Opção inválida!")

def main():
    """Função principal"""
    try:
        uploader = GitHubUploader()
        uploader.run()
    except KeyboardInterrupt:
        print("\n\n👋 Aplicativo interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ ERRO CRÍTICO: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()