#!/usr/bin/env python3
"""
GitHub Uploader GUI - Interface gráfica para upload automático para GitHub
Desenvolvido para o projeto Midnight PDV
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import os
import sys
import json
import threading
import subprocess
from pathlib import Path
from datetime import datetime
import requests
import base64

class MidnightTheme:
    """Tema visual da marca Midnight"""
    
    # Cores da marca
    PRIMARY = "#2C0B5A"      # Roxo escuro principal
    SECONDARY = "#9B64E3"    # Roxo claro
    ACCENT = "#7B4AC3"       # Roxo médio
    
    # Interface
    BG_DARK = "#1A0533"      # Fundo escuro
    BG_LIGHT = "#2D1B3D"     # Fundo claro
    TEXT_PRIMARY = "#FFFFFF"  # Texto principal
    TEXT_SECONDARY = "#B8A9C9" # Texto secundário
    
    # Status
    SUCCESS = "#4CAF50"      # Verde sucesso
    ERROR = "#F44336"        # Vermelho erro
    WARNING = "#FF9800"      # Laranja aviso
    INFO = "#2196F3"         # Azul info

class GitHubUploaderGUI:
    def __init__(self, root):
        self.root = root
        self.theme = MidnightTheme()
        self.project_dir = Path(__file__).parent
        self.config_file = self.project_dir / "github_config.json"
        self.config = {}
        
        self.setup_window()
        self.create_widgets()
        self.load_config()
        
    def setup_window(self):
        """Configura janela principal"""
        self.root.title("🚀 GitHub Uploader - Midnight PDV")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        
        # Tema escuro
        self.root.configure(bg=self.theme.BG_DARK)
        
        # Ícone (se existir)
        try:
            icon_path = self.project_dir / "static" / "favicon.ico"
            if icon_path.exists():
                self.root.iconbitmap(str(icon_path))
        except:
            pass
    
    def create_widgets(self):
        """Cria interface gráfica"""
        # Frame principal
        main_frame = tk.Frame(self.root, bg=self.theme.BG_DARK)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header
        self.create_header(main_frame)
        
        # Notebook (abas)
        self.create_notebook(main_frame)
        
        # Status bar
        self.create_status_bar(main_frame)
    
    def create_header(self, parent):
        """Cria cabeçalho"""
        header_frame = tk.Frame(parent, bg=self.theme.BG_DARK)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Logo/Título
        title_frame = tk.Frame(header_frame, bg=self.theme.PRIMARY, relief=tk.RAISED, bd=2)
        title_frame.pack(fill=tk.X)
        
        title_label = tk.Label(
            title_frame, 
            text="🚀 GITHUB UPLOADER", 
            font=("Arial", 18, "bold"),
            bg=self.theme.PRIMARY,
            fg=self.theme.TEXT_PRIMARY
        )
        title_label.pack(pady=10)
        
        subtitle_label = tk.Label(
            title_frame, 
            text="Midnight PDV - Upload para a Nuvem", 
            font=("Arial", 10),
            bg=self.theme.PRIMARY,
            fg=self.theme.TEXT_SECONDARY
        )
        subtitle_label.pack(pady=(0, 10))
    
    def create_notebook(self, parent):
        """Cria abas principais"""
        # Configurar estilo do notebook
        style = ttk.Style()
        style.theme_use('clam')
        
        # Customizar cores
        style.configure('TNotebook', background=self.theme.BG_DARK)
        style.configure('TNotebook.Tab', 
                       background=self.theme.BG_LIGHT,
                       foreground=self.theme.TEXT_SECONDARY,
                       padding=[20, 10])
        style.map('TNotebook.Tab', 
                 background=[('selected', self.theme.SECONDARY)],
                 foreground=[('selected', self.theme.TEXT_PRIMARY)])
        
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Abas
        self.create_config_tab()
        self.create_upload_tab()
        self.create_status_tab()
        self.create_files_tab()
        self.create_logs_tab()
    
    def create_config_tab(self):
        """Aba de configuração"""
        config_frame = tk.Frame(self.notebook, bg=self.theme.BG_DARK)
        self.notebook.add(config_frame, text="🔧 Configuração")
        
        # Título
        title = tk.Label(
            config_frame, 
            text="Configurações do GitHub",
            font=("Arial", 14, "bold"),
            bg=self.theme.BG_DARK,
            fg=self.theme.TEXT_PRIMARY
        )
        title.pack(pady=(20, 30))
        
        # Frame de configuração
        form_frame = tk.Frame(config_frame, bg=self.theme.BG_LIGHT, relief=tk.RAISED, bd=2)
        form_frame.pack(fill=tk.X, padx=50, pady=20)
        
        # Campos de configuração
        self.config_vars = {}
        
        fields = [
            ("👤 GitHub Username:", "github_username"),
            ("📁 Nome do Repositório:", "repository_name"),
            ("🔐 GitHub Token:", "github_token"),
            ("🌿 Branch (padrão: main):", "branch")
        ]
        
        for i, (label_text, var_name) in enumerate(fields):
            # Label
            label = tk.Label(
                form_frame,
                text=label_text,
                font=("Arial", 10, "bold"),
                bg=self.theme.BG_LIGHT,
                fg=self.theme.TEXT_PRIMARY
            )
            label.grid(row=i, column=0, sticky=tk.W, padx=20, pady=10)
            
            # Entry
            var = tk.StringVar()
            self.config_vars[var_name] = var
            
            entry = tk.Entry(
                form_frame,
                textvariable=var,
                font=("Arial", 10),
                bg=self.theme.BG_DARK,
                fg=self.theme.TEXT_PRIMARY,
                insertbackground=self.theme.TEXT_PRIMARY,
                width=40,
                show="*" if "token" in var_name else None
            )
            entry.grid(row=i, column=1, padx=20, pady=10, sticky=tk.EW)
            
            # Placeholder para branch
            if var_name == "branch":
                var.set("main")  # Valor padrão
        
        form_frame.columnconfigure(1, weight=1)
        
        # Explicação sobre branch
        info_frame = tk.Frame(form_frame, bg=self.theme.BG_DARK, relief=tk.SUNKEN, bd=1)
        info_frame.grid(row=len(fields), column=0, columnspan=2, padx=20, pady=10, sticky=tk.EW)
        
        info_text = """ℹ️ SOBRE O BRANCH:
