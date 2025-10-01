#!/usr/bin/env python3
"""Arquivo para testar apenas o Flask sem a GUI PyQt5"""

from flask import Flask, render_template, request, jsonify
from database import Database
import sys
import traceback

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/produtos')
def produtos():
    return render_template('produtos.html')

@app.route('/api/produtos', methods=['POST'])
def criar_produto():
    """Rota para criar um novo produto"""
    try:
        print(f"[DEBUG] Dados recebidos na API: {request.json}")
        db = Database()
        resultado = db.inserir_produto(request.json)
        db.close()
        
        if 'erro' in resultado:
            print(f"[ERROR] Erro ao criar produto: {resultado['erro']}")
            return jsonify({'erro': resultado['erro']}), 400
        else:
            print(f"[SUCCESS] Produto criado com sucesso: {resultado}")
            return jsonify(resultado), 200
            
    except Exception as e:
        print(f"[ERROR] Erro na API de produtos: {str(e)}")
        traceback.print_exc()
        return jsonify({'erro': f'Erro interno do servidor: {str(e)}'}), 500

if __name__ == '__main__':
    print("Iniciando servidor Flask para teste...")
    app.run(debug=True, host='127.0.0.1', port=5000)
