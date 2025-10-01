import os
import mysql.connector
from mysql.connector import Error, IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
import base64
import ssl

class Database:
    def __init__(self):
        try:
            # Configuração para produção (PlanetScale)
            if os.getenv('DATABASE_URL'):
                # Parse da URL de conexão do PlanetScale
                db_url = os.getenv('DATABASE_URL')
                
                # PlanetScale connection via SSL
                self.connection = mysql.connector.connect(
                    host=os.getenv('DB_HOST'),
                    user=os.getenv('DB_USERNAME'), 
                    password=os.getenv('DB_PASSWORD'),
                    database=os.getenv('DB_NAME'),
                    port=int(os.getenv('DB_PORT', 3306)),
                    ssl_disabled=False,
                    ssl_verify_cert=True,
                    ssl_verify_identity=True,
                    autocommit=True
                )
            else:
                # Configuração local (desenvolvimento)
                self.connection = mysql.connector.connect(
                    host=os.getenv('DB_HOST', 'localhost'),
                    user=os.getenv('DB_USERNAME', 'root'),
                    password=os.getenv('DB_PASSWORD', 'als32@#nss'),
                    database=os.getenv('DB_NAME', 'midnight')
                )
            
            self.cursor = self.connection.cursor(dictionary=True)
            print("[INFO] Conectado ao banco de dados com sucesso!")
            
        except Error as e:
            print(f"[ERROR] Erro ao conectar ao MySQL: {e}")
            # Em produção, você pode querer usar logging em vez de print
            
    def close(self):
        if hasattr(self, 'connection') and self.connection.is_connected():
            self.cursor.close()
            self.connection.close()

    # CREATE
    def criar_usuario(self, nome, email, senha, cargo, nivel_de_acesso, foto_de_perfil=None):
        try:
            # Verifica se o email já existe
            self.cursor.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
            if self.cursor.fetchone():
                return {"erro": "Email já cadastrado"}

            # Hash da senha
            senha_hash = generate_password_hash(senha)

            # Prepara a query
            query = """INSERT INTO usuarios 
                    (nome, email, senha, cargo, nivel_de_acesso, foto_de_perfil) 
                    VALUES (%s, %s, %s, %s, %s, %s)"""
            
            # Executa a query
            self.cursor.execute(query, (nome, email, senha_hash, cargo, 
                                      nivel_de_acesso, foto_de_perfil))
            self.connection.commit()

            return {"sucesso": "Usuário criado com sucesso", 
                    "id": self.cursor.lastrowid}

        except Error as e:
            self.connection.rollback()
            return {"erro": f"Erro ao criar usuário: {str(e)}"}

    # READ
    def buscar_usuarios(self, filtro_nome=None, filtro_cargo=None, filtro_status=None):
        try:
            query = "SELECT id, nome, email, cargo, nivel_de_acesso, foto_de_perfil, status FROM usuarios WHERE 1=1"
            params = []

            if filtro_nome:
                query += " AND (nome LIKE %s OR email LIKE %s)"
                params.extend([f"%{filtro_nome}%", f"%{filtro_nome}%"])

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
            print(f"[DEBUG] Usuários recuperados: {len(usuarios)}")

            # Converte BLOB para base64 para cada usuário
            for usuario in usuarios:
                if usuario['foto_de_perfil']:
                    usuario['foto_de_perfil'] = base64.b64encode(usuario['foto_de_perfil']).decode('utf-8')

            return usuarios

        except Error as e:
            print(f"[ERROR] Erro ao executar query: {str(e)}")
            return {"erro": f"Erro ao buscar usuários: {str(e)}"}

    def buscar_usuario_por_id(self, id):
        try:
            self.cursor.execute("SELECT id, nome, email, cargo, nivel_de_acesso, foto_de_perfil "
                               "FROM usuarios WHERE id = %s", (id,))
            usuario = self.cursor.fetchone()

            if usuario and usuario['foto_de_perfil']:
                usuario['foto_de_perfil'] = base64.b64encode(usuario['foto_de_perfil']).decode('utf-8')

            return usuario if usuario else {"erro": "Usuário não encontrado"}

        except Error as e:
            return {"erro": f"Erro ao buscar usuário: {str(e)}"}

    # UPDATE
    def atualizar_usuario(self, id, nome=None, email=None, senha=None, 
                         cargo=None, nivel_de_acesso=None, foto_de_perfil=None):
        try:
            # Verifica se o usuário existe
            self.cursor.execute("SELECT id FROM usuarios WHERE id = %s", (id,))
            if not self.cursor.fetchone():
                return {"erro": "Usuário não encontrado"}

            # Prepara os campos a serem atualizados
            updates = []
            params = []

            if nome:
                updates.append("nome = %s")
                params.append(nome)

            if email:
                # Verifica se o novo email já existe para outro usuário
                self.cursor.execute("SELECT id FROM usuarios WHERE email = %s AND id != %s", 
                                  (email, id))
                if self.cursor.fetchone():
                    return {"erro": "Email já está em uso"}
                updates.append("email = %s")
                params.append(email)

            if senha:
                updates.append("senha = %s")
                params.append(generate_password_hash(senha))

            if cargo:
                updates.append("cargo = %s")
                params.append(cargo)

            if nivel_de_acesso:
                updates.append("nivel_de_acesso = %s")
                params.append(nivel_de_acesso)

            if foto_de_perfil:
                updates.append("foto_de_perfil = %s")
                params.append(foto_de_perfil)

            if not updates:
                return {"erro": "Nenhum campo para atualizar"}

            # Monta e executa a query
            query = f"UPDATE usuarios SET {', '.join(updates)} WHERE id = %s"
            params.append(id)
            
            self.cursor.execute(query, params)
            self.connection.commit()

            return {"sucesso": "Usuário atualizado com sucesso"}

        except Error as e:
            self.connection.rollback()
            return {"erro": f"Erro ao atualizar usuário: {str(e)}"}

    # DELETE
    def deletar_usuario(self, id):
        try:
            # Verifica se o usuário existe
            self.cursor.execute("SELECT id FROM usuarios WHERE id = %s", (id,))
            if not self.cursor.fetchone():
                return {"erro": "Usuário não encontrado"}

            # Deleta o usuário
            self.cursor.execute("DELETE FROM usuarios WHERE id = %s", (id,))
            self.connection.commit()

            return {"sucesso": "Usuário deletado com sucesso"}

        except Error as e:
            self.connection.rollback()
            return {"erro": f"Erro ao deletar usuário: {str(e)}"}

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
            if usuario:
                print(f"[DEBUG] autenticar_usuario - Nome do usuario: {usuario['nome']}")
                print(f"[DEBUG] autenticar_usuario - Email do usuario: {usuario['email']}")

            if not usuario:
                print("[DEBUG] autenticar_usuario - Usuário não encontrado no banco")
                return {"erro": "Usuário não encontrado"}

            print(f"[DEBUG] autenticar_usuario - Verificando senha...")
            senha_valida = check_password_hash(usuario['senha'], senha)
            print(f"[DEBUG] autenticar_usuario - Senha válida: {senha_valida}")

            if not senha_valida:
                print("[DEBUG] autenticar_usuario - Senha incorreta")
                return {"erro": "Senha incorreta"}

            # Remove a senha do retorno
            del usuario['senha']
            print(f"[DEBUG] autenticar_usuario - Autenticação bem-sucedida para: {usuario['nome']}")
            return {"sucesso": "Autenticação bem-sucedida", "usuario": usuario}

        except Error as e:
            print(f"[ERROR] autenticar_usuario - Erro na autenticação: {str(e)}")
            return {"erro": f"Erro na autenticação: {str(e)}"}
        except Exception as e:
            print(f"[ERROR] autenticar_usuario - Erro inesperado: {str(e)}")
            return {"erro": f"Erro inesperado: {str(e)}"}

    # Adicione aqui todos os outros métodos do database.py original
    # Por brevidade, estou incluindo apenas os essenciais
    # Você deve copiar TODOS os métodos do arquivo original

    def listar_produtos(self):
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
            return self.cursor.fetchall()
        except Error as e:
            return {"erro": f"Erro ao listar produtos: {str(e)}"}

    # IMPORTANTE: Copie TODOS os métodos restantes do database.py original
    # Este é apenas um exemplo com os métodos essenciais
