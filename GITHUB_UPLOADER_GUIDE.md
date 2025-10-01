# 🚀 GitHub Uploader - Guia Completo

## 📋 Descrição
App Python para upload automático dos arquivos do Midnight PDV para repositório GitHub, preparando para deploy na nuvem.

## 🔧 Instalação

### 1. Instalar dependências
```bash
python setup_uploader.py
```

### 2. Executar o uploader
```bash
python github_uploader.py
```

## ⚙️ Configuração Inicial

### 1. Criar Personal Access Token no GitHub
1. Vá para GitHub → Settings → Developer settings → Personal access tokens
2. Clique em "Generate new token (classic)"
3. Selecione as permissões:
   - ✅ `repo` (Full control of private repositories)
   - ✅ `write:packages` (Upload packages)
4. Copie o token gerado

### 2. Configurar no app
O app vai solicitar:
- **GitHub Username**: Seu nome de usuário
- **Repository Name**: Nome do repositório (ex: `midnight-pdv`)
- **GitHub Token**: O token que você criou
- **Branch**: Branch de destino (padrão: `main`)

## 🎯 Funcionalidades

### 📤 Upload Automático
- Upload de todos os arquivos do projeto
- Respeita arquivo `.gitignore`
- Atualiza arquivos existentes automaticamente
- Limite de 25MB por arquivo

### 📊 Gerenciamento
- Status do repositório
- Lista de arquivos para upload
- Configuração de credenciais
- Histórico de uploads

### 🔒 Segurança
- Token armazenado localmente
- Arquivo de configuração no `.gitignore`
- Verificação de arquivos sensíveis

## 📁 Arquivos Ignorados

O app automaticamente ignora:
```
# Configuração
github_config.json
github_uploader.log

# Python
__pycache__/
*.pyc
.env

# Database
*.db
*.sqlite

# Logs
*.log
nohup.out

# Arquivos grandes
*.mp4
*.avi
```

## 🚀 Uso Prático

### 📱 Interface Gráfica (Recomendado):
```bash
# Primeira vez
python setup_uploader.py    # Instalar dependências
python uploader.py          # Escolher GUI (opção 1)

# Ou diretamente
python github_uploader_gui.py
```

### 💻 Linha de Comando:
```bash
# Primeira vez
python setup_uploader.py    # Instalar dependências
python uploader.py          # Escolher CLI (opção 2)

# Ou diretamente
python github_uploader.py
```

### Interface Gráfica - Recursos:
- 🔧 **Aba Configuração**: Gerenciar credenciais GitHub
- 📤 **Aba Upload**: Upload com barra de progresso
- 📊 **Aba Status**: Informações do repositório
- 📄 **Aba Arquivos**: Lista de arquivos para upload  
- 📝 **Aba Logs**: Monitoramento em tempo real
- 🎨 **Tema Midnight**: Visual com cores da marca

## 📊 Monitoramento

### Ver arquivos para upload:
- Opção "4. Ver arquivos para upload"
- Lista todos os arquivos que serão enviados

### Status do repositório:
- Opção "2. Ver status do repositório"
- Mostra último upload e estatísticas

## 🛠️ Troubleshooting

### Erro de autenticação:
- Verificar se o token está correto
- Verificar permissões do token no GitHub

### Arquivo muito grande:
- Limite do GitHub: 25MB por arquivo
- Use Git LFS para arquivos grandes ou remova do upload

### Erro de rede:
- Verificar conexão com internet
- Tentar novamente em alguns minutos

## 🎯 Deploy na Nuvem

Após o upload, você pode usar plataformas como:

### Heroku:
```bash
git clone https://github.com/SEU-USERNAME/SEU-REPO.git
cd SEU-REPO
heroku create midnight-pdv
git push heroku main
```

### Railway:
1. Conectar GitHub no Railway
2. Selecionar o repositório
3. Deploy automático

### DigitalOcean App Platform:
1. Conectar GitHub
2. Selecionar repositório
3. Configurar build settings

## 📝 Dicas Importantes

### 🔐 Segurança:
- Nunca commite `github_config.json`
- Use variáveis de ambiente para tokens em produção
- Revogue tokens não utilizados

### 📊 Performance:
- Upload em lotes para muitos arquivos
- Verifique `.gitignore` para evitar arquivos desnecessários
- Monitore tamanho dos arquivos

### 🚀 Deploy:
- Teste localmente antes do upload
- Configure `requirements.txt` para a nuvem
- Use variáveis de ambiente para configurações

## 📞 Suporte

Em caso de problemas:
1. Verificar mensagens de erro no terminal
2. Consultar logs em `github_uploader.log`
3. Verificar status do GitHub API

---
*Desenvolvido para o projeto Midnight PDV* 🌟