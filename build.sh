#!/bin/bash

# ====================================
# SCRIPT DE BUILD PARA RENDER
# ====================================

echo "🚀 Iniciando build para Render..."

# Atualizar pip
echo "📦 Atualizando pip..."
python -m pip install --upgrade pip

# Instalar dependências
echo "📦 Instalando dependências..."
pip install -r requirements.txt

# Verificar se as variáveis de ambiente estão configuradas
echo "🔍 Verificando configuração..."
if [ -z "$PLANETSCALE_HOST" ]; then
    echo "❌ ERRO: PLANETSCALE_HOST não configurado"
    exit 1
fi

if [ -z "$PLANETSCALE_USERNAME" ]; then
    echo "❌ ERRO: PLANETSCALE_USERNAME não configurado"
    exit 1
fi

if [ -z "$PLANETSCALE_PASSWORD" ]; then
    echo "❌ ERRO: PLANETSCALE_PASSWORD não configurado"
    exit 1
fi

echo "✅ Configuração validada"

# Testar conexão com banco (opcional)
echo "🔌 Testando conexão com banco de dados..."
python -c "
try:
    from database import Database
    db = Database()
    result = db.testar_conexao()
    if 'erro' in result:
        print('❌ Erro na conexão:', result['erro'])
        exit(1)
    else:
        print('✅ Conexão com banco de dados OK')
        db.close()
except Exception as e:
    print('❌ Erro ao testar conexão:', str(e))
    exit(1)
"

# Criar diretório temporário se não existir
mkdir -p /tmp

echo "🎉 Build concluído com sucesso!"

# Informações do build
echo "📊 Informações do Build:"
echo "   - Python: $(python --version)"
echo "   - Pip: $(pip --version)"
echo "   - Workers disponíveis: $(nproc)"
echo "   - Memória disponível: $(free -h | awk '/^Mem:/ {print $2}' || echo 'N/A')"