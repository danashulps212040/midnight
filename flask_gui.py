import sys
import json
import threading
from decimal import Decimal
from datetime import datetime, date
from collections import defaultdict, deque
# from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QTextEdit, QWidget, QVBoxLayout, QHBoxLayout
# from PyQt5.QtCore import QProcess, QTimer, QObject, pyqtSignal
# from PyQt5.QtChart import QChart, QChartView, QLineSeries
# from PyQt5.QtGui import QPainter
import psutil
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from datetime import timedelta
from database import Database

# Sistema de proteção contra força bruta
failed_attempts = defaultdict(lambda: deque(maxlen=10))  # Últimas 10 tentativas por IP
BLOCK_THRESHOLD = 5  # Bloquear após 5 tentativas
BLOCK_TIME = 300  # 5 minutos em segundos

def is_ip_blocked(ip):
    """Verifica se um IP está bloqueado por tentativas de força bruta"""
    attempts = failed_attempts[ip]
    if len(attempts) >= BLOCK_THRESHOLD:
        # Verificar se as tentativas foram nos últimos 5 minutos
        current_time = datetime.now().timestamp()
        recent_attempts = [t for t in attempts if current_time - t < BLOCK_TIME]
        if len(recent_attempts) >= BLOCK_THRESHOLD:
            return True
    return False

def record_failed_attempt(ip):
    """Registra uma tentativa de login falhada"""
    failed_attempts[ip].append(datetime.now().timestamp())

def clear_failed_attempts(ip):
    """Limpa tentativas falhadas após login bem-sucedido"""
    if ip in failed_attempts:
        failed_attempts[ip].clear()

