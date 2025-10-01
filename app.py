#!/usr/bin/env python3
"""
Configuração de produção para Render
Este arquivo substitui o flask_gui.py local quando deployado no Render
"""

import os
import sys
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, send_from_directory
from flask_cors import CORS

# Importar a versão de produção do database
try:
    from database_cloud import Database
except ImportError:
    # Fallback para desenvolvimento local
    from database import Database

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'midnight-pdv-secret-key-change-in-production')

# Configuração CORS para produção
CORS(app, origins=['*'], methods=['GET', 'POST', 'PUT', 'DELETE'])

# Configuração para Render
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

@app.route('/')
def home():
    """Rota principal que serve o PDV"""
    return render_template('pdv_full.html')

@app.route('/manifest.json')
def manifest():
    """Serve o manifest PWA"""
    return send_from_directory('static', 'manifest.json', mimetype='application/json')

@app.route('/sw.js')
def service_worker():
    """Serve o service worker"""
    return send_from_directory('static', 'sw.js', mimetype='application/javascript')

@app.route('/api/produtos')
def api_produtos():
    """API para listar produtos"""
    try:
        db = Database()
        
        # Parâmetros de busca
        nome = request.args.get('nome', '').strip()
        categoria = request.args.get('categoria', '').strip()
        
        if nome or categoria:
            produtos = db.buscar_produtos_com_filtros(nome=nome, categoria=categoria)
        else:
            produtos = db.listar_produtos()
        
        db.close()
        
        if isinstance(produtos, dict) and 'erro' in produtos:
            return jsonify({'error': produtos['erro']}), 500
        
        return jsonify({
            'produtos': produtos,
            'total': len(produtos) if produtos else 0
        })
        
    except Exception as e:
        print(f"[ERROR] Erro na API de produtos: {str(e)}")
        return jsonify({'error': f'Erro interno do servidor: {str(e)}'}), 500

@app.route('/api/usuarios/login', methods=['POST'])
def login():
    """API para autenticação de usuários"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Dados não fornecidos'}), 400
        
        login_input = data.get('login', '').strip()
        senha = data.get('senha', '').strip()
        
        if not login_input or not senha:
            return jsonify({'error': 'Login e senha são obrigatórios'}), 400
        
        db = Database()
        resultado = db.autenticar_usuario(login_input, senha)
        db.close()
        
        if 'erro' in resultado:
            return jsonify({'error': resultado['erro']}), 401
        
        # Sucesso na autenticação
        session['usuario_id'] = resultado['usuario']['id']
        session['usuario_nome'] = resultado['usuario']['nome']
        session['usuario_cargo'] = resultado['usuario']['cargo']
        
        return jsonify({
            'success': True,
            'message': 'Login realizado com sucesso',
            'usuario': resultado['usuario']
        })
        
    except Exception as e:
        print(f"[ERROR] Erro no login: {str(e)}")
        return jsonify({'error': f'Erro interno do servidor: {str(e)}'}), 500

@app.route('/api/health')
def health_check():
    """Health check para Render"""
    try:
        # Testa conexão com banco
        db = Database()
        db.cursor.execute("SELECT 1")
        db.close()
        
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'timestamp': __import__('datetime').datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': __import__('datetime').datetime.now().isoformat()
        }), 500

@app.errorhandler(404)
def not_found(error):
    """Handler para páginas não encontradas"""
    return render_template('pdv_full.html'), 200  # Redirect para SPA

@app.errorhandler(500)
def internal_error(error):
    """Handler para erros internos"""
    return jsonify({
        'error': 'Erro interno do servidor',
        'message': 'Tente novamente mais tarde'
    }), 500

if __name__ == '__main__':
    # Configuração para Render
    port = int(os.environ.get('PORT', 8000))
    
    if DEBUG:
        # Desenvolvimento
        app.run(host='0.0.0.0', port=port, debug=True)
    else:
        # Produção com Gunicorn
        print(f"[INFO] Iniciando aplicação em produção na porta {port}")
        app.run(host='0.0.0.0', port=port, debug=False)