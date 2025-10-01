#!/usr/bin/env python3
"""Teste simples do servidor Flask para verificar a coluna de margem"""

import sys
import os

# Adicionar o diretório atual ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar apenas o Flask app
from flask_gui import flask_app

if __name__ == '__main__':
    print("Iniciando servidor Flask para teste...")
    print("Acesse: http://localhost:8000/produtos")
    flask_app.run(host='0.0.0.0', port=8000, debug=True)