def convert_values_to_json_safe(data):
    """
    Converte valores que podem causar problemas na serialização JSON
    """
    if isinstance(data, dict):
        return {key: convert_values_to_json_safe(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [convert_values_to_json_safe(item) for item in data]
    elif isinstance(data, Decimal):
        return float(data)
    elif isinstance(data, (datetime, date)):
        return data.isoformat()
    elif hasattr(data, '__dict__'):
        # Para objetos customizados, converter para dict
        return convert_values_to_json_safe(data.__dict__)
    else:
        return data

# class Stream(QObject):
#     """
#     Classe para redirecionar a saída padrão (stdout/stderr) para a interface gráfica E manter no terminal.
#     """
#     textWritten = pyqtSignal(str)

#     def __init__(self, original_stream):
#         super().__init__()
#         self.original_stream = original_stream

#     def write(self, text):
#         # Escrever no terminal original
#         self.original_stream.write(text)
#         self.original_stream.flush()
#         # Também enviar para a GUI
#         self.textWritten.emit(str(text))

#     def flush(self):
#         if hasattr(self.original_stream, 'flush'):
#             self.original_stream.flush()

# class FlaskControlGUI(QMainWindow):
#     def __init__(self):
#         """
#         Inicializa a interface gráfica e configura os redirecionamentos de saída.
#         """
#         super().__init__()
#         self.process = QProcess()

#         # Store original stdout and stderr
#         self._original_stdout = sys.stdout
#         self._original_stderr = sys.stderr

#         self.initUI() # This initializes self.log_text

#         # Redirect stdout and stderr for embedded Flask logs MANTENDO no terminal
#         self.log_stream_stdout = Stream(self._original_stdout)
#         self.log_stream_stderr = Stream(self._original_stderr)
#         self.log_stream_stdout.textWritten.connect(self.append_log_text_from_stream)
#         self.log_stream_stderr.textWritten.connect(self.append_log_text_from_stream)
#         sys.stdout = self.log_stream_stdout
#         sys.stderr = self.log_stream_stderr

#     def initUI(self):
#         """
#         Configura a interface gráfica principal com botões, área de logs e gráficos.
#         """
#         self.setWindowTitle('Controle do Servidor Flask')
        
        # Centraliza a janela na tela
#         screen_geometry = QApplication.desktop().screenGeometry()
#         x = (screen_geometry.width() - 800) // 2
#         y = (screen_geometry.height() - 600) // 2
#         self.setGeometry(x, y, 800, 600)
        
        # Layout principal
#         self.main_widget = QWidget()
#         self.setCentralWidget(self.main_widget)
#         self.main_layout = QVBoxLayout()
#         self.main_widget.setLayout(self.main_layout)
        
        # Layout para botões
#         self.button_layout = QHBoxLayout()
#         self.main_layout.addLayout(self.button_layout)
        
        # Botão Iniciar
#         self.start_btn = QPushButton('Iniciar Servidor')
#         self.start_btn.clicked.connect(self.start_server)
#         self.button_layout.addWidget(self.start_btn)

        # Botão Parar
#         self.stop_btn = QPushButton('Parar Servidor')
#         self.stop_btn.clicked.connect(self.stop_server)
#         self.stop_btn.setEnabled(False)
#         self.button_layout.addWidget(self.stop_btn)

        # Botão Reiniciar
#         self.restart_btn = QPushButton('Reiniciar Servidor')
#         self.restart_btn.clicked.connect(self.restart_server)
#         self.restart_btn.setEnabled(False)
#         self.button_layout.addWidget(self.restart_btn)
        
        # Área de logs
#         self.log_text = QTextEdit()
#         self.log_text.setReadOnly(True)
#         self.main_layout.addWidget(self.log_text)
        
        # Conexão do log permanece a mesma
#         self.process.readyReadStandardOutput.connect(self.handle_output)
        
        # Configuração dos gráficos
#         self.setup_charts()
#         self.timer = QTimer()
#         self.timer.timeout.connect(self.update_stats)
#         self.timer.start(1000)

#     def start_server(self):
#         """
#         Inicia o servidor Flask em uma thread separada e atualiza o estado dos botões.
#         """
#         self.process.start('python', ['app.py'])
#         self.start_btn.setEnabled(False)
#         self.stop_btn.setEnabled(True)
#         self.restart_btn.setEnabled(True)
        
        # Inicia o servidor Flask em uma thread separada
#         import threading
#         flask_thread = threading.Thread(target=flask_app.run, kwargs={'port': 8000, 'debug': True, 'use_reloader': False})
#         flask_thread.daemon = True
#         flask_thread.start()

#     def stop_server(self):
#         """
#         Para o servidor Flask e atualiza o estado dos botões.
#         """
#         self.process.terminate()
#         self.start_btn.setEnabled(True)
#         self.stop_btn.setEnabled(False)
#         self.restart_btn.setEnabled(False)

#     def restart_server(self):
#         """
#         Reinicia o servidor Flask, parando e iniciando novamente.
#         """
#         self.stop_server()
#         self.start_server()
        
#     def setup_charts(self):
#         """
#         Configura os gráficos de monitoramento de CPU, memória e disco.
#         """
        # Limpa widgets existentes
#         if hasattr(self, 'charts_layout'):
            # Remove o layout antigo completamente
#             while self.charts_layout.count():
#                 item = self.charts_layout.takeAt(0)
#                 widget = item.widget()
#                 if widget:
#                     widget.deleteLater()
            # Remove o layout do widget principal
#             self.main_layout.removeItem(self.charts_layout)
#             self.charts_layout.deleteLater()
        
        # Cria novo layout para gráficos
#         self.charts_layout = QHBoxLayout()
#         self.charts_layout.setContentsMargins(0, 0, 0, 0)
#         self.main_layout.addLayout(self.charts_layout)
        
        # Gráfico de CPU
#         self.cpu_chart = QChart()
#         self.cpu_series = QLineSeries()
#         self.cpu_chart.addSeries(self.cpu_series)
#         self.cpu_chart.createDefaultAxes()
#         self.cpu_chart.axisX().setRange(0, 60)
#         self.cpu_chart.axisY().setRange(0, 100)
#         self.cpu_chart.setTitle('Uso de CPU (%)')
#         self.cpu_view = QChartView(self.cpu_chart)
#         self.cpu_view.setRenderHint(QPainter.Antialiasing)
#         self.charts_layout.addWidget(self.cpu_view)
        
        # Gráfico de Memória
#         self.mem_chart = QChart()
#         self.mem_series = QLineSeries()
#         self.mem_chart.addSeries(self.mem_series)
#         self.mem_chart.createDefaultAxes()
#         self.mem_chart.axisX().setRange(0, 60)
#         self.mem_chart.axisY().setRange(0, 100)
#         self.mem_chart.setTitle('Uso de Memória (%)')
#         self.mem_view = QChartView(self.mem_chart)
#         self.mem_view.setRenderHint(QPainter.Antialiasing)
#         self.charts_layout.addWidget(self.mem_view)
        
        # Gráfico de Disco
#         self.disk_chart = QChart()
#         self.disk_series = QLineSeries()
#         self.disk_chart.addSeries(self.disk_series)
#         self.disk_chart.createDefaultAxes()
#         self.disk_chart.axisX().setRange(0, 60)
#         self.disk_chart.axisY().setRange(0, 100)
#         self.disk_chart.setTitle('Uso de Disco (%)')
#         self.disk_view = QChartView(self.disk_chart)
#         self.disk_view.setRenderHint(QPainter.Antialiasing)
#         self.charts_layout.addWidget(self.disk_view)
        
        # Conexão do log permanece a mesma
#         self.process.readyReadStandardOutput.connect(self.handle_output)
    
#     def handle_output(self):
#         """
#         Processa a saída do servidor Flask e exibe na área de logs.
#         """
#         output = self.process.readAllStandardOutput().data().decode('utf-8')
#         timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#         cleaned_output = output.rstrip('\r\n')
#         self.log_text.append(f'[{timestamp}] {cleaned_output}')
        
#     def update_stats(self):
#         """
#         Atualiza as estatísticas de CPU, memória e disco nos gráficos.
#         """
        # Atualiza estatísticas de CPU
#         cpu_percent = psutil.cpu_percent()
#         self.cpu_series.append(len(self.cpu_series), cpu_percent)
#         if len(self.cpu_series) > 60:
#             self.cpu_series.remove(0)
#         self.cpu_chart.setTitle(f'Uso de CPU: {cpu_percent:.1f}%')
        
        # Atualiza estatísticas de Memória
#         mem_percent = psutil.virtual_memory().percent
#         self.mem_series.append(len(self.mem_series), mem_percent)
#         if len(self.mem_series) > 60:
#             self.mem_series.remove(0)
#         self.mem_chart.setTitle(f'Uso de Memória: {mem_percent:.1f}%')
        
        # Atualiza estatísticas de Disco
#         disk_percent = psutil.disk_usage('/').percent
#         self.disk_series.append(len(self.disk_series), disk_percent)
#         if len(self.disk_series) > 60:
#             self.disk_series.remove(0)
#         self.disk_chart.setTitle(f'Uso de Disco: {disk_percent:.1f}%')

#     def append_log_text_from_stream(self, text):
#         """
#         Adiciona texto ao log a partir do stream redirecionado.
#         """
#         timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # rstrip newlines from the incoming text, as append() will add one
#         cleaned_text = text.rstrip('\r\n')
#         self.log_text.append(f'[{timestamp}] {cleaned_text}')
        # QApplication.processEvents() # Uncomment if GUI freezes during heavy logging

#     def closeEvent(self, event):
#         """
#         Restaura os redirecionamentos de saída ao fechar a janela.
#         """
        # Restore stdout and stderr
#         sys.stdout = self._original_stdout
#         sys.stderr = self._original_stderr

        # Terminate the QProcess if it's running
#         if self.process.state() == QProcess.Running:
#             self.process.terminate()
#             self.process.waitForFinished(3000) # Wait up to 3 seconds for graceful termination

#         super().closeEvent(event)

# Configuração do servidor Flask
flask_app = Flask(__name__)

# Configurar chave secreta para sessões
flask_app.secret_key = 'midnight_secret_key_2025'

# Habilitar modo debug e recarregamento automático
flask_app.config['DEBUG'] = True
flask_app.config['TEMPLATES_AUTO_RELOAD'] = True

# Configuração de segurança
flask_app.config['SESSION_COOKIE_SECURE'] = False  # True apenas para HTTPS
flask_app.config['SESSION_COOKIE_HTTPONLY'] = True
flask_app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
flask_app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)  # 30 dias para sessões permanentes

# Configurar o encoder JSON personalizado para lidar com Decimal
flask_app.json.default = lambda obj: float(obj) if isinstance(obj, Decimal) else obj

# Middleware de segurança básica
@flask_app.before_request
def security_headers():
    # Capturar IP real do cliente (considerando proxies)
    client_ip = request.headers.get('X-Forwarded-For', request.headers.get('X-Real-IP', request.remote_addr))
    if client_ip and ',' in client_ip:
        client_ip = client_ip.split(',')[0].strip()
    
    # Log detalhado de todas as requisições
    user_agent = request.headers.get('User-Agent', 'Unknown')
    method = request.method
    path = request.path
    
    # Log mais silencioso para requisições locais e arquivos estáticos
    if client_ip in ['127.0.0.1', '::1', 'localhost']:
        # Apenas log de requisições importantes localmente
        if method == 'POST' or path.startswith('/login') or path.startswith('/logout') or path.startswith('/api'):
            print(f"[LOCAL] {client_ip} -> {method} {path}")
    elif not path.startswith('/static') and not path.endswith('.ico'):
        # Log completo para IPs externos
        print(f"[EXTERNAL] IP: {client_ip} | METHOD: {method} | PATH: {path} | USER-AGENT: {user_agent}")
    
    # Bloquear métodos HTTP perigosos (removido OPTIONS para permitir CORS)
    if request.method in ['CONNECT', 'TRACE']:
        print(f"[SECURITY BLOCK] Método perigoso: {client_ip} -> {method} {path}")
        return 'Method not allowed', 405
    
    # Verificar se é uma tentativa de proxy
    if request.path.startswith('http://') or request.path.startswith('https://'):
        print(f"[SECURITY BLOCK] Tentativa de proxy: {client_ip} -> {path}")
        return 'Forbidden', 403
    
    # Bloquear tentativas de acesso a APIs externas
    external_apis = ['api.ipify.org', 'shadowserver.org', 'packetsdatabase.com']
    if any(api in request.path for api in external_apis):
        print(f"[SECURITY BLOCK] API externa: {client_ip} -> {path}")
        return 'Forbidden', 403
    
    # Log de tentativas suspeitas (excluindo nossas próprias rotas de API)
    suspicious_paths = ['/wp-admin', '/admin', '/config', '/.env', '/phpmyadmin', '/xmlrpc.php', '/wp-login.php']
    if any(path in request.path.lower() for path in suspicious_paths):
        print(f"[SECURITY ALERT] Tentativa suspeita: {client_ip} -> {path} | USER-AGENT: {user_agent}")
        return 'Not Found', 404

@flask_app.after_request
def add_security_headers(response):
    # Adicionar headers de segurança
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response

# Função helper para verificar autenticação com redirecionamento
def require_login(message='Você precisa fazer login primeiro!', category='warning'):
    """Verifica se o usuário está logado, se não, redireciona para login com next parameter"""
    if 'user_id' not in session:
        flash(message, category)
        return redirect(url_for('login', next=request.url))
    return None

# Rota para favicon
@flask_app.route('/favicon.ico')
def favicon():
    return '', 204

@flask_app.route('/login', methods=['GET', 'POST'])
def login():
    # Capturar IP para logs de segurança
    client_ip = request.headers.get('X-Forwarded-For', request.headers.get('X-Real-IP', request.remote_addr))
    if client_ip and ',' in client_ip:
        client_ip = client_ip.split(',')[0].strip()
    
    # Verificar se IP está bloqueado por força bruta
    if is_ip_blocked(client_ip):
        print(f"[SECURITY BLOCK] IP bloqueado por força bruta: {client_ip}")
        flash('Muitas tentativas de login. Tente novamente em 5 minutos.', 'danger')
        return render_template('login.html'), 429
    
    if request.method == 'POST':
        # Obter dados do formulário
        username = request.form.get('username')
        password = request.form.get('password')
        keep_connected = request.form.get('keep_connected')
        
        print(f"[LOGIN ATTEMPT] IP: {client_ip} | Username: {username}")
        
        if not username or not password:
            print(f"[LOGIN FAILED] IP: {client_ip} | Reason: Campos vazios")
            record_failed_attempt(client_ip)
            flash('Usuário e senha são obrigatórios!', 'danger')
            return render_template('login.html')
        
        # Autenticar usuário
        db = Database()
        try:
            print(f"[DEBUG] Chamando autenticar_usuario com login: {username}")
            resultado = db.autenticar_usuario(username, password)
            print(f"[DEBUG] Resultado da autenticação: {resultado}")
            db.close()
            
            if 'erro' in resultado:
                print(f"[LOGIN FAILED] IP: {client_ip} | Username: {username} | Reason: {resultado['erro']}")
                record_failed_attempt(client_ip)
                flash(resultado['erro'], 'danger')
                return render_template('login.html')
            
            # Sucesso na autenticação - salvar dados na sessão
            usuario = resultado['usuario']
            print(f"[LOGIN SUCCESS] IP: {client_ip} | Username: {usuario['nome']} | User ID: {usuario['id']}")
            
            # Limpar tentativas falhadas após sucesso
            clear_failed_attempts(client_ip)
            
            session['user_id'] = usuario['id']
            session['user_name'] = usuario['nome']
            session['user_email'] = usuario['email']
            session['user_cargo'] = usuario['cargo']
            session['user_nivel_acesso'] = usuario['nivel_de_acesso']
            session['keep_connected'] = bool(keep_connected)
            
            # Configurar sessão permanente se 'manter conectado' estiver marcado
            if keep_connected:
                session.permanent = True
                print(f"[DEBUG] Sessão permanente ativada para usuário: {usuario['nome']}")
            else:
                session.permanent = False
                print(f"[DEBUG] Sessão temporária para usuário: {usuario['nome']}")
            
            # Adicionar variáveis compatíveis com o template
            session['logged_in'] = True
            session['username'] = usuario['nome']  # Para compatibilidade com template
            
            print(f"[DEBUG] Sessão criada para usuário ID: {session['user_id']}")
            flash('Login realizado com sucesso!', 'success')
            
            # Verificar se há uma URL de destino (next)
            next_page = request.args.get('next') or request.form.get('next')
            if next_page:
                # Validar se a URL é segura (mesmo domínio)
                from urllib.parse import urlparse, urljoin
                if urlparse(next_page).netloc == '':
                    print(f"[DEBUG] Redirecionando para: {next_page}")
                    return redirect(next_page)
                else:
                    print(f"[SECURITY] URL externa rejeitada: {next_page}")
            
            return redirect(url_for('dashboard'))
            
        except Exception as e:
            print(f"[ERROR] Erro no login: {str(e)}")
            import traceback
            print(f"[ERROR] Traceback: {traceback.format_exc()}")
            flash('Erro interno do servidor. Tente novamente.', 'danger')
            return render_template('login.html')
    
    # GET request - mostrar formulário de login
    next_page = request.args.get('next')
    return render_template('login.html', next=next_page)

# Rota principal - redirecionar para login
@flask_app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@flask_app.route('/dashboard')
def dashboard():
    # Verificar autenticação
    auth_check = require_login()
    if auth_check:
        return auth_check
    
    return render_template('dashboard.html')

@flask_app.route('/logout')
def logout():
    # Capturar IP e dados da sessão para log
    client_ip = request.headers.get('X-Forwarded-For', request.headers.get('X-Real-IP', request.remote_addr))
    if client_ip and ',' in client_ip:
        client_ip = client_ip.split(',')[0].strip()
    
    username = session.get('username', 'Unknown')
    user_id = session.get('user_id', 'Unknown')
    
    print(f"[LOGOUT] IP: {client_ip} | Username: {username} | User ID: {user_id}")
    
    session.clear()
    flash('Logout realizado com sucesso!', 'success')
    return redirect(url_for('login'))

@flask_app.route('/usuarios')
def usuarios():
    db = Database()
    try:
        search = request.args.get('search', '')
        cargo = request.args.get('cargo', 'all')
        status = request.args.get('status', 'all')
        
        usuarios_list = db.buscar_usuarios(filtro_nome=search, filtro_cargo=cargo, filtro_status=status)
        
        # Verificar se usuarios_list é uma lista
        if isinstance(usuarios_list, dict) and 'erro' in usuarios_list:
            print(f"[ERROR] Erro ao buscar usuários: {usuarios_list['erro']}")
            return render_template('usuarios.html', usuarios=[], error=usuarios_list['erro'])
        
        print(f"[DEBUG] Usuários encontrados: {len(usuarios_list)}")
        print(f"[DEBUG] Primeiro usuário (se houver): {usuarios_list[0] if usuarios_list else 'Nenhum'}")
        return render_template('usuarios.html', usuarios=usuarios_list)
    except Exception as e:
        print(f"[ERROR] Exceção na rota /usuarios: {str(e)}")
        return render_template('usuarios.html', usuarios=[], error=str(e))
    finally:
        db.close()

@flask_app.route('/produtos')
def produtos():
    return render_template('produtos.html')

@flask_app.route('/pdv-ios12')
def pdv_ios12():
    """PDV compatível com iOS 12 Safari"""
    return render_template('pdv_ios12.html')

@flask_app.route('/pdv-simple')
def pdv_simple():
    """PDV versão simples para iOS 12"""
    return render_template('pdv_ios12_simple.html')

@flask_app.route('/pdv-full')
def pdv_full():
    """PDV versão completa para iOS 12 com todos os recursos"""
    # Verificar autenticação
    auth_check = require_login('Você precisa estar logado para acessar o PDV.', 'danger')
    if auth_check:
        return auth_check
    
    return render_template('pdv_full.html')

@flask_app.route('/api/usuarios', methods=['GET', 'POST'])
def handle_usuarios():
    db = Database()
    try:
        if request.method == 'GET':
            search = request.args.get('search', '')
            cargo = request.args.get('cargo', 'all')
            status = request.args.get('status', 'all')
            
            usuarios_list = db.buscar_usuarios(filtro_nome=search, filtro_cargo=cargo, filtro_status=status)
            
            if isinstance(usuarios_list, dict) and 'erro' in usuarios_list:
                return jsonify({'status': 'error', 'message': usuarios_list['erro']}), 500
            
            print(f"[DEBUG] API /api/usuarios GET: {len(usuarios_list)} usuários retornados")
            return jsonify({'status': 'success', 'data': usuarios_list}), 200

        elif request.method == 'POST':
            data = request.form
            foto = request.files.get('foto_de_perfil')
            foto_bytes = foto.read() if foto else None
            
            result = db.criar_usuario(
                nome=data['nome'],
                email=data['email'],
                senha=data['senha'],
                cargo=data.get('cargo'),
                nivel_de_acesso=int(data['nivel_de_acesso']),
                foto_de_perfil=foto_bytes
            )
            
            if 'erro' in result:
                return jsonify({'status': 'error', 'message': result['erro']}), 400
            return jsonify({'status': 'success', 'message': 'Usuário criado com sucesso', 'id': result['id']}), 201

    except Exception as e:
        print(f"[ERROR] Exceção na API /api/usuarios: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        db.close()

@flask_app.route('/api/usuarios/<int:id>', methods=['GET'])
def buscar_usuario(id):
    db = Database()
    try:
        usuario = db.buscar_usuario_por_id(id)
        if 'erro' in usuario:
            return jsonify({'status': 'error', 'message': usuario['erro']}), 404
        return jsonify({'status': 'success', 'data': usuario})
    except Exception as e:
        print(f"[ERROR] Exceção ao buscar usuário {id}: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        db.close()

@flask_app.route('/api/usuarios/<int:id>', methods=['PUT'])
def atualizar_usuario(id):
    db = Database()
    try:
        data = request.form
        foto = request.files.get('foto_de_perfil')
        foto_bytes = foto.read() if foto else None
        
        result = db.atualizar_usuario(
            id=id,
            nome=data.get('nome'),
            email=data.get('email'),
            senha=data.get('senha') if data.get('senha') else None,
            cargo=data.get('cargo'),
            nivel_de_acesso=data.get('nivel_de_acesso'),
            foto_de_perfil=foto_bytes
        )
        
        if 'erro' in result:
            return jsonify({'status': 'error', 'message': result['erro']}), 400
        return jsonify({'status': 'success', 'message': 'Usuário atualizado com sucesso'})
        
    except Exception as e:
        print(f"[ERROR] Exceção ao atualizar usuário {id}: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        db.close()

@flask_app.route('/api/usuarios/<int:id>', methods=['DELETE'])
def deletar_usuario(id):
    db = Database()
    try:
        result = db.deletar_usuario(id)
        if 'erro' in result:
            return jsonify({'status': 'error', 'message': result['erro']}), 404
        return jsonify({'status': 'success', 'message': 'Usuário excluído com sucesso'})
    except Exception as e:
        print(f"[ERROR] Exceção ao deletar usuário {id}: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        db.close()

@flask_app.route('/api/user-session', methods=['GET'])
def get_user_session():
    """Retorna dados do usuário logado na sessão"""
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'Usuário não logado'}), 401
    
    return jsonify({
        'status': 'success',
        'user': {
            'id': session['user_id'],
            'nome': session['user_name'],
            'email': session['user_email'],
            'cargo': session['user_cargo'],
            'nivel_de_acesso': session['user_nivel_acesso']
        }
    }), 200

@flask_app.route('/api/usuario-atual', methods=['GET'])
def get_current_user():
    """Retorna o usuário atualmente logado"""
    return get_user_session()

@flask_app.route('/api/debug-log', methods=['POST'])
def debug_log():
    """Recebe logs do frontend e exibe no terminal Flask"""
    try:
        data = request.json
        message = data.get('message', '')
        level = data.get('level', 'INFO')
        source = data.get('source', 'FRONTEND')
        
        # Cores para diferentes níveis de log
        colors = {
            'INFO': '\033[94m',      # Azul
            'SUCCESS': '\033[92m',   # Verde
            'WARNING': '\033[93m',   # Amarelo
            'ERROR': '\033[91m',     # Vermelho
            'DEBUG': '\033[95m'      # Magenta
        }
        
        reset_color = '\033[0m'
        color = colors.get(level, '\033[97m')  # Branco como padrão
        
        # Timestamp
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        # Imprimir no terminal Flask com cores
        print(f"{color}[{timestamp}] {source} - {level}: {message}{reset_color}")
        
        return jsonify({'status': 'success'}), 200
    
    except Exception as e:
        print(f"\033[91m[FLASK] ERRO no debug-log: {str(e)}\033[0m")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@flask_app.route('/api/user-photo/<int:user_id>', methods=['GET'])
def get_user_photo(user_id):
    """Retorna a foto do usuário como base64"""
    try:
        db = Database()
        
        # Buscar a foto do usuário
        db.cursor.execute("SELECT foto_de_perfil FROM usuarios WHERE id = %s", (user_id,))
        result = db.cursor.fetchone()
        
        db.close()
        
        if result:
            foto_blob = result['foto_de_perfil']
            if foto_blob:
                # Converter blob para base64
                import base64
                foto_base64 = base64.b64encode(foto_blob).decode('utf-8')
                return jsonify({
                    'status': 'success',
                    'photo': f"data:image/jpeg;base64,{foto_base64}"
                })
            else:
                return jsonify({
                    'status': 'error',
                    'message': 'Usuário não possui foto'
                }), 404
        else:
            return jsonify({
                'status': 'error',
                'message': 'Usuário não encontrado'
            }), 404
            
    except Exception as e:
        print(f"[ERROR] Erro ao buscar foto do usuário {user_id}: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Erro interno do servidor'
        }), 500

@flask_app.route('/debug/usuarios', methods=['GET'])
def debug_usuarios():
    """Rota temporária para debugar usuários no banco"""
    db = Database()
    try:
        db.cursor.execute("SELECT id, nome, email, cargo FROM usuarios")
        usuarios = db.cursor.fetchall()
        
        print(f"[DEBUG] Total de usuários no banco: {len(usuarios)}")
        for usuario in usuarios:
            print(f"[DEBUG] ID: {usuario['id']}, Nome: {usuario['nome']}, Email: {usuario['email']}, Cargo: {usuario['cargo']}")
            
        return jsonify({
            'status': 'success',
            'total': len(usuarios),
            'usuarios': usuarios
        })
    except Exception as e:
        print(f"[ERROR] Erro ao buscar usuários: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        db.close()

@flask_app.route('/api/itens_estoque', methods=['POST'])
def criar_item_estoque():
    try:
        # Debug: imprimir todos os dados recebidos
        print("=== DEBUG: Dados recebidos no formulário ===")
        for key, value in request.form.items():
            print(f"{key}: {value}")
        print("=== FIM DEBUG ===")
        
        nome = request.form.get('itemName')
        codigo = request.form.get('itemCode')
        categoria_id = request.form.get('itemCategory')  # Agora é o ID da categoria
        tipo_item_id = request.form.get('itemTipoItem')
        cor = request.form.get('itemColor')
        quantidade_inicial = float(request.form.get('itemInitialQuantity', 0))
        estoque_minimo = float(request.form.get('itemMinStock', 0))
        unidades_por_pacote = request.form.get('itemUnidades')
        unidade_medida_id = request.form.get('itemUnit')  # Agora é o ID da unidade de medida
        fornecedor_id = request.form.get('itemSupplier')  # Agora é o ID do fornecedor
        localizacao_estoque = request.form.get('itemLocation')
        especificacoes_tecnicas = request.form.get('itemTechSpecs')
        descricao = request.form.get('itemDescription')
        
        # Get dimension and weight fields
        largura = request.form.get('itemLargura')
        comprimento = request.form.get('itemComprimento')
        espessura = request.form.get('itemEspessura')
        volume = request.form.get('itemVolume')
        peso = request.form.get('itemPeso')
        
        # Convert fields to appropriate types if provided
        largura = float(largura) if largura else None
        comprimento = float(comprimento) if comprimento else None
        espessura = float(espessura) if espessura else None
        
        # Convert volume to milliliters (integer)
        if volume:
            # Handle decimal separator - replace comma with dot for proper float conversion
            volume_str = str(volume).replace(',', '.')
            # Remove any non-numeric characters except decimal point
            volume_cleaned = ''.join(c for c in volume_str if c.isdigit() or c == '.')
            if volume_cleaned:
                volume_value = float(volume_cleaned)
                # Check if the original input had "L" or similar indicating liters
                original_volume = str(request.form.get('itemVolume', '')).upper()
                if 'L' in original_volume and 'ML' not in original_volume:
                    # Convert liters to milliliters - keep precision
                    volume = int(volume_value * 1000)
                else:
                    # Assume already in milliliters
                    volume = int(volume_value)
            else:
                volume = None
        else:
            volume = None
            
        peso = float(peso) if peso else None
        tipo_item_id = int(tipo_item_id) if tipo_item_id else None
        unidades_por_pacote = int(unidades_por_pacote) if unidades_por_pacote else None
        categoria_id = int(categoria_id) if categoria_id else None
        unidade_medida_id = int(unidade_medida_id) if unidade_medida_id else None
        fornecedor_id = int(fornecedor_id) if fornecedor_id else None

        # Capturar campo fabricante
        fabricante = request.form.get('itemFabricante')

        # Debug: imprimir valores processados
        print("=== DEBUG: Valores processados ===")
        print(f"nome: {nome}")
        print(f"codigo: {codigo}")
        print(f"categoria_id: {categoria_id}")
        print(f"tipo_item_id: {tipo_item_id}")
        print(f"unidades_por_pacote: {unidades_por_pacote}")
        print(f"espessura: {espessura}")
        print(f"volume: {volume} (tipo: {type(volume)})")
        print(f"volume original recebido: {request.form.get('itemVolume')}")
        print(f"unidade_medida_id: {unidade_medida_id}")
        print(f"fornecedor_id: {fornecedor_id}")
        print(f"fabricante: {fabricante}")
        print(f"especificacoes_tecnicas: {especificacoes_tecnicas}")
        print("=== FIM DEBUG ===")

        db = Database()
        resultado = db.criar_item_estoque(
            nome, codigo, categoria_id, cor, quantidade_inicial, estoque_minimo,
            unidade_medida_id, fornecedor_id, localizacao_estoque,
            especificacoes_tecnicas, descricao, largura, comprimento, peso,
            tipo_item_id, unidades_por_pacote, espessura, volume, None, fabricante
        )
        db.close()

        if "sucesso" in resultado:
            return jsonify({"status": "success", "message": resultado["sucesso"], "id": resultado["id"]})
        else:
            return jsonify({"status": "error", "message": resultado["erro"]}), 400

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@flask_app.route('/api/itens_estoque/lista', methods=['GET'])
def listar_itens_estoque():
    try:
        print("Iniciando busca de itens de estoque...")
        db = Database()
        itens = db.buscar_itens_estoque()
        print(f"Resultado da busca: {itens}")
        print(f"Tipo do resultado: {type(itens)}")
        db.close()

        if isinstance(itens, list):
            print(f"Lista encontrada com {len(itens)} itens")
            return jsonify({
                "status": "success",
                "items": [{
                    "id": item["id"],
                    "nome": item["nome"],
                    "codigo": item["codigo"]
                } for item in itens]
            })
        elif isinstance(itens, dict) and "erro" in itens:
            print(f"Erro encontrado: {itens['erro']}")
            return jsonify({"status": "error", "message": itens["erro"]}), 400
        else:
            print(f"Formato inesperado: {itens}")
            return jsonify({"status": "error", "message": "Formato de resposta inesperado"}), 500

    except Exception as e:
        print(f"Exceção capturada: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@flask_app.route('/api/entradas_estoque', methods=['POST'])
def criar_entrada_estoque():
    try:
        item_id = int(request.form.get('itemId'))
        quantidade = float(request.form.get('quantidade'))
        data_entrada = request.form.get('dataEntrada')
        fornecedor = request.form.get('fornecedor')
        nota_fiscal = request.form.get('notaFiscal')
        custo_unitario = request.form.get('custoUnitario')
        data_validade = request.form.get('dataValidade')
        lote = request.form.get('lote')
        localizacao = request.form.get('localizacao')
        observacoes = request.form.get('observacoes')
        
        # Convert custo_unitario to float if provided
        if custo_unitario:
            custo_unitario = custo_unitario.replace('R$', '').replace('.', '').replace(',', '.').strip()
            custo_unitario = float(custo_unitario) if custo_unitario else None

        db = Database()
        resultado = db.criar_entrada_estoque(item_id, quantidade, data_entrada, fornecedor, nota_fiscal, custo_unitario, data_validade, lote, localizacao, observacoes)
        db.close()

        if "sucesso" in resultado:
            return jsonify({"status": "success", "message": resultado["sucesso"], "id": resultado["id"]})
        else:
            return jsonify({"status": "error", "message": resultado["erro"]}), 400

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@flask_app.route('/api/saidas_estoque', methods=['POST'])
def criar_saida_estoque():
    try:
        item_id = int(request.form.get('itemId'))
        quantidade = float(request.form.get('quantidadeSaida'))
        data_saida = request.form.get('dataSaida')
        motivo_saida = request.form.get('motivoSaida')
        destino = request.form.get('destino')
        localizacao = request.form.get('localizacaoSaida')
        observacoes = request.form.get('observacoesSaida')

        db = Database()
        resultado = db.criar_saida_estoque(item_id, quantidade, data_saida, motivo_saida, destino, localizacao, observacoes)
        db.close()

        if "sucesso" in resultado:
            return jsonify({"status": "success", "message": resultado["sucesso"], "id": resultado["id"]})
        else:
            return jsonify({"status": "error", "message": resultado["erro"]}), 400

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@flask_app.route('/api/itens_estoque/<int:item_id>', methods=['DELETE'])
def deletar_item_estoque(item_id):
    db = Database()
    try:
        result = db.deletar_item_estoque(item_id)
        if 'erro' in result:
            return jsonify({'status': 'error', 'message': result['erro']}), 404
        return jsonify({'status': 'success', 'message': 'Item excluído com sucesso'})
    except Exception as e:
        print(f"[ERROR] Exceção ao deletar item {item_id}: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        db.close()

@flask_app.route('/api/itens_estoque/<int:item_id>', methods=['GET'])
def buscar_item_estoque_por_id(item_id):
    try:
        db = Database()
        item = db.buscar_item_estoque_por_id(item_id)
        db.close()

        if item and 'erro' not in item:
            return jsonify({"status": "success", "item": item})
        elif item and 'erro' in item:
            return jsonify({"status": "error", "message": item["erro"]}), 404
        else:
            return jsonify({"status": "error", "message": "Item não encontrado"}), 404

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@flask_app.route('/api/itens_estoque/<int:item_id>', methods=['PUT'])
def atualizar_item_estoque(item_id):
    try:
        nome = request.form.get('itemName')
        codigo = request.form.get('itemCode')
        categoria_id = request.form.get('itemCategory')  # Agora é o ID da categoria
        tipo_item_id = request.form.get('itemTipoItem')
        cor = request.form.get('itemColor')
        estoque_minimo = request.form.get('itemMinStock')
        unidades_por_pacote = request.form.get('itemUnidades')
        if estoque_minimo:
            estoque_minimo = float(estoque_minimo)
        unidade_medida_id = request.form.get('itemUnit')  # Agora é o ID da unidade de medida
        fornecedor_id = request.form.get('itemSupplier')  # Agora é o ID do fornecedor
        localizacao_estoque = request.form.get('itemLocation')
        especificacoes_tecnicas = request.form.get('itemTechSpecs')
        descricao = request.form.get('itemDescription')
        
        # Get dimension and weight fields
        largura = request.form.get('itemLargura')
        comprimento = request.form.get('itemComprimento')
        espessura = request.form.get('itemEspessura')
        volume = request.form.get('itemVolume')
        peso = request.form.get('itemPeso')
        
        # Convert fields to appropriate types if provided
        largura = float(largura) if largura else None
        comprimento = float(comprimento) if comprimento else None
        espessura = float(espessura) if espessura else None
        
        # Special handling for volume to prevent "10L" being converted to "10.000"
        if volume:
            # Remove any non-numeric characters except decimal point
            volume_cleaned = ''.join(c for c in str(volume) if c.isdigit() or c == '.')
            volume = float(volume_cleaned) if volume_cleaned else None
        else:
            volume = None
            
        peso = float(peso) if peso else None
        tipo_item_id = int(tipo_item_id) if tipo_item_id else None
        unidades_por_pacote = int(unidades_por_pacote) if unidades_por_pacote else None
        categoria_id = int(categoria_id) if categoria_id else None
        unidade_medida_id = int(unidade_medida_id) if unidade_medida_id else None
        fornecedor_id = int(fornecedor_id) if fornecedor_id else None

        # Capturar campo fabricante
        fabricante = request.form.get('itemFabricante')

        db = Database()
        resultado = db.atualizar_item_estoque(
            item_id, nome, codigo, categoria_id, cor, estoque_minimo,
            unidade_medida_id, fornecedor_id, localizacao_estoque,
            especificacoes_tecnicas, descricao,
            largura, comprimento, peso, tipo_item_id, 
            unidades_por_pacote, espessura, volume, None, fabricante
        )
        db.close()

        if "sucesso" in resultado:
            return jsonify({"status": "success", "message": resultado["sucesso"]})
        else:
            return jsonify({"status": "error", "message": resultado["erro"]}), 400

    except Exception as e:
        print(f"[ERROR] Exceção ao atualizar item {item_id}: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@flask_app.route('/api/itens_estoque/completo', methods=['GET'])
def listar_itens_estoque_completo():
    try:
        db = Database()
        itens = db.buscar_itens_estoque_completo()
        db.close()

        if isinstance(itens, list):
            # Debug: verificar se is_measurement está presente
            if len(itens) > 0:
                print(f"[DEBUG] Primeiro item da lista completa: {itens[0]}")
                print(f"[DEBUG] Keys do primeiro item: {list(itens[0].keys()) if itens[0] else 'None'}")
            
            return jsonify(
                {
                    "status": "success",
                    "items": itens
                }
            )
        else:
            return jsonify({"status": "error", "message": itens["erro"]}), 400

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@flask_app.route('/api/categorias', methods=['POST'])
def criar_categoria():
    try:
        data = request.get_json()
        nome_categoria = data.get('nome')

        if not nome_categoria:
            return jsonify({'status': 'error', 'message': 'Nome da categoria é obrigatório'}), 400

        db = Database()
        resultado = db.criar_categoria_item_estoque(nome_categoria)
        db.close()

        if 'erro' in resultado:
            return jsonify({'status': 'error', 'message': resultado['erro']}), 400
        return jsonify({'status': 'success', 'message': 'Categoria criada com sucesso', 'id': resultado['id']}), 201

    except Exception as e:
        print(f"[ERROR] Exceção na API /api/categorias POST: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@flask_app.route('/api/categorias', methods=['GET'])
def listar_categorias():
    try:
        db = Database()
        categorias = db.listar_categorias_itens_estoque()
        db.close()

        if 'erro' in categorias:
            return jsonify({'status': 'error', 'message': categorias['erro']}), 500
        
        return jsonify({'status': 'success', 'categorias': categorias}), 200

    except Exception as e:
        print(f"[ERROR] Exceção na API /api/categorias GET: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@flask_app.route('/api/fornecedores', methods=['POST'])
def criar_fornecedor():
    try:
        dados = request.form
        nome = dados.get('nome')
        cnpj = dados.get('cnpj')
        telefone = dados.get('telefone')
        email = dados.get('email')
        endereco = dados.get('endereco')
        cidade = dados.get('cidade')
        estado = dados.get('estado')
        cep = dados.get('cep')
        contato_nome = dados.get('contato_nome')
        contato_telefone = dados.get('contato_telefone')
        contato_email = dados.get('contato_email')
        website = dados.get('website')
        categoria_produtos = dados.get('categoria_produtos')
        prazo_entrega = dados.get('prazo_entrega')
        condicoes_pagamento = dados.get('condicoes_pagamento')
        observacoes = dados.get('observacoes')
        status = dados.get('status', 'Ativo')
        
        if not nome:
            return jsonify({"erro": "Nome do fornecedor é obrigatório"}), 400
        
        db = Database()
        resultado = db.criar_fornecedor(
            nome=nome, cnpj=cnpj, telefone=telefone, email=email, endereco=endereco,
            cidade=cidade, estado=estado, cep=cep, contato_nome=contato_nome,
            contato_telefone=contato_telefone, contato_email=contato_email, website=website,
            categoria_produtos=categoria_produtos, prazo_entrega=prazo_entrega,
            condicoes_pagamento=condicoes_pagamento, observacoes=observacoes, status=status
        )
        db.close()
        
        if 'erro' in resultado:
            return jsonify(resultado), 400
        return jsonify(resultado), 201
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@flask_app.route('/api/fornecedores', methods=['GET'])
def listar_fornecedores():
    try:
        db = Database()
        fornecedores = db.listar_fornecedores()
        db.close()
        
        if isinstance(fornecedores, dict) and 'erro' in fornecedores:
            return jsonify(fornecedores), 400
        return jsonify(fornecedores), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@flask_app.route('/api/fornecedores/<int:fornecedor_id>', methods=['GET'])
def buscar_fornecedor(fornecedor_id):
    try:
        db = Database()
        fornecedor = db.buscar_fornecedor_por_id(fornecedor_id)
        db.close()
        
        if isinstance(fornecedor, dict) and 'erro' in fornecedor:
            return jsonify(fornecedor), 404
        return jsonify(fornecedor), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@flask_app.route('/api/fornecedores/<int:fornecedor_id>', methods=['PUT'])
def atualizar_fornecedor(fornecedor_id):
    try:
        dados = request.form
        
        db = Database()
        resultado = db.atualizar_fornecedor(
            fornecedor_id=fornecedor_id,
            nome=dados.get('nome'),
            cnpj=dados.get('cnpj'),
            telefone=dados.get('telefone'),
            email=dados.get('email'),
            endereco=dados.get('endereco'),
            cidade=dados.get('cidade'),
            estado=dados.get('estado'),
            cep=dados.get('cep'),
            contato_nome=dados.get('contato_nome'),
            contato_telefone=dados.get('contato_telefone'),
            contato_email=dados.get('contato_email'),
            website=dados.get('website'),
            categoria_produtos=dados.get('categoria_produtos'),
            prazo_entrega=dados.get('prazo_entrega'),
            condicoes_pagamento=dados.get('condicoes_pagamento'),
            observacoes=dados.get('observacoes'),
            status=dados.get('status')
        )
        db.close()
        
        if 'erro' in resultado:
            return jsonify(resultado), 400
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@flask_app.route('/api/fornecedores/<int:fornecedor_id>', methods=['DELETE'])
def deletar_fornecedor(fornecedor_id):
    try:
        db = Database()
        resultado = db.deletar_fornecedor(fornecedor_id)
        db.close()
        
        if 'erro' in resultado:
            return jsonify(resultado), 400
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

# ==================== ROTAS PWA ====================

@flask_app.route('/manifest.json')
def manifest():
    """Serve o manifest PWA"""
    return flask_app.send_static_file('manifest.json'), 200, {
        'Content-Type': 'application/manifest+json',
        'Cache-Control': 'public, max-age=604800'  # 1 semana
    }

@flask_app.route('/sw.js')
def service_worker():
    """Serve o service worker"""
    return flask_app.send_static_file('sw.js'), 200, {
        'Content-Type': 'application/javascript',
        'Cache-Control': 'no-cache'  # Service worker não deve ser cacheado
    }

@flask_app.route('/offline')
def offline():
    """Página offline para PWA"""
    return render_template('offline.html')

@flask_app.route('/api/health')
def health_check():
    """Endpoint para verificar se o servidor está funcionando"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }), 200

# ==================== FIM ROTAS PWA ====================

@flask_app.route('/pdv')
def pdv():
    # Verificar autenticação
    auth_check = require_login()
    if auth_check:
        return auth_check
    
    return render_template('pdv.html')

@flask_app.route('/test-pdv')
def test_pdv():
    """Rota de teste para debugar carregamento de produtos no iPad"""
    return render_template('test_pdv_load.html')

@flask_app.route('/clientes')
def clientes():
    return render_template('clientes.html')

@flask_app.route('/api/clientes', methods=['POST'])
def criar_cliente():
    try:
        # Aceita tanto form data quanto JSON
        if request.content_type and 'application/json' in request.content_type:
            dados = request.get_json()
        else:
            dados = request.form
            
        nome = dados.get('nome')
        tipo_pessoa = dados.get('tipo_pessoa', 'Fisica')  # Default para Fisica
        cpf_cnpj = dados.get('cpf_cnpj')
        telefone = dados.get('telefone')
        whatsapp = dados.get('whatsapp')
        email = dados.get('email')
        endereco = dados.get('endereco')
        bairro = dados.get('bairro')
        cidade = dados.get('cidade')
        estado = dados.get('estado')
        pais = dados.get('pais')
        cep = dados.get('cep')
        observacoes = dados.get('observacoes')
        status = dados.get('status', 'Ativo')
        
        if not nome or not email:
            return jsonify({"erro": "Nome e email do cliente são obrigatórios"}), 400
        
        db = Database()
        resultado = db.criar_cliente(
            nome=nome, tipo_pessoa=tipo_pessoa, cpf_cnpj=cpf_cnpj, telefone=telefone, whatsapp=whatsapp, email=email,
            endereco=endereco, bairro=bairro, cidade=cidade, estado=estado, pais=pais, cep=cep, observacoes=observacoes,
            status=status
        )
        db.close()
        
        if 'erro' in resultado:
            return jsonify(resultado), 400
        return jsonify(resultado), 201
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@flask_app.route('/api/clientes', methods=['GET'])
def listar_clientes():
    try:
        db = Database()
        clientes_list = db.listar_clientes()
        db.close()
        
        if isinstance(clientes_list, dict) and 'erro' in clientes_list:
            return jsonify(clientes_list), 400
        
        # Verificar se já são dicionários ou precisam ser formatados
        if clientes_list and isinstance(clientes_list[0], dict):
            # Já são dicionários, usar diretamente
            clientes_formatados = clientes_list
        else:
            # São tuplas, formatar para dicionários
            clientes_formatados = []
            for cliente in clientes_list:
                clientes_formatados.append({
                    'id': cliente[0],
                    'nome': cliente[1],
                    'tipo_pessoa': cliente[2],
                    'cpf_cnpj': cliente[3],
                    'telefone': cliente[4],
                    'whatsapp': cliente[5],
                    'email': cliente[6],
                    'bairro': cliente[7],
                    'status': cliente[8]
                })
        
        return jsonify({
            'status': 'success',
            'clientes': clientes_formatados
        }), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@flask_app.route('/api/clientes/<int:cliente_id>', methods=['GET'])
def buscar_cliente(cliente_id):
    try:
        db = Database()
        cliente = db.buscar_cliente_por_id(cliente_id)
        db.close()
        
        if isinstance(cliente, dict) and 'erro' in cliente:
            return jsonify(cliente), 404
        return jsonify(cliente), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@flask_app.route('/api/clientes/<int:cliente_id>', methods=['PUT'])
def atualizar_cliente(cliente_id):
    try:
        # Aceita tanto form data quanto JSON
        if request.content_type and 'application/json' in request.content_type:
            dados = request.get_json()
        else:
            dados = request.form
        
        db = Database()
        resultado = db.atualizar_cliente(
            cliente_id=cliente_id,
            nome=dados.get('nome'),
            tipo_pessoa=dados.get('tipo_pessoa'),
            cpf_cnpj=dados.get('cpf_cnpj'),
            telefone=dados.get('telefone'),
            whatsapp=dados.get('whatsapp'),
            email=dados.get('email'),
            endereco=dados.get('endereco'),
            bairro=dados.get('bairro'),
            cidade=dados.get('cidade'),
            estado=dados.get('estado'),
            pais=dados.get('pais'),
            cep=dados.get('cep'),
            observacoes=dados.get('observacoes'),
            status=dados.get('status')
        )
        db.close()
        
        if 'erro' in resultado:
            return jsonify(resultado), 400
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@flask_app.route('/api/clientes/<int:cliente_id>', methods=['DELETE'])
def deletar_cliente(cliente_id):
    try:
        db = Database()
        resultado = db.deletar_cliente(cliente_id)
        db.close()
        
        if 'erro' in resultado:
            return jsonify(resultado), 400
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@flask_app.route('/api/unidades_de_medida', methods=['POST'])
def criar_unidade_medida():
    try:
        data = request.get_json()
        nome_unidade = data.get('nome')
        is_measurement = data.get('is_measurement', 0) # Default to 0 if not provided

        if not nome_unidade:
            return jsonify({'status': 'error', 'message': 'Nome da unidade é obrigatório'}), 400

        db = Database()
        resultado = db.criar_unidade_medida(nome_unidade, is_measurement)
        db.close()

        if 'erro' in resultado:
            return jsonify({'status': 'error', 'message': resultado['erro']}), 400
        return jsonify({'status': 'success', 'message': 'Unidade de medida criada com sucesso', 'id': resultado['id']}), 201

    except Exception as e:
        print(f"[ERROR] Exceção na API /api/unidades_de_medida POST: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@flask_app.route('/api/unidades_de_medida', methods=['GET'])
def listar_unidades_medida():
    try:
        db = Database()
        unidades = db.listar_unidades_medida()
        db.close()

        if isinstance(unidades, dict) and 'erro' in unidades:
            return jsonify({'status': 'error', 'message': unidades['erro']}), 500
        
        print(f"[DEBUG] Unidades retornadas pela database: {unidades}")
        
        return jsonify({'status': 'success', 'unidades': unidades}), 200

    except Exception as e:
        print(f"[ERROR] Exceção na API /api/unidades_de_medida GET: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@flask_app.route('/api/tipo_itens', methods=['POST'])
def criar_tipo_item():
    try:
        data = request.get_json()
        nome = data.get('nome')
        descricao = data.get('descricao', '')

        if not nome:
            return jsonify({'status': 'error', 'message': 'Nome do tipo é obrigatório'}), 400

        db = Database()
        resultado = db.criar_tipo_item(nome, descricao)
        db.close()

        if 'erro' in resultado:
            return jsonify({'status': 'error', 'message': resultado['erro']}), 400
        return jsonify({'status': 'success', 'message': 'Tipo de item criado com sucesso', 'id': resultado['id']}), 201

    except Exception as e:
        print(f"[ERROR] Exceção na API /api/tipo_itens POST: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@flask_app.route('/api/tipo_itens', methods=['GET'])
def listar_tipos_itens():
    try:
        db = Database()
        tipos = db.listar_tipos_itens()
        db.close()

        if isinstance(tipos, dict) and 'erro' in tipos:
            return jsonify({'status': 'error', 'message': tipos['erro']}), 500
        
        return jsonify({'status': 'success', 'tipos': tipos}), 200

    except Exception as e:
        print(f"[ERROR] Exceção na API /api/tipo_itens GET: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@flask_app.route('/api/notificacoes/baixo-estoque', methods=['GET'])
def verificar_baixo_estoque():
    try:
        db = Database()
        itens_baixo_estoque = db.verificar_itens_baixo_estoque()

        if isinstance(itens_baixo_estoque, dict) and 'erro' in itens_baixo_estoque:
            return jsonify({"status": "error", "message": itens_baixo_estoque['erro']}), 500

        notificacoes = []
        for item in itens_baixo_estoque:
            mensagem = f"O item '{item['nome']}' está com estoque baixo. Quantidade atual: {item['quantidade_atual']}"
            resultado = db.criar_notificacao("baixo_estoque", mensagem, item['id'])
            
            if 'sucesso' in resultado:
                notificacoes.append({
                    "item_id": item['id'],
                    "nome": item['nome'],
                    "quantidade_atual": item['quantidade_atual'],
                    "estoque_minimo": item['estoque_minimo']
                })

        db.close()
        return jsonify({"status": "success", "notificacoes": notificacoes})

    except Exception as e:
        print(f"[ERROR] Exceção ao verificar estoque baixo: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@flask_app.route('/api/estoque/check_low_stock', methods=['GET'])
def check_low_stock():
    """Rota alternativa para verificar estoque baixo (compatibilidade com dashboard)"""
    try:
        db = Database()
        itens_baixo_estoque = db.verificar_itens_baixo_estoque()
        db.close()

        if isinstance(itens_baixo_estoque, dict) and 'erro' in itens_baixo_estoque:
            return jsonify({"status": "error", "message": itens_baixo_estoque['erro']}), 500

        return jsonify({"status": "success", "items": itens_baixo_estoque})

    except Exception as e:
        print(f"[ERROR] Exceção ao verificar estoque baixo: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@flask_app.route('/api/notificacoes', methods=['GET'])
def listar_notificacoes():
    try:
        db = Database()
        notificacoes = db.listar_notificacoes()
        db.close()

        if isinstance(notificacoes, dict) and 'erro' in notificacoes:
            return jsonify({"status": "error", "message": notificacoes['erro']}), 500

        return jsonify({"status": "success", "notificacoes": notificacoes})

    except Exception as e:
        print(f"[ERROR] Exceção ao listar notificações: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@flask_app.route('/api/notificacoes/marcar-como-lida/<int:notificacao_id>', methods=['PUT'])
def marcar_notificacao_como_lida(notificacao_id):
    try:
        db = Database()
        resultado = db.marcar_notificacao_como_lida(notificacao_id)
        db.close()

        if 'erro' in resultado:
            return jsonify({"status": "error", "message": resultado['erro']}), 400

        return jsonify({"status": "success", "message": resultado['sucesso']})

    except Exception as e:
        print(f"[ERROR] Exceção ao marcar notificação como lida: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@flask_app.route('/entradas_estoque')
def entradas_estoque():
    return render_template('entrada_estoque.html')

@flask_app.route('/<template_name>')
def render_page(template_name):
    try:
        # Ensure template name ends with .html
        if not template_name.endswith('.html'):
            template_name += '.html'
        return render_template(template_name)
    except Exception as e:
        # Log the error and return a 404 if template not found
        print(f"Error rendering template {template_name}: {e}")
        from flask import abort
        abort(404)

@flask_app.route('/api/entradas_estoque', methods=['GET'])
def listar_entradas():
    try:
        db = Database()
        entradas = db.listar_entradas_estoque()
        db.close()

        if isinstance(entradas, list):
            # Serializar manualmente para evitar referências circulares
            entradas_safe = []
            for entrada in entradas:
                entrada_dict = {
                    'id': entrada.get('id'),
                    'item_id': entrada.get('item_id'),
                    'item_nome': entrada.get('item_nome'),
                    'quantidade': float(entrada.get('quantidade')) if entrada.get('quantidade') else None,
                    'custo_unitario': float(entrada.get('custo_unitario')) if entrada.get('custo_unitario') else None,
                    'custo_total': float(entrada.get('custo_total')) if entrada.get('custo_total') else None,
                    'data_entrada': str(entrada.get('data_entrada')) if entrada.get('data_entrada') else None,
                    'responsavel': entrada.get('responsavel'),
                    'fornecedor_id': entrada.get('fornecedor_id'),
                    'fornecedor_nome': entrada.get('fornecedor_nome'),
                    'observacoes': entrada.get('observacoes')
                }
                entradas_safe.append(entrada_dict)
            
            return jsonify({"status": "success", "entradas": entradas_safe})
        else:
            return jsonify({"status": "error", "message": "Erro ao buscar entradas"}), 500

    except Exception as e:
        print(f"[ERROR] Exceção ao listar entradas: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@flask_app.route('/api/categoria_produtos', methods=['POST'])
def criar_categoria_produto():
    try:
        data = request.get_json()
        nome = data.get('nome')
        descricao = data.get('descricao', '')

        if not nome:
            return jsonify({'status': 'error', 'message': 'Nome da categoria é obrigatório'}), 400

        db = Database()
        resultado = db.criar_categoria_produto(nome, descricao)
        db.close()

        if 'erro' in resultado:
            return jsonify({'status': 'error', 'message': resultado['erro']}), 400
        return jsonify({'status': 'success', 'message': 'Categoria criada com sucesso', 'id': resultado['id']}), 201

    except Exception as e:
        print(f"[ERROR] Exceção na API /api/categoria_produtos POST: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@flask_app.route('/api/categoria_produtos', methods=['GET'])
def listar_categorias_produtos():
    try:
        db = Database()
        categorias = db.listar_categorias_produtos()
        db.close()

        if isinstance(categorias, dict) and 'erro' in categorias:
            return jsonify({'status': 'error', 'message': categorias['erro']}), 500
        
        return jsonify({'status': 'success', 'categorias': categorias}), 200

    except Exception as e:
        print(f"[ERROR] Exceção na API /api/categoria_produtos GET: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@flask_app.route('/api/usuarios/ativos', methods=['GET'])
def listar_usuarios_ativos():
    try:
        db = Database()
        usuarios = db.buscar_usuarios_ativos()
        db.close()

        if isinstance(usuarios, dict) and 'erro' in usuarios:
            return jsonify({'status': 'error', 'message': usuarios['erro']}), 500
        
        return jsonify({'status': 'success', 'usuarios': usuarios}), 200

    except Exception as e:
        print(f"[ERROR] Exceção na API /api/usuarios/ativos GET: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@flask_app.route('/api/favoritos', methods=['POST'])
def adicionar_favorito():
    try:
        print("[DEBUG] Iniciando adição de favorito")
        data = request.get_json()
        print(f"[DEBUG] Dados recebidos: {data}")
        
        usuario_id = data.get('usuario_id')
        produto_id = data.get('produto_id')

        if not usuario_id or not produto_id:
            print("[ERROR] Usuário ou produto não fornecidos")
            return jsonify({'status': 'error', 'message': 'Usuário e produto são obrigatórios'}), 400

        action = data.get('action', 'add')
        
        db = Database()
        
        if action == 'add':
            print(f"[DEBUG] Adicionando favorito - Usuário: {usuario_id}, Produto: {produto_id}")
            resultado = db.adicionar_favorito(usuario_id, produto_id)
            print(f"[DEBUG] Resultado da operação: {resultado}")
            
            if 'erro' in resultado and "já está nos favoritos" in resultado['erro']:
                # Se já está nos favoritos, considerar como sucesso
                print("[DEBUG] Produto já estava nos favoritos - considerando como sucesso")
                db.close()
                return jsonify({'status': 'success', 'message': 'Produto já está nos favoritos'}), 200
            elif 'erro' in resultado:
                print(f"[ERROR] Erro ao adicionar favorito: {resultado['erro']}")
                db.close()
                return jsonify({'status': 'error', 'message': resultado['erro']}), 400
                
        elif action == 'remove':
            print(f"[DEBUG] Removendo favorito - Usuário: {usuario_id}, Produto: {produto_id}")
            resultado = db.remover_favorito(usuario_id, produto_id)
            print(f"[DEBUG] Resultado da operação: {resultado}")
            
            if 'erro' in resultado:
                print(f"[ERROR] Erro ao remover favorito: {resultado['erro']}")
                db.close()
                return jsonify({'status': 'error', 'message': resultado['erro']}), 400
        
        db.close()
        return jsonify({'status': 'success', 'message': resultado.get('sucesso', 'Operação realizada com sucesso')}), 200

    except Exception as e:
        print(f"[ERROR] Exceção na API /api/favoritos POST: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@flask_app.route('/api/favoritos/<int:usuario_id>', methods=['GET'])
def listar_favoritos(usuario_id):
    try:
        print(f"[DEBUG] Listando favoritos para usuário {usuario_id}")
        db = Database()
        favoritos = db.listar_favoritos(usuario_id)
        db.close()

        if isinstance(favoritos, dict) and 'erro' in favoritos:
            print(f"[ERROR] Erro ao listar favoritos: {favoritos['erro']}")
            return jsonify({'status': 'error', 'message': favoritos['erro']}), 500
        
        # Garantir que favoritos seja sempre uma lista
        if not isinstance(favoritos, list):
            favoritos = []
            
        print(f"[DEBUG] Favoritos encontrados: {favoritos}")
        return jsonify({'status': 'success', 'favoritos': favoritos}), 200

    except Exception as e:
        print(f"[ERROR] Exceção na API /api/favoritos GET: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@flask_app.route('/api/favoritos/<int:usuario_id>/<int:produto_id>', methods=['DELETE'])
def remover_favorito(usuario_id, produto_id):
    try:
        print(f"[DEBUG] Removendo favorito - Usuário: {usuario_id}, Produto: {produto_id}")
        db = Database()
        resultado = db.remover_favorito(usuario_id, produto_id)
        print(f"[DEBUG] Resultado da remoção: {resultado}")
        db.close()

        if 'erro' in resultado:
            print(f"[ERROR] Erro ao remover favorito: {resultado['erro']}")
            return jsonify({'status': 'error', 'message': resultado['erro']}), 500
        
        return jsonify({'status': 'success', 'message': resultado['sucesso']}), 200

    except Exception as e:
        print(f"[ERROR] Exceção na API /api/favoritos DELETE: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@flask_app.route('/api/favoritos/<int:usuario_id>/produtos', methods=['GET'])
def listar_produtos_favoritos(usuario_id):
    try:
        print(f"[DEBUG] Listando produtos favoritos para usuário {usuario_id}")
        db = Database()
        favoritos = db.listar_favoritos(usuario_id)
        db.close()

        if isinstance(favoritos, dict) and 'erro' in favoritos:
            print(f"[ERROR] Erro ao listar produtos favoritos: {favoritos['erro']}")
            return jsonify({'status': 'error', 'message': favoritos['erro']}), 500
        
        # Garantir que favoritos seja sempre uma lista
        if not isinstance(favoritos, list):
            favoritos = []
            
        # Converter para o formato esperado pelo PDV
        produtos_favoritos = []
        for fav in favoritos:
            produto = {
                'produto_id': fav['produto_id'] if isinstance(fav, dict) else fav[0],  # Usar produto_id em vez de id
                'nome': fav['nome'] if isinstance(fav, dict) else fav[1],
                'codigo': fav['codigo'] if isinstance(fav, dict) else fav[2],
                'preco': fav['preco'] if isinstance(fav, dict) else fav[3],
                'estoque': fav['estoque'] if isinstance(fav, dict) else fav[4]
            }
            produtos_favoritos.append(produto)
            
        print(f"[DEBUG] Produtos favoritos encontrados: {len(produtos_favoritos)}")
        return jsonify({'status': 'success', 'produtos': produtos_favoritos}), 200

    except Exception as e:
        print(f"[ERROR] Exceção na API /api/favoritos/produtos GET: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@flask_app.route('/api/vendas', methods=['POST'])
def criar_venda():
    try:
        data = request.get_json()
        print(f"[DEBUG] Dados da venda recebidos: {data}")
        
        # Validar dados obrigatórios
        if not data.get('itens') or len(data['itens']) == 0:
            return jsonify({'status': 'error', 'message': 'Nenhum item na venda'}), 400
        
        if not data.get('metodo_pagamento'):
            return jsonify({'status': 'error', 'message': 'Método de pagamento é obrigatório'}), 400
        
        # Preparar dados da venda
        venda_data = {
            'usuario_id': data.get('usuario_id'),
            'subtotal': float(data.get('subtotal', 0)),
            'desconto': float(data.get('desconto', 0)),
            'total': float(data.get('total', 0)),
            'metodo_pagamento': data.get('metodo_pagamento'),
            'parcelas': int(data.get('parcelas', 1)),
            'itens': data.get('itens', [])
        }
        
        # Adicionar observações para pagamento em dinheiro
        observacoes = []
        if data.get('valor_recebido') and data.get('metodo_pagamento') == 'dinheiro':
            valor_recebido = float(data.get('valor_recebido'))
            troco = float(data.get('troco', 0))
            observacoes.append(f"Valor recebido: R$ {valor_recebido:.2f}")
            if troco > 0:
                observacoes.append(f"Troco: R$ {troco:.2f}")
        
        venda_data['observacoes'] = '; '.join(observacoes) if observacoes else None
        
        # Validar parcelas para crédito
        if venda_data['metodo_pagamento'] == 'credito' and (venda_data['parcelas'] < 1 or venda_data['parcelas'] > 12):
            return jsonify({'status': 'error', 'message': 'Número de parcelas inválido (1-12)'}), 400
        
        # Se não for crédito, forçar parcelas = 1
        if venda_data['metodo_pagamento'] != 'credito':
            venda_data['parcelas'] = 1
        
        db = Database()
        resultado = db.criar_venda(venda_data)
        db.close()
        
        if 'erro' in resultado:
            print(f"[ERROR] Erro ao criar venda: {resultado['erro']}")
            return jsonify({'status': 'error', 'message': resultado['erro']}), 500
        
        print(f"[DEBUG] Venda criada com sucesso: ID {resultado['id']}")
        return jsonify({'status': 'success', 'message': resultado['sucesso'], 'venda_id': resultado['id']}), 201
    
    except Exception as e:
        print(f"[ERROR] Exceção na API /api/vendas POST: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@flask_app.route('/api/vendas', methods=['GET'])
def listar_vendas():
    try:
        # Obter parâmetros de filtro
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        usuario_id = request.args.get('usuario_id')
        
        print(f"[DEBUG] Listando vendas - data_inicio: {data_inicio}, data_fim: {data_fim}, usuario_id: {usuario_id}")
        
        db = Database()
        vendas = db.listar_vendas(data_inicio=data_inicio, data_fim=data_fim, usuario_id=usuario_id)
        db.close()
        
        if isinstance(vendas, dict) and 'erro' in vendas:
            print(f"[ERROR] Erro ao listar vendas: {vendas['erro']}")
            return jsonify({'status': 'error', 'message': vendas['erro']}), 500
        
        print(f"[DEBUG] Vendas encontradas: {len(vendas)}")
        return jsonify({'status': 'success', 'vendas': vendas}), 200
    
    except Exception as e:
        print(f"[ERROR] Exceção na API /api/vendas GET: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@flask_app.route('/api/vendas/<int:venda_id>', methods=['GET'])
def buscar_venda(venda_id):
    try:
        print(f"[DEBUG] Buscando venda ID: {venda_id}")
        
        db = Database()
        venda = db.buscar_venda_por_id(venda_id)
        db.close()
        
        if isinstance(venda, dict) and 'erro' in venda:
            print(f"[ERROR] Erro ao buscar venda: {venda['erro']}")
            return jsonify({'status': 'error', 'message': venda['erro']}), 500
        
        if not venda:
            return jsonify({'status': 'error', 'message': 'Venda não encontrada'}), 404
        
        print(f"[DEBUG] Venda encontrada: {venda['id']}")
        return jsonify({'status': 'success', 'venda': venda}), 200
    
    except Exception as e:
        print(f"[ERROR] Exceção na API /api/vendas/{venda_id} GET: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@flask_app.route('/api/produtos', methods=['GET'])
def listar_produtos():
    try:
        # Obter parâmetros de busca
        nome = request.args.get('nome', '').strip()
        categoria = request.args.get('categoria', '').strip()
        
        print(f"[DEBUG] Buscando produtos - nome: '{nome}', categoria: '{categoria}'")
        
        db = Database()
        
        # Se há parâmetros de busca, usar a função de busca com filtros
        if nome or (categoria and categoria.lower() != 'all'):
            print(f"[DEBUG] Usando busca com filtros")
            produtos = db.buscar_produtos_com_filtros(nome=nome, categoria=categoria)
        else:
            print(f"[DEBUG] Usando busca sem filtros")
            produtos = db.listar_produtos()
            
        db.close()

        print(f"[DEBUG] Total de produtos encontrados: {len(produtos) if isinstance(produtos, list) else 'erro'}")

        if isinstance(produtos, dict) and 'erro' in produtos:
            print(f"[ERROR] Erro ao buscar produtos: {produtos['erro']}")
            return jsonify({'status': 'error', 'message': produtos['erro']}), 500
        
        # Serializar manualmente para evitar referências circulares
        if isinstance(produtos, list):
            produtos_safe = []
            for produto in produtos:
                # Verificar se produto tem imagem de capa
                anexos = db.listar_anexos_produto(produto.get('id'))
                tem_imagem = any(anexo.get('tipo_mime', '').startswith('image/') for anexo in anexos) if anexos else False
                
                produto_dict = {
                    'id': produto.get('id'),
                    'nome': produto.get('nome'),
                    'codigo': produto.get('codigo'),
                    'categoria': produto.get('categoria'),
                    'categoria_id': produto.get('categoria_id'),
                    'preco': float(produto.get('preco')) if produto.get('preco') else None,
                    'margem_lucro': float(produto.get('margem_lucro')) if produto.get('margem_lucro') else None,
                    'descricao': produto.get('descricao'),
                    'especificacoes': produto.get('especificacoes'),
                    'custo_materiais': float(produto.get('custo_materiais')) if produto.get('custo_materiais') else None,
                    'custo_etapas': float(produto.get('custo_etapas')) if produto.get('custo_etapas') else None,
                    'status': produto.get('status'),
                    'etapas_count': produto.get('etapas_count', 0),
                    'estoque': produto.get('estoque', 0),
                    'fornecedor': produto.get('fornecedor'),
                    'data_criacao': str(produto.get('data_criacao')) if produto.get('data_criacao') else None,
                    'data_atualizacao': str(produto.get('data_atualizacao')) if produto.get('data_atualizacao') else None,
                    'tem_imagem': tem_imagem,
                    'foto_capa': f'/api/produtos/{produto.get("id")}/imagem?quality=compressed' if tem_imagem else None
                }
                produtos_safe.append(produto_dict)
            
            # Sempre buscar favoritos se tiver usuario_id
            favoritos_array = []
            usuario_id = request.args.get('usuario_id')
            if usuario_id:
                print(f"[DEBUG] Buscando favoritos para usuário {usuario_id}")
                favoritos = db.listar_favoritos(int(usuario_id))
                # Criar array de IDs dos favoritos e um set para busca rápida
                favoritos_ids = set()
                if isinstance(favoritos, list):
                    favoritos_array = [f['produto_id'] for f in favoritos]
                    favoritos_ids = set(favoritos_array)  # Converter para set para busca mais eficiente
                print(f"[DEBUG] Favoritos encontrados: {favoritos_array}")

                # Se não houver termo de busca e houver favoritos, retornar apenas os favoritos
                nome = request.args.get('nome', '').strip()
                categoria = request.args.get('categoria', '').strip()
                print(f"[DEBUG] Favoritos array antes da conversão: {favoritos_array}")
                if not nome and not categoria and favoritos_ids:
                    print(f"[DEBUG] Filtrando apenas favoritos. Total de favoritos: {len(favoritos_ids)}")
                    produtos_filtrados = []
                    favoritos_ids_int = {int(fav_id) for fav_id in favoritos_ids}  # Convert all IDs to integers
                    print(f"[DEBUG] IDs dos favoritos convertidos para inteiros: {favoritos_ids_int}")
                    
                    for p in produtos_safe:
                        try:
                            produto_id = int(p.get('id')) if p.get('id') is not None else None
                            if produto_id is not None and produto_id in favoritos_ids_int:
                                produtos_filtrados.append(p)
                                print(f"[DEBUG] Produto {produto_id} é favorito!")
                        except (ValueError, TypeError) as e:
                            print(f"[ERROR] Erro ao processar produto ID: {e}")
                            continue
                    produtos_safe = produtos_filtrados
                    print(f"[DEBUG] Produtos filtrados: {len(produtos_safe)}")
            
            return jsonify({
                'status': 'success', 
                'produtos': produtos_safe,
                'favoritos': favoritos_array
            }), 200
        else:
            return jsonify({
                'status': 'success', 
                'produtos': produtos,
                'favoritos': []
            }), 200

    except Exception as e:
        print(f"[ERROR] Exceção na API /api/produtos GET: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@flask_app.route('/api/produtos', methods=['POST'])
def salvar_produto():
    try:
        print(f"[DEBUG] Content-Type: {request.content_type}")
        print(f"[DEBUG] Request form keys: {list(request.form.keys())}")
        print(f"[DEBUG] Request files keys: {list(request.files.keys())}")
        
        # Verificar se há anexos (FormData) ou apenas dados JSON
        tem_arquivos = bool(request.files)
        if (request.content_type and 'multipart/form-data' in request.content_type) or tem_arquivos:
            print(f"[DEBUG] Detectado FormData (content-type ou arquivos presentes)")
            # Request com anexos - usar FormData
            dados_str = request.form.get('dados')
            print(f"[DEBUG] dados_str do form: {dados_str}")
            if dados_str:
                dados = json.loads(dados_str)
            else:
                print(f"[ERROR] Dados não encontrados no FormData")
                return jsonify({'status': 'error', 'message': 'Dados não fornecidos no FormData'}), 400
            
            # Processar anexos
            anexos = request.files.getlist('anexos') if 'anexos' in request.files else []
        else:
            print(f"[DEBUG] Detectado JSON")
            # Request sem anexos - usar JSON
            dados = request.get_json()
            anexos = []
        
        print(f"[DEBUG] Dados recebidos: {dados}")
        print(f"[DEBUG] Anexos recebidos: {len(anexos)}")
        
        if not dados:
            return jsonify({'status': 'error', 'message': 'Dados não fornecidos'}), 400
        
        # Validar dados obrigatórios
        campos_obrigatorios = ['nome', 'codigo', 'categoria', 'preco']
        for campo in campos_obrigatorios:
            if not dados.get(campo):
                return jsonify({'status': 'error', 'message': f'O campo {campo} é obrigatório'}), 400
        
        db = Database()
        
        # Verificar se já existe produto com o mesmo código
        produto_existente = db.buscar_produto_por_codigo(dados['codigo'])
        if produto_existente:
            db.close()
            return jsonify({'status': 'error', 'message': 'Já existe um produto com este código'}), 400
        
        # Preparar dados para inserção
        produto_data = {
            'nome': dados['nome'],
            'codigo': dados['codigo'],
            'categoria': dados['categoria'],
            'preco': dados['preco'],
            'margem': dados.get('margem', 0),
            'descricao': dados.get('descricao', ''),
            'especificacoes': dados.get('especificacoes', ''),
            'custo_materiais': dados.get('custoMateriais', 0),
            'custo_etapas': dados.get('custoEtapas', 0)
        }
        
        print(f"[DEBUG] Produto data preparado: {produto_data}")
        
        # Inserir produto principal
        produto_id = db.inserir_produto(produto_data)
        print(f"[DEBUG] Produto inserido com ID: {produto_id}")
        
        if not produto_id:
            db.close()
            return jsonify({'status': 'error', 'message': 'Erro ao salvar produto'}), 500
        
        # Inserir materiais do produto
        materiais = dados.get('materiais', [])
        print(f"[DEBUG] Materiais a inserir: {materiais}")
        for material in materiais:
            material_data = {
                'produto_id': produto_id,
                'material_id': material.get('material_id', material.get('id')),  # Usar material_id primeiro, depois id como fallback
                'quantidade': material.get('quantidade_necessaria', material.get('quantidade')),
                'preco_unitario': material.get('custo_unitario', material.get('precoUnitario')),
                'preco_total': material.get('subtotal', material.get('precoTotal')),
                'largura': material.get('largura'),
                'altura': material.get('altura'),
                'area_utilizada': material.get('area_utilizada')
            }
            print(f"[DEBUG] Inserindo material: {material_data}")
            db.inserir_material_produto(material_data)
        
        # Inserir etapas do produto
        etapas = dados.get('etapas', [])
        print(f"[DEBUG] Etapas a inserir: {etapas}")
        for etapa in etapas:
            # Usar o tipo que vem do frontend, não sobrescrever
            tipo_etapa = etapa.get('tipo', 'Manual')
            equipamento_id = etapa.get('equipamento_id')
            
            # Se o equipamento_id está no formato "maquina_X" ou "ferramenta_X", extrair apenas o ID numérico
            if equipamento_id and isinstance(equipamento_id, str):
                if equipamento_id.startswith('maquina_'):
                    # Extrair apenas o ID numérico, mas manter o tipo do frontend
                    equipamento_id = equipamento_id.replace('maquina_', '')
                    try:
                        equipamento_id = int(equipamento_id)
                    except ValueError:
                        equipamento_id = None
                elif equipamento_id.startswith('ferramenta_'):
                    # Extrair apenas o ID numérico, mas manter o tipo do frontend
                    equipamento_id = equipamento_id.replace('ferramenta_', '')
                    try:
                        equipamento_id = int(equipamento_id)
                    except ValueError:
                        equipamento_id = None
            
            etapa_data = {
                'produto_id': produto_id,
                'nome': etapa['nome'],
                'tipo': tipo_etapa,  # Usar o tipo que vem do frontend
                'equipamento_id': equipamento_id,
                'equipamento': etapa.get('equipamento_nome', etapa.get('equipamento', '')),
                'material_id': etapa.get('material_id'),
                'material': etapa.get('material_nome', etapa.get('material', '')),
                'tempo_estimado': etapa.get('tempo_estimado', etapa.get('tempoEstimado', 0)),
                'custo': etapa.get('custo_estimado', etapa.get('custo', 0))
            }
            print(f"[DEBUG] Inserindo etapa: {etapa_data}")
            db.inserir_etapa_produto(etapa_data)
        
        # Processar anexos se houver
        anexos_salvos = []
        for i, arquivo in enumerate(anexos):
            if arquivo.filename != '':
                # Ler conteúdo do arquivo
                arquivo.seek(0)
                conteudo_blob = arquivo.read()
                tamanho = len(conteudo_blob)
                tipo_mime = arquivo.content_type or 'application/octet-stream'
                
                # Obter categoria do anexo (se disponível)
                categoria_key = f'anexo_categoria_{i}'
                categoria = request.form.get(categoria_key, '')
                print(f"[DEBUG] Categoria do anexo {i}: {categoria}")
                
                # Salvar no banco de dados
                anexo_id = db.inserir_anexo_produto(
                    produto_id=produto_id,
                    nome_original=arquivo.filename,
                    conteudo_blob=conteudo_blob,
                    tamanho=tamanho,
                    tipo_mime=tipo_mime,
                    descricao=categoria
                )
                
                if anexo_id:
                    anexos_salvos.append({
                        'id': anexo_id,
                        'nome': arquivo.filename,
                        'tamanho': tamanho
                    })
        
        db.close()
        
        response_data = {
            'status': 'success',
            'message': 'Produto salvo com sucesso',
            'produto_id': produto_id
        }
        
        if anexos_salvos:
            response_data['anexos'] = anexos_salvos
            response_data['message'] += f' com {len(anexos_salvos)} anexo(s)'
        
        return jsonify(response_data), 201
    
    except Exception as e:
        print(f"[ERROR] Exceção na API /api/produtos POST: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@flask_app.route('/api/produtos/<int:produto_id>', methods=['GET'])
def buscar_produto_por_id(produto_id):
    try:
        db = Database()
        produto = db.buscar_produto_por_id(produto_id)
        db.close()

        if produto and 'erro' not in produto:
            return jsonify({"status": "success", "produto": produto})
        elif produto and 'erro' in produto:
            return jsonify({"status": "error", "message": produto["erro"]}), 404
        else:
            return jsonify({"status": "error", "message": "Produto não encontrado"}), 404

    except Exception as e:
        print(f"[ERROR] Exceção na API /api/produtos/{produto_id} GET: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@flask_app.route('/api/produtos/<int:produto_id>', methods=['PUT'])
def atualizar_produto(produto_id):
    try:
        print(f"[DEBUG] ===== ATUALIZAR PRODUTO ID: {produto_id} =====")
        print(f"[DEBUG] Content-Type: {request.content_type}")
        print(f"[DEBUG] Request form keys: {list(request.form.keys())}")
        print(f"[DEBUG] Request files keys: {list(request.files.keys())}")
        print(f"[DEBUG] Form data: {dict(request.form)}")
        
        # Verificar se há anexos (FormData) ou apenas dados JSON
        tem_arquivos = bool(request.files)
        if (request.content_type and 'multipart/form-data' in request.content_type) or tem_arquivos:
            print(f"[DEBUG] Detectado FormData (content-type ou arquivos presentes)")
            # Request com anexos - usar FormData
            dados_str = request.form.get('dados')
            print(f"[DEBUG] dados_str do form: {dados_str}")
            if dados_str:
                dados = json.loads(dados_str)
            else:
                print(f"[ERROR] Dados não encontrados no FormData")
                return jsonify({'status': 'error', 'message': 'Dados não fornecidos no FormData'}), 400
            
            # Processar anexos novos e anexos para deletar
            anexos = request.files.getlist('anexos') if 'anexos' in request.files else []
            anexos_para_deletar_str = request.form.get('anexosParaDeletar')
            anexos_para_deletar = json.loads(anexos_para_deletar_str) if anexos_para_deletar_str else []
            anexos_existentes_categoria_str = request.form.get('anexosExistentesCategoria')
            anexos_existentes_categoria = json.loads(anexos_existentes_categoria_str) if anexos_existentes_categoria_str else []
        else:
            print(f"[DEBUG] Detectado JSON")
            # Request sem anexos - usar JSON
            dados = request.get_json()
            anexos = []
            anexos_para_deletar = dados.get('anexosParaDeletar', [])
            anexos_existentes_categoria = dados.get('anexosExistentesCategoria', [])
        
        print(f"[DEBUG] Dados recebidos para edição: {dados}")
        print(f"[DEBUG] Anexos novos recebidos: {len(anexos)}")
        print(f"[DEBUG] Anexos para deletar: {anexos_para_deletar}")
        
        if not dados:
            return jsonify({'status': 'error', 'message': 'Dados não fornecidos'}), 400
        
        # Validar dados obrigatórios
        campos_obrigatorios = ['nome', 'codigo', 'categoria', 'preco']
        for campo in campos_obrigatorios:
            if not dados.get(campo):
                return jsonify({'status': 'error', 'message': f'O campo {campo} é obrigatório'}), 400
        
        db = Database()
        
        # Verificar se o produto existe
        produto_existente = db.buscar_produto_por_id(produto_id)
        if not produto_existente or 'erro' in produto_existente:
            db.close()
            return jsonify({'status': 'error', 'message': 'Produto não encontrado'}), 404
        
        # Verificar se já existe outro produto com o mesmo código (excluindo o atual)
        produto_mesmo_codigo = db.buscar_produto_por_codigo(dados['codigo'])
        if produto_mesmo_codigo and produto_mesmo_codigo.get('id') != produto_id:
            db.close()
            return jsonify({'status': 'error', 'message': 'Já existe outro produto com este código'}), 400
        
        # Preparar dados para atualização
        produto_data = {
            'nome': dados['nome'],
            'codigo': dados['codigo'],
            'categoria': dados['categoria'],
            'preco': dados['preco'],
            'margem': dados.get('margem', 0),
            'descricao': dados.get('descricao', ''),
            'especificacoes': dados.get('especificacoes', ''),
            'custo_materiais': dados.get('custoMateriais', 0),
            'custo_etapas': dados.get('custoEtapas', 0)
        }
        
        print(f"[DEBUG] Produto data preparado para atualização: {produto_data}")
        
        # Atualizar produto principal
        resultado = db.atualizar_produto(produto_id, produto_data)
        print(f"[DEBUG] Resultado da atualização do produto: {resultado}")
        
        if not resultado or 'erro' in resultado:
            db.close()
            return jsonify({'status': 'error', 'message': 'Erro ao atualizar produto'}), 500
        
        # Remover materiais existentes e inserir os novos
        db.remover_materiais_produto(produto_id)
        materiais = dados.get('materiais', [])
        print(f"[DEBUG] Materiais a atualizar: {materiais}")
        for material in materiais:
            material_data = {
                'produto_id': produto_id,
                'material_id': material.get('material_id', material.get('id')),  # Usar material_id primeiro, depois id como fallback
                'quantidade': material.get('quantidade_necessaria', material.get('quantidade')),
                'preco_unitario': material.get('custo_unitario', material.get('precoUnitario')),
                'preco_total': material.get('subtotal', material.get('precoTotal')),
                'largura': material.get('largura'),
                'altura': material.get('altura'),
                'area_utilizada': material.get('area_utilizada')
            }
            print(f"[DEBUG] Inserindo material atualizado: {material_data}")
            db.inserir_material_produto(material_data)
        
        # Remover etapas existentes e inserir as novas
        db.remover_etapas_produto(produto_id)
        etapas = dados.get('etapas', [])
        print(f"[DEBUG] Etapas a atualizar: {etapas}")
        for etapa in etapas:
            # Usar o tipo que vem do frontend, não sobrescrever
            tipo_etapa = etapa.get('tipo', 'Manual')
            equipamento_id = etapa.get('equipamento_id')
            
            # Se o equipamento_id está no formato "maquina_X" ou "ferramenta_X", extrair apenas o ID numérico
            if equipamento_id and isinstance(equipamento_id, str):
                if equipamento_id.startswith('maquina_'):
                    # Extrair apenas o ID numérico, mas manter o tipo do frontend
                    equipamento_id = equipamento_id.replace('maquina_', '')
                    try:
                        equipamento_id = int(equipamento_id)
                    except ValueError:
                        equipamento_id = None
                elif equipamento_id.startswith('ferramenta_'):
                    # Extrair apenas o ID numérico, mas manter o tipo do frontend
                    equipamento_id = equipamento_id.replace('ferramenta_', '')
                    try:
                        equipamento_id = int(equipamento_id)
                    except ValueError:
                        equipamento_id = None
            
            etapa_data = {
                'produto_id': produto_id,
                'nome': etapa['nome'],
                'tipo': tipo_etapa,  # Usar o tipo que vem do frontend
                'equipamento_id': equipamento_id,
                'equipamento': etapa.get('equipamento_nome', etapa.get('equipamento', '')),
                'material_id': etapa.get('material_id'),
                'material': etapa.get('material_nome', etapa.get('material', '')),
                'tempo_estimado': etapa.get('tempo_estimado', etapa.get('tempoEstimado', 0)),
                'custo': etapa.get('custo_estimado', etapa.get('custo', 0))
            }
            print(f"[DEBUG] Inserindo etapa atualizada: {etapa_data}")
            db.inserir_etapa_produto(etapa_data)
        
        # Processar remoção de anexos marcados para deletar
        anexos_removidos = 0
        for anexo_id in anexos_para_deletar:
            if db.remover_anexo_produto(anexo_id):
                anexos_removidos += 1
        
        # Processar novos anexos se houver
        anexos_salvos = []
        print(f"[DEBUG] Processando {len(anexos)} anexos para atualização...")
        for i, arquivo in enumerate(anexos):
            if arquivo.filename != '':
                # Ler conteúdo do arquivo
                arquivo.seek(0)
                conteudo_blob = arquivo.read()
                tamanho = len(conteudo_blob)
                tipo_mime = arquivo.content_type or 'application/octet-stream'
                
                # Obter categoria do anexo (se disponível)
                categoria_key = f'anexo_categoria_{i}'
                categoria = request.form.get(categoria_key, '')
                print(f"[DEBUG] Anexo {i}: '{arquivo.filename}' -> categoria_key: '{categoria_key}' -> categoria: '{categoria}'")
                print(f"[DEBUG] Todas as chaves do form: {list(request.form.keys())}")
                print(f"[DEBUG] Categoria do anexo {i} na atualização: {categoria}")
                
                # Salvar no banco de dados
                anexo_id = db.inserir_anexo_produto(
                    produto_id=produto_id,
                    nome_original=arquivo.filename,
                    conteudo_blob=conteudo_blob,
                    tamanho=tamanho,
                    tipo_mime=tipo_mime,
                    descricao=categoria
                )
                
                if anexo_id:
                    anexos_salvos.append({
                        'id': anexo_id,
                        'nome': arquivo.filename,
                        'tamanho': tamanho
                    })
        
        # Processar categorias alteradas de anexos existentes
        anexos_categoria_atualizados = 0
        print(f"[DEBUG] Processando {len(anexos_existentes_categoria)} anexos existentes com categoria alterada...")
        for anexo_categoria in anexos_existentes_categoria:
            anexo_id = anexo_categoria.get('id')
            nova_categoria = anexo_categoria.get('categoria', '')
            
            if anexo_id:
                print(f"[DEBUG] Atualizando categoria do anexo {anexo_id} para: '{nova_categoria}'")
                if db.atualizar_categoria_anexo_produto(anexo_id, nova_categoria):
                    anexos_categoria_atualizados += 1
        
        db.close()
        
        response_data = {
            'status': 'success',
            'message': 'Produto atualizado com sucesso'
        }
        
        # Adicionar informações sobre anexos na resposta
        if anexos_removidos > 0:
            response_data['message'] += f', {anexos_removidos} anexo(s) removido(s)'
        
        if anexos_salvos:
            response_data['anexos'] = anexos_salvos
            response_data['message'] += f', {len(anexos_salvos)} anexo(s) adicionado(s)'
        
        if anexos_categoria_atualizados > 0:
            response_data['message'] += f', {anexos_categoria_atualizados} categoria(s) de anexo(s) alterada(s)'
        
        return jsonify(response_data), 200
    
    except Exception as e:
        print(f"[ERROR] Exceção na API /api/produtos/{produto_id} PUT: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@flask_app.route('/api/produtos/<int:produto_id>', methods=['DELETE'])
def deletar_produto(produto_id):
    """Deleta um produto"""
    try:
        db = Database()
        
        # Verificar se o produto existe
        produto = db.buscar_produto_por_id(produto_id)
        if not produto or 'erro' in produto:
            db.close()
            return jsonify({'status': 'error', 'message': 'Produto não encontrado'}), 404
        
        # Deletar produto
        resultado = db.deletar_produto(produto_id)
        db.close()
        
        if 'erro' in resultado:
            return jsonify({'status': 'error', 'message': resultado['erro']}), 500
        else:
            return jsonify({
                'status': 'success', 
                'message': resultado['sucesso'],
                'detalhes': resultado['detalhes']
            }), 200
    
    except Exception as e:
        print(f"[ERROR] Exceção na API /api/produtos/{produto_id} DELETE: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@flask_app.route('/api/itens_estoque/busca', methods=['GET'])
def buscar_materiais():
    try:
        termo = request.args.get('termo', '')
        if len(termo) < 2:
            return jsonify({'status': 'success', 'itens': []}), 200

        db = Database()
        itens = db.buscar_itens_estoque_por_termo(termo)
        db.close()

        if isinstance(itens, dict) and 'erro' in itens:
            return jsonify({'status': 'error', 'message': itens['erro']}), 500
        
        return jsonify({'status': 'success', 'itens': itens}), 200

    except Exception as e:
        print(f"[ERROR] Exceção na API /api/itens_estoque/busca GET: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Rotas para Anexos de Produtos
@flask_app.route('/api/produtos/<int:produto_id>/anexos', methods=['POST'])
def upload_anexo_produto(produto_id):
    """Upload de anexo para um produto"""
    try:
        # Verificar se o produto existe
        db = Database()
        produto = db.buscar_produto_por_id(produto_id)
        if not produto or 'erro' in produto:
            db.close()
            return jsonify({'status': 'error', 'message': 'Produto não encontrado'}), 404
        
        # Verificar se há arquivos no request
        if 'anexos' not in request.files:
            return jsonify({'status': 'error', 'message': 'Nenhum arquivo enviado'}), 400
        
        arquivos = request.files.getlist('anexos')
        anexos_salvos = []
        
        for arquivo in arquivos:
            if arquivo.filename == '':
                continue
            
            # Ler conteúdo do arquivo
            arquivo.seek(0)
            conteudo_blob = arquivo.read()
            tamanho = len(conteudo_blob)
            tipo_mime = arquivo.content_type or 'application/octet-stream'
            
            # Salvar no banco de dados
            anexo_id = db.inserir_anexo_produto(
                produto_id=produto_id,
                nome_original=arquivo.filename,
                conteudo_blob=conteudo_blob,
                tamanho=tamanho,
                tipo_mime=tipo_mime
            )
            
            if anexo_id:
                anexos_salvos.append({
                    'id': anexo_id,
                    'nome': arquivo.filename,
                    'tamanho': tamanho,
                    'tipo': tipo_mime
                })
        
        db.close()
        
        if anexos_salvos:
            return jsonify({
                'status': 'success',
                'message': f'{len(anexos_salvos)} anexo(s) enviado(s) com sucesso',
                'anexos': anexos_salvos
            }), 201
        else:
            return jsonify({'status': 'error', 'message': 'Erro ao salvar anexos'}), 500
    
    except Exception as e:
        print(f"[ERROR] Exceção na API /api/produtos/{produto_id}/anexos POST: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@flask_app.route('/api/produtos/<int:produto_id>/anexos', methods=['GET'])
def listar_anexos_produto(produto_id):
    """Lista anexos de um produto"""
    try:
        db = Database()
        
        # Verificar se o produto existe
        produto = db.buscar_produto_por_id(produto_id)
        if not produto or 'erro' in produto:
            db.close()
            return jsonify({'status': 'error', 'message': 'Produto não encontrado'}), 404
        
        anexos = db.listar_anexos_produto(produto_id)
        db.close()
        
        # Converter anexos para formato JSON-safe
        anexos_safe = []
        for anexo in anexos:
            anexo_dict = {
                'id': anexo['id'],
                'nome_original': anexo['nome_original'],
                'tamanho': anexo['tamanho'],
                'tamanho_formatado': anexo.get('tamanho_formatado', ''),
                'tipo_mime': anexo['tipo_mime'],
                'data_upload': anexo['data_upload'].strftime('%Y-%m-%d %H:%M:%S') if anexo['data_upload'] else None,
                'caminho_fisico': anexo['caminho_fisico'],
                'descricao': anexo.get('descricao', '')  # Incluir a categoria/descrição
            }
            anexos_safe.append(anexo_dict)
        
        return jsonify({'status': 'success', 'anexos': anexos_safe}), 200
    
    except Exception as e:
        print(f"[ERROR] Exceção na API /api/produtos/{produto_id}/anexos GET: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@flask_app.route('/api/anexos/<int:anexo_id>', methods=['GET'])
def download_anexo(anexo_id):
    """Download de um anexo"""
    try:
        from flask import Response
        
        db = Database()
        anexo = db.buscar_anexo_produto(anexo_id)
        db.close()
        
        if not anexo:
            return jsonify({'status': 'error', 'message': 'Anexo não encontrado'}), 404
        
        # Retornar o arquivo
        return Response(
            anexo['conteudo_blob'],
            mimetype=anexo['tipo_mime'],
            headers={
                'Content-Disposition': f'attachment; filename="{anexo["nome_original"]}"',
                'Content-Length': str(anexo['tamanho'])
            }
        )
    
    except Exception as e:
        print(f"[ERROR] Exceção na API /api/anexos/{anexo_id} GET: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@flask_app.route('/api/anexos/<int:anexo_id>', methods=['DELETE'])
def remover_anexo(anexo_id):
    """Remove um anexo"""
    try:
        db = Database()
        
        # Verificar se o anexo existe
        anexo = db.buscar_anexo_produto(anexo_id)
        if not anexo:
            db.close()
            return jsonify({'status': 'error', 'message': 'Anexo não encontrado'}), 404
        
        # Remover anexo
        sucesso = db.remover_anexo_produto(anexo_id)
        db.close()
        
        if sucesso:
            return jsonify({'status': 'success', 'message': 'Anexo removido com sucesso'}), 200
        else:
            return jsonify({'status': 'error', 'message': 'Erro ao remover anexo'}), 500
    
    except Exception as e:
        print(f"[ERROR] Exceção na API /api/anexos/{anexo_id} DELETE: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@flask_app.route('/api/produtos/<int:produto_id>/layout', methods=['GET'])
def get_produto_layout(produto_id):
    """Retorna o layout/design de um produto como imagem base64"""
    try:
        db = Database()
        
        # Buscar anexo do tipo Layout/Design para o produto
        db.cursor.execute("""
            SELECT conteudo_blob, tipo_mime, nome_original 
            FROM produtos_anexos 
            WHERE produto_id = %s AND descricao = '🎨 Layout/Design'
            LIMIT 1
        """, (produto_id,))
        
        resultado = db.cursor.fetchone()
        db.close()
        
        if resultado and resultado['conteudo_blob']:
            import base64
            
            # Converter blob para base64
            layout_base64 = base64.b64encode(resultado['conteudo_blob']).decode('utf-8')
            
            return jsonify({
                'status': 'success',
                'layout': f"data:{resultado['tipo_mime']};base64,{layout_base64}",
                'nome_arquivo': resultado['nome_original']
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Layout não encontrado para este produto'
            }), 404
    
    except Exception as e:
        print(f"[ERROR] Exceção na API /api/produtos/{produto_id}/layout: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@flask_app.route('/api/produtos/verificar_codigo', methods=['POST'])
def verificar_codigo_produto():
    """Verifica se um código de produto já existe no banco de dados"""
    try:
        data = request.get_json()
        if not data or 'codigo' not in data:
            return jsonify({'status': 'error', 'message': 'Código não fornecido'}), 400
        
        codigo = data['codigo'].strip()
        if not codigo:
            return jsonify({'status': 'error', 'message': 'Código não pode estar vazio'}), 400
        
        db = Database()
        try:
            # Verificar se existe produto com este código
            resultado = db.verificar_codigo_produto_existe(codigo)
            
            if isinstance(resultado, dict) and 'erro' in resultado:
                return jsonify({'status': 'error', 'message': resultado['erro']}), 500
            
            # resultado deve ser True se existe, False se não existe
            existe = bool(resultado)
            
            return jsonify({
                'status': 'success', 
                'existe': existe,
                'message': f'Código {"já existe" if existe else "disponível"}'
            }), 200
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"[ERROR] Exceção na verificação de código de produto: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Rotas para Kits
@flask_app.route('/api/kits', methods=['POST'])
def criar_kit():
    """Cria um novo kit"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'Dados não fornecidos'}), 400
        
        codigo = (data.get('codigo') or '').strip()
        nome = (data.get('nome') or '').strip()
        descricao = (data.get('descricao') or '').strip()
        produtos = data.get('produtos', [])
        
        print(f"[DEBUG] Dados recebidos para kit: codigo={codigo}, nome={nome}, descricao={descricao}, produtos={len(produtos)}")
        
        if not codigo:
            return jsonify({'success': False, 'message': 'Código é obrigatório'}), 400
        
        if not nome:
            return jsonify({'success': False, 'message': 'Nome é obrigatório'}), 400
        
        if not produtos or len(produtos) == 0:
            return jsonify({'success': False, 'message': 'Kit deve ter pelo menos um produto'}), 400
        
        db = Database()
        try:
            result = db.criar_kit(codigo, nome, descricao, produtos)
            
            if 'erro' in result:
                return jsonify({'success': False, 'message': result['erro']}), 400
            else:
                return jsonify({'success': True, 'message': 'Kit criado com sucesso', 'id': result['id']}), 201
                
        finally:
            db.close()
            
    except Exception as e:
        print(f"[ERROR] Erro ao criar kit: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

# Rotas para Orçamentos
@flask_app.route('/api/orcamentos', methods=['POST'])
def criar_orcamento():
    """Cria um novo orçamento"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'Dados não fornecidos'}), 400
        
        # Extrair dados do orçamento
        numero = data.get('numero')
        data_orcamento = data.get('data')
        cliente_id = data.get('cliente_id')
        cliente_nome = data.get('cliente_nome')
        vendedor_id = data.get('vendedor_id')
        vendedor_nome = data.get('vendedor_nome')
        validade = data.get('validade')
        prazo_entrega = data.get('prazo_entrega')
        data_hora_entrega = data.get('data_entrega')  # Data e hora de entrega
        condicoes_pagamento = data.get('condicoes_pagamento')
        parcelas = data.get('parcelas')
        observacoes = data.get('observacoes', '')
        itens = data.get('itens', [])
        total = data.get('total', 0)
        
        print(f"[DEBUG] Dados recebidos para orçamento: numero={numero}, cliente_id={cliente_id}, itens={len(itens)}")
        
        # Gerar número automaticamente se não fornecido
        if not numero:
            import random
            numero = str(random.randint(100000, 999999))
            print(f"[DEBUG] Número do orçamento gerado automaticamente: {numero}")
        
        # Validações
        if not cliente_id:
            return jsonify({'success': False, 'message': 'Cliente é obrigatório'}), 400
        
        if not itens or len(itens) == 0:
            return jsonify({'success': False, 'message': 'Orçamento deve ter pelo menos um item'}), 400
        
        db = Database()
        try:
            # Calcular totais baseados nos itens
            subtotal = 0  # Total sem desconto
            custo_total = 0  # Custo total dos itens
            total_com_desconto = 0  # Total com desconto aplicado
            margem_total_ponderada = 0  # Soma das margens ponderadas pelo preço
            lucro_estimado = 0  # Lucro estimado considerando desconto
            
            # Buscar dados de margem de cada produto
            for item in itens:
                quantidade = item.get('quantidade', 1)
                preco_unitario = item.get('preco_unitario', 0)
                custo_unitario = item.get('custo_unitario', 0)
                desconto_item = item.get('desconto', 0)
                produto_id = item.get('id')
                
                # Buscar margem de lucro do produto na base de dados
                margem_produto = 0
                if produto_id:
                    produto_info = db.buscar_produto_por_id(produto_id)
                    print(f"[DEBUG] Produto {produto_id} info: {produto_info}")
                    if produto_info and (not isinstance(produto_info, dict) or 'erro' not in produto_info):
                        margem_lucro_raw = produto_info.get('margem_lucro', 0)
                        print(f"[DEBUG] Produto {produto_id} margem_lucro raw: {margem_lucro_raw} (tipo: {type(margem_lucro_raw)})")
                        margem_produto = float(margem_lucro_raw) if margem_lucro_raw is not None else 0
                
                # Subtotal: preço sem desconto
                subtotal_item = preco_unitario * quantidade
                subtotal += subtotal_item
                
                # Custo total
                custo_total += custo_unitario * quantidade
                
                # Total com desconto aplicado
                total_item_com_desconto = subtotal_item * (1 - desconto_item / 100)
                total_com_desconto += total_item_com_desconto
                
                # Margem ponderada (margem do produto * valor do item sem desconto)
                margem_total_ponderada += (margem_produto * subtotal_item)
                
                # Lucro do item: (preço - custo) * quantidade * (1 - desconto)
                lucro_item = (preco_unitario - custo_unitario) * quantidade * (1 - desconto_item / 100)
                lucro_estimado += lucro_item
                
                print(f"[DEBUG] Item {produto_id}: margem={margem_produto}%, lucro_item={lucro_item:.2f}")
            
            # Calcular desconto proporcional geral
            desconto_proporcional = 0
            if subtotal > 0:
                desconto_proporcional = ((subtotal - total_com_desconto) / subtotal) * 100
            
            # Calcular margem média ponderada
            margem_lucro_media = 0
            if subtotal > 0:
                margem_lucro_media = margem_total_ponderada / subtotal
            
            # Processar data do orçamento - usar data atual se não fornecida
            from datetime import datetime, date
            if data_orcamento:
                # Converter data string para date object (não datetime)
                try:
                    if isinstance(data_orcamento, str):
                        data_orcamento_obj = datetime.strptime(data_orcamento, '%Y-%m-%d').date()
                    else:
                        data_orcamento_obj = data_orcamento
                except:
                    data_orcamento_obj = date.today()
            else:
                data_orcamento_obj = date.today()
            
            # Processar validade - calcular dias se data_validade fornecida
            validade_dias = 30  # Padrão
            data_validade_obj = None
            if validade:
                try:
                    if isinstance(validade, str):
                        data_validade_obj = datetime.strptime(validade, '%Y-%m-%d').date()
                    else:
                        data_validade_obj = validade
                    
                    # Calcular diferença em dias entre data do orçamento e validade
                    diferenca = data_validade_obj - data_orcamento_obj
                    validade_dias = max(1, diferenca.days)  # Mínimo 1 dia
                    
                    print(f"[DEBUG] Validade calculada: {validade_dias} dias (de {data_orcamento_obj} até {data_validade_obj})")
                except Exception as e:
                    print(f"[DEBUG] Erro ao processar validade: {e}")
                    validade_dias = 30
                    data_validade_obj = None
            
            # Processar data/hora de entrega
            data_hora_entrega_obj = None
            if data_hora_entrega:
                try:
                    if isinstance(data_hora_entrega, str):
                        # Converter string datetime-local para datetime object
                        data_hora_entrega_obj = datetime.strptime(data_hora_entrega, '%Y-%m-%dT%H:%M')
                    else:
                        data_hora_entrega_obj = data_hora_entrega
                    print(f"[DEBUG] Data/hora entrega processada: {data_hora_entrega_obj}")
                except Exception as e:
                    print(f"[DEBUG] Erro ao processar data/hora entrega: {e}")
                    data_hora_entrega_obj = None
            
            # Criar orçamento principal
            orcamento_data = {
                'numero': numero,
                'data_orcamento': data_orcamento_obj,  # Usar date object
                'cliente_id': cliente_id,
                'vendedor_id': vendedor_id,
                'validade': data_validade_obj,  # Data de validade como date
                'validade_dias': validade_dias,  # Dias calculados
                'prazo_entrega': prazo_entrega,
                'data_hora_entrega': data_hora_entrega_obj,  # Data/hora de entrega
                'condicoes_pagamento': condicoes_pagamento,
                'parcelas': parcelas,
                'observacoes': observacoes,  # Garantir que observações sejam salvas
                'valor_total': total_com_desconto,  # Total final com desconto
                'subtotal': subtotal,  # Total sem desconto
                'desconto': desconto_proporcional,  # Desconto proporcional em %
                'custo_total': custo_total,  # Custo total dos itens
                'margem_lucro': margem_lucro_media,  # Margem média ponderada
                'lucro_estimado': lucro_estimado,  # Lucro estimado com desconto
                'status': 'Pendente'
            }
            
            print(f"[DEBUG] Calculados - Subtotal: {subtotal}, Desconto: {desconto_proporcional}%, Custo Total: {custo_total}, Total Final: {total_com_desconto}")
            print(f"[DEBUG] Margem Lucro Média: {margem_lucro_media:.2f}%, Lucro Estimado: {lucro_estimado:.2f}")
            print(f"[DEBUG] Data orçamento: {data_orcamento_obj}, Validade: {data_validade_obj}, Dias: {validade_dias}")
            print(f"[DEBUG] Observações enviadas: '{observacoes}' (tipo: {type(observacoes)}, tamanho: {len(observacoes) if observacoes else 0})")
            
            orcamento_id = db.criar_orcamento(orcamento_data)
            
            if not orcamento_id:
                return jsonify({'success': False, 'message': 'Erro ao criar orçamento'}), 500
            
            # Adicionar itens do orçamento
            for item in itens:
                item_data = {
                    'orcamento_id': orcamento_id,
                    'produto_id': item.get('id'),
                    'produto_nome': item.get('nome'),
                    'quantidade': item.get('quantidade', 1),
                    'preco_unitario': item.get('preco_unitario', 0),
                    'preco_total': item.get('total', 0),
                    'descricao': item.get('descricao', ''),
                    'kit_origem': item.get('kit_origem', ''),
                    'kit_id': item.get('kit_id'),
                    'custo_unitario': item.get('custo_unitario', 0),
                    'desconto_item': item.get('desconto', 0),
                    'subtotal': item.get('total', 0)
                }
                db.criar_item_orcamento(item_data)
            
            return jsonify({
                'success': True, 
                'message': 'Orçamento criado com sucesso', 
                'id': orcamento_id,
                'numero': numero,
                'subtotal': subtotal,
                'desconto': desconto_proporcional,
                'custo_total': custo_total,
                'margem_lucro': margem_lucro_media,
                'lucro_estimado': lucro_estimado,
                'total': total_com_desconto
            }), 201
                
        finally:
            db.close()
            
    except Exception as e:
        print(f"[ERROR] Erro ao criar orçamento: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@flask_app.route('/api/orcamentos', methods=['GET'])
def listar_orcamentos():
    """Lista todos os orçamentos"""
    try:
        db = Database()
        try:
            orcamentos = db.listar_orcamentos()
            return jsonify({'success': True, 'orcamentos': convert_values_to_json_safe(orcamentos)}), 200
        finally:
            db.close()
            
    except Exception as e:
        print(f"[ERROR] Erro ao listar orçamentos: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@flask_app.route('/api/orcamentos/<int:orcamento_id>', methods=['GET'])
def buscar_orcamento(orcamento_id):
    """Busca um orçamento específico"""
    try:
        db = Database()
        try:
            orcamento = db.buscar_orcamento_por_id(orcamento_id)
            
            if not orcamento:
                return jsonify({'success': False, 'message': 'Orçamento não encontrado'}), 404
            
            return jsonify({'success': True, 'orcamento': convert_values_to_json_safe(orcamento)}), 200
        finally:
            db.close()
            
    except Exception as e:
        print(f"[ERROR] Erro ao buscar orçamento: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@flask_app.route('/api/orcamentos/<int:orcamento_id>', methods=['PUT'])
def atualizar_orcamento(orcamento_id):
    """Atualiza um orçamento existente"""
    try:
        data = request.get_json()
        print(f"[DEBUG] Atualizando orçamento ID: {orcamento_id}")
        print(f"[DEBUG] Dados recebidos para atualização: {data}")
        
        if not data:
            return jsonify({'success': False, 'message': 'Dados não fornecidos'}), 400
        
        db = Database()
        try:
            # Verificar se o orçamento existe
            orcamento_existente = db.buscar_orcamento_por_id(orcamento_id)
            if not orcamento_existente:
                return jsonify({'success': False, 'message': 'Orçamento não encontrado'}), 404
            
            # Processar dados da mesma forma que criar_orcamento, mas para atualização
            numero = data.get('numero')
            data_orcamento = data.get('data')
            cliente_id = data.get('cliente_id')
            cliente_nome = data.get('cliente_nome')
            vendedor_id = data.get('vendedor_id')
            vendedor_nome = data.get('vendedor_nome')
            validade = data.get('validade')
            prazo_entrega = data.get('prazo_entrega')
            data_hora_entrega = data.get('data_entrega')
            condicoes_pagamento = data.get('condicoes_pagamento')
            parcelas = data.get('parcelas')
            observacoes = data.get('observacoes', '')
            itens = data.get('itens', [])
            total = data.get('total', 0)
            
            # Se vendedor_id é None mas temos vendedor_nome, tentar buscar o ID
            if not vendedor_id and vendedor_nome:
                try:
                    # Buscar vendedor pelo nome - isso pode precisar ser implementado no database.py
                    # Por enquanto, vamos manter o valor existente do orçamento
                    vendedor_id = orcamento_existente.get('vendedor_id')
                except:
                    vendedor_id = None
            
            print(f"[DEBUG] Dados processados para atualização: cliente_id={cliente_id}, itens={len(itens)}")
            
            # Validações
            if not cliente_id:
                return jsonify({'success': False, 'message': 'Cliente é obrigatório'}), 400
            
            if not itens or len(itens) == 0:
                return jsonify({'success': False, 'message': 'Orçamento deve ter pelo menos um item'}), 400
            
            # Calcular totais baseados nos itens (mesmo processo do criar_orcamento)
            subtotal = 0
            custo_total = 0
            total_com_desconto = 0
            margem_total_ponderada = 0
            lucro_estimado = 0
            
            for item in itens:
                quantidade = float(item.get('quantidade', 1))
                preco_unitario = float(item.get('preco_unitario', 0))  # Campo correto do frontend
                custo_unitario = float(item.get('custo_unitario', 0))  # Campo correto do frontend
                desconto_item = float(item.get('desconto', 0))  # Campo 'desconto' do frontend
                produto_id = item.get('id')
                
                # Buscar margem de lucro do produto
                margem_produto = 0
                if produto_id:
                    produto_info = db.buscar_produto_por_id(produto_id)
                    if produto_info and 'margem_lucro' in produto_info:
                        margem_produto = float(produto_info['margem_lucro'])
                
                # Cálculos corretos
                subtotal_item = preco_unitario * quantidade
                subtotal += subtotal_item
                custo_total += custo_unitario * quantidade
                
                # Desconto: se for > 100, é valor absoluto, senão é percentual
                if desconto_item > 100:
                    # Desconto em valor absoluto
                    total_item_com_desconto = subtotal_item - desconto_item
                else:
                    # Desconto em percentual
                    total_item_com_desconto = subtotal_item * (1 - desconto_item / 100)
                
                total_com_desconto += total_item_com_desconto
                margem_total_ponderada += (margem_produto * subtotal_item)
                
                # Lucro: (preço - custo) * quantidade - desconto aplicado
                lucro_base = (preco_unitario - custo_unitario) * quantidade
                if desconto_item > 100:
                    lucro_item = lucro_base - desconto_item
                else:
                    lucro_item = lucro_base * (1 - desconto_item / 100)
                lucro_estimado += lucro_item
            
            # Calcular desconto e margem
            desconto_proporcional = 0
            if subtotal > 0:
                desconto_proporcional = ((subtotal - total_com_desconto) / subtotal) * 100
            
            margem_lucro_media = 0
            if subtotal > 0:
                margem_lucro_media = margem_total_ponderada / subtotal
            
            # Processar datas
            from datetime import datetime, date
            if data_orcamento:
                try:
                    data_orcamento_obj = datetime.strptime(data_orcamento, '%Y-%m-%d').date()
                except:
                    data_orcamento_obj = date.today()
            else:
                data_orcamento_obj = date.today()
            
            # Processar validade
            validade_dias = 30
            data_validade_obj = None
            if validade:
                try:
                    data_validade_obj = datetime.strptime(validade, '%Y-%m-%d').date()
                    validade_dias = (data_validade_obj - data_orcamento_obj).days
                except Exception as e:
                    print(f"[DEBUG] Erro ao processar validade: {e}")
            
            # Processar data/hora de entrega
            data_hora_entrega_obj = None
            if data_hora_entrega:
                try:
                    data_hora_entrega_obj = datetime.strptime(data_hora_entrega, '%Y-%m-%dT%H:%M')
                except Exception as e:
                    print(f"[DEBUG] Erro ao processar data/hora entrega: {e}")
            
            # Preparar itens para inserção (convertendo formato do frontend para database)
            itens_processados = []
            for item in itens:
                item_processado = {
                    'produto_id': item.get('id'),
                    'produto_nome': item.get('nome', ''),
                    'quantidade': item.get('quantidade', 1),
                    'preco_unitario': item.get('preco_unitario', 0),  # Campo correto do frontend
                    'custo_unitario': item.get('custo_unitario', 0),  # Campo correto do frontend
                    'desconto_item': item.get('desconto', 0),  # Convertendo 'desconto' para 'desconto_item'
                    'descricao': item.get('descricao', ''),
                    'kit_origem': item.get('kit_origem'),
                    'kit_id': item.get('kit_id')
                }
                
                # Calcular preco_total e subtotal
                quantidade = float(item_processado['quantidade'])
                preco_unitario = float(item_processado['preco_unitario'])
                desconto_valor = float(item_processado['desconto_item'])
                
                subtotal_item = quantidade * preco_unitario
                
                # Aplicar desconto corretamente
                if desconto_valor > 100:
                    # Desconto em valor absoluto
                    preco_total = subtotal_item - desconto_valor
                else:
                    # Desconto em percentual
                    preco_total = subtotal_item * (1 - desconto_valor / 100)
                
                item_processado.update({
                    'preco_total': preco_total,
                    'subtotal': subtotal_item
                })
                
                itens_processados.append(item_processado)
            
            # Criar dados para atualização
            orcamento_data = {
                'cliente_id': cliente_id,
                'vendedor_id': vendedor_id,
                'validade': data_validade_obj,
                'validade_dias': validade_dias,
                'prazo_entrega': prazo_entrega,
                'data_hora_entrega': data_hora_entrega_obj,
                'condicoes_pagamento': condicoes_pagamento,
                'parcelas': parcelas,
                'observacoes': observacoes,
                'valor_total': total_com_desconto,
                'subtotal': subtotal,
                'desconto': desconto_proporcional,
                'custo_total': custo_total,
                'margem_lucro': margem_lucro_media,
                'lucro_estimado': lucro_estimado,
                'status': 'Pendente',
                'itens': itens_processados  # Usando itens processados
            }
            
            print(f"[DEBUG] Dados preparados para atualização do orçamento ID {orcamento_id}")
            
            # Atualizar o orçamento
            resultado = db.atualizar_orcamento(orcamento_id, orcamento_data)
            
            if resultado.get('success'):
                return jsonify({
                    'success': True, 
                    'message': 'Orçamento atualizado com sucesso',
                    'id': orcamento_id,
                    'subtotal': subtotal,
                    'desconto': desconto_proporcional,
                    'custo_total': custo_total,
                    'margem_lucro': margem_lucro_media,
                    'lucro_estimado': lucro_estimado,
                    'total': total_com_desconto
                }), 200
            else:
                return jsonify({'success': False, 'message': resultado.get('message', 'Erro ao atualizar orçamento')}), 500
                
        finally:
            db.close()
            
    except Exception as e:
        print(f"[ERROR] Erro ao atualizar orçamento: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@flask_app.route('/api/kits', methods=['GET'])
def listar_kits():
    """Lista todos os kits"""
    try:
        db = Database()
        try:
            kits = db.listar_kits()
            return jsonify({'success': True, 'kits': convert_values_to_json_safe(kits)}), 200
        finally:
            db.close()
            
    except Exception as e:
        print(f"[ERROR] Erro ao listar kits: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@flask_app.route('/api/kits/<int:kit_id>', methods=['GET'])
def buscar_kit(kit_id):
    """Busca um kit específico"""
    try:
        db = Database()
        try:
            kit = db.buscar_kit_por_id(kit_id)
            
            if not kit:
                return jsonify({'success': False, 'message': 'Kit não encontrado'}), 404
            
            return jsonify({'success': True, 'kit': convert_values_to_json_safe(kit)}), 200
        finally:
            db.close()
            
    except Exception as e:
        print(f"[ERROR] Erro ao buscar kit: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@flask_app.route('/api/kits/<int:kit_id>', methods=['PUT'])
def atualizar_kit(kit_id):
    """Atualiza um kit existente"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'Dados não fornecidos'}), 400
        
        codigo = data.get('codigo')
        nome = data.get('nome')
        descricao = data.get('descricao')
        produtos = data.get('produtos')
        
        db = Database()
        try:
            result = db.atualizar_kit(kit_id, codigo, nome, descricao, produtos)
            
            if 'erro' in result:
                return jsonify({'success': False, 'message': result['erro']}), 400
            else:
                return jsonify({'success': True, 'message': result['sucesso']}), 200
                
        finally:
            db.close()
            
    except Exception as e:
        print(f"[ERROR] Erro ao atualizar kit: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@flask_app.route('/api/kits/<int:kit_id>', methods=['DELETE'])
def deletar_kit(kit_id):
    """Remove um kit (soft delete)"""
    try:
        db = Database()
        try:
            result = db.deletar_kit(kit_id)
            
            if 'erro' in result:
                return jsonify({'success': False, 'message': result['erro']}), 400
            else:
                return jsonify({'success': True, 'message': result['sucesso']}), 200
                
        finally:
            db.close()
            
    except Exception as e:
        print(f"[ERROR] Erro ao deletar kit: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@flask_app.route('/api/kits/verificar_codigo', methods=['POST'])
def verificar_codigo_kit():
    """Verifica se um código de kit já existe"""
    try:
        data = request.get_json()
        if not data or 'codigo' not in data:
            return jsonify({'success': False, 'message': 'Código não fornecido'}), 400
        
        codigo = data['codigo'].strip()
        if not codigo:
            return jsonify({'success': False, 'message': 'Código não pode estar vazio'}), 400
        
        db = Database()
        try:
            existe = db.verificar_codigo_kit_existe(codigo)
            return jsonify({
                'success': True, 
                'existe': existe,
                'message': f'Código {"já existe" if existe else "disponível"}'
            }), 200
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"[ERROR] Erro ao verificar código do kit: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

# Rotas para Máquinas
@flask_app.route('/maquinas')
def maquinas():
    return render_template('maquinas.html')

@flask_app.route('/api/maquinas', methods=['POST'])
def criar_maquina():
    try:
        data = request.form
        
        # Processar dados do formulário
        nome = data.get('machineName')
        codigo = data.get('machineCode')
        marca = data.get('machineBrand')
        tipo = data.get('machineType')
        numero_serie = data.get('machineSerial')
        data_aquisicao = data.get('machineAcquisitionDate')
        valor_aquisicao = data.get('machineValue')
        hora_maquina = data.get('machineHourlyRate')
        metros_quadrados_por_hora = data.get('machineM2PerHour')
        estado = data.get('machineCondition')
        localizacao = data.get('machineLocation')
        responsavel = data.get('machineResponsible')
        status = data.get('machineStatus')
        especificacoes_tecnicas = data.get('machineTechSpecs')
        observacoes = data.get('machineObservations')
        
        # Processar valores monetários
        if valor_aquisicao:
            valor_aquisicao = valor_aquisicao.replace('R$', '').replace('.', '').replace(',', '.').strip()
            valor_aquisicao = float(valor_aquisicao) if valor_aquisicao else 0.0
        
        if hora_maquina:
            hora_maquina = hora_maquina.replace('R$', '').replace('.', '').replace(',', '.').strip()
            hora_maquina = float(hora_maquina) if hora_maquina else 0.0
        
        # Processar metros quadrados por hora
        if metros_quadrados_por_hora:
            metros_quadrados_por_hora = metros_quadrados_por_hora.replace(',', '.').strip()
            metros_quadrados_por_hora = float(metros_quadrados_por_hora) if metros_quadrados_por_hora else 0.0
        else:
            metros_quadrados_por_hora = 0.0

        db = Database()
        resultado = db.criar_maquina(
            nome, codigo, marca, tipo, numero_serie, data_aquisicao,
            valor_aquisicao, hora_maquina, metros_quadrados_por_hora, estado, 
            localizacao, responsavel, status, especificacoes_tecnicas, observacoes
        )
        db.close()

        if "sucesso" in resultado:
            return jsonify({"status": "success", "message": resultado["sucesso"], "id": resultado["id"]})
        else:
            return jsonify({"status": "error", "message": resultado["erro"]}), 400

    except Exception as e:
        print(f"[ERROR] Exceção ao criar máquina: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@flask_app.route('/api/maquinas', methods=['GET'])
def listar_maquinas():
    try:
        db = Database()
        maquinas = db.listar_maquinas()
        db.close()

        if isinstance(maquinas, list):
            # Serializar manualmente para evitar referências circulares
            maquinas_safe = []
            for maquina in maquinas:
                maquina_dict = {
                    'id': maquina.get('id'),
                    'codigo': maquina.get('codigo'),
                    'nome': maquina.get('nome'),
                    'marca': maquina.get('marca'),
                    'tipo': maquina.get('tipo'),
                    'numero_serie': maquina.get('numero_serie'),
                    'data_aquisicao': str(maquina.get('data_aquisicao')) if maquina.get('data_aquisicao') else None,
                    'valor_aquisicao': float(maquina.get('valor_aquisicao')) if maquina.get('valor_aquisicao') else None,
                    'hora_maquina': float(maquina.get('hora_maquina')) if maquina.get('hora_maquina') else None,
                    'metros_quadrados_por_hora': float(maquina.get('metros_quadrados_por_hora')) if maquina.get('metros_quadrados_por_hora') else None,
                    'estado': maquina.get('estado'),
                    'localizacao': maquina.get('localizacao'),
                    'responsavel': maquina.get('responsavel'),
                    'status': maquina.get('status'),
                    'especificacoes_tecnicas': maquina.get('especificacoes_tecnicas'),
                    'observacoes': maquina.get('observacoes')
                }
                maquinas_safe.append(maquina_dict)
            
            return jsonify({"status": "success", "machines": maquinas_safe})
        else:
            return jsonify({"status": "error", "message": maquinas["erro"]}), 400

    except Exception as e:
        print(f"[ERROR] Exceção ao listar máquinas: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@flask_app.route('/api/maquinas/<int:maquina_id>', methods=['GET'])
def buscar_maquina(maquina_id):
    try:
        db = Database()
        maquina = db.buscar_maquina_por_id(maquina_id)
        db.close()

        if isinstance(maquina, dict) and 'erro' in maquina:
            return jsonify({"status": "error", "message": maquina["erro"]}), 404
        
        # Converter para formato JSON-safe para evitar referências circulares
        maquina_safe = convert_values_to_json_safe(maquina)
        return jsonify({"status": "success", "machine": maquina_safe})

    except Exception as e:
        print(f"[ERROR] Exceção ao buscar máquina: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@flask_app.route('/api/maquinas/<int:maquina_id>', methods=['PUT'])
def atualizar_maquina(maquina_id):
    try:
        data = request.form
        
        # Processar valores monetários
        valor_aquisicao = data.get('machineValue')
        if valor_aquisicao:
            valor_aquisicao = valor_aquisicao.replace('R$', '').replace('.', '').replace(',', '.').strip()
            valor_aquisicao = float(valor_aquisicao) if valor_aquisicao else None
        
        hora_maquina = data.get('machineHourlyRate')
        if hora_maquina:
            hora_maquina = hora_maquina.replace('R$', '').replace('.', '').replace(',', '.').strip()
            hora_maquina = float(hora_maquina) if hora_maquina else None
        
        # Processar metros quadrados por hora
        metros_quadrados_por_hora = data.get('machineM2PerHour')
        if metros_quadrados_por_hora:
            metros_quadrados_por_hora = metros_quadrados_por_hora.replace(',', '.').strip()
            metros_quadrados_por_hora = float(metros_quadrados_por_hora) if metros_quadrados_por_hora else None

        db = Database()
        resultado = db.atualizar_maquina(
            maquina_id=maquina_id,
            nome=data.get('machineName'),
            codigo=data.get('machineCode'),
            marca=data.get('machineBrand'),
            tipo=data.get('machineType'),
            numero_serie=data.get('machineSerial'),
            data_aquisicao=data.get('machineAcquisitionDate'),
            valor_aquisicao=valor_aquisicao,
            hora_maquina=hora_maquina,
            metros_quadrados_por_hora=metros_quadrados_por_hora,
            estado=data.get('machineCondition'),
            localizacao=data.get('machineLocation'),
            responsavel=data.get('machineResponsible'),
            status=data.get('machineStatus'),
            especificacoes_tecnicas=data.get('machineTechSpecs'),
            observacoes=data.get('machineObservations')
        )
        db.close()

        if "sucesso" in resultado:
            return jsonify({"status": "success", "message": resultado["sucesso"]})
        else:
            return jsonify({"status": "error", "message": resultado["erro"]}), 400

    except Exception as e:
        print(f"[ERROR] Exceção ao atualizar máquina: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@flask_app.route('/api/maquinas/<int:maquina_id>', methods=['DELETE'])
def deletar_maquina(maquina_id):
    try:
        db = Database()
        resultado = db.deletar_maquina(maquina_id)
        db.close()

        if 'erro' in resultado:
            return jsonify({'status': 'error', 'message': resultado['erro']}), 404
        return jsonify({'status': 'success', 'message': 'Máquina excluída com sucesso'})

    except Exception as e:
        print(f"[ERROR] Exceção ao deletar máquina: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@flask_app.route('/api/tipos_maquinas', methods=['POST'])
def criar_tipo_maquina():
    try:
        data = request.form
        nome = data.get('novoTipoNome')

        if not nome:
            return jsonify({'status': 'error', 'message': 'Nome do tipo é obrigatório'}), 400

        db = Database()
        resultado = db.criar_tipo_maquina(nome)
        db.close()

        if 'erro' in resultado:
            return jsonify({'status': 'error', 'message': resultado['erro']}), 400
        return jsonify({'status': 'success', 'message': 'Tipo de máquina criado com sucesso', 'id': resultado['id']}), 201

    except Exception as e:
        print(f"[ERROR] Exceção ao criar tipo de máquina: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@flask_app.route('/api/tipos_maquinas', methods=['GET'])
def listar_tipos_maquinas():
    try:
        db = Database()
        tipos = db.listar_tipos_maquinas()
        db.close()

        if isinstance(tipos, dict) and 'erro' in tipos:
            return jsonify({'status': 'error', 'message': tipos['erro']}), 500
        
        return jsonify({'status': 'success', 'tipos': tipos}), 200

    except Exception as e:
        print(f"[ERROR] Exceção ao listar tipos de máquinas: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@flask_app.route('/api/manutencoes', methods=['POST'])
def criar_manutencao():
    try:
        data = request.form
        
        maquina_id = data.get('maquinaId')
        tipo_manutencao = data.get('tipoManutencao')
        data_manutencao = data.get('dataManutencao')
        responsavel = data.get('responsavelManutencao')
        fornecedor_empresa = data.get('fornecedorManutencao')
        descricao_servicos = data.get('descricaoManutencao')
        custo = data.get('custoManutencao')
        proxima_manutencao = data.get('proximaManutencao')
        observacoes = data.get('observacoesManutencao')
        
        # Processar custo
        if custo:
            custo = custo.replace('R$', '').replace('.', '').replace(',', '.').strip()
            custo = float(custo) if custo else 0.0

        db = Database()
        resultado = db.criar_manutencao(
            maquina_id, tipo_manutencao, data_manutencao, responsavel,
            fornecedor_empresa, descricao_servicos, custo, proxima_manutencao, observacoes
        )
        db.close()

        if "sucesso" in resultado:
            return jsonify({"status": "success", "message": resultado["sucesso"], "id": resultado["id"]})
        else:
            return jsonify({"status": "error", "message": resultado["erro"]}), 400

    except Exception as e:
        print(f"[ERROR] Exceção ao criar manutenção: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

# Rotas para Ferramentas
@flask_app.route('/ferramentas')
def ferramentas():
    return render_template('ferramentas.html')

@flask_app.route('/api/ferramentas', methods=['POST'])
def criar_ferramenta():
    try:
        data = request.get_json()
        
        # Extrair dados do JSON
        nome = data.get('nome')
        codigo = data.get('codigo')
        tipo = data.get('tipo')
        descricao = data.get('descricao')
        status = data.get('status')
        localizacao = data.get('localizacao')
        estado = data.get('estado')
        responsavel = data.get('responsavel')
        marca = data.get('marca')
        modelo = data.get('modelo')
        data_aquisicao = data.get('data_aquisicao')
        observacoes = data.get('observacoes')

        if not nome:
            return jsonify({"status": "error", "message": "Nome da ferramenta é obrigatório"}), 400

        db = Database()
        resultado = db.criar_ferramenta(
            nome, codigo, tipo, descricao, status, localizacao,
            estado, responsavel, marca, modelo, data_aquisicao, observacoes
        )
        db.close()

        if "sucesso" in resultado:
            return jsonify({"status": "success", "message": resultado["sucesso"], "id": resultado["id"]})
        else:
            return jsonify({"status": "error", "message": resultado["erro"]}), 400

    except Exception as e:
        print(f"[ERROR] Exceção ao criar ferramenta: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@flask_app.route('/api/ferramentas', methods=['GET'])
def listar_ferramentas():
    try:
        db = Database()
        ferramentas = db.listar_ferramentas()
        db.close()

        if isinstance(ferramentas, list):
            # Serializar manualmente para evitar referências circulares
            ferramentas_safe = []
            for ferramenta in ferramentas:
                ferramenta_dict = {
                    'id': ferramenta.get('id'),
                    'codigo': ferramenta.get('codigo'),
                    'nome': ferramenta.get('nome'),
                    'marca': ferramenta.get('marca'),
                    'tipo': ferramenta.get('tipo'),
                    'numero_serie': ferramenta.get('numero_serie'),
                    'data_aquisicao': str(ferramenta.get('data_aquisicao')) if ferramenta.get('data_aquisicao') else None,
                    'valor_aquisicao': float(ferramenta.get('valor_aquisicao')) if ferramenta.get('valor_aquisicao') else None,
                    'custo_por_uso': float(ferramenta.get('custo_por_uso')) if ferramenta.get('custo_por_uso') else None,
                    'estado': ferramenta.get('estado'),
                    'localizacao': ferramenta.get('localizacao'),
                    'responsavel': ferramenta.get('responsavel'),
                    'status': ferramenta.get('status'),
                    'especificacoes_tecnicas': ferramenta.get('especificacoes_tecnicas'),
                    'observacoes': ferramenta.get('observacoes')
                }
                ferramentas_safe.append(ferramenta_dict)
            
            return jsonify({"status": "success", "ferramentas": ferramentas_safe})
        else:
            return jsonify({"status": "error", "message": ferramentas["erro"]}), 400

    except Exception as e:
        print(f"[ERROR] Exceção ao listar ferramentas: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@flask_app.route('/api/ferramentas/<int:ferramenta_id>', methods=['GET'])
def buscar_ferramenta(ferramenta_id):
    try:
        db = Database()
        ferramenta = db.buscar_ferramenta_por_id(ferramenta_id)
        db.close()

        if isinstance(ferramenta, dict) and 'erro' in ferramenta:
            return jsonify({"status": "error", "message": ferramenta["erro"]}), 404
        return jsonify({"status": "success", "ferramenta": ferramenta})

    except Exception as e:
        print(f"[ERROR] Exceção ao buscar ferramenta: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@flask_app.route('/api/ferramentas/<int:ferramenta_id>', methods=['PUT'])
def atualizar_ferramenta(ferramenta_id):
    try:
        data = request.get_json()

        db = Database()
        resultado = db.atualizar_ferramenta(
            ferramenta_id=ferramenta_id,
            nome=data.get('nome'),
            codigo=data.get('codigo'),
            tipo=data.get('tipo'),
            descricao=data.get('descricao'),
            status=data.get('status'),
            localizacao=data.get('localizacao'),
            estado=data.get('estado'),
            responsavel=data.get('responsavel'),
            marca=data.get('marca'),
            modelo=data.get('modelo'),
            data_aquisicao=data.get('data_aquisicao'),
            observacoes=data.get('observacoes')
        )
        db.close()

        if "sucesso" in resultado:
            return jsonify({"status": "success", "message": resultado["sucesso"]})
        else:
            return jsonify({"status": "error", "message": resultado["erro"]}), 400

    except Exception as e:
        print(f"[ERROR] Exceção ao atualizar ferramenta: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@flask_app.route('/api/ferramentas/<int:ferramenta_id>', methods=['DELETE'])
def deletar_ferramenta(ferramenta_id):
    try:
        db = Database()
        resultado = db.deletar_ferramenta(ferramenta_id)
        db.close()

        if 'erro' in resultado:
            return jsonify({'status': 'error', 'message': resultado['erro']}), 404
        return jsonify({'status': 'success', 'message': 'Ferramenta excluída com sucesso'})

    except Exception as e:
        print(f"[ERROR] Exceção ao deletar ferramenta: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Rotas para Etapas de Confecção
@flask_app.route('/etapas_confeccao')
def etapas_confeccao():
    return render_template('etapas_confeccao.html')

@flask_app.route('/api/etapas_confeccao', methods=['POST'])
def criar_etapa_confeccao():
    try:
        data = request.get_json()
        
        nome = data.get('nome')
        tempo_estimado = data.get('tempo_estimado')
        descricao = data.get('descricao')
        observacoes = data.get('observacoes')
        maquina_id = data.get('maquina_id')
        ferramenta_id = data.get('ferramenta_id')
        mao_obra = data.get('mao_obra')
        custo_por_hora = data.get('custo_por_hora')

        if not nome:
            return jsonify({"status": "error", "message": "Nome da etapa é obrigatório"}), 400

        # Processar custo por hora se fornecido
        if custo_por_hora:
            custo_por_hora = custo_por_hora.replace('R$', '').replace('.', '').replace(',', '.').strip()
            custo_por_hora = float(custo_por_hora) if custo_por_hora else 0.0

        db = Database()
        resultado = db.criar_etapa_confeccao(
            nome, tempo_estimado, descricao, observacoes, maquina_id,
            ferramenta_id, mao_obra, custo_por_hora
        )
        db.close()

        if "sucesso" in resultado:
            return jsonify({"status": "success", "message": resultado["sucesso"], "id": resultado["id"]})
        else:
            return jsonify({"status": "error", "message": resultado["erro"]}), 400

    except Exception as e:
        print(f"[ERROR] Exceção ao criar etapa de confecção: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@flask_app.route('/api/etapas_confeccao', methods=['GET'])
def listar_etapas_confeccao():
    try:
        db = Database()
        etapas = db.listar_etapas_confeccao()
        db.close()

        if isinstance(etapas, list):
            # Serializar manualmente para evitar referências circulares
            etapas_safe = []
            for etapa in etapas:
                etapa_dict = {
                    'id': etapa.get('id'),
                    'nome': etapa.get('nome'),
                    'tipo': etapa.get('tipo'),
                    'equipamento_id': etapa.get('equipamento_id'),
                    'equipamento': etapa.get('equipamento'),
                    'material_id': etapa.get('material_id'),
                    'material': etapa.get('material'),
                    'tempo_estimado': etapa.get('tempo_estimado'),
                    'custo': float(etapa.get('custo')) if etapa.get('custo') else None,
                    'descricao': etapa.get('descricao'),
                    'observacoes': etapa.get('observacoes')
                }
                etapas_safe.append(etapa_dict)
            
            return jsonify({"status": "success", "etapas": etapas_safe})
        else:
            return jsonify({"status": "error", "message": etapas["erro"]}), 400

    except Exception as e:
        print(f"[ERROR] Exceção ao listar etapas de confecção: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@flask_app.route('/api/etapas_confeccao/<int:etapa_id>', methods=['GET'])
def buscar_etapa_confeccao(etapa_id):
    try:
        db = Database()
        etapa = db.buscar_etapa_confeccao_por_id(etapa_id)
        db.close()

        if isinstance(etapa, dict) and 'erro' in etapa:
            return jsonify({"status": "error", "message": etapa["erro"]}), 404
        return jsonify({"status": "success", "etapa": etapa})

    except Exception as e:
        print(f"[ERROR] Exceção ao buscar etapa de confecção: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@flask_app.route('/api/etapas_confeccao/<int:etapa_id>', methods=['PUT'])
def atualizar_etapa_confeccao(etapa_id):
    try:
        data = request.get_json()
        
        # Processar custo por hora se fornecido
        custo_por_hora = data.get('custo_por_hora')
        if custo_por_hora:
            custo_por_hora = custo_por_hora.replace('R$', '').replace('.', '').replace(',', '.').strip()
            custo_por_hora = float(custo_por_hora) if custo_por_hora else None

        db = Database()
        resultado = db.atualizar_etapa_confeccao(
            etapa_id=etapa_id,
            nome=data.get('nome'),
            tempo_estimado=data.get('tempo_estimado'),
            descricao=data.get('descricao'),
            observacoes=data.get('observacoes'),
            maquina_id=data.get('maquina_id'),
            ferramenta_id=data.get('ferramenta_id'),
            mao_obra=data.get('mao_obra'),
            custo_por_hora=custo_por_hora
        )
        db.close()

        if "sucesso" in resultado:
            return jsonify({"status": "success", "message": resultado["sucesso"]})
        else:
            return jsonify({"status": "error", "message": resultado["erro"]}), 400

    except Exception as e:
        print(f"[ERROR] Exceção ao atualizar etapa de confecção: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@flask_app.route('/api/etapas_confeccao/<int:etapa_id>', methods=['DELETE'])
def deletar_etapa_confeccao(etapa_id):
    try:
        db = Database()
        resultado = db.deletar_etapa_confeccao(etapa_id)
        db.close()

        if 'erro' in resultado:
            return jsonify({'status': 'error', 'message': resultado['erro']}), 404
        return jsonify({'status': 'success', 'message': 'Etapa excluída com sucesso'})

    except Exception as e:
        print(f"[ERROR] Exceção ao deletar etapa de confecção: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Rota para fracionamento de pacotes
@flask_app.route('/api/itens_estoque/<int:item_id>/fracionar', methods=['POST'])
def fracionar_pacote_estoque(item_id):
    try:
        # Obter dados JSON da requisição
        data = request.get_json()
        
        if not data:
            return jsonify({'status': 'error', 'message': 'Dados não fornecidos'}), 400
        
        quantidade_pacotes = data.get('quantidade_pacotes')
        
        # Validações básicas
        if not quantidade_pacotes:
            return jsonify({'status': 'error', 'message': 'Quantidade de pacotes é obrigatória'}), 400
        
        try:
            quantidade_pacotes = int(quantidade_pacotes)
            if quantidade_pacotes <= 0:
                return jsonify({'status': 'error', 'message': 'Quantidade deve ser maior que zero'}), 400
        except (ValueError, TypeError):
            return jsonify({'status': 'error', 'message': 'Quantidade deve ser um número válido'}), 400
        
        # Executar fracionamento
        db = Database()
        resultado = db.fracionar_pacote(item_id, quantidade_pacotes)
        db.close()
        
        if 'erro' in resultado:
            return jsonify({'status': 'error', 'message': resultado['erro']}), 400
        
        return jsonify({
            'status': 'success', 
            'message': resultado['sucesso'],
            'data': {
                'pacotes_fracionados': resultado['pacotes_fracionados'],
                'unidades_adicionadas': resultado['unidades_adicionadas'],
                'nova_quantidade_total': resultado['nova_quantidade_total']
            }
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Exceção ao fracionar pacote: {str(e)}")
        return jsonify({'status': 'error', 'message': f'Erro interno: {str(e)}'}), 500

# Rota para verificar se código já existe
@flask_app.route('/api/itens_estoque/verificar_codigo', methods=['POST'])
def verificar_codigo_existente():
    try:
        data = request.get_json()
        codigo = data.get('codigo')
        
        if not codigo:
            return jsonify({'status': 'error', 'message': 'Código é obrigatório'}), 400
        
        db = Database()
        resultado = db.verificar_codigo_existente(codigo)
        db.close()
        
        return jsonify({'existe': resultado}), 200
        
    except Exception as e:
        print(f"[ERROR] Exceção ao verificar código: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Rota para fracionamento por volume (frascos/garrafas)
@flask_app.route('/api/itens_estoque/<int:item_id>/fracionar_volume', methods=['POST'])
def fracionar_volume_estoque(item_id):
    try:
        # Obter dados JSON da requisição
        data = request.get_json()
        
        if not data:
            return jsonify({'status': 'error', 'message': 'Dados não fornecidos'}), 400
        
        quantidade_recipientes = data.get('quantidade_recipientes')
        volume_por_porcao = data.get('volume_por_porcao')
        total_porcoes = data.get('total_porcoes')
        
        # Validações básicas
        if not quantidade_recipientes:
            return jsonify({'status': 'error', 'message': 'Quantidade de recipientes é obrigatória'}), 400
        
        if not volume_por_porcao:
            return jsonify({'status': 'error', 'message': 'Volume por porção é obrigatório'}), 400
        
        if not total_porcoes:
            return jsonify({'status': 'error', 'message': 'Total de porções é obrigatório'}), 400
        
        try:
            quantidade_recipientes = int(quantidade_recipientes)
            volume_por_porcao = float(volume_por_porcao)
            total_porcoes = int(total_porcoes)
            
            if quantidade_recipientes <= 0:
                return jsonify({'status': 'error', 'message': 'Quantidade de recipientes deve ser maior que zero'}), 400
            
            if volume_por_porcao <= 0:
                return jsonify({'status': 'error', 'message': 'Volume por porção deve ser maior que zero'}), 400
            
            if total_porcoes <= 0:
                return jsonify({'status': 'error', 'message': 'Total de porções deve ser maior que zero'}), 400
                
        except (ValueError, TypeError):
            return jsonify({'status': 'error', 'message': 'Valores devem ser números válidos'}), 400
        
        # Executar fracionamento por volume
        db = Database()
        resultado = db.fracionar_volume(item_id, quantidade_recipientes, volume_por_porcao, total_porcoes)
        db.close()
        
        if 'erro' in resultado:
            return jsonify({'status': 'error', 'message': resultado['erro']}), 400
        
        return jsonify({
            'status': 'success', 
            'message': resultado['sucesso'],
            'data': {
                'recipientes_fracionados': resultado['recipientes_fracionados'],
                'porcoes_adicionadas': resultado['porcoes_adicionadas'],
                'volume_utilizado': resultado['volume_utilizado'],
                'nova_quantidade_total': resultado['nova_quantidade_total']
            }
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Exceção ao fracionar por volume: {str(e)}")
        return jsonify({'status': 'error', 'message': f'Erro interno: {str(e)}'}), 500

@flask_app.route('/api/itens_estoque/<int:item_id>/fracionar_peso', methods=['POST'])
def fracionar_peso_estoque(item_id):
    try:
        # Obter dados JSON da requisição
        data = request.get_json()
        
        if not data:
            return jsonify({'status': 'error', 'message': 'Dados não fornecidos'}), 400
        
        quantidade_embalagens = data.get('quantidade_embalagens')
        peso_por_porcao = data.get('peso_por_porcao')
        total_porcoes = data.get('total_porcoes')
        
        # Validações básicas
        if not quantidade_embalagens:
            return jsonify({'status': 'error', 'message': 'Quantidade de embalagens é obrigatória'}), 400
        
        if not peso_por_porcao:
            return jsonify({'status': 'error', 'message': 'Peso por porção é obrigatório'}), 400
        
        if not total_porcoes:
            return jsonify({'status': 'error', 'message': 'Total de porções é obrigatório'}), 400
        
        try:
            quantidade_embalagens = int(quantidade_embalagens)
            peso_por_porcao = float(peso_por_porcao)
            total_porcoes = int(total_porcoes)
            
            if quantidade_embalagens <= 0:
                return jsonify({'status': 'error', 'message': 'Quantidade de embalagens deve ser maior que zero'}), 400
            
            if peso_por_porcao <= 0:
                return jsonify({'status': 'error', 'message': 'Peso por porção deve ser maior que zero'}), 400
            
            if total_porcoes <= 0:
                return jsonify({'status': 'error', 'message': 'Total de porções deve ser maior que zero'}), 400
                
        except (ValueError, TypeError):
            return jsonify({'status': 'error', 'message': 'Valores devem ser números válidos'}), 400
        
        # Executar fracionamento por peso
        db = Database()
        resultado = db.fracionar_peso(item_id, quantidade_embalagens, peso_por_porcao, total_porcoes)
        db.close()
        
        if 'erro' in resultado:
            return jsonify({'status': 'error', 'message': resultado['erro']}), 400
        
        return jsonify({
            'status': 'success', 
            'message': resultado['sucesso'],
            'data': {
                'embalagens_fracionadas': resultado['embalagens_fracionadas'],
                'porcoes_adicionadas': resultado['porcoes_adicionadas'],
                'peso_utilizado': resultado['peso_utilizado'],
                'nova_quantidade_total': resultado['nova_quantidade_total']
            }
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Exceção ao fracionar por peso: {str(e)}")
        return jsonify({'status': 'error', 'message': f'Erro interno: {str(e)}'}), 500

# Rotas para Cálculo Proporcional de Materiais
@flask_app.route('/api/materiais/<int:material_id>/calcular_custo_proporcional', methods=['POST'])
def calcular_custo_proporcional_material(material_id):
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'status': 'error', 'message': 'Dados não fornecidos'}), 400
        
        dimensoes_necessarias = {
            'largura': float(data.get('largura', 0)),
            'comprimento': float(data.get('comprimento', 0)),
            'unidade': data.get('unidade', 'cm')
        }
        
        if dimensoes_necessarias['largura'] <= 0 or dimensoes_necessarias['comprimento'] <= 0:
            return jsonify({'status': 'error', 'message': 'Largura e comprimento devem ser maiores que zero'}), 400
        
        db = Database()
        resultado = db.calcular_custo_proporcional_material(material_id, dimensoes_necessarias)
        db.close()
        
        if 'erro' in resultado:
            return jsonify({'status': 'error', 'message': resultado['erro']}), 400
        
        return jsonify({
            'status': 'success',
            'message': 'Cálculo realizado com sucesso',
            'calculo': resultado
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Exceção ao calcular custo proporcional: {str(e)}")
        return jsonify({'status': 'error', 'message': f'Erro interno: {str(e)}'}), 500

@flask_app.route('/api/materiais/<int:material_id>/calcular_custo_linear', methods=['POST'])
def calcular_custo_por_metros_lineares(material_id):
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'status': 'error', 'message': 'Dados não fornecidos'}), 400
        
        metros_necessarios = float(data.get('metros_necessarios', 0))
        
        if metros_necessarios <= 0:
            return jsonify({'status': 'error', 'message': 'Metros necessários deve ser maior que zero'}), 400
        
        db = Database()
        resultado = db.calcular_custo_por_metros_lineares(material_id, metros_necessarios)
        db.close()
        
        if 'erro' in resultado:
            return jsonify({'status': 'error', 'message': resultado['erro']}), 400
        
        return jsonify({
            'status': 'success',
            'message': 'Cálculo realizado com sucesso',
            'calculo': resultado
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Exceção ao calcular custo linear: {str(e)}")
        return jsonify({'status': 'error', 'message': f'Erro interno: {str(e)}'}), 500

@flask_app.route('/api/materiais/<int:material_id>/registrar_consumo_proporcional', methods=['POST'])
def registrar_consumo_proporcional_material(material_id):
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'status': 'error', 'message': 'Dados não fornecidos'}), 400
        
        quantidade_consumida = float(data.get('quantidade_consumida', 0))
        tipo_consumo = data.get('tipo_consumo', 'area')  # 'area' ou 'linear'
        dimensoes_consumidas = data.get('dimensoes_consumidas', {})
        observacoes = data.get('observacoes', '')
        
        if quantidade_consumida <= 0:
            return jsonify({'status': 'error', 'message': 'Quantidade consumida deve ser maior que zero'}), 400
        
        if tipo_consumo not in ['area', 'linear']:
            return jsonify({'status': 'error', 'message': 'Tipo de consumo deve ser "area" ou "linear"'}), 400
        
        db = Database()
        resultado = db.registrar_consumo_proporcional(
            material_id, quantidade_consumida, tipo_consumo, dimensoes_consumidas, observacoes
        )
        db.close()
        
        if 'erro' in resultado:
            return jsonify({'status': 'error', 'message': resultado['erro']}), 400
        
        return jsonify({
            'status': 'success',
            'message': 'Consumo registrado com sucesso',
            'consumo': resultado
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Exceção ao registrar consumo proporcional: {str(e)}")
        return jsonify({'status': 'error', 'message': f'Erro interno: {str(e)}'}), 500

@flask_app.route('/api/materiais/buscar_por_dimensoes', methods=['GET'])
def buscar_materiais_por_dimensoes():
    """
    Busca materiais que suportam cálculo proporcional (bobinas, chapas, etc.)
    """
    try:
        db = Database()
        
        # Buscar materiais que possuem dimensões (área ou comprimento)
        db.cursor.execute("""
            SELECT i.id, i.nome, i.codigo, i.largura, i.comprimento, i.area, i.volume,
                   i.custo_atual, i.custo_medio, i.quantidade_atual,
                   ti.nome as tipo_item_nome, u.nome as unidade_medida_nome
            FROM itens_estoque i
            LEFT JOIN tipo_itens ti ON i.tipo_item_id = ti.id
            LEFT JOIN unidades_de_medida u ON i.unidade_medida_id = u.id
            WHERE (i.area > 0 OR (i.largura > 0 AND i.comprimento > 0)) 
               OR (i.comprimento > 50 AND i.largura IS NULL)
            ORDER BY i.nome
        """)
        
        materiais = db.cursor.fetchall()
        db.close()
        
        # Formatar dados para exibição
        materiais_formatados = []
        for material in materiais:
            material_info = {
                'id': material['id'],
                'nome': material['nome'],
                'codigo': material['codigo'],
                'largura': float(material['largura'] or 0),
                'comprimento': float(material['comprimento'] or 0),
                'area': float(material['area'] or 0),
                'volume': float(material['volume'] or 0),
                'custo_atual': float(material['custo_atual'] or 0),
                'custo_medio': float(material['custo_medio'] or 0),
                'quantidade_atual': float(material['quantidade_atual'] or 0),
                'tipo_item_nome': material['tipo_item_nome'],
                'unidade_medida_nome': material['unidade_medida_nome'],
                'suporta_calculo_area': bool(material['area']) or (bool(material['largura']) and bool(material['comprimento'])),
                'suporta_calculo_linear': bool(material['comprimento']) and material['comprimento'] > 50
            }
            
            # Calcular área se não estiver definida mas tiver largura e comprimento
            if not material_info['area'] and material_info['largura'] > 0 and material_info['comprimento'] > 0:
                material_info['area'] = (material_info['largura'] * material_info['comprimento']) / 10000
            
            # Calcular custo por unidade
            if material_info['area'] > 0 and material_info['custo_atual'] > 0:
                material_info['custo_por_m2'] = material_info['custo_atual'] / material_info['area']
            else:
                material_info['custo_por_m2'] = 0
            
            if material_info['comprimento'] > 50 and material_info['custo_atual'] > 0:
                comprimento_metros = material_info['comprimento'] / 100  # cm para metros
                material_info['custo_por_metro'] = material_info['custo_atual'] / comprimento_metros
            else:
                material_info['custo_por_metro'] = 0
            
            materiais_formatados.append(material_info)
        
        return jsonify({
            'status': 'success',
            'materiais': materiais_formatados
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Exceção ao buscar materiais por dimensões: {str(e)}")
        return jsonify({'status': 'error', 'message': f'Erro interno: {str(e)}'}), 500

# Rotas para verificação e atualização de preços
@flask_app.route('/api/precos/atualizar', methods=['POST'])
def atualizar_precos_alternativos():
    """Rota alternativa para atualização de preços (compatibilidade com frontend)"""
    return atualizar_precos()

@flask_app.route('/api/produtos/atualizar-precos', methods=['POST'])
def atualizar_precos():
    """
    Aplica as atualizações de preços nos produtos selecionados
    """
    try:
        data = request.get_json()
        produtos = data.get('produtos', [])
        
        if not produtos:
            return jsonify({'status': 'error', 'message': 'Nenhum produto fornecido para atualização'}), 400
        
        db = Database()
        resultado = db.aplicar_atualizacao_precos(produtos)
        db.close()
        
        return jsonify({
            'status': 'success',
            'atualizados': resultado['atualizados'],
            'erros': resultado['erros']
        })
        
    except Exception as e:
        print(f"Erro ao atualizar preços: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@flask_app.route('/api/produtos/verificar-alteracoes-precos', methods=['POST'])
def verificar_alteracoes_precos():
    """
    Verifica se houve alterações nos custos de materiais ou máquinas
    que possam impactar os preços dos produtos
    """
    try:
        db = Database()
        
        # Verificar alterações nos últimos dias (configurável)
        dias_verificacao = request.json.get('dias', 7) if request.json else 7
        
        alteracoes_detectadas = db.verificar_alteracoes_custos(dias_verificacao)
        
        if alteracoes_detectadas:
            resultado_impacto = db.calcular_impacto_alteracoes_precos(alteracoes_detectadas)
            
            # Extrair o array de produtos do resultado
            produtos_afetados = resultado_impacto.get('produtos_afetados', [])
            
            # Converter para formato JSON-safe
            alteracoes_safe = convert_values_to_json_safe(alteracoes_detectadas)
            produtos_safe = convert_values_to_json_safe(produtos_afetados)
            
            return jsonify({
                'alteracoes_detectadas': True,
                'produtos_afetados': produtos_safe,
                'resumo': {
                    'total_produtos': len(produtos_afetados),
                    'materiais_alterados': len(alteracoes_detectadas.get('materiais', [])),
                    'maquinas_alteradas': len(alteracoes_detectadas.get('maquinas', []))
                },
                'detalhes_alteracoes': alteracoes_safe
            })
        else:
            return jsonify({
                'alteracoes_detectadas': False,
                'produtos_afetados': [],
                'resumo': {
                    'total_produtos': 0,
                    'materiais_alterados': 0,
                    'maquinas_alteradas': 0
                }
            })
        
        db.close()
    
    except Exception as e:
        print(f"Erro ao verificar alterações de preços: {e}")
        return jsonify({'error': str(e)}), 500

@flask_app.route('/api/produtos/verificar-mudancas-custos', methods=['POST'])
def verificar_mudancas_custos():
    """
    Verifica mudanças nos custos de materiais e máquinas específicos
    e calcula o impacto nos preços dos produtos
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'message': 'Dados não fornecidos'}), 400
        
        materiais_ids = data.get('materiais_ids', [])
        maquinas_ids = data.get('maquinas_ids', [])
        
        db = Database()
        
        # Buscar alterações reais usando o histórico
        alteracoes = {'materiais': [], 'maquinas': []}
        
        # Para cada material, buscar alterações recentes
        for material_id in materiais_ids:
            query = """
                SELECT ie.id, ie.nome, ie.custo_atual, ie.custo_medio
                FROM itens_estoque ie
                WHERE ie.id = %s
            """
            db.cursor.execute(query, (material_id,))
            material = db.cursor.fetchone()
            
            if material:
                # Buscar alterações no histórico
                custo_atual = float(material['custo_atual'] or material['custo_medio'] or 0)
                custo_anterior = db._calcular_custo_antes_periodo(material['id'], 7)  # 7 dias
                
                if abs(custo_atual - custo_anterior) > 0.01:
                    alteracoes['materiais'].append({
                        'id': material['id'],
                        'nome': material['nome'],
                        'custo_anterior': custo_anterior,
                        'custo_novo': custo_atual
                    })
        
        # Para cada máquina, buscar alterações no histórico
        for maquina_id in maquinas_ids:
            query_historico = """
                SELECT hcm.*, m.nome
                FROM historico_custos_maquinas hcm
                INNER JOIN maquinas m ON hcm.maquina_id = m.id
                WHERE hcm.maquina_id = %s
                ORDER BY hcm.data_alteracao DESC
                LIMIT 1
            """
            db.cursor.execute(query_historico, (maquina_id,))
            historico = db.cursor.fetchone()
            
            if historico:
                alteracoes['maquinas'].append({
                    'id': historico['maquina_id'],
                    'nome': historico['nome'],
                    'custo_por_hora_anterior': float(historico['hora_maquina_anterior'] or 0),
                    'custo_por_hora': float(historico['hora_maquina_nova'] or 0),
                    'metros_quadrados_por_hora': float(historico['metros_quadrados_nova'] or 0),
                    'data_alteracao': historico['data_alteracao'].strftime('%Y-%m-%d %H:%M:%S'),
                    'variacao_percentual': db._calcular_variacao_percentual(
                        float(historico['hora_maquina_anterior'] or 0),
                        float(historico['hora_maquina_nova'] or 0)
                    )
                })
            else:
                # Se não há histórico, buscar dados atuais da máquina
                query_maquina_atual = """
                    SELECT m.id, m.nome, m.hora_maquina, m.metros_quadrados_por_hora
                    FROM maquinas m
                    WHERE m.id = %s
                """
                db.cursor.execute(query_maquina_atual, (maquina_id,))
                maquina = db.cursor.fetchone()
                
                if maquina:
                    alteracoes['maquinas'].append({
                        'id': maquina['id'],
                        'nome': maquina['nome'],
                        'custo_por_hora_anterior': 0,  # Sem histórico, assumir 0
                        'custo_por_hora': float(maquina['hora_maquina'] or 0),
                        'metros_quadrados_por_hora': float(maquina['metros_quadrados_por_hora'] or 0),
                        'data_alteracao': 'Sem histórico disponível',
                        'variacao_percentual': 100  # 100% se não havia custo antes
                    })
        
        # Calcular impacto nos produtos
        resultado_impacto = db.calcular_impacto_alteracoes_precos(alteracoes)
        
        # Converter para formato JSON-safe
        produtos_safe = convert_values_to_json_safe(resultado_impacto['produtos_afetados'])
        alteracoes_safe = convert_values_to_json_safe(alteracoes)
        
        db.close()
        
        return jsonify({
            'status': 'success',
            'produtos_afetados': produtos_safe,
            'materiais_alterados': len(alteracoes_safe['materiais']),
            'maquinas_alteradas': len(alteracoes_safe['maquinas']),
            'total_produtos': resultado_impacto['total']
        })
        
    except Exception as e:
        print(f"[ERROR] Erro ao verificar mudanças de custos: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@flask_app.route('/api/produtos/simular-mudancas', methods=['GET'])
def simular_mudancas():
    """
    Simula detecção de mudanças de custos para teste do sistema
    """
    try:
        db = Database()
        
        # Buscar alguns materiais para simular mudanças
        query_materiais = """
            SELECT ie.id, ie.nome, ie.custo_atual, ie.custo_medio
            FROM itens_estoque ie
            WHERE ie.custo_atual > 0 OR ie.custo_medio > 0
            LIMIT 3
        """
        db.cursor.execute(query_materiais)
        materiais = db.cursor.fetchall()
        
        # Buscar algumas máquinas para simular mudanças
        query_maquinas = """
            SELECT m.id, m.nome, m.hora_maquina
            FROM maquinas m
            WHERE m.hora_maquina > 0
            LIMIT 2
        """
        db.cursor.execute(query_maquinas)
        maquinas = db.cursor.fetchall()
        
        # Simular alterações
        alteracoes = {'materiais': [], 'maquinas': []}
        
        for material in materiais:
            custo_atual = float(material['custo_atual'] or material['custo_medio'] or 0)
            custo_anterior = custo_atual * 0.85  # Simular 15% de aumento
            
            alteracoes['materiais'].append({
                'id': material['id'],
                'nome': material['nome'],
                'custo_anterior': custo_anterior,
                'custo_novo': custo_atual
            })
        
        for maquina in maquinas:
            custo_atual = float(maquina['hora_maquina'] or 0)
            custo_anterior = custo_atual * 0.85  # Simular 15% de aumento
            
            alteracoes['maquinas'].append({
                'id': maquina['id'],
                'nome': maquina['nome'],
                'custo_por_hora': custo_atual,
                'custo_anterior': custo_anterior
            })
        
        # Calcular impacto nos produtos
        resultado_impacto = db.calcular_impacto_alteracoes_precos(alteracoes)
        
        # Converter para formato JSON-safe
        produtos_safe = convert_values_to_json_safe(resultado_impacto['produtos_afetados'])
        alteracoes_safe = convert_values_to_json_safe(alteracoes)
        
        db.close()
        
        return jsonify({
            'status': 'success',
            'produtos_afetados': produtos_safe,
            'materiais_alterados': len(alteracoes_safe['materiais']),
            'maquinas_alteradas': len(alteracoes_safe['maquinas']),
            'total_produtos': resultado_impacto['total']
        })
        
    except Exception as e:
        print(f"[ERROR] Erro ao simular mudanças: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@flask_app.route('/api/produtos/<int:produto_id>/detalhes-calculo', methods=['GET'])
def obter_detalhes_calculo_produto(produto_id):
    """
    Obtém detalhes completos do produto para cálculo correto de preços,
    incluindo materiais com suas especificações dimensionais
    """
    try:
        db = Database()
        
        # Buscar dados básicos do produto
        query_produto = """
            SELECT p.id, p.nome, p.codigo, p.preco, p.margem_lucro,
                   cp.nome as categoria_nome
            FROM produtos p
            LEFT JOIN categoria_produtos cp ON p.categoria_id = cp.id
            WHERE p.id = %s
        """
        db.cursor.execute(query_produto, (produto_id,))
        produto = db.cursor.fetchone()
        
        if not produto:
            return jsonify({'error': 'Produto não encontrado'}), 404
        
        # Buscar materiais do produto com detalhes completos
        query_materiais = """
            SELECT pm.material_id, pm.quantidade_necessaria, pm.area_utilizada,
                   ie.nome, ie.custo_atual, ie.custo_medio, ie.largura, ie.comprimento,
                   ie.area, ie.unidades_por_pacote,
                   u.nome as unidade_nome, u.is_measurement
            FROM produtos_materiais pm
            INNER JOIN itens_estoque ie ON pm.material_id = ie.id
            LEFT JOIN unidades_de_medida u ON ie.unidade_medida_id = u.id
            WHERE pm.produto_id = %s
        """
        db.cursor.execute(query_materiais, (produto_id,))
        materiais = db.cursor.fetchall()
        
        # Verificar se há alterações recentes nos custos dos materiais (últimos 7 dias)
        query_alteracoes = """
            SELECT ee.item_id, 
                   (SELECT custo_unitario FROM entradas_estoque ee1 
                    WHERE ee1.item_id = ee.item_id 
                    ORDER BY ee1.data_entrada DESC, ee1.id DESC LIMIT 1) as custo_mais_recente,
                   (SELECT custo_unitario FROM entradas_estoque ee2 
                    WHERE ee2.item_id = ee.item_id 
                    ORDER BY ee2.data_entrada DESC, ee2.id DESC LIMIT 1 OFFSET 1) as custo_anterior
            FROM entradas_estoque ee
            WHERE ee.data_entrada >= (NOW() - INTERVAL 7 DAY)
            AND ee.item_id IN ({})
            GROUP BY ee.item_id
        """.format(','.join(['%s'] * len(materiais)))
        
        material_ids = [m['material_id'] for m in materiais]
        if material_ids:
            db.cursor.execute(query_alteracoes, material_ids)
            alteracoes_materiais = {row['item_id']: row for row in db.cursor.fetchall()}
        else:
            alteracoes_materiais = {}
        
        # Buscar custo das etapas considerando alterações recentes em máquinas
        # Primeiro verificar se há alterações recentes nos custos das máquinas (últimos 7 dias)
        query_maquinas_alteradas = """
            SELECT hm.maquina_id, 
                   (SELECT hora_maquina_nova 
                    FROM historico_custos_maquinas hm2 
                    WHERE hm2.maquina_id = hm.maquina_id 
                    AND hm2.data_alteracao >= (NOW() - INTERVAL 7 DAY)
                    ORDER BY hm2.data_alteracao DESC 
                    LIMIT 1) as valor_hora_mais_recente,
                   m.hora_maquina as valor_hora_atual
            FROM historico_custos_maquinas hm
            INNER JOIN maquinas m ON hm.maquina_id = m.id
            WHERE hm.data_alteracao >= (NOW() - INTERVAL 7 DAY)
            GROUP BY hm.maquina_id, m.hora_maquina
        """
        db.cursor.execute(query_maquinas_alteradas)
        alteracoes_maquinas = {row['maquina_id']: row for row in db.cursor.fetchall()}
        
        # Buscar etapas do produto
        query_etapas = """
            SELECT pe.equipamento_id, pe.equipamento_tipo, pe.custo_estimado, pe.tempo_estimado,
                   m.hora_maquina, m.nome as maquina_nome
            FROM produtos_etapas pe
            LEFT JOIN maquinas m ON pe.equipamento_id = m.id AND pe.equipamento_tipo = 'maquina'
            WHERE pe.produto_id = %s
        """
        db.cursor.execute(query_etapas, (produto_id,))
        etapas = db.cursor.fetchall()
        
        custo_etapas = 0
        for etapa in etapas:
            if etapa['equipamento_tipo'] == 'maquina' and etapa['equipamento_id']:
                # Para máquinas, sempre recalcular baseado no tempo e valor da hora atual/alterado
                tempo_horas = 0
                if etapa['tempo_estimado']:
                    tempo_str = str(etapa['tempo_estimado'])
                    if ':' in tempo_str:
                        partes = tempo_str.split(':')
                        horas = float(partes[0]) if len(partes) > 0 else 0
                        minutos = float(partes[1]) if len(partes) > 1 else 0
                        segundos = float(partes[2]) if len(partes) > 2 else 0
                        tempo_horas = horas + (minutos / 60.0) + (segundos / 3600.0)
                    else:
                        tempo_horas = float(tempo_str)
                
                # Verificar se há alteração recente no valor da hora desta máquina
                # Usar sempre o valor atual da máquina, já que o historico_custos_maquinas 
                # é usado apenas para detectar alterações, não para calcular valores
                valor_hora = float(etapa['hora_maquina'] or 0)
                print(f"[DEBUG] Máquina {etapa['maquina_nome']}: usando valor atual R$ {valor_hora:.2f}/h")
                
                custo_etapa = tempo_horas * valor_hora
                custo_etapas += custo_etapa
                print(f"[DEBUG] Etapa com {etapa['maquina_nome']}: {tempo_horas:.6f}h × R$ {valor_hora:.2f} = R$ {custo_etapa:.2f}")
            elif etapa['custo_estimado'] and etapa['custo_estimado'] > 0:
                # Para outros tipos de etapas (ferramentas, manual), usar custo estimado
                custo_etapas += float(etapa['custo_estimado'])
                print(f"[DEBUG] Etapa manual/ferramenta: usando custo estimado R$ {float(etapa['custo_estimado']):.2f}")
        
        print(f"[DEBUG] Custo total das etapas (considerando alterações): R$ {custo_etapas:.2f}")
        
        # Processar materiais para incluir informações necessárias
        materiais_processados = []
        for material in materiais:
            custo_atual = float(material['custo_atual'] or material['custo_medio'] or 0)
            
            # Verificar se houve alteração recente de preço
            alteracao = alteracoes_materiais.get(material['material_id'])
            custo_novo = None
            if alteracao and alteracao['custo_mais_recente']:
                custo_novo = float(alteracao['custo_mais_recente'])
                if abs(custo_novo - custo_atual) < 0.01:  # Se a diferença for muito pequena, ignorar
                    custo_novo = None
            
            material_info = {
                'id': material['material_id'],
                'nome': material['nome'],
                'custo_unitario': custo_atual,
                'custo_unitario_novo': custo_novo,  # Novo campo para alterações de preço
                'quantidade_necessaria': float(material['quantidade_necessaria'] or 0),
                'area_utilizada': float(material['area_utilizada'] or 0),
                'largura': float(material['largura']) if material['largura'] is not None else None,
                'comprimento': float(material['comprimento']) if material['comprimento'] is not None else None,
                'area_total': float(material['area']) if material['area'] is not None else 0,
                'unidades_por_pacote': material['unidades_por_pacote'],
                'is_measurement': bool(material['is_measurement']) if material['is_measurement'] is not None else False,
                'unidade_nome': material['unidade_nome']
            }
            
            # Calcular área total se não estiver definida
            if (not material_info['area_total'] or material_info['area_total'] == 0) and material_info['largura'] and material_info['comprimento']:
                material_info['area_total'] = material_info['largura'] * material_info['comprimento']
            
            materiais_processados.append(material_info)
        
        # Calcular custo total dos materiais usando lógica inteligente (como no frontend)
        custo_materiais = 0
        for material in materiais_processados:
            # Usar o custo mais recente se houver alteração
            custo_unitario = material['custo_unitario_novo'] or material['custo_unitario']
            
            # Aplicar a mesma lógica do frontend para calcular custo do material
            nome_material = material['nome']
            quantidade_necessaria = material['quantidade_necessaria']
            area_utilizada = material['area_utilizada']
            unidades_por_pacote = material['unidades_por_pacote']
            is_measurement = material['is_measurement']
            tem_dimensoes = bool(material['largura'] and material['comprimento'])
            area_total_material = material['area_total'] or 0
            
            # Lógica 1: Materiais vendidos por pacote
            if unidades_por_pacote and unidades_por_pacote > 1:
                custo_material = custo_unitario * quantidade_necessaria
                print(f"[DEBUG] Material {nome_material}: PACOTE - {quantidade_necessaria:.3f} pacotes × R${custo_unitario:.2f} = R${custo_material:.2f}")
            # Lógica 2: Materiais dimensionais - calcular preço por m²
            elif tem_dimensoes and is_measurement and area_total_material > 0:
                if area_utilizada == 0:
                    custo_material = 0
                    print(f"[DEBUG] Material {nome_material}: ÁREA ZERO - R$0.00")
                else:
                    preco_por_m2 = custo_unitario / area_total_material
                    area_esperada_para_quantidade = area_total_material * quantidade_necessaria
                    tolerancia = 0.01  # 1% de tolerância
                    
                    if area_esperada_para_quantidade > 0 and abs(area_utilizada - area_esperada_para_quantidade) / area_esperada_para_quantidade <= tolerancia:
                        # Usar quantidade quando a área utilizada é próxima à área esperada (chapas inteiras)
                        custo_material = custo_unitario * quantidade_necessaria
                        print(f"[DEBUG] Material {nome_material}: CHAPA INTEIRA - {quantidade_necessaria:.3f} chapas × R${custo_unitario:.2f} = R${custo_material:.2f}")
                    else:
                        # Usar cálculo proporcional por área (preço por m² × área utilizada)
                        custo_material = preco_por_m2 * area_utilizada
                        print(f"[DEBUG] Material {nome_material}: ÁREA PROPORCIONAL - {area_utilizada:.4f} m² de {area_total_material:.4f} m² × R${custo_unitario:.2f} = R${custo_material:.2f}")
            # Lógica 3: Materiais unitários (quantidade >= 1)
            elif quantidade_necessaria >= 1.0:
                custo_material = custo_unitario * quantidade_necessaria
                print(f"[DEBUG] Material {nome_material}: UNITÁRIO - quantidade {quantidade_necessaria:.3f} × R${custo_unitario:.2f} = R${custo_material:.2f}")
            # Lógica 4: Fallback para área quando quantidade < 1
            elif area_utilizada > 0:
                custo_material = custo_unitario * area_utilizada
                print(f"[DEBUG] Material {nome_material}: ÁREA FALLBACK - {area_utilizada:.4f} × R${custo_unitario:.2f} = R${custo_material:.2f}")
            else:
                # Fallback final: usar quantidade mesmo que seja < 1
                custo_material = custo_unitario * quantidade_necessaria
                print(f"[DEBUG] Material {nome_material}: FALLBACK FINAL - quantidade {quantidade_necessaria:.3f} × R${custo_unitario:.2f} = R${custo_material:.2f}")
            
            custo_materiais += custo_material
        
        # Calcular custo total e preço final
        custo_total = custo_materiais + custo_etapas
        margem = float(produto['margem_lucro'] or 0)
        preco_final = custo_total * (1 + margem / 100)
        
        # Converter dados para formato JSON-safe
        detalhes = {
            'produto': {
                'id': produto['id'],
                'nome': produto['nome'],
                'codigo': produto['codigo'],
                'preco': preco_final,
                'preco_atual': float(produto['preco'] or 0),
                'margem_lucro': margem,
                'categoria': produto['categoria_nome'],
                'custo_materiais': custo_materiais,
                'custo_etapas': custo_etapas,
                'custo_total': custo_total
            },
            'materiais': materiais_processados,
            'custo_etapas': custo_etapas
        }
        
        db.close()
        
        return jsonify(convert_values_to_json_safe(detalhes))
        
    except Exception as e:
        print(f"[ERROR] Erro ao obter detalhes do produto {produto_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Rotas para lidar com arquivos que podem gerar 404
@flask_app.route('/.well-known/appspecific/com.chrome.devtools.json')
def chrome_devtools():
    return '', 404

# Endpoint para servir imagens de produtos com compressão
@flask_app.route('/api/produtos/<int:produto_id>/imagem', methods=['GET'])
def get_produto_imagem(produto_id):
    """Retorna a imagem do produto (comprimida ou completa)"""
    try:
        from flask import Response
        
        quality = request.args.get('quality', 'compressed')  # 'compressed' ou 'full'
        
        db = Database()
        
        # Buscar anexos do produto (imagens)
        anexos = db.listar_anexos_produto(produto_id)
        
        # Filtrar apenas imagens
        imagens = [anexo for anexo in anexos if anexo.get('tipo_mime', '').startswith('image/')]
        
        if not imagens:
            db.close()
            return jsonify({'status': 'error', 'message': 'Imagem não encontrada'}), 404
            
        # Pegar o primeiro anexo de imagem como capa
        primeiro_anexo_id = imagens[0]['id']
        anexo = db.buscar_anexo_produto(primeiro_anexo_id)
        db.close()
        
        if not anexo or not anexo.get('conteudo_blob'):
            return jsonify({'status': 'error', 'message': 'Dados da imagem não encontrados'}), 404
            
        try:
            from PIL import Image
            import io
            
            # Carregar a imagem dos dados BLOB
            image_data = anexo['conteudo_blob']
            image = Image.open(io.BytesIO(image_data))
            
            # Configurar qualidade baseada no parâmetro
            if quality == 'compressed':
                # Redimensionar para thumbnail e comprimir
                image.thumbnail((300, 300), Image.Resampling.LANCZOS)
                output_quality = 60
            else:  # full quality
                # Manter tamanho original mas com boa qualidade
                output_quality = 90
                
            # Converter para JPEG se necessário
            if image.mode in ('RGBA', 'LA', 'P'):
                # Criar fundo branco para imagens com transparência
                background = Image.new('RGB', image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[-1] if 'A' in image.mode else None)
                image = background
            elif image.mode != 'RGB':
                image = image.convert('RGB')
                
            # Salvar imagem processada
            output = io.BytesIO()
            image.save(output, format='JPEG', quality=output_quality, optimize=True)
            output.seek(0)
            
            return Response(
                output.read(),
                mimetype='image/jpeg',
                headers={
                    'Cache-Control': 'public, max-age=3600',  # Cache por 1 hora
                    'Content-Disposition': f'inline; filename="produto_{produto_id}_{quality}.jpg"'
                }
            )
            
        except Exception as img_error:
            print(f"[ERROR] Erro ao processar imagem: {str(img_error)}")
            # Retornar a imagem original se houver erro no processamento
            return Response(
                anexo['conteudo_blob'],
                mimetype=anexo['tipo_mime'],
                headers={
                    'Cache-Control': 'public, max-age=3600',
                    'Content-Disposition': f'inline; filename="produto_{produto_id}_original.{anexo["tipo_mime"].split("/")[1]}"'
                }
            )
            
    except Exception as e:
        print(f"[ERROR] Exceção na API /api/produtos/{produto_id}/imagem: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    # GUI PyQt5 desabilitada temporariamente
    # app = QApplication(sys.argv)
    # gui = FlaskControlGUI()
    # gui.show()
    # sys.exit(app.exec_())
    
    # Executar apenas o servidor Flask
    print("Iniciando servidor Flask sem GUI...")
    import os
    # Usar porta do Render ou 8000 localmente
    port = int(os.environ.get('PORT', 8000))
    flask_app.run(host='0.0.0.0', port=port, debug=False)