• Use "main" - versão principal do repositório (padrão moderno)
• Use "master" - apenas se seu repositório usar este nome antigo
• Para seu caso, deixe "main" que já está preenchido"""
        
        info_label = tk.Label(
            info_frame,
            text=info_text,
            font=("Arial", 9),
            bg=self.theme.BG_DARK,
            fg=self.theme.TEXT_SECONDARY,
            justify=tk.LEFT
        )
        info_label.pack(padx=10, pady=8)
        
        # Botões
        btn_frame = tk.Frame(form_frame, bg=self.theme.BG_LIGHT)
        btn_frame.grid(row=len(fields)+1, column=0, columnspan=2, pady=20)
        
        save_btn = tk.Button(
            btn_frame,
            text="💾 Salvar Configuração",
            command=self.save_config,
            bg=self.theme.SUCCESS,
            fg="white",
            font=("Arial", 10, "bold"),
            padx=20,
            pady=5
        )
        save_btn.pack(side=tk.LEFT, padx=10)
        
        test_btn = tk.Button(
            btn_frame,
            text="🔍 Testar Conexão",
            command=self.test_connection,
            bg=self.theme.INFO,
            fg="white",
            font=("Arial", 10, "bold"),
            padx=20,
            pady=5
        )
        test_btn.pack(side=tk.LEFT, padx=10)
    
    def create_upload_tab(self):
        """Aba de upload"""
        upload_frame = tk.Frame(self.notebook, bg=self.theme.BG_DARK)
        self.notebook.add(upload_frame, text="📤 Upload")
        
        # Título
        title = tk.Label(
            upload_frame,
            text="Upload de Arquivos",
            font=("Arial", 14, "bold"),
            bg=self.theme.BG_DARK,
            fg=self.theme.TEXT_PRIMARY
        )
        title.pack(pady=(20, 20))
        
        # Frame de status
        status_frame = tk.Frame(upload_frame, bg=self.theme.BG_LIGHT, relief=tk.RAISED, bd=2)
        status_frame.pack(fill=tk.X, padx=50, pady=20)
        
        # Info do repositório
        self.repo_info_label = tk.Label(
            status_frame,
            text="📁 Repositório: Não configurado",
            font=("Arial", 10),
            bg=self.theme.BG_LIGHT,
            fg=self.theme.TEXT_SECONDARY
        )
        self.repo_info_label.pack(pady=10)
        
        self.files_count_label = tk.Label(
            status_frame,
            text="📄 Arquivos para upload: 0",
            font=("Arial", 10),
            bg=self.theme.BG_LIGHT,
            fg=self.theme.TEXT_SECONDARY
        )
        self.files_count_label.pack(pady=(0, 10))
        
        # Botões de upload
        btn_frame = tk.Frame(upload_frame, bg=self.theme.BG_DARK)
        btn_frame.pack(pady=30)
        
        self.upload_btn = tk.Button(
            btn_frame,
            text="🚀 INICIAR UPLOAD",
            command=self.start_upload,
            bg=self.theme.SECONDARY,
            fg="white",
            font=("Arial", 12, "bold"),
            padx=30,
            pady=10,
            state=tk.DISABLED
        )
        self.upload_btn.pack(pady=10)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            upload_frame,
            variable=self.progress_var,
            maximum=100,
            length=400
        )
        self.progress_bar.pack(pady=20)
        
        self.progress_label = tk.Label(
            upload_frame,
            text="",
            bg=self.theme.BG_DARK,
            fg=self.theme.TEXT_SECONDARY
        )
        self.progress_label.pack()
    
    def create_status_tab(self):
        """Aba de status"""
        status_frame = tk.Frame(self.notebook, bg=self.theme.BG_DARK)
        self.notebook.add(status_frame, text="📊 Status")
        
        # Título
        title = tk.Label(
            status_frame,
            text="Status do Repositório",
            font=("Arial", 14, "bold"),
            bg=self.theme.BG_DARK,
            fg=self.theme.TEXT_PRIMARY
        )
        title.pack(pady=(20, 30))
        
        # Frame de informações
        info_frame = tk.Frame(status_frame, bg=self.theme.BG_LIGHT, relief=tk.RAISED, bd=2)
        info_frame.pack(fill=tk.BOTH, expand=True, padx=50, pady=20)
        
        self.status_text = scrolledtext.ScrolledText(
            info_frame,
            bg=self.theme.BG_DARK,
            fg=self.theme.TEXT_PRIMARY,
            font=("Consolas", 10),
            wrap=tk.WORD,
            height=20
        )
        self.status_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Botão atualizar
        refresh_btn = tk.Button(
            status_frame,
            text="🔄 Atualizar Status",
            command=self.update_status,
            bg=self.theme.INFO,
            fg="white",
            font=("Arial", 10, "bold"),
            padx=20,
            pady=5
        )
        refresh_btn.pack(pady=20)
    
    def create_files_tab(self):
        """Aba de arquivos"""
        files_frame = tk.Frame(self.notebook, bg=self.theme.BG_DARK)
        self.notebook.add(files_frame, text="📄 Arquivos")
        
        # Título
        title = tk.Label(
            files_frame,
            text="Arquivos para Upload",
            font=("Arial", 14, "bold"),
            bg=self.theme.BG_DARK,
            fg=self.theme.TEXT_PRIMARY
        )
        title.pack(pady=(20, 20))
        
        # Frame da lista
        list_frame = tk.Frame(files_frame, bg=self.theme.BG_LIGHT, relief=tk.RAISED, bd=2)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=50, pady=20)
        
        # Listbox com scroll
        listbox_frame = tk.Frame(list_frame, bg=self.theme.BG_LIGHT)
        listbox_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        scrollbar = tk.Scrollbar(listbox_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.files_listbox = tk.Listbox(
            listbox_frame,
            bg=self.theme.BG_DARK,
            fg=self.theme.TEXT_PRIMARY,
            font=("Consolas", 9),
            yscrollcommand=scrollbar.set
        )
        self.files_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.files_listbox.yview)
        
        # Botão atualizar lista
        refresh_files_btn = tk.Button(
            files_frame,
            text="🔄 Atualizar Lista",
            command=self.update_files_list,
            bg=self.theme.INFO,
            fg="white",
            font=("Arial", 10, "bold"),
            padx=20,
            pady=5
        )
        refresh_files_btn.pack(pady=20)
    
    def create_logs_tab(self):
        """Aba de logs"""
        logs_frame = tk.Frame(self.notebook, bg=self.theme.BG_DARK)
        self.notebook.add(logs_frame, text="📝 Logs")
        
        # Título
        title = tk.Label(
            logs_frame,
            text="Logs de Atividade",
            font=("Arial", 14, "bold"),
            bg=self.theme.BG_DARK,
            fg=self.theme.TEXT_PRIMARY
        )
        title.pack(pady=(20, 20))
        
        # Frame de logs
        log_frame = tk.Frame(logs_frame, bg=self.theme.BG_LIGHT, relief=tk.RAISED, bd=2)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=50, pady=20)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            bg=self.theme.BG_DARK,
            fg=self.theme.TEXT_PRIMARY,
            font=("Consolas", 9),
            wrap=tk.WORD
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Botões
        log_btn_frame = tk.Frame(logs_frame, bg=self.theme.BG_DARK)
        log_btn_frame.pack(pady=20)
        
        clear_btn = tk.Button(
            log_btn_frame,
            text="🗑️ Limpar Logs",
            command=self.clear_logs,
            bg=self.theme.WARNING,
            fg="white",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=5
        )
        clear_btn.pack(side=tk.LEFT, padx=10)
        
        save_logs_btn = tk.Button(
            log_btn_frame,
            text="💾 Salvar Logs",
            command=self.save_logs,
            bg=self.theme.SUCCESS,
            fg="white",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=5
        )
        save_logs_btn.pack(side=tk.LEFT, padx=10)
    
    def create_status_bar(self, parent):
        """Cria barra de status"""
        status_frame = tk.Frame(parent, bg=self.theme.PRIMARY, relief=tk.SUNKEN, bd=1)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_label = tk.Label(
            status_frame,
            text="✅ Pronto",
            bg=self.theme.PRIMARY,
            fg=self.theme.TEXT_PRIMARY,
            font=("Arial", 9)
        )
        self.status_label.pack(side=tk.LEFT, padx=10, pady=2)
        
        # Versão
        version_label = tk.Label(
            status_frame,
            text="v1.0.0",
            bg=self.theme.PRIMARY,
            fg=self.theme.TEXT_SECONDARY,
            font=("Arial", 8)
        )
        version_label.pack(side=tk.RIGHT, padx=10, pady=2)
    
    def log(self, message, level="INFO"):
        """Adiciona mensagem aos logs"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Cores por nível
        colors = {
            "INFO": self.theme.TEXT_PRIMARY,
            "SUCCESS": self.theme.SUCCESS,
            "WARNING": self.theme.WARNING,
            "ERROR": self.theme.ERROR
        }
        
        # Ícones por nível
        icons = {
            "INFO": "ℹ️",
            "SUCCESS": "✅",
            "WARNING": "⚠️",
            "ERROR": "❌"
        }
        
        formatted_message = f"[{timestamp}] {icons.get(level, '•')} {message}\n"
        
        # Adicionar ao log
        self.log_text.insert(tk.END, formatted_message)
        self.log_text.see(tk.END)
        
        # Atualizar status bar
        self.status_label.config(text=f"{icons.get(level, '•')} {message}")
        
        self.root.update_idletasks()
    
    def load_config(self):
        """Carrega configuração do arquivo"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                
                # Preencher campos
                for key, var in self.config_vars.items():
                    if key in self.config:
                        var.set(self.config[key])
                
                self.log("Configuração carregada com sucesso", "SUCCESS")
                self.update_ui_state()
                
            except Exception as e:
                self.log(f"Erro ao carregar configuração: {str(e)}", "ERROR")
        else:
            self.log("Nenhuma configuração encontrada", "WARNING")
    
    def save_config(self):
        """Salva configuração"""
        try:
            # Obter valores dos campos
            new_config = {}
            for key, var in self.config_vars.items():
                value = var.get().strip()
                if value:
                    new_config[key] = value
            
            # Validar campos obrigatórios
            required_fields = ["github_username", "repository_name", "github_token"]
            missing_fields = [field for field in required_fields if not new_config.get(field)]
            
            if missing_fields:
                messagebox.showerror("Erro", f"Campos obrigatórios não preenchidos:\n{', '.join(missing_fields)}")
                return
            
            # Adicionar valores padrão
            if not new_config.get("branch"):
                new_config["branch"] = "main"
            
            new_config["api_url"] = f"https://api.github.com/repos/{new_config['github_username']}/{new_config['repository_name']}"
            new_config["last_upload"] = self.config.get("last_upload")
            
            # Salvar
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(new_config, f, indent=4, ensure_ascii=False)
            
            self.config = new_config
            self.log("Configuração salva com sucesso!", "SUCCESS")
            self.update_ui_state()
            
            messagebox.showinfo("Sucesso", "Configuração salva com sucesso!")
            
        except Exception as e:
            self.log(f"Erro ao salvar configuração: {str(e)}", "ERROR")
            messagebox.showerror("Erro", f"Erro ao salvar configuração:\n{str(e)}")
    
    def test_connection(self):
        """Testa conexão com GitHub"""
        if not self.config.get("github_token"):
            messagebox.showerror("Erro", "Configure o token do GitHub primeiro!")
            return
        
        def test_thread():
            try:
                self.log("Testando conexão com GitHub...", "INFO")
                
                headers = {
                    'Authorization': f"token {self.config['github_token']}",
                    'Accept': 'application/vnd.github.v3+json'
                }
                
                # Testar API do usuário
                response = requests.get("https://api.github.com/user", headers=headers, timeout=10)
                
                if response.status_code == 200:
                    user_data = response.json()
                    self.log(f"✅ Conectado como: {user_data.get('login', 'N/A')}", "SUCCESS")
                    
                    # Testar repositório se configurado
                    if self.config.get("api_url"):
                        repo_response = requests.get(self.config["api_url"], headers=headers, timeout=10)
                        if repo_response.status_code == 200:
                            self.log("✅ Repositório acessível", "SUCCESS")
                            messagebox.showinfo("Sucesso", "Conexão estabelecida com sucesso!\nRepositório acessível.")
                        else:
                            self.log("⚠️ Repositório não encontrado ou sem acesso", "WARNING")
                            messagebox.showwarning("Aviso", "Usuário válido, mas repositório não acessível.\nVerifique o nome do repositório.")
                    else:
                        messagebox.showinfo("Sucesso", "Token válido!\nConfigure o repositório para testar acesso completo.")
                else:
                    self.log(f"❌ Erro de autenticação: {response.status_code}", "ERROR")
                    messagebox.showerror("Erro", f"Erro de autenticação:\nCódigo: {response.status_code}\nVerifique o token.")
                    
            except requests.RequestException as e:
                self.log(f"❌ Erro de conexão: {str(e)}", "ERROR")
                messagebox.showerror("Erro", f"Erro de conexão:\n{str(e)}")
            except Exception as e:
                self.log(f"❌ Erro inesperado: {str(e)}", "ERROR")
                messagebox.showerror("Erro", f"Erro inesperado:\n{str(e)}")
        
        # Executar em thread separada
        threading.Thread(target=test_thread, daemon=True).start()
    
    def update_ui_state(self):
        """Atualiza estado da interface"""
        if self.config.get("github_token") and self.config.get("repository_name"):
            self.upload_btn.config(state=tk.NORMAL)
            repo_info = f"📁 {self.config['github_username']}/{self.config['repository_name']} ({self.config.get('branch', 'main')})"
            self.repo_info_label.config(text=repo_info, fg=self.theme.SUCCESS)
        else:
            self.upload_btn.config(state=tk.DISABLED)
            self.repo_info_label.config(text="📁 Repositório: Não configurado", fg=self.theme.ERROR)
        
        # Atualizar contagem de arquivos
        self.update_files_count()
    
    def update_files_count(self):
        """Atualiza contagem de arquivos"""
        try:
            files = self.get_files_to_upload()
            count = len(files)
            self.files_count_label.config(text=f"📄 Arquivos para upload: {count}")
        except:
            self.files_count_label.config(text="📄 Arquivos para upload: Erro ao contar")
    
    def get_files_to_upload(self):
        """Obtém lista de arquivos para upload"""
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
            '__pycache__',
            '*.pyc',
            '.git',
            'github_config.json',
            '*.log'
        ]
        
        gitignore_file = self.project_dir / ".gitignore"
        if gitignore_file.exists():
            try:
                with open(gitignore_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            patterns.append(line)
            except:
                pass
        
        return patterns
    
    def should_ignore(self, path, patterns):
        """Verifica se arquivo deve ser ignorado"""
        for pattern in patterns:
            if pattern in path or path.endswith(pattern.replace('*', '')):
                return True
        return False
    
    def start_upload(self):
        """Inicia processo de upload"""
        if not messagebox.askyesno("Confirmar", "Iniciar upload de todos os arquivos para o GitHub?"):
            return
        
        def upload_thread():
            try:
                files = self.get_files_to_upload()
                total_files = len(files)
                
                if total_files == 0:
                    self.log("Nenhum arquivo para upload", "WARNING")
                    return
                
                self.log(f"Iniciando upload de {total_files} arquivos...", "INFO")
                self.upload_btn.config(state=tk.DISABLED)
                
                success_count = 0
                error_count = 0
                
                for i, file_path in enumerate(files):
                    # Atualizar progresso
                    progress = (i / total_files) * 100
                    self.progress_var.set(progress)
                    self.progress_label.config(text=f"Uploading {i+1}/{total_files}: {file_path}")
                    
                    # Upload do arquivo
                    if self.upload_file_to_github(file_path):
                        success_count += 1
                        self.log(f"✅ {file_path}", "SUCCESS")
                    else:
                        error_count += 1
                        self.log(f"❌ {file_path}", "ERROR")
                    
                    self.root.update_idletasks()
                
                # Finalizar
                self.progress_var.set(100)
                self.progress_label.config(text=f"Concluído! ✅ {success_count} | ❌ {error_count}")
                
                # Atualizar configuração
                self.config['last_upload'] = datetime.now().isoformat()
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    json.dump(self.config, f, indent=4, ensure_ascii=False)
                
                self.log(f"Upload concluído! Sucessos: {success_count}, Erros: {error_count}", "SUCCESS")
                messagebox.showinfo("Concluído", f"Upload concluído!\n\nSucessos: {success_count}\nErros: {error_count}")
                
            except Exception as e:
                self.log(f"Erro durante upload: {str(e)}", "ERROR")
                messagebox.showerror("Erro", f"Erro durante upload:\n{str(e)}")
            finally:
                self.upload_btn.config(state=tk.NORMAL)
                self.progress_var.set(0)
                self.progress_label.config(text="")
        
        # Executar em thread separada
        threading.Thread(target=upload_thread, daemon=True).start()
    
    def upload_file_to_github(self, file_path):
        """Upload de um arquivo para GitHub"""
        try:
            # Ler arquivo
            full_path = self.project_dir / file_path
            
            if full_path.stat().st_size > 25 * 1024 * 1024:  # 25MB limit
                return False
            
            with open(full_path, 'rb') as f:
                content = f.read()
            
            # Codificar
            content_encoded = base64.b64encode(content).decode('utf-8')
            
            # API GitHub
            url = f"{self.config['api_url']}/contents/{file_path}"
            headers = {
                'Authorization': f"token {self.config['github_token']}",
                'Accept': 'application/vnd.github.v3+json',
                'Content-Type': 'application/json'
            }
            
            # Verificar se existe
            response = requests.get(url, headers=headers)
            sha = None
            if response.status_code == 200:
                sha = response.json().get('sha')
            
            # Dados
            data = {
                'message': f'Upload: {file_path} - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
                'content': content_encoded,
                'branch': self.config['branch']
            }
            
            if sha:
                data['sha'] = sha
            
            # Upload
            response = requests.put(url, headers=headers, json=data, timeout=30)
            return response.status_code in [200, 201]
            
        except Exception:
            return False
    
    def update_status(self):
        """Atualiza informações de status"""
        self.status_text.delete(1.0, tk.END)
        
        # Informações básicas
        status_info = f"""📊 STATUS DO REPOSITÓRIO
{'='*50}

