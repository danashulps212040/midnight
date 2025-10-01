#!/bin/bash

# Script de inicialização para Render
echo "🚀 Iniciando aplicação Midnight PDV..."

# Verificar se o arquivo database.db existe, se não, criar
if [ ! -f database.db ]; then
    echo "📊 Criando database inicial..."
    python -c "from database import Database; db = Database(); print('✅ Database criado!')"
fi

echo "✅ Inicialização completa!"