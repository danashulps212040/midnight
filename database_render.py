import os
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import Error, IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
import base64

class Database:
    def __init__(self):
        try:
            # Configuração para Render usando variáveis de ambiente
            database_url = os.environ.get('DATABASE_URL')
            
            if database_url:
                # Render fornece DATABASE_URL automaticamente
                self.connection = psycopg2.connect(database_url, sslmode='require')
            else:
                # Fallback para desenvolvimento local
                self.connection = psycopg2.connect(
                    host=os.environ.get('DB_HOST', 'localhost'),
                    database=os.environ.get('DB_NAME', 'midnight'),
                    user=os.environ.get('DB_USER', 'postgres'),
                    password=os.environ.get('DB_PASSWORD', ''),
                    port=os.environ.get('DB_PORT', '5432')
                )
            
            self.connection.autocommit = False
            self.cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            print("✅ Conexão com PostgreSQL estabelecida com sucesso!")
            
        except Error as e:
            print(f"❌ Erro ao conectar ao PostgreSQL: {e}")
            raise

    def close(self):
        if hasattr(self, 'connection') and self.connection:
            if hasattr(self, 'cursor'):
                self.cursor.close()
            self.connection.close()

    def commit(self):
        """Commit manual das transações"""
        self.connection.commit()

    def rollback(self):
        """Rollback das transações"""
        self.connection.rollback()

    # ===== MÉTODOS DE USUÁRIOS =====
    def criar_usuario(self, nome, email, senha, cargo, nivel_de_acesso, foto_de_perfil=None):
        try:
            # Verifica se o email já existe
            self.cursor.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
            if self.cursor.fetchone():
                return {"erro": "Email já cadastrado"}

            # Hash da senha
            senha_hash = generate_password_hash(senha)

            # Prepara a query (PostgreSQL usa RETURNING ao invés de lastrowid)
            query = """INSERT INTO usuarios 
                    (nome, email, senha, cargo, nivel_de_acesso, foto_de_perfil) 
                    VALUES (%s, %s, %s, %s, %s, %s) RETURNING id"""
            
            # Executa a query
            self.cursor.execute(query, (nome, email, senha_hash, cargo, 
                                      nivel_de_acesso, foto_de_perfil))
            user_id = self.cursor.fetchone()['id']
            self.commit()

            return {"sucesso": "Usuário criado com sucesso", "id": user_id}

        except Error as e:
            self.rollback()
            return {"erro": f"Erro ao criar usuário: {str(e)}"}

    def buscar_usuarios(self, filtro_nome=None, filtro_cargo=None, filtro_status=None):
        try:
            query = "SELECT id, nome, email, cargo, nivel_de_acesso, foto_de_perfil, status FROM usuarios WHERE 1=1"
            params = []

            if filtro_nome:
                query += " AND nome ILIKE %s"
                params.append(f"%{filtro_nome}%")

            if filtro_cargo and filtro_cargo != 'all':
                query += " AND cargo = %s"
                params.append(filtro_cargo)

            if filtro_status and filtro_status != 'all':
                query += " AND status = %s"
                params.append(filtro_status)

            print(f"[DEBUG] Executando query: {query}")
            print(f"[DEBUG] Parâmetros: {params}")
            self.cursor.execute(query, params)
            usuarios = self.cursor.fetchall()
            
            # Converte para lista de dicionários
            usuarios_list = []
            for usuario in usuarios:
                usuario_dict = dict(usuario)
                if usuario_dict.get('foto_de_perfil'):
                    usuario_dict['foto_de_perfil'] = base64.b64encode(usuario_dict['foto_de_perfil']).decode('utf-8')
                usuarios_list.append(usuario_dict)

            print(f"[DEBUG] Usuários recuperados: {len(usuarios_list)}")
            return usuarios_list

        except Error as e:
            print(f"[ERROR] Erro ao executar query: {str(e)}")
            return {"erro": f"Erro ao buscar usuários: {str(e)}"}

    def autenticar_usuario(self, login, senha):
        try:
            print(f"[DEBUG] autenticar_usuario - Buscando login: {login}")
            # Buscar por email OU nome
            self.cursor.execute("""
                SELECT id, nome, email, senha, cargo, nivel_de_acesso 
                FROM usuarios 
                WHERE email = %s OR nome = %s
            """, (login, login))
            usuario = self.cursor.fetchone()

            print(f"[DEBUG] autenticar_usuario - Usuario encontrado: {usuario is not None}")
            
            if not usuario:
                print("[DEBUG] autenticar_usuario - Usuário não encontrado")
                return {"erro": "Usuário não encontrado"}

            usuario_dict = dict(usuario)
            print(f"[DEBUG] autenticar_usuario - Verificando senha...")
            senha_valida = check_password_hash(usuario_dict['senha'], senha)
            print(f"[DEBUG] autenticar_usuario - Senha válida: {senha_valida}")

            if not senha_valida:
                print("[DEBUG] autenticar_usuario - Senha inválida")
                return {"erro": "Senha inválida"}

            # Remove a senha do retorno
            del usuario_dict['senha']
            print(f"[DEBUG] autenticar_usuario - Autenticação bem-sucedida para: {usuario_dict['nome']}")
            return {"sucesso": "Autenticação bem-sucedida", "usuario": usuario_dict}

        except Error as e:
            print(f"[ERROR] autenticar_usuario - Erro na autenticação: {str(e)}")
            return {"erro": f"Erro na autenticação: {str(e)}"}
        except Exception as e:
            print(f"[ERROR] autenticar_usuario - Erro inesperado: {str(e)}")
            return {"erro": f"Erro inesperado: {str(e)}"}

    # ===== PLACEHOLDER PARA OUTROS MÉTODOS =====
    # Nota: Apenas alguns métodos principais foram implementados como exemplo.
    # Os demais métodos do database.py original precisariam ser adaptados seguindo o mesmo padrão:
    # 1. Trocar mysql.connector por psycopg2
    # 2. Usar %s ao invés de %s para parâmetros (PostgreSQL)
    # 3. Usar RETURNING ao invés de lastrowid
    # 4. Usar ILIKE ao invés de LIKE para busca case-insensitive
    # 5. Ajustar tipos de dados específicos do MySQL para PostgreSQL

    def listar_produtos(self):
        """Exemplo de método adaptado para PostgreSQL"""
        try:
            self.cursor.execute("""
                SELECT p.id, p.codigo, p.nome, p.preco, p.status, p.estoque,
                       p.descricao, p.especificacoes_tecnicas as especificacoes,
                       p.custo_materiais, p.custo_etapas, p.margem_lucro,
                       p.categoria_id,
                       cp.nome as categoria, f.nome as fornecedor,
                       (SELECT COUNT(*) FROM produtos_etapas pe WHERE pe.produto_id = p.id) as etapas_count
                FROM produtos p
                LEFT JOIN categoria_produtos cp ON p.categoria_id = cp.id
                LEFT JOIN fornecedores f ON p.fornecedor_id = f.id
                ORDER BY p.nome
            """)
            produtos = self.cursor.fetchall()
            return [dict(produto) for produto in produtos]
        except Error as e:
            return {"erro": f"Erro ao listar produtos: {str(e)}"}

    # Adicione aqui os demais métodos adaptados conforme necessário