👤 GitHub Username: {self.config.get('github_username', 'N/A')}
📁 Repositório: {self.config.get('repository_name', 'N/A')}
🌿 Branch: {self.config.get('branch', 'N/A')}
🔗 URL: {self.config.get('api_url', 'N/A')}
🕒 Último upload: {self.config.get('last_upload', 'Nunca')}

📄 ARQUIVOS:
{'='*20}
"""
        
        self.status_text.insert(tk.END, status_info)
        
        # Lista de arquivos
        try:
            files = self.get_files_to_upload()
            self.status_text.insert(tk.END, f"Total de arquivos para upload: {len(files)}\n\n")
            
            for i, file in enumerate(files[:20], 1):
                self.status_text.insert(tk.END, f"{i:3d}. {file}\n")
            
            if len(files) > 20:
                self.status_text.insert(tk.END, f"... e mais {len(files) - 20} arquivos\n")
                
        except Exception as e:
            self.status_text.insert(tk.END, f"Erro ao listar arquivos: {str(e)}\n")
    
    def update_files_list(self):
        """Atualiza lista de arquivos"""
        self.files_listbox.delete(0, tk.END)
        
        try:
            files = self.get_files_to_upload()
            for file in files:
                self.files_listbox.insert(tk.END, str(file))
            
            self.update_files_count()
            
        except Exception as e:
            self.files_listbox.insert(tk.END, f"Erro: {str(e)}")
    
    def clear_logs(self):
        """Limpa logs"""
        if messagebox.askyesno("Confirmar", "Limpar todos os logs?"):
            self.log_text.delete(1.0, tk.END)
            self.log("Logs limpos", "INFO")
    
    def save_logs(self):
        """Salva logs em arquivo"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                title="Salvar Logs"
            )
            
            if filename:
                content = self.log_text.get(1.0, tk.END)
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.log(f"Logs salvos em: {filename}", "SUCCESS")
                messagebox.showinfo("Sucesso", f"Logs salvos em:\n{filename}")
                
        except Exception as e:
            self.log(f"Erro ao salvar logs: {str(e)}", "ERROR")
            messagebox.showerror("Erro", f"Erro ao salvar logs:\n{str(e)}")
    
    def run(self):
        """Executa aplicação"""
        self.log("🚀 GitHub Uploader iniciado", "SUCCESS")
        self.update_ui_state()
        self.update_files_list()
        self.root.mainloop()

def main():
    """Função principal"""
    try:
        # Verificar dependências
        import requests
    except ImportError:
        print("❌ Dependência 'requests' não encontrada!")
        print("Execute: pip install requests")
        sys.exit(1)
    
    root = tk.Tk()
    app = GitHubUploaderGUI(root)
    app.run()

if __name__ == "__main__":
    main()