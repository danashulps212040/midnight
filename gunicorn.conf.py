# ====================================
# CONFIGURAÇÃO GUNICORN PARA RENDER
# ====================================

import os

# Configurações básicas
bind = f"0.0.0.0:{os.getenv('PORT', 8000)}"
workers = int(os.getenv('WEB_CONCURRENCY', 2))  # 2 workers para plano básico
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 120
keepalive = 5
preload_app = True

# Logs
accesslog = "-"  # stdout
errorlog = "-"   # stderr
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'
loglevel = "info"

# Configurações de processo
daemon = False
pidfile = None
user = None
group = None
tmp_upload_dir = "/tmp"

# Configurações de segurança
limit_request_line = 4096
limit_request_fields = 100
limit_request_field_size = 8190

# Hooks para logging
def when_ready(server):
    server.log.info("🚀 Servidor Gunicorn iniciado com sucesso!")
    server.log.info(f"👥 Workers: {workers}")
    server.log.info(f"🌐 Bind: {bind}")

def worker_int(worker):
    worker.log.info(f"💀 Worker {worker.pid} interrompido pelo usuário")

def on_exit(server):
    server.log.info("🛑 Servidor Gunicorn finalizado")

def post_worker_init(worker):
    worker.log.info(f"🔧 Worker {worker.pid} inicializado")

def pre_request(worker, req):
    worker.log.debug(f"📥 {req.method} {req.path}")

def post_request(worker, req, environ, resp):
    worker.log.debug(f"📤 {req.method} {req.path} - {resp.status}")