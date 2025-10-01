# 🚀 Guia Completo: Migração Render + PlanetScale

## 📋 Visão Geral

Este guia te levará passo a passo para migrar sua aplicação Flask do ambiente local (MySQL no iMac) para a nuvem usando:
- **Render**: Hospedagem da aplicação Flask
- **PlanetScale**: Banco de dados MySQL na nuvem

## 🎯 Situação Atual vs. Final

### Atual (Local)
- ✅ Flask rodando em `localhost:8000`
- ✅ MySQL local no iMac
- ✅ `database.py` com conexão hardcoded

### Final (Nuvem)
- 🚀 Flask rodando no Render (URL pública)
- ☁️ MySQL PlanetScale (alta disponibilidade)
- 🔒 Variáveis de ambiente seguras

## 📝 Pré-requisitos

1. **Conta GitHub** (para o código)
2. **Conta PlanetScale** (banco de dados)
3. **Conta Render** (hospedagem)
4. **Backup do banco local** (segurança)

---

## 🗄️ ETAPA 1: Configuração do PlanetScale

### 1.1 Criação da Conta
1. Acesse [planetscale.com](https://planetscale.com)
2. Clique em "Get Started" e crie uma conta gratuita
3. Verifique seu email

### 1.2 Criação do Database
1. No dashboard do PlanetScale, clique em "Create database"
2. Nome: `midnight`
3. Região: Escolha a mais próxima (ex: `us-east-1`)
4. Clique em "Create database"

### 1.3 Obter Credenciais de Conexão
1. Vá para seu database `midnight`
2. Clique em "Connect"
3. Selecione "General" 
4. Anote as credenciais:
   ```
   Host: aws.connect.psdb.cloud
   Username: xxxxxxxxx
   Password: pscale_pw_xxxxxxxxx
   Database: midnight
   Port: 3306
   ```

### 1.4 Configurar Branch de Produção
1. No database, vá para "Branches"
2. Promote a branch `main` para produção:
   - Clique nos 3 pontos da branch `main`
   - Selecione "Promote to production"

---

## ⚙️ ETAPA 2: Preparação do Código

### 2.1 Configurar Variáveis de Ambiente Locais
Crie um arquivo `.env` no diretório do projeto:

```bash
# Copie o template
cp .env.example .env

# Edite com suas credenciais
nano .env
```

Conteúdo do `.env`:
```env
# PlanetScale Configuration
PLANETSCALE_HOST=aws.connect.psdb.cloud
PLANETSCALE_USERNAME=sua_credencial_username
PLANETSCALE_PASSWORD=sua_credencial_password
PLANETSCALE_DATABASE=midnight
PLANETSCALE_PORT=3306

# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=gere_uma_chave_secreta_aqui

# Render Configuration
PORT=8000
```

### 2.2 Instalar Dependências
```bash
pip install -r requirements.txt
```

### 2.3 Executar Migração
```bash
# Tornar o script executável
chmod +x setup_planetscale.py

# Executar configuração
python setup_planetscale.py
```

### 2.4 Testar Localmente
```bash
# O Flask agora deve se conectar ao PlanetScale
python flask_gui.py
```

Acesse `http://localhost:8000` e verifique se tudo funciona.

---

## 📤 ETAPA 3: Upload para GitHub

### 3.1 Usar o GitHub Uploader
```bash
# Execute o uploader GUI
python github_uploader_gui.py
```

**Configuração no Uploader:**
- **Repository Name**: `midnight-pdv`
- **Description**: `Sistema PDV Midnight - Render Deploy`
- **Visibility**: Private (recomendado)

**Arquivos para incluir:**
- ✅ `flask_gui.py`
- ✅ `database_cloud.py`
- ✅ `templates/`
- ✅ `static/`
- ✅ `requirements.txt`
- ✅ `build.sh`
- ❌ `.env` (NUNCA enviar para GitHub)
- ❌ `database.py` (versão local)

### 3.2 Verificar Upload
1. Acesse seu repositório GitHub
2. Confirme que todos os arquivos foram enviados
3. Anote a URL: `https://github.com/seu_usuario/midnight-pdv`

---

## 🚀 ETAPA 4: Deploy no Render

### 4.1 Conectar GitHub ao Render
1. Acesse [render.com](https://render.com)
2. Faça login com sua conta GitHub
3. Autorize o Render a acessar seus repositórios

### 4.2 Criar Novo Serviço Web
1. No dashboard Render, clique em "New +"
2. Selecione "Web Service"
3. Conecte seu repositório `midnight-pdv`
4. Configure:
   ```
   Name: midnight-pdv
   Region: Oregon (US West) ou mais próxima
   Branch: main
   Runtime: Python 3
   Build Command: chmod +x build.sh && ./build.sh
   Start Command: gunicorn flask_gui:app --bind 0.0.0.0:$PORT
   ```

### 4.3 Configurar Variáveis de Ambiente
Na seção "Environment Variables", adicione:

```
PLANETSCALE_HOST=aws.connect.psdb.cloud
PLANETSCALE_USERNAME=sua_credencial
PLANETSCALE_PASSWORD=sua_credencial  
PLANETSCALE_DATABASE=midnight
PLANETSCALE_PORT=3306
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=sua_chave_secreta_forte
PORT=8000
```

### 4.4 Fazer Deploy
1. Clique em "Create Web Service"
2. Aguarde o build (3-5 minutos)
3. Acompanhe os logs para ver se tudo está OK

### 4.5 Verificar Deploy
- URL será algo como: `https://midnight-pdv-xxxx.onrender.com`
- Teste todas as funcionalidades principais
- Verifique conexão com banco de dados

---

## 🔧 ETAPA 5: Migração de Dados

### 5.1 Exportar Dados Locais
```bash
# Fazer backup do MySQL local
mysqldump -u root -p midnight > backup_midnight.sql

# Ou usar phpMyAdmin para exportar
```

### 5.2 Importar no PlanetScale
**Opção A: PlanetScale CLI**
```bash
# Instalar PlanetScale CLI
curl -fsSL https://github.com/planetscale/cli/releases/latest/download/pscale_linux_amd64.tar.gz | tar -xz

# Fazer login
./pscale auth login

# Importar dados
./pscale shell midnight main < backup_midnight.sql
```

**Opção B: Importação Manual**
1. Use o console web do PlanetScale
2. Execute os INSERTs manualmente
3. Ou use uma ferramenta como MySQL Workbench

---

## ✅ ETAPA 6: Verificações Finais

### 6.1 Checklist Funcionalidades
- [ ] Login/logout funcionando
- [ ] Cadastros (usuários, produtos, etc.)
- [ ] Consultas e relatórios
- [ ] Upload de arquivos
- [ ] PWA funcionando no iPad

### 6.2 Monitoramento
**Render Dashboard:**
- Verificar logs de aplicação
- Monitorar uso de recursos
- Configurar alertas

**PlanetScale Dashboard:**
- Verificar conexões ativas
- Monitorar queries lentas
- Verificar uso de storage

---

## 🔒 ETAPA 7: Configurações de Segurança

### 7.1 Variáveis Sensíveis
- ✅ Nunca commite `.env` para Git
- ✅ Use senhas fortes para SECRET_KEY
- ✅ Ative 2FA no PlanetScale e Render

### 7.2 Backup Automático
- PlanetScale faz backup automático
- Configure backup adicional se necessário
- Documente processo de restore

---

## 🆘 Troubleshooting

### Problemas Comuns

#### ❌ Erro de Conexão com Banco
```
Error: Can't connect to MySQL server
```
**Solução:**
1. Verificar credenciais PlanetScale
2. Verificar se branch está em produção
3. Verificar variáveis de ambiente no Render

#### ❌ Aplicação não Inicia
```
Error: Module not found
```
**Solução:**
1. Verificar `requirements.txt`
2. Verificar comando de build
3. Verificar logs do Render

#### ❌ PWA não Funciona
```
Service Worker registration failed
```
**Solução:**
1. Verificar HTTPS no Render
2. Verificar paths dos arquivos estáticos
3. Verificar manifest.json

### Logs Úteis
```bash
# Ver logs da aplicação
curl https://api.render.com/v1/services/seu-service-id/logs

# Ver status do serviço
curl https://api.render.com/v1/services/seu-service-id
```

---

## 📊 Monitoramento Pós-Deploy

### Métricas Importantes
- **Tempo de resposta** < 2 segundos
- **Uptime** > 99%
- **Conexões de banco** < 80% do limite
- **Uso de memória** < 512MB

### Alertas Recomendados
- Aplicação offline por > 1 minuto
- Erro de conexão com banco
- Uso de memória > 80%
- Tempo de resposta > 5 segundos

---

## 💰 Custos Esperados

### Render (Web Service)
- **Starter**: $7/mês
- **Standard**: $25/mês (recomendado)

### PlanetScale
- **Hobby**: Gratuito (5GB)
- **Scaler**: $29/mês (quando crescer)

### Total Mensal
- **Inicial**: $7 (Render Starter + PlanetScale Hobby)
- **Crescimento**: $54 (Render Standard + PlanetScale Scaler)

---

## 🎉 Conclusão

Após seguir este guia, você terá:

✅ **Aplicação funcionando na nuvem**
✅ **Banco de dados escalável e confiável**  
✅ **Backup automático dos dados**
✅ **URL pública para acesso remoto**
✅ **PWA funcionando em qualquer dispositivo**

### Próximos Passos
1. Configurar domínio personalizado (opcional)
2. Configurar CDN para arquivos estáticos
3. Implementar cache Redis (futuro)
4. Configurar monitoramento avançado

---

## 📞 Suporte

Se encontrar problemas:

1. **Verificar logs** no dashboard do Render
2. **Consultar documentação**:
   - [Render Docs](https://render.com/docs)
   - [PlanetScale Docs](https://planetscale.com/docs)
3. **Verificar status**:
   - [Render Status](https://status.render.com/)
   - [PlanetScale Status](https://status.planetscale.com/)

**Lembre-se**: A migração para a nuvem é um processo iterativo. Comece simples e vá otimizando conforme a necessidade!
