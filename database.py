import mysql.connector
from mysql.connector import Error, IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
import base64

class Database:
    def __init__(self):
        try:
            self.connection = mysql.connector.connect(
                host='localhost',
                user='root',  # Altere conforme suas credenciais
                password='als32@#nss',  # Altere conforme suas credenciais
                database='midnight'
            )
            self.cursor = self.connection.cursor(dictionary=True)
        except Error as e:
            print(f"Erro ao conectar ao MySQL: {e}")

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
            
    # Métodos para Unidades de Medida
    def criar_unidade_medida(self, nome, is_measurement):
        try:
            # Verifica se a unidade já existe
            self.cursor.execute("SELECT id FROM unidades_de_medida WHERE nome = %s", (nome,))
            if self.cursor.fetchone():
                return {"erro": "Unidade de medida já cadastrada"}

            # Insere a nova unidade
            query = "INSERT INTO unidades_de_medida (nome, is_measurement) VALUES (%s, %s)"
            self.cursor.execute(query, (nome, is_measurement,))
            self.connection.commit()

            return {"sucesso": "Unidade de medida criada com sucesso", "id": self.cursor.lastrowid}

        except Error as e:
            self.connection.rollback()
            return {"erro": f"Erro ao criar unidade de medida: {str(e)}"}

    def listar_unidades_medida(self):
        try:
            self.cursor.execute("SELECT id, nome, is_measurement FROM unidades_de_medida ORDER BY nome")
            unidades = self.cursor.fetchall()
            return unidades

        except Error as e:
            return {"erro": f"Erro ao listar unidades de medida: {str(e)}"}

    # Métodos para Tipos de Itens
    def criar_tipo_item(self, nome, descricao=''):
        try:
            # Verifica se o tipo já existe
            self.cursor.execute("SELECT id FROM tipo_itens WHERE nome = %s", (nome,))
            if self.cursor.fetchone():
                return {"erro": "Tipo de item já cadastrado"}

            # Insere o novo tipo
            query = "INSERT INTO tipo_itens (nome, descricao) VALUES (%s, %s)"
            self.cursor.execute(query, (nome, descricao))
            self.connection.commit()

            return {"sucesso": "Tipo de item criado com sucesso", "id": self.cursor.lastrowid}

        except Error as e:
            self.connection.rollback()
            return {"erro": f"Erro ao criar tipo de item: {str(e)}"}

    def listar_tipos_itens(self):
        try:
            self.cursor.execute("SELECT id, nome, descricao FROM tipo_itens ORDER BY nome")
            tipos = self.cursor.fetchall()
            return tipos

        except Error as e:
            return {"erro": f"Erro ao listar tipos de itens: {str(e)}"}
            
    # Métodos para notificações
    def criar_notificacao(self, tipo, mensagem, item_id=None):
        try:
            query = "INSERT INTO notificacoes (tipo, mensagem, item_id) VALUES (%s, %s, %s)"
            self.cursor.execute(query, (tipo, mensagem, item_id))
            self.connection.commit()
            return {"sucesso": "Notificação criada com sucesso", "id": self.cursor.lastrowid}
        except Error as e:
            self.connection.rollback()
            return {"erro": f"Erro ao criar notificação: {str(e)}"}
    
    def listar_notificacoes(self):
        try:
            self.cursor.execute("""
                SELECT n.*, i.nome as item_nome 
                FROM notificacoes n 
                LEFT JOIN itens_estoque i ON n.item_id = i.id 
                ORDER BY n.data_criacao DESC
            """)
            return self.cursor.fetchall()
        except Error as e:
            return {"erro": f"Erro ao listar notificações: {str(e)}"}
    
    def marcar_notificacao_como_lida(self, notificacao_id):
        try:
            self.cursor.execute("UPDATE notificacoes SET lida = TRUE WHERE id = %s", (notificacao_id,))
            self.connection.commit()
            return {"sucesso": "Notificação marcada como lida"}
        except Error as e:
            self.connection.rollback()
            return {"erro": f"Erro ao marcar notificação como lida: {str(e)}"}
    
    def verificar_itens_baixo_estoque(self):
        try:
            self.cursor.execute("""
                SELECT id, nome, quantidade_atual, estoque_minimo 
                FROM itens_estoque 
                WHERE quantidade_atual <= estoque_minimo
            """)
            return self.cursor.fetchall()
        except Error as e:
            return {"erro": f"Erro ao verificar itens com baixo estoque: {str(e)}"}

    # DELETE para itens_estoque
    def deletar_item_estoque(self, id):
        try:
            # Verifica se o item existe
            self.cursor.execute("SELECT id FROM itens_estoque WHERE id = %s", (id,))
            if not self.cursor.fetchone():
                return {"erro": "Item não encontrado"}

            # Deleta o item
            self.cursor.execute("DELETE FROM itens_estoque WHERE id = %s", (id,))
            self.connection.commit()

            return {"sucesso": "Item deletado com sucesso"}

        except Error as e:
            self.connection.rollback()
            return {"erro": f"Erro ao deletar item: {str(e)}"}

    # Autenticação
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
                print(f"[DEBUG] autenticar_usuario - Hash da senha: {usuario['senha'][:20]}...")

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

    # CREATE para itens_estoque
    def criar_item_estoque(self, nome, codigo, categoria_id, cor, quantidade_inicial, estoque_minimo, unidade_medida_id, fornecedor_id, localizacao_estoque, especificacoes_tecnicas, descricao, largura=None, comprimento=None, peso=None, tipo_item_id=None, unidades_por_pacote=None, espessura=None, volume=None, area=None, fabricante=None):
        try:
            # Verifica se o código já existe sem usar lock
            self.cursor.execute("SELECT id FROM itens_estoque WHERE codigo = %s", (codigo,))
            if self.cursor.fetchone():
                return {"erro": "Código já cadastrado"}
                
            # Calcular área automaticamente se largura e comprimento foram fornecidos
            if largura and comprimento and not area:
                # Área em m² = (largura em cm * comprimento em cm) / 10000
                area = (float(largura) * float(comprimento)) / 10000
                
            query = """INSERT INTO itens_estoque (
                nome, codigo, categoria_id, tipo_item_id, cor, quantidade_inicial, quantidade_atual, estoque_minimo,
                unidades_por_pacote, unidade_medida_id, fornecedor_id, fabricante, localizacao_estoque, especificacoes_tecnicas, descricao,
                largura, comprimento, espessura, volume, area, peso
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            print(f"[DEBUG DATABASE] Executando INSERT com volume: {volume} (tipo: {type(volume)})")
            
            self.cursor.execute(query, (
                nome, codigo, categoria_id, tipo_item_id, cor, quantidade_inicial, quantidade_inicial, estoque_minimo,
                unidades_por_pacote, unidade_medida_id, fornecedor_id, fabricante, localizacao_estoque, especificacoes_tecnicas, descricao,
                largura, comprimento, espessura, volume, area, peso
            ))
            
            # Verificar o que foi salvo no banco
            item_id = self.cursor.lastrowid
            self.cursor.execute("SELECT volume FROM itens_estoque WHERE id = %s", (item_id,))
            volume_salvo = self.cursor.fetchone()
            print(f"[DEBUG DATABASE] Volume salvo no banco: {volume_salvo['volume'] if volume_salvo else 'NULL'}")
            
            self.connection.commit()
            return {"sucesso": "Item de estoque criado com sucesso", "id": self.cursor.lastrowid}
        except Error as e:
            self.connection.rollback()
            if e.errno == 1062:  # MySQL error number for duplicate entry
                return {"erro": "Código já cadastrado"}
            return {"erro": f"Erro ao criar item de estoque: {str(e)}"}
            
    def criar_entrada_estoque(self, item_id, quantidade, data_entrada, fornecedor=None, nota_fiscal=None, custo_unitario=None, data_validade=None, lote=None, localizacao=None, observacoes=None):
        try:
            # Verifica se o item existe e busca dados atuais
            self.cursor.execute("SELECT quantidade_atual, custo_medio FROM itens_estoque WHERE id = %s", (item_id,))
            item_data = self.cursor.fetchone()
            if not item_data:
                return {"erro": "Item não encontrado"}

            # Insere a entrada de estoque
            query = """INSERT INTO entradas_estoque (item_id, quantidade, data_entrada, fornecedor, nota_fiscal, custo_unitario, data_validade, lote, localizacao, observacoes)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            self.cursor.execute(query, (item_id, quantidade, data_entrada, fornecedor, nota_fiscal, custo_unitario, data_validade, lote, localizacao, observacoes))
            
            # Calcula o novo custo médio se custo_unitario foi fornecido
            quantidade_atual = float(item_data['quantidade_atual']) if item_data['quantidade_atual'] is not None else 0.0
            custo_medio_atual = float(item_data['custo_medio']) if item_data['custo_medio'] is not None else 0.0
            quantidade = float(quantidade)
            
            if custo_unitario is not None and float(custo_unitario) > 0:
                custo_unitario = float(custo_unitario)
                
                # Fórmula do custo médio ponderado:
                # Novo custo médio = ((Qtd atual * Custo médio atual) + (Qtd entrada * Custo unitário)) / (Qtd atual + Qtd entrada)
                valor_total_atual = quantidade_atual * custo_medio_atual
                valor_entrada = quantidade * custo_unitario
                quantidade_total = quantidade_atual + quantidade
                
                if quantidade_total > 0:
                    novo_custo_medio = (valor_total_atual + valor_entrada) / quantidade_total
                else:
                    novo_custo_medio = custo_unitario
                
                # Atualiza a quantidade, o custo médio e o custo atual do item no estoque
                update_query = """UPDATE itens_estoque 
                                SET quantidade_atual = quantidade_atual + %s,
                                    custo_medio = %s,
                                    custo_atual = %s
                                WHERE id = %s"""
                self.cursor.execute(update_query, (quantidade, novo_custo_medio, custo_unitario, item_id))
            else:
                # Atualiza apenas a quantidade do item no estoque (sem custo unitário)
                update_query = """UPDATE itens_estoque 
                                SET quantidade_atual = quantidade_atual + %s 
                                WHERE id = %s"""
                self.cursor.execute(update_query, (quantidade, item_id))
            
            self.connection.commit()
            return {"sucesso": "Entrada de estoque registrada com sucesso", "id": self.cursor.lastrowid}
        except Error as e:
            self.connection.rollback()
            return {"erro": f"Erro ao registrar entrada de estoque: {str(e)}"}
            
    def buscar_itens_estoque(self):
        try:
            self.cursor.execute("SELECT id, nome, codigo FROM itens_estoque ORDER BY nome")
            return self.cursor.fetchall()
        except Error as e:
            return {"erro": f"Erro ao buscar itens do estoque: {str(e)}"}
            
    def buscar_item_estoque_por_id(self, item_id):
        try:
            print(f"Buscando item de estoque com ID: {item_id}")
            self.cursor.execute("""
                SELECT i.id, i.nome, i.codigo, 
                       i.categoria_id, c.nome as categoria_nome,
                       i.tipo_item_id, ti.nome as tipo_item_nome,
                       i.cor, i.quantidade_inicial, i.quantidade_atual, i.estoque_minimo, i.unidades_por_pacote,
                       i.unidade_medida_id, u.nome as unidade_medida_nome, 
                       i.fornecedor_id, f.nome as fornecedor_nome, i.fabricante,
                       i.localizacao_estoque, i.especificacoes_tecnicas, i.descricao, 
                       i.largura, i.comprimento, i.espessura, i.volume, i.area, i.peso, i.custo_medio, i.custo_atual,
                       COALESCE(u.is_measurement, 0) as is_measurement
                FROM itens_estoque i
                LEFT JOIN unidades_de_medida u ON i.unidade_medida_id = u.id
                LEFT JOIN tipo_itens ti ON i.tipo_item_id = ti.id
                LEFT JOIN categoria_itens_estoque c ON i.categoria_id = c.id
                LEFT JOIN fornecedores f ON i.fornecedor_id = f.id
                WHERE i.id = %s
            """, (item_id,))
            item = self.cursor.fetchone()
            
            if item:
                print(f"Item encontrado: {item}")
                print(f"[DEBUG] Campo is_measurement no item: {item.get('is_measurement')}")
                # Garantir que todos os campos existam, mesmo que sejam nulos
                campos_esperados = ['id', 'nome', 'codigo', 'categoria_id', 'categoria_nome', 'tipo_item_id', 'tipo_item_nome',
                                   'cor', 'quantidade_inicial', 'quantidade_atual', 'estoque_minimo', 
                                   'unidades_por_pacote', 'unidade_medida_id', 'unidade_medida_nome', 
                                   'fornecedor_id', 'fornecedor_nome', 'localizacao_estoque', 'especificacoes_tecnicas', 'descricao',
                                   'largura', 'comprimento', 'espessura', 'volume', 'area', 'peso', 'custo_medio', 'custo_atual', 'is_measurement']
                
                for campo in campos_esperados:
                    if campo not in item:
                        print(f"Campo '{campo}' não encontrado no item, adicionando como None")
                        item[campo] = None
                
                # Verificar se todos os campos estão presentes após a adição
                campos_faltantes = [campo for campo in campos_esperados if campo not in item]
                if campos_faltantes:
                    print(f"AVISO: Ainda faltam campos após a correção: {campos_faltantes}")
                        
                return item
            else:
                print(f"Item com ID {item_id} não encontrado")
                return {"erro": "Item não encontrado"}
        except Error as e:
            print(f"Erro ao buscar item do estoque com ID {item_id}: {str(e)}")
            return {"erro": f"Erro ao buscar item do estoque: {str(e)}"}

    def buscar_itens_estoque_completo(self):
        try:
            self.cursor.execute("""
                SELECT i.id, i.nome, i.codigo, 
                       COALESCE(c.nome, 'Sem categoria') as categoria,
                       COALESCE(ti.nome, 'Sem tipo') as tipo_item,
                       i.cor, i.quantidade_atual, 
                       i.estoque_minimo, COALESCE(u.nome, i.unidade_medida) as unidade_medida, 
                       COALESCE(f.nome, 'Sem fornecedor') as fornecedor, 
                       i.fabricante,
                       i.localizacao_estoque, i.status, i.largura, i.comprimento, i.peso, i.volume, i.custo_medio, i.custo_atual,
                       COALESCE(u.is_measurement, 0) as is_measurement
                FROM itens_estoque i
                LEFT JOIN unidades_de_medida u ON i.unidade_medida_id = u.id
                LEFT JOIN categoria_itens_estoque c ON i.categoria_id = c.id
                LEFT JOIN tipo_itens ti ON i.tipo_item_id = ti.id
                LEFT JOIN fornecedores f ON i.fornecedor_id = f.id
                ORDER BY i.nome
            """)
            return self.cursor.fetchall()
        except Error as e:
            return {"erro": f"Erro ao buscar itens do estoque: {str(e)}"}
            
    def criar_saida_estoque(self, item_id, quantidade, data_saida, motivo_saida, destino=None, localizacao=None, observacoes=None):
        try:
            # Verifica se o item existe e tem quantidade suficiente
            self.cursor.execute("SELECT quantidade_atual FROM itens_estoque WHERE id = %s", (item_id,))
            item = self.cursor.fetchone()
            if not item:
                return {"erro": "Item não encontrado"}
            
            if item['quantidade_atual'] < quantidade:
                return {"erro": "Quantidade insuficiente em estoque"}

            # Insere a saída de estoque
            query = """
                INSERT INTO saidas_estoque (item_id, quantidade, data_saida, motivo_saida, destino, localizacao, observacoes)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            self.cursor.execute(query, (item_id, quantidade, data_saida, motivo_saida, destino, localizacao, observacoes))
            
            # Atualiza a quantidade do item no estoque
            update_query = """
                UPDATE itens_estoque 
                SET quantidade_atual = quantidade_atual - %s 
                WHERE id = %s
            """
            self.cursor.execute(update_query, (quantidade, item_id))
            
            self.connection.commit()
            return {"sucesso": "Saída de estoque registrada com sucesso", "id": self.cursor.lastrowid}
        except Error as e:
            self.connection.rollback()
            return {"erro": f"Erro ao registrar saída de estoque: {str(e)}"}
            
    # UPDATE para itens_estoque
    def atualizar_item_estoque(self, item_id, nome=None, codigo=None, categoria_id=None, cor=None, 
                             estoque_minimo=None, unidade_medida_id=None, fornecedor_id=None, 
                             localizacao_estoque=None, especificacoes_tecnicas=None, descricao=None,
                             largura=None, comprimento=None, peso=None, tipo_item_id=None, 
                             unidades_por_pacote=None, espessura=None, volume=None, area=None, fabricante=None):
        try:
            # Verifica se o item existe
            self.cursor.execute("SELECT id FROM itens_estoque WHERE id = %s", (item_id,))
            if not self.cursor.fetchone():
                return {"erro": "Item não encontrado"}

            # Verifica se o código já existe para outro item
            if codigo:
                self.cursor.execute("SELECT id FROM itens_estoque WHERE codigo = %s AND id != %s", (codigo, item_id))
                if self.cursor.fetchone():
                    return {"erro": "Código já está em uso por outro item"}

            # Prepara os campos a serem atualizados
            updates = []
            params = []

            if nome:
                updates.append("nome = %s")
                params.append(nome)

            if codigo:
                updates.append("codigo = %s")
                params.append(codigo)

            if categoria_id:
                updates.append("categoria_id = %s")
                params.append(categoria_id)

            if tipo_item_id is not None:
                updates.append("tipo_item_id = %s")
                params.append(tipo_item_id)

            if cor:
                updates.append("cor = %s")
                params.append(cor)

            if estoque_minimo is not None:
                updates.append("estoque_minimo = %s")
                params.append(estoque_minimo)

            if unidades_por_pacote is not None:
                updates.append("unidades_por_pacote = %s")
                params.append(unidades_por_pacote)

            if unidade_medida_id:
                updates.append("unidade_medida_id = %s")
                params.append(unidade_medida_id)

            if fornecedor_id:
                updates.append("fornecedor_id = %s")
                params.append(fornecedor_id)

            if fabricante is not None:
                updates.append("fabricante = %s")
                params.append(fabricante)

            if localizacao_estoque:
                updates.append("localizacao_estoque = %s")
                params.append(localizacao_estoque)

            if especificacoes_tecnicas:
                updates.append("especificacoes_tecnicas = %s")
                params.append(especificacoes_tecnicas)

            if descricao:
                updates.append("descricao = %s")
                params.append(descricao)
                
            if largura is not None:
                updates.append("largura = %s")
                params.append(largura)
                
            if comprimento is not None:
                updates.append("comprimento = %s")
                params.append(comprimento)

            if espessura is not None:
                updates.append("espessura = %s")
                params.append(espessura)

            if volume is not None:
                updates.append("volume = %s")
                params.append(volume)

            # Calcular área automaticamente se largura e comprimento foram fornecidos
            if largura is not None and comprimento is not None and area is None:
                # Área em m² = (largura em cm * comprimento em cm) / 10000
                area = (float(largura) * float(comprimento)) / 10000

            if area is not None:
                updates.append("area = %s")
                params.append(area)
                
            if peso is not None:
                updates.append("peso = %s")
                params.append(peso)

            if not updates:
                return {"erro": "Nenhum campo para atualizar"}

            # Monta e executa a query
            query = f"UPDATE itens_estoque SET {', '.join(updates)} WHERE id = %s"
            params.append(item_id)
            
            self.cursor.execute(query, params)
            self.connection.commit()

            return {"sucesso": "Item atualizado com sucesso"}

        except Error as e:
            self.connection.rollback()
            return {"erro": f"Erro ao atualizar item: {str(e)}"}

    # CREATE para categoria_itens_estoque
    def criar_categoria_item_estoque(self, nome):
        try:
            # Verifica se a categoria já existe
            self.cursor.execute("SELECT id FROM categoria_itens_estoque WHERE nome = %s", (nome,))
            if self.cursor.fetchone():
                return {"erro": "Categoria já cadastrada"}

            query = "INSERT INTO categoria_itens_estoque (nome) VALUES (%s)"
            self.cursor.execute(query, (nome,))
            self.connection.commit()
            return {"sucesso": "Categoria criada com sucesso", "id": self.cursor.lastrowid}
        except Error as e:
            self.connection.rollback()
            return {"erro": f"Erro ao criar categoria: {str(e)}"}

    # READ para categoria_itens_estoque
    def listar_categorias_itens_estoque(self):
        try:
            self.cursor.execute("SELECT id, nome FROM categoria_itens_estoque ORDER BY nome")
            return self.cursor.fetchall()
        except Error as e:
            return {"erro": f"Erro ao listar categorias: {str(e)}"}
            
    # CREATE para fornecedores
    def criar_fornecedor(self, nome, cnpj=None, telefone=None, email=None, endereco=None, cidade=None, estado=None, 
                        cep=None, contato_nome=None, contato_telefone=None, contato_email=None, website=None, 
                        categoria_produtos=None, prazo_entrega=None, condicoes_pagamento=None, observacoes=None, 
                        status='Ativo'):
        try:
            # Verifica se o fornecedor já existe pelo nome
            self.cursor.execute("SELECT id FROM fornecedores WHERE nome = %s", (nome,))
            if self.cursor.fetchone():
                return {"erro": "Fornecedor com este nome já cadastrado"}
                
            # Verifica se o CNPJ já existe (se fornecido)
            if cnpj:
                self.cursor.execute("SELECT id FROM fornecedores WHERE cnpj = %s", (cnpj,))
                if self.cursor.fetchone():
                    return {"erro": "CNPJ já cadastrado para outro fornecedor"}
            
            query = """INSERT INTO fornecedores (
                nome, cnpj, telefone, email, endereco, cidade, estado, cep, 
                contato_nome, contato_telefone, contato_email, website, 
                categoria_produtos, prazo_entrega, condicoes_pagamento, observacoes, 
                status, data_criacao, data_atualizacao
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())"""
            
            self.cursor.execute(query, (
                nome, cnpj, telefone, email, endereco, cidade, estado, cep,
                contato_nome, contato_telefone, contato_email, website,
                categoria_produtos, prazo_entrega, condicoes_pagamento, observacoes,
                status
            ))
            
            self.connection.commit()
            return {"sucesso": "Fornecedor criado com sucesso", "id": self.cursor.lastrowid}
        except Error as e:
            self.connection.rollback()
            return {"erro": f"Erro ao criar fornecedor: {str(e)}"}
    
    # READ para fornecedores
    def listar_fornecedores(self):
        try:
            self.cursor.execute("SELECT id, nome, cnpj, telefone, email, status FROM fornecedores ORDER BY nome")
            return self.cursor.fetchall()
        except Error as e:
            return {"erro": f"Erro ao listar fornecedores: {str(e)}"}
    
    # READ para fornecedor específico
    def buscar_fornecedor_por_id(self, fornecedor_id):
        try:
            self.cursor.execute("SELECT * FROM fornecedores WHERE id = %s", (fornecedor_id,))
            fornecedor = self.cursor.fetchone()
            if not fornecedor:
                return {"erro": "Fornecedor não encontrado"}
            return fornecedor
        except Error as e:
            return {"erro": f"Erro ao buscar fornecedor: {str(e)}"}
    
    # UPDATE para fornecedores
    def atualizar_fornecedor(self, fornecedor_id, nome=None, cnpj=None, telefone=None, email=None, endereco=None, 
                           cidade=None, estado=None, cep=None, contato_nome=None, contato_telefone=None, 
                           contato_email=None, website=None, categoria_produtos=None, prazo_entrega=None, 
                           condicoes_pagamento=None, observacoes=None, status=None):
        try:
            # Verifica se o fornecedor existe
            self.cursor.execute("SELECT id FROM fornecedores WHERE id = %s", (fornecedor_id,))
            if not self.cursor.fetchone():
                return {"erro": "Fornecedor não encontrado"}
            
            # Verifica se o nome já existe para outro fornecedor
            if nome:
                self.cursor.execute("SELECT id FROM fornecedores WHERE nome = %s AND id != %s", (nome, fornecedor_id))
                if self.cursor.fetchone():
                    return {"erro": "Nome já está em uso por outro fornecedor"}
            
            # Verifica se o CNPJ já existe para outro fornecedor
            if cnpj:
                self.cursor.execute("SELECT id FROM fornecedores WHERE cnpj = %s AND id != %s", (cnpj, fornecedor_id))
                if self.cursor.fetchone():
                    return {"erro": "CNPJ já está em uso por outro fornecedor"}
            
            # Prepara os campos a serem atualizados
            updates = []
            params = []
            
            if nome:
                updates.append("nome = %s")
                params.append(nome)
            
            if cnpj:
                updates.append("cnpj = %s")
                params.append(cnpj)
            
            if telefone:
                updates.append("telefone = %s")
                params.append(telefone)
            
            if email:
                updates.append("email = %s")
                params.append(email)
            
            if endereco:
                updates.append("endereco = %s")
                params.append(endereco)
            
            if cidade:
                updates.append("cidade = %s")
                params.append(cidade)
            
            if estado:
                updates.append("estado = %s")
                params.append(estado)
            
            if cep:
                updates.append("cep = %s")
                params.append(cep)
            
            if contato_nome:
                updates.append("contato_nome = %s")
                params.append(contato_nome)
            
            if contato_telefone:
                updates.append("contato_telefone = %s")
                params.append(contato_telefone)
            
            if contato_email:
                updates.append("contato_email = %s")
                params.append(contato_email)
            
            if website:
                updates.append("website = %s")
                params.append(website)
            
            if categoria_produtos:
                updates.append("categoria_produtos = %s")
                params.append(categoria_produtos)
            
            if prazo_entrega:
                updates.append("prazo_entrega = %s")
                params.append(prazo_entrega)
            
            if condicoes_pagamento:
                updates.append("condicoes_pagamento = %s")
                params.append(condicoes_pagamento)
            
            if observacoes:
                updates.append("observacoes = %s")
                params.append(observacoes)
            
            if status:
                updates.append("status = %s")
                params.append(status)
            
            # Adiciona a data de atualização
            updates.append("data_atualizacao = NOW()")
            
            if not updates:
                return {"erro": "Nenhum campo para atualizar"}
            
            # Monta e executa a query
            query = f"UPDATE fornecedores SET {', '.join(updates)} WHERE id = %s"
            params.append(fornecedor_id)
            
            self.cursor.execute(query, params)
            self.connection.commit()
            
            return {"sucesso": "Fornecedor atualizado com sucesso"}
        except Error as e:
            self.connection.rollback()
            return {"erro": f"Erro ao atualizar fornecedor: {str(e)}"}
    
    def listar_entradas_estoque(self):
        """Retorna todas as entradas de estoque com informações do item"""
        try:
            query = """
                SELECT e.*, i.nome as item_nome
                FROM entradas_estoque e
                LEFT JOIN itens_estoque i ON e.item_id = i.id
                ORDER BY e.data_entrada DESC
            """
            self.cursor.execute(query)
            entradas = self.cursor.fetchall()
            
            # Formata as datas para o formato esperado
            for entrada in entradas:
                if entrada['data_entrada']:
                    entrada['data_entrada'] = entrada['data_entrada'].strftime('%Y-%m-%d')
                if entrada['data_validade']:
                    entrada['data_validade'] = entrada['data_validade'].strftime('%Y-%m-%d')
                if entrada['data_criacao']:
                    entrada['data_criacao'] = entrada['data_criacao'].strftime('%Y-%m-%d %H:%M:%S')
            
            return entradas
        except Error as e:
            return {"erro": f"Erro ao listar entradas de estoque: {str(e)}"}
    
    # DELETE para fornecedores
    def deletar_fornecedor(self, fornecedor_id):
        try:
            # Verifica se o fornecedor existe
            self.cursor.execute("SELECT id FROM fornecedores WHERE id = %s", (fornecedor_id,))
            if not self.cursor.fetchone():
                return {"erro": "Fornecedor não encontrado"}
            
            # Verifica se o fornecedor está sendo usado em itens de estoque
            self.cursor.execute("SELECT id FROM itens_estoque WHERE fornecedor = (SELECT nome FROM fornecedores WHERE id = %s)", (fornecedor_id,))
            if self.cursor.fetchone():
                return {"erro": "Não é possível excluir o fornecedor pois está sendo usado em itens de estoque"}
            
            # Exclui o fornecedor
            self.cursor.execute("DELETE FROM fornecedores WHERE id = %s", (fornecedor_id,))
            self.connection.commit()
            
            return {"sucesso": "Fornecedor excluído com sucesso"}
        except Error as e:
            self.connection.rollback()
            return {"erro": f"Erro ao excluir fornecedor: {str(e)}"}

    def buscar_usuarios_ativos(self):
        """Retorna todos os usuários do sistema"""
        try:
            self.cursor.execute("""
                SELECT id, nome, email, cargo, nivel_de_acesso, status
                FROM usuarios 
                ORDER BY nome
            """)
            return self.cursor.fetchall()
        except Error as e:
            print(f"[ERROR] Erro ao buscar usuários: {str(e)}")
            return {"erro": f"Erro ao buscar usuários: {str(e)}"}

    def adicionar_favorito(self, usuario_id, produto_id):
        try:
            # Verificar se o favorito já existe
            self.cursor.execute("""
                SELECT id FROM favoritos_produtos 
                WHERE usuario_id = %s AND produto_id = %s
            """, (usuario_id, produto_id))
            
            if self.cursor.fetchone():
                return {"erro": "Este produto já está nos favoritos"}

            # Verificar se o produto existe
            self.cursor.execute("SELECT id FROM produtos WHERE id = %s", (produto_id,))
            if not self.cursor.fetchone():
                return {"erro": "Produto não encontrado"}

            # Inserir o favorito
            self.cursor.execute("""
                INSERT INTO favoritos_produtos (usuario_id, produto_id)
                VALUES (%s, %s)
            """, (usuario_id, produto_id))
            
            self.connection.commit()
            return {"sucesso": "Produto adicionado aos favoritos"}
        except Error as e:
            self.connection.rollback()
            return {"erro": f"Erro ao adicionar favorito: {str(e)}"}

    def remover_favorito(self, usuario_id, produto_id):
        try:
            # Verificar se o favorito existe
            self.cursor.execute("""
                SELECT id FROM favoritos_produtos 
                WHERE usuario_id = %s AND produto_id = %s
            """, (usuario_id, produto_id))
            
            if not self.cursor.fetchone():
                return {"erro": "Favorito não encontrado"}

            # Remover o favorito
            self.cursor.execute("""
                DELETE FROM favoritos_produtos 
                WHERE usuario_id = %s AND produto_id = %s
            """, (usuario_id, produto_id))
            
            self.connection.commit()
            return {"sucesso": "Produto removido dos favoritos"}
        except Error as e:
            self.connection.rollback()
            return {"erro": f"Erro ao remover favorito: {str(e)}"}

    def listar_favoritos(self, usuario_id):
        try:
            self.cursor.execute("""
                SELECT p.id as produto_id, p.nome, p.codigo, p.preco, p.estoque
                FROM favoritos_produtos fp
                INNER JOIN produtos p ON fp.produto_id = p.id
                WHERE fp.usuario_id = %s
                ORDER BY p.nome
            """, (usuario_id,))
            
            return self.cursor.fetchall()
        except Error as e:
            return {"status": "error", "message": f"Erro ao listar favoritos: {str(e)}"}

    # Métodos para Clientes
    def criar_cliente(self, nome, tipo_pessoa, cpf_cnpj, telefone, whatsapp, email, endereco, bairro, cidade, estado, pais, cep, observacoes=None, status='Ativo'):
        try:
            # Verifica se o cliente já existe pelo CPF/CNPJ (apenas se fornecido)
            if cpf_cnpj:
                self.cursor.execute("SELECT id FROM clientes WHERE cpf_cnpj = %s", (cpf_cnpj,))
                if self.cursor.fetchone():
                    return {"erro": "CPF/CNPJ já cadastrado"}

            query = """INSERT INTO clientes (
                nome, tipo_pessoa, cpf_cnpj, telefone, whatsapp, email, endereco, bairro, cidade, estado, pais, cep,
                observacoes, status, data_criacao, data_atualizacao
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())"""
            
            self.cursor.execute(query, (
                nome, tipo_pessoa, cpf_cnpj, telefone, whatsapp, email, endereco, bairro, cidade, estado, pais, cep,
                observacoes, status
            ))
            
            self.connection.commit()
            return {"sucesso": "Cliente criado com sucesso", "id": self.cursor.lastrowid}
        except Error as e:
            self.connection.rollback()
            return {"erro": f"Erro ao criar cliente: {str(e)}"}

    def listar_clientes(self):
        try:
            self.cursor.execute("SELECT id, nome, tipo_pessoa, cpf_cnpj, telefone, whatsapp, email, bairro, status FROM clientes ORDER BY nome")
            return self.cursor.fetchall()
        except Error as e:
            return {"erro": f"Erro ao listar clientes: {str(e)}"}

    def buscar_cliente_por_id(self, cliente_id):
        try:
            self.cursor.execute("SELECT * FROM clientes WHERE id = %s", (cliente_id,))
            cliente = self.cursor.fetchone()
            if not cliente:
                return {"erro": "Cliente não encontrado"}
            return cliente
        except Error as e:
            return {"erro": f"Erro ao buscar cliente: {str(e)}"}

    def atualizar_cliente(self, cliente_id, nome=None, tipo_pessoa=None, cpf_cnpj=None, telefone=None, whatsapp=None,
                          email=None, endereco=None, bairro=None, cidade=None, estado=None, pais=None, cep=None,
                          observacoes=None, status=None):
        try:
            # Verifica se o cliente existe
            self.cursor.execute("SELECT id FROM clientes WHERE id = %s", (cliente_id,))
            if not self.cursor.fetchone():
                return {"erro": "Cliente não encontrado"}
            
            # Verifica se o CPF/CNPJ já existe para outro cliente
            if cpf_cnpj:
                self.cursor.execute("SELECT id FROM clientes WHERE cpf_cnpj = %s AND id != %s", (cpf_cnpj, cliente_id))
                if self.cursor.fetchone():
                    return {"erro": "CPF/CNPJ já está em uso por outro cliente"}
            
            # Prepara os campos a serem atualizados
            updates = []
            params = []
            
            if nome:
                updates.append("nome = %s")
                params.append(nome)
            
            if tipo_pessoa:
                updates.append("tipo_pessoa = %s")
                params.append(tipo_pessoa)
            
            if cpf_cnpj:
                updates.append("cpf_cnpj = %s")
                params.append(cpf_cnpj)
            
            if telefone:
                updates.append("telefone = %s")
                params.append(telefone)
            
            if whatsapp:
                updates.append("whatsapp = %s")
                params.append(whatsapp)
            
            if email:
                updates.append("email = %s")
                params.append(email)
            
            if endereco:
                updates.append("endereco = %s")
                params.append(endereco)
            
            if bairro:
                updates.append("bairro = %s")
                params.append(bairro)
            
            if cidade:
                updates.append("cidade = %s")
                params.append(cidade)
            
            if estado:
                updates.append("estado = %s")
                params.append(estado)
            
            if pais:
                updates.append("pais = %s")
                params.append(pais)
            
            if cep:
                updates.append("cep = %s")
                params.append(cep)
            
            if observacoes:
                updates.append("observacoes = %s")
                params.append(observacoes)
            
            if status:
                updates.append("status = %s")
                params.append(status)
            
            # Adiciona a data de atualização
            updates.append("data_atualizacao = NOW()")
            
            if len(updates) == 1:  # Apenas data_atualizacao
                return {"erro": "Nenhum campo para atualizar"}
            
            # Monta e executa a query
            query = f"UPDATE clientes SET {', '.join(updates)} WHERE id = %s"
            params.append(cliente_id)
            
            self.cursor.execute(query, params)
            self.connection.commit()
            
            return {"sucesso": "Cliente atualizado com sucesso"}
        except Error as e:
            self.connection.rollback()
            return {"erro": f"Erro ao atualizar cliente: {str(e)}"}

    def deletar_cliente(self, cliente_id):
        try:
            # Verifica se o cliente existe
            self.cursor.execute("SELECT id FROM clientes WHERE id = %s", (cliente_id,))
            if not self.cursor.fetchone():
                return {"erro": "Cliente não encontrado"}
            
            # Exclui o cliente
            self.cursor.execute("DELETE FROM clientes WHERE id = %s", (cliente_id,))
            self.connection.commit()
            
            return {"sucesso": "Cliente excluído com sucesso"}
        except Error as e:
            self.connection.rollback()
            return {"erro": f"Erro ao excluir cliente: {str(e)}"}

    # Métodos para Categorias de Produtos
    def criar_categoria_produto(self, nome, descricao=''):
        try:
            # Verifica se a categoria já existe
            self.cursor.execute("SELECT id FROM categoria_produtos WHERE nome = %s", (nome,))
            if self.cursor.fetchone():
                return {"erro": "Categoria já cadastrada"}

            query = "INSERT INTO categoria_produtos (nome, descricao) VALUES (%s, %s)"
            self.cursor.execute(query, (nome, descricao))
            self.connection.commit()
            return {"sucesso": "Categoria criada com sucesso", "id": self.cursor.lastrowid}
        except Error as e:
            self.connection.rollback()
            return {"erro": f"Erro ao criar categoria: {str(e)}"}

    def listar_categorias_produtos(self):
        try:
            self.cursor.execute("SELECT id, nome, descricao FROM categoria_produtos ORDER BY nome")
            return self.cursor.fetchall()
        except Error as e:
            return {"erro": f"Erro ao listar categorias de produtos: {str(e)}"}

    # Métodos para Produtos
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

    def buscar_produtos_com_filtros(self, nome=None, categoria=None):
        """
        Busca produtos com filtros de nome e categoria, usando busca aproximada
        """
        try:
            query = """
                SELECT p.id, p.codigo, p.nome, p.preco, p.status, p.estoque,
                       p.descricao, p.especificacoes_tecnicas as especificacoes,
                       p.custo_materiais, p.custo_etapas, p.margem_lucro,
                       p.categoria_id,
                       cp.nome as categoria, f.nome as fornecedor,
                       (SELECT COUNT(*) FROM produtos_etapas pe WHERE pe.produto_id = p.id) as etapas_count
                FROM produtos p
                LEFT JOIN categoria_produtos cp ON p.categoria_id = cp.id
                LEFT JOIN fornecedores f ON p.fornecedor_id = f.id
                WHERE 1=1
            """
            
            params = []
            
            # Filtro por nome (busca aproximada, case insensitive)
            if nome and nome.strip():
                termo_normalizado = nome.strip().lower()
                query += " AND (LOWER(p.nome) LIKE %s OR LOWER(p.codigo) LIKE %s)"
                params.extend([f'%{termo_normalizado}%', f'%{termo_normalizado}%'])
            
            # Filtro por categoria
            if categoria and categoria.strip() and categoria.lower() != 'all':
                query += " AND cp.nome LIKE %s"
                params.append(f'%{categoria.strip()}%')
            
            query += " ORDER BY p.nome"
            
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
            
        except Error as e:
            return {"erro": f"Erro ao buscar produtos com filtros: {str(e)}"}

    def buscar_produto_por_codigo(self, codigo):
        """Busca um produto pelo código"""
        try:
            self.cursor.execute("SELECT id, codigo, nome FROM produtos WHERE codigo = %s", (codigo,))
            return self.cursor.fetchone()
        except Error as e:
            return None

    def verificar_codigo_produto_existe(self, codigo):
        """
        Verifica se um código já existe na tabela de produtos
        """
        try:
            cursor = self.mysql.cursor()
            cursor.execute("SELECT COUNT(*) FROM produtos WHERE codigo = %s", (codigo,))
            resultado = cursor.fetchone()[0]
            cursor.close()
            
            # Retorna True se existe (count > 0), False se não existe
            return resultado > 0
            
        except Exception as e:
            print(f"[ERROR] Erro ao verificar código de produto existente: {str(e)}")
            return False  # Em caso de erro, assume que não existe

    def inserir_produto(self, dados):
        """Insere um novo produto no banco de dados"""
        try:
            # Primeiro, buscar ou criar a categoria
            categoria_id = self.obter_categoria_id(dados['categoria'])
            
            if not categoria_id:
                print(f"[DEBUG] Erro: não foi possível obter categoria_id para: {dados['categoria']}")
                return None
            
            print(f"[DEBUG] Inserindo produto com categoria_id: {categoria_id}")
            
            query = """
                INSERT INTO produtos (codigo, nome, categoria_id, preco, margem_lucro, descricao, 
                                    especificacoes_tecnicas, custo_materiais, custo_etapas)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            self.cursor.execute(query, (
                dados['codigo'],
                dados['nome'], 
                categoria_id,
                dados['preco'],
                dados['margem'],
                dados['descricao'],
                dados['especificacoes'],
                dados['custo_materiais'],
                dados['custo_etapas']
            ))
            
            self.connection.commit()
            produto_id = self.cursor.lastrowid
            print(f"[DEBUG] Produto inserido com sucesso. ID: {produto_id}")
            return produto_id
            
        except Error as e:
            print(f"[DEBUG] Erro ao inserir produto: {str(e)}")
            import traceback
            traceback.print_exc()
            self.connection.rollback()
            return None

    def obter_categoria_id(self, nome_categoria):
        """Obtém o ID da categoria, criando se não existir"""
        try:
            # Buscar categoria existente
            self.cursor.execute("SELECT id FROM categoria_produtos WHERE nome = %s", (nome_categoria,))
            resultado = self.cursor.fetchone()
            
            # Como o cursor foi configurado com dictionary=True, o resultado é um dicionário
            if resultado and isinstance(resultado, dict) and 'id' in resultado:
                print(f"[DEBUG] Categoria encontrada: {resultado['id']} para nome: {nome_categoria}")
                return resultado['id']
            
            # Criar nova categoria se não existir
            print(f"[DEBUG] Criando nova categoria: {nome_categoria}")
            self.cursor.execute("INSERT INTO categoria_produtos (nome) VALUES (%s)", (nome_categoria,))
            self.connection.commit()
            categoria_id = self.cursor.lastrowid
            print(f"[DEBUG] Nova categoria criada com ID: {categoria_id}")
            return categoria_id
            
        except IntegrityError as e:
            # Se der erro de duplicação, tentar buscar novamente (pode ter sido criada por outro processo)
            if "Duplicate entry" in str(e):
                print(f"[DEBUG] Categoria já existe, tentando buscar novamente: {nome_categoria}")
                try:
                    # Rollback para limpar qualquer transação pendente
                    self.connection.rollback()
                    self.cursor.execute("SELECT id FROM categoria_produtos WHERE nome = %s", (nome_categoria,))
                    resultado = self.cursor.fetchone()
                    if resultado and isinstance(resultado, dict) and 'id' in resultado:
                        print(f"[DEBUG] Categoria encontrada após duplicação: {resultado['id']} para nome: {nome_categoria}")
                        return resultado['id']
                    else:
                        print(f"[DEBUG] Erro: categoria não encontrada mesmo após erro de duplicação. Resultado: {resultado}")
                        return None
                except Error as e2:
                    print(f"[DEBUG] Erro ao buscar categoria após duplicação: {str(e2)}")
                    return None
            else:
                print(f"[DEBUG] Erro de integridade não relacionado a duplicação: {str(e)}")
                return None
        except Error as e:
            print(f"[DEBUG] Erro ao obter/criar categoria: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

    def inserir_material_produto(self, dados):
        """Insere um material associado ao produto"""
        try:
            query = """
                INSERT INTO produtos_materiais (produto_id, material_id, quantidade_necessaria, 
                                              custo_unitario, subtotal, largura, altura, area_utilizada)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            print(f"[DEBUG] Inserindo material - largura: {dados.get('largura')}, altura: {dados.get('altura')}, area: {dados.get('area_utilizada')}")
            print(f"[DEBUG] Material ID a ser inserido: {dados['material_id']}")
            
            # Verificar se o material existe antes de inserir
            self.cursor.execute("SELECT id, nome FROM itens_estoque WHERE id = %s", (dados['material_id'],))
            material_existe = self.cursor.fetchone()
            if not material_existe:
                print(f"[ERROR] Material com ID {dados['material_id']} não encontrado na tabela itens_estoque")
                return None
            
            print(f"[DEBUG] Material encontrado: {material_existe['nome']} (ID: {material_existe['id']})")
            
            self.cursor.execute(query, (
                dados['produto_id'],
                dados['material_id'],
                dados.get('quantidade', dados.get('quantidade_necessaria')),  # Aceitar ambos os campos
                dados['preco_unitario'],
                dados['preco_total'],
                dados.get('largura'),
                dados.get('altura'),
                dados.get('area_utilizada')
            ))
            
            self.connection.commit()
            return self.cursor.lastrowid
            
        except Error as e:
            print(f"[DEBUG] Erro ao inserir material do produto: {str(e)}")
            import traceback
            traceback.print_exc()
            self.connection.rollback()
            return None

    def inserir_etapa_produto(self, dados):
        """Insere uma etapa associada ao produto"""
        try:
            query = """
                INSERT INTO produtos_etapas (produto_id, nome, tipo, equipamento_tipo, equipamento_id, equipamento_nome, 
                                           material_id, material_nome, tempo_estimado, custo_estimado)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            # Extrair IDs dos equipamentos e materiais se disponíveis
            equipamento_id = None
            equipamento_tipo = 'manual'  # Default
            
            if dados.get('equipamento_id'):
                equipamento_id_raw = dados['equipamento_id']
                # Se já é um inteiro, usar diretamente
                if isinstance(equipamento_id_raw, int):
                    equipamento_id = equipamento_id_raw
                    # Se temos um ID numérico, assumir que é máquina por compatibilidade
                    equipamento_tipo = 'maquina'
                # Se é string, processar
                elif isinstance(equipamento_id_raw, str):
                    if equipamento_id_raw.startswith('maquina_'):
                        equipamento_id = int(equipamento_id_raw.replace('maquina_', ''))
                        equipamento_tipo = 'maquina'
                    elif equipamento_id_raw.startswith('ferramenta_'):
                        equipamento_id = int(equipamento_id_raw.replace('ferramenta_', ''))
                        equipamento_tipo = 'ferramenta'
                    # Se é string numérica simples
                    elif equipamento_id_raw.isdigit():
                        equipamento_id = int(equipamento_id_raw)
                        equipamento_tipo = 'maquina'  # Assumir máquina por compatibilidade
            
            # Tratar material_id - deve ser int ou None
            material_id = None
            if dados.get('material_id'):
                material_id_str = str(dados['material_id'])
                if material_id_str.startswith('material_') and material_id_str != 'material_0':
                    try:
                        material_id = int(material_id_str.replace('material_', ''))
                    except ValueError:
                        material_id = None
                elif material_id_str.isdigit():
                    material_id = int(material_id_str)
                # Se for 'material_0' ou outro valor inválido, deixa como None
            
            print(f"[DEBUG] Inserindo etapa - equipamento_id: {equipamento_id}, equipamento_tipo: {equipamento_tipo}, material_id: {material_id}")
            
            self.cursor.execute(query, (
                dados['produto_id'],
                dados['nome'],
                dados.get('tipo', 'Manual'),
                equipamento_tipo,
                equipamento_id,
                dados.get('equipamento', ''),
                material_id,
                dados.get('material', ''),
                dados['tempo_estimado'],
                dados['custo']
            ))
            
            self.connection.commit()
            return self.cursor.lastrowid
            
        except Error as e:
            print(f"[DEBUG] Erro ao inserir etapa do produto: {str(e)}")
            import traceback
            traceback.print_exc()
            self.connection.rollback()
            return None

    # Método para buscar itens de estoque por termo de pesquisa
    def buscar_itens_estoque_por_termo(self, termo):
        try:
            query = """
                SELECT i.id, i.nome as descricao, i.quantidade_atual, i.custo_atual as preco_unitario,
                       COALESCE(ti.nome, 'Sem tipo') as tipo_item_nome,
                       i.unidades_por_pacote, i.unidade_medida_id, u.is_measurement,
                       i.largura, i.comprimento, i.area
                FROM itens_estoque i
                LEFT JOIN tipo_itens ti ON i.tipo_item_id = ti.id
                LEFT JOIN unidades_de_medida u ON i.unidade_medida_id = u.id
                WHERE i.nome LIKE %s OR i.codigo LIKE %s OR i.categoria LIKE %s
                ORDER BY i.nome
                LIMIT 20
            """
            termo_busca = f"%{termo}%"
            self.cursor.execute(query, (termo_busca, termo_busca, termo_busca))
            return self.cursor.fetchall()
        except Error as e:
            return {"erro": f"Erro ao buscar materiais: {str(e)}"}

    # Métodos para Máquinas
    def criar_maquina(self, nome, codigo, marca=None, tipo=None, numero_serie=None, data_aquisicao=None,
                     valor_aquisicao=0.0, hora_maquina=0.0, metros_quadrados_por_hora=0.0, estado='Novo', 
                     localizacao=None, responsavel=None, status='Ativa', especificacoes_tecnicas=None, observacoes=None):
        try:
            # Verifica se o código já existe
            self.cursor.execute("SELECT id FROM maquinas WHERE codigo = %s", (codigo,))
            if self.cursor.fetchone():
                return {"erro": "Código já cadastrado"}

            query = """INSERT INTO maquinas (
                nome, codigo, marca, tipo, numero_serie, data_aquisicao, valor_aquisicao, hora_maquina,
                metros_quadrados_por_hora, estado, localizacao, responsavel, status, especificacoes_tecnicas, observacoes
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

            self.cursor.execute(query, (
                nome, codigo, marca, tipo, numero_serie, data_aquisicao, valor_aquisicao, hora_maquina,
                metros_quadrados_por_hora, estado, localizacao, responsavel, status, especificacoes_tecnicas, observacoes
            ))
            
            self.connection.commit()
            return {"sucesso": "Máquina criada com sucesso", "id": self.cursor.lastrowid}
        except Error as e:
            self.connection.rollback()
            return {"erro": f"Erro ao criar máquina: {str(e)}"}

    def listar_maquinas(self):
        try:
            self.cursor.execute("""
                SELECT id, codigo, nome, marca, tipo, numero_serie, data_aquisicao, valor_aquisicao, 
                       hora_maquina, metros_quadrados_por_hora, estado, localizacao, responsavel, status, 
                       especificacoes_tecnicas, observacoes
                FROM maquinas ORDER BY nome
            """)
            return self.cursor.fetchall()
        except Error as e:
            return {"erro": f"Erro ao listar máquinas: {str(e)}"}

    def buscar_maquina_por_id(self, maquina_id):
        try:
            self.cursor.execute("SELECT * FROM maquinas WHERE id = %s", (maquina_id,))
            maquina = self.cursor.fetchone()
            if not maquina:
                return {"erro": "Máquina não encontrada"}
            return maquina
        except Error as e:
            return {"erro": f"Erro ao buscar máquina: {str(e)}"}

    def atualizar_maquina(self, maquina_id, nome=None, codigo=None, marca=None, tipo=None, numero_serie=None,
                         data_aquisicao=None, valor_aquisicao=None, hora_maquina=None, metros_quadrados_por_hora=None, 
                         estado=None, localizacao=None, responsavel=None, status=None, especificacoes_tecnicas=None, observacoes=None):
        try:
            # Primeiro, obter os valores atuais para registro de histórico
            self.cursor.execute("SELECT hora_maquina, metros_quadrados_por_hora FROM maquinas WHERE id = %s", (maquina_id,))
            valores_atuais = self.cursor.fetchone()
            if not valores_atuais:
                return {"erro": "Máquina não encontrada"}
            
            hora_maquina_anterior = float(valores_atuais['hora_maquina'] or 0)
            metros_anterior = float(valores_atuais['metros_quadrados_por_hora'] or 0)

            # Verifica se o código já existe para outra máquina
            if codigo:
                self.cursor.execute("SELECT id FROM maquinas WHERE codigo = %s AND id != %s", (codigo, maquina_id))
                if self.cursor.fetchone():
                    return {"erro": "Código já está em uso por outra máquina"}

            # Verificar se houve alteração nos custos para registrar histórico
            alteracao_custo = False
            if hora_maquina is not None and abs(float(hora_maquina) - hora_maquina_anterior) > 0.01:
                alteracao_custo = True
            if metros_quadrados_por_hora is not None and abs(float(metros_quadrados_por_hora) - metros_anterior) > 0.01:
                alteracao_custo = True

            # Registrar histórico antes da alteração, se houver mudança nos custos
            if alteracao_custo:
                print(f"[DEBUG] Registrando histórico de alteração para máquina {maquina_id}")
                historico_query = """
                    INSERT INTO historico_custos_maquinas 
                    (maquina_id, hora_maquina_anterior, hora_maquina_nova, 
                     metros_quadrados_anterior, metros_quadrados_nova, 
                     data_alteracao, observacoes)
                    VALUES (%s, %s, %s, %s, %s, NOW(), %s)
                """
                historico_values = (
                    maquina_id,
                    hora_maquina_anterior,
                    float(hora_maquina) if hora_maquina is not None else hora_maquina_anterior,
                    metros_anterior,
                    float(metros_quadrados_por_hora) if metros_quadrados_por_hora is not None else metros_anterior,
                    f"Alteração automática: hora/máquina de R${hora_maquina_anterior:.2f} para R${float(hora_maquina) if hora_maquina is not None else hora_maquina_anterior:.2f}"
                )
                self.cursor.execute(historico_query, historico_values)

            # Prepara os campos a serem atualizados
            updates = []
            params = []

            if nome:
                updates.append("nome = %s")
                params.append(nome)
            if codigo:
                updates.append("codigo = %s")
                params.append(codigo)
            if marca:
                updates.append("marca = %s")
                params.append(marca)
            if tipo:
                updates.append("tipo = %s")
                params.append(tipo)
            if numero_serie:
                updates.append("numero_serie = %s")
                params.append(numero_serie)
            if data_aquisicao:
                updates.append("data_aquisicao = %s")
                params.append(data_aquisicao)
            if valor_aquisicao is not None:
                updates.append("valor_aquisicao = %s")
                params.append(valor_aquisicao)
            if hora_maquina is not None:
                updates.append("hora_maquina = %s")
                params.append(hora_maquina)
            if metros_quadrados_por_hora is not None:
                updates.append("metros_quadrados_por_hora = %s")
                params.append(metros_quadrados_por_hora)
            if estado:
                updates.append("estado = %s")
                params.append(estado)
            if localizacao:
                updates.append("localizacao = %s")
                params.append(localizacao)
            if responsavel:
                updates.append("responsavel = %s")
                params.append(responsavel)
            if status:
                updates.append("status = %s")
                params.append(status)
            if especificacoes_tecnicas:
                updates.append("especificacoes_tecnicas = %s")
                params.append(especificacoes_tecnicas)
            if observacoes:
                updates.append("observacoes = %s")
                params.append(observacoes)

            if not updates:
                return {"erro": "Nenhum campo para atualizar"}

            # Adiciona a data de atualização
            updates.append("data_atualizacao = CURRENT_TIMESTAMP")

            # Monta e executa a query
            query = f"UPDATE maquinas SET {', '.join(updates)} WHERE id = %s"
            params.append(maquina_id)
            
            self.cursor.execute(query, params)
            self.connection.commit()

            return {"sucesso": "Máquina atualizada com sucesso"}

        except Error as e:
            self.connection.rollback()
            return {"erro": f"Erro ao atualizar máquina: {str(e)}"}

    def deletar_maquina(self, maquina_id):
        try:
            # Verifica se a máquina existe
            self.cursor.execute("SELECT id FROM maquinas WHERE id = %s", (maquina_id,))
            if not self.cursor.fetchone():
                return {"erro": "Máquina não encontrada"}

            # Verifica se há manutenções vinculadas
            self.cursor.execute("SELECT id FROM manutencoes WHERE maquina_id = %s", (maquina_id,))
            if self.cursor.fetchone():
                return {"erro": "Não é possível excluir a máquina pois há manutenções vinculadas"}

            # Exclui a máquina
            self.cursor.execute("DELETE FROM maquinas WHERE id = %s", (maquina_id,))
            self.connection.commit()

            return {"sucesso": "Máquina excluída com sucesso"}
        except Error as e:
            self.connection.rollback()
            return {"erro": f"Erro ao excluir máquina: {str(e)}"}

    # Métodos para Tipos de Máquinas
    def criar_tipo_maquina(self, nome):
        try:
            # Verifica se o tipo já existe
            self.cursor.execute("SELECT id FROM tipos_maquinas WHERE nome = %s", (nome,))
            if self.cursor.fetchone():
                return {"erro": "Tipo de máquina já cadastrado"}

            query = "INSERT INTO tipos_maquinas (nome) VALUES (%s)"
            self.cursor.execute(query, (nome,))
            self.connection.commit()
            return {"sucesso": "Tipo de máquina criado com sucesso", "id": self.cursor.lastrowid}
        except Error as e:
            self.connection.rollback()
            return {"erro": f"Erro ao criar tipo de máquina: {str(e)}"}

    def listar_tipos_maquinas(self):
        try:
            self.cursor.execute("SELECT id, nome, descricao FROM tipos_maquinas ORDER BY nome")
            return self.cursor.fetchall()
        except Error as e:
            return {"erro": f"Erro ao listar tipos de máquinas: {str(e)}"}

    # Métodos para Manutenções
    def criar_manutencao(self, maquina_id, tipo_manutencao, data_manutencao, responsavel=None,
                        fornecedor_empresa=None, descricao_servicos=None, custo=0.0, proxima_manutencao=None, observacoes=None):
        try:
            # Verifica se a máquina existe
            self.cursor.execute("SELECT id FROM maquinas WHERE id = %s", (maquina_id,))
            if not self.cursor.fetchone():
                return {"erro": "Máquina não encontrada"}

            query = """INSERT INTO manutencoes (
                maquina_id, tipo_manutencao, data_manutencao, responsavel, fornecedor_empresa,
                descricao_servicos, custo, proxima_manutencao, observacoes
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""

            self.cursor.execute(query, (
                maquina_id, tipo_manutencao, data_manutencao, responsavel, fornecedor_empresa,
                descricao_servicos, custo, proxima_manutencao, observacoes
            ))
            
            self.connection.commit()
            return {"sucesso": "Manutenção registrada com sucesso", "id": self.cursor.lastrowid}
        except Error as e:
            self.connection.rollback()
            return {"erro": f"Erro ao registrar manutenção: {str(e)}"}

    def listar_manutencoes(self, maquina_id=None):
        try:
            if maquina_id:
                query = """
                    SELECT m.*, maq.nome as maquina_nome, maq.codigo as maquina_codigo
                    FROM manutencoes m
                    LEFT JOIN maquinas maq ON m.maquina_id = maq.id
                    WHERE m.maquina_id = %s
                    ORDER BY m.data_manutencao DESC
                """
                self.cursor.execute(query, (maquina_id,))
            else:
                query = """
                    SELECT m.*, maq.nome as maquina_nome, maq.codigo as maquina_codigo
                    FROM manutencoes m
                    LEFT JOIN maquinas maq ON m.maquina_id = maq.id
                    ORDER BY m.data_manutencao DESC
                """
                self.cursor.execute(query)
            
            return self.cursor.fetchall()
        except Error as e:
            return {"erro": f"Erro ao listar manutenções: {str(e)}"}

    # Métodos para Ferramentas
    def criar_ferramenta(self, nome, codigo=None, tipo=None, descricao=None, status='Disponível',
                        localizacao=None, estado='Bom', responsavel=None, marca=None, modelo=None,
                        data_aquisicao=None, observacoes=None):
        try:
            # Verifica se o código já existe (se fornecido)
            if codigo:
                self.cursor.execute("SELECT id FROM ferramentas WHERE codigo = %s", (codigo,))
                if self.cursor.fetchone():
                    return {"erro": "Código já cadastrado"}

            query = """INSERT INTO ferramentas (
                nome, codigo, tipo, descricao, status, localizacao, estado, responsavel,
                marca, modelo, data_aquisicao, observacoes
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

            self.cursor.execute(query, (
                nome, codigo, tipo, descricao, status, localizacao, estado, responsavel,
                marca, modelo, data_aquisicao, observacoes
            ))
            
            self.connection.commit()
            return {"sucesso": "Ferramenta criada com sucesso", "id": self.cursor.lastrowid}
        except Error as e:
            self.connection.rollback()
            return {"erro": f"Erro ao criar ferramenta: {str(e)}"}

    def listar_ferramentas(self):
        try:
            self.cursor.execute("""
                SELECT id, nome, codigo, tipo, status, localizacao, estado, responsavel,
                       marca, modelo, data_aquisicao, observacoes
                FROM ferramentas ORDER BY nome
            """)
            return self.cursor.fetchall()
        except Error as e:
            return {"erro": f"Erro ao listar ferramentas: {str(e)}"}

    def buscar_ferramenta_por_id(self, ferramenta_id):
        try:
            self.cursor.execute("SELECT * FROM ferramentas WHERE id = %s", (ferramenta_id,))
            ferramenta = self.cursor.fetchone()
            if not ferramenta:
                return {"erro": "Ferramenta não encontrada"}
            return ferramenta
        except Error as e:
            return {"erro": f"Erro ao buscar ferramenta: {str(e)}"}

    def atualizar_ferramenta(self, ferramenta_id, nome=None, codigo=None, tipo=None, descricao=None,
                           status=None, localizacao=None, estado=None, responsavel=None, marca=None,
                           modelo=None, data_aquisicao=None, observacoes=None):
        try:
            # Verifica se a ferramenta existe
            self.cursor.execute("SELECT id FROM ferramentas WHERE id = %s", (ferramenta_id,))
            if not self.cursor.fetchone():
                return {"erro": "Ferramenta não encontrada"}

            # Verifica se o código já existe para outra ferramenta
            if codigo:
                self.cursor.execute("SELECT id FROM ferramentas WHERE codigo = %s AND id != %s", (codigo, ferramenta_id))
                if self.cursor.fetchone():
                    return {"erro": "Código já está em uso por outra ferramenta"}

            # Prepara os campos a serem atualizados
            updates = []
            params = []

            if nome:
                updates.append("nome = %s")
                params.append(nome)
            if codigo:
                updates.append("codigo = %s")
                params.append(codigo)
            if tipo:
                updates.append("tipo = %s")
                params.append(tipo)
            if descricao:
                updates.append("descricao = %s")
                params.append(descricao)
            if status:
                updates.append("status = %s")
                params.append(status)
            if localizacao:
                updates.append("localizacao = %s")
                params.append(localizacao)
            if estado:
                updates.append("estado = %s")
                params.append(estado)
            if responsavel:
                updates.append("responsavel = %s")
                params.append(responsavel)
            if marca:
                updates.append("marca = %s")
                params.append(marca)
            if modelo:
                updates.append("modelo = %s")
                params.append(modelo)
            if data_aquisicao:
                updates.append("data_aquisicao = %s")
                params.append(data_aquisicao)
            if observacoes:
                updates.append("observacoes = %s")
                params.append(observacoes)

            if not updates:
                return {"erro": "Nenhum campo para atualizar"}

            # Monta e executa a query
            query = f"UPDATE ferramentas SET {', '.join(updates)} WHERE id = %s"
            params.append(ferramenta_id)
            
            self.cursor.execute(query, params)
            self.connection.commit()

            return {"sucesso": "Ferramenta atualizada com sucesso"}

        except Error as e:
            self.connection.rollback()
            return {"erro": f"Erro ao atualizar ferramenta: {str(e)}"}

    def deletar_ferramenta(self, ferramenta_id):
        try:
            # Verifica se a ferramenta existe
            self.cursor.execute("SELECT id FROM ferramentas WHERE id = %s", (ferramenta_id,))
            if not self.cursor.fetchone():
                return {"erro": "Ferramenta não encontrada"}

            # Verifica se há etapas de confecção vinculadas
            self.cursor.execute("SELECT id FROM etapas_confeccao WHERE ferramenta_id = %s", (ferramenta_id,))
            if self.cursor.fetchone():
                return {"erro": "Não é possível excluir a ferramenta pois há etapas de confecção vinculadas"}

            # Exclui a ferramenta
            self.cursor.execute("DELETE FROM ferramentas WHERE id = %s", (ferramenta_id,))
            self.connection.commit()

            return {"sucesso": "Ferramenta excluída com sucesso"}
        except Error as e:
            self.connection.rollback()
            return {"erro": f"Erro ao excluir ferramenta: {str(e)}"}

    # Métodos para Etapas de Confecção
    def criar_etapa_confeccao(self, nome, tempo_estimado=None, descricao=None, observacoes=None,
                             maquina_id=None, ferramenta_id=None, mao_obra=None, custo_por_hora=0.0):
        try:
            query = """INSERT INTO etapas_confeccao (
                nome, tempo_estimado, descricao, observacoes, maquina_id, ferramenta_id, mao_obra, custo_por_hora
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""

            self.cursor.execute(query, (
                nome, tempo_estimado, descricao, observacoes, maquina_id, ferramenta_id, mao_obra, custo_por_hora
            ))
            
            self.connection.commit()
            return {"sucesso": "Etapa de confecção criada com sucesso", "id": self.cursor.lastrowid}
        except Error as e:
            self.connection.rollback()
            return {"erro": f"Erro ao criar etapa de confecção: {str(e)}"}

    def listar_etapas_confeccao(self):
        try:
            self.cursor.execute("""
                SELECT ec.id, ec.nome, ec.tempo_estimado, ec.descricao, ec.observacoes, 
                       ec.mao_obra, ec.custo_por_hora,
                       m.nome as maquina_nome, f.nome as ferramenta_nome
                FROM etapas_confeccao ec
                LEFT JOIN maquinas m ON ec.maquina_id = m.id
                LEFT JOIN ferramentas f ON ec.ferramenta_id = f.id
                ORDER BY ec.nome
            """)
            return self.cursor.fetchall()
        except Error as e:
            return {"erro": f"Erro ao listar etapas de confecção: {str(e)}"}

    def buscar_etapa_confeccao_por_id(self, etapa_id):
        try:
            self.cursor.execute("""
                SELECT ec.id, ec.nome, ec.tempo_estimado, ec.descricao, ec.observacoes, 
                       ec.mao_obra, ec.custo_por_hora, ec.maquina_id, ec.ferramenta_id,
                       m.nome as maquina_nome, f.nome as ferramenta_nome
                FROM etapas_confeccao ec
                LEFT JOIN maquinas m ON ec.maquina_id = m.id
                LEFT JOIN ferramentas f ON ec.ferramenta_id = f.id
                WHERE ec.id = %s
            """, (etapa_id,))
            etapa = self.cursor.fetchone()
            if not etapa:
                return {"erro": "Etapa de confecção não encontrada"}
            return etapa
        except Error as e:
            return {"erro": f"Erro ao buscar etapa de confecção: {str(e)}"}

    def atualizar_etapa_confeccao(self, etapa_id, nome=None, tempo_estimado=None, descricao=None,
                                 observacoes=None, maquina_id=None, ferramenta_id=None, mao_obra=None, custo_por_hora=None):
        try:
            # Verifica se a etapa existe
            self.cursor.execute("SELECT id FROM etapas_confeccao WHERE id = %s", (etapa_id,))
            if not self.cursor.fetchone():
                return {"erro": "Etapa de confecção não encontrada"}

            # Prepara os campos a serem atualizados
            updates = []
            params = []

            if nome:
                updates.append("nome = %s")
                params.append(nome)
            if tempo_estimado:
                updates.append("tempo_estimado = %s")
                params.append(tempo_estimado)
            if descricao:
                updates.append("descricao = %s")
                params.append(descricao)
            if observacoes:
                updates.append("observacoes = %s")
                params.append(observacoes)
            if maquina_id:
                updates.append("maquina_id = %s")
                params.append(maquina_id)
            if ferramenta_id:
                updates.append("ferramenta_id = %s")
                params.append(ferramenta_id)
            if mao_obra:
                updates.append("mao_obra = %s")
                params.append(mao_obra)
            if custo_por_hora is not None:
                updates.append("custo_por_hora = %s")
                params.append(custo_por_hora)

            if not updates:
                return {"erro": "Nenhum campo para atualizar"}

            # Adiciona a data de atualização
            updates.append("data_atualizacao = CURRENT_TIMESTAMP")

            # Monta e executa a query
            query = f"UPDATE etapas_confeccao SET {', '.join(updates)} WHERE id = %s"
            params.append(etapa_id)
            
            self.cursor.execute(query, params)
            self.connection.commit()

            return {"sucesso": "Etapa de confecção atualizada com sucesso"}

        except Error as e:
            self.connection.rollback()
            return {"erro": f"Erro ao atualizar etapa de confecção: {str(e)}"}

    def deletar_etapa_confeccao(self, etapa_id):
        try:
            # Verifica se a etapa existe
            self.cursor.execute("SELECT id FROM etapas_confeccao WHERE id = %s", (etapa_id,))
            if not self.cursor.fetchone():
                return {"erro": "Etapa de confecção não encontrada"}

            # Exclui a etapa
            self.cursor.execute("DELETE FROM etapas_confeccao WHERE id = %s", (etapa_id,))
            self.connection.commit()

            return {"sucesso": "Etapa de confecção excluída com sucesso"}
        except Error as e:
            self.connection.rollback()
            return {"erro": f"Erro ao excluir etapa de confecção: {str(e)}"}

    # Método para fracionamento de pacotes
    def fracionar_pacote(self, item_id, quantidade_pacotes):
        try:
            # Buscar dados completos do item original para verificar se é um pacote fechado
            self.cursor.execute("""
                SELECT i.*, ti.nome as tipo_item_nome
                FROM itens_estoque i
                LEFT JOIN tipo_itens ti ON i.tipo_item_id = ti.id
                WHERE i.id = %s
            """, (item_id,))
            
            item_original = self.cursor.fetchone()
            if not item_original:
                return {"erro": "Item não encontrado"}
            
            # Verificar se é um pacote fechado
            tipo_item_nome = item_original['tipo_item_nome'] or ''
            if 'pacote fechado' not in tipo_item_nome.lower():
                return {"erro": "Este item não é um pacote fechado"}
            
            # Verificar se tem unidades por pacote definidas
            unidades_por_pacote = item_original['unidades_por_pacote'] or 0
            if unidades_por_pacote <= 1:
                return {"erro": "Este pacote não tem unidades por pacote definidas"}
            
            # Verificar se há estoque suficiente
            quantidade_atual = item_original['quantidade_atual'] or 0
            if quantidade_atual < quantidade_pacotes:
                return {"erro": f"Estoque insuficiente. Disponível: {quantidade_atual} pacotes"}
            
            # Calcular total de unidades que serão fracionadas
            total_unidades = quantidade_pacotes * unidades_por_pacote
            
            # Calcular custo unitário correto para as unidades fracionadas
            custo_atual_pacote = float(item_original['custo_atual'] or 0)
            custo_medio_pacote = float(item_original['custo_medio'] or 0)
            
            # O custo unitário da unidade fracionada é o custo do pacote dividido pelas unidades por pacote
            custo_unitario_fracionado = custo_atual_pacote / unidades_por_pacote if custo_atual_pacote > 0 else 0
            custo_medio_fracionado = custo_medio_pacote / unidades_por_pacote if custo_medio_pacote > 0 else 0
            
            # 1. Reduzir a quantidade do item original (remover os pacotes)
            nova_quantidade_original = quantidade_atual - quantidade_pacotes
            self.cursor.execute("""
                UPDATE itens_estoque 
                SET quantidade_atual = %s
                WHERE id = %s
            """, (nova_quantidade_original, item_id))
            
            # 2. Buscar o ID do tipo "Unidade Fracionada"
            self.cursor.execute("""
                SELECT id FROM tipo_itens WHERE nome = 'Unidade Fracionada'
            """)
            tipo_unidade_fracionada = self.cursor.fetchone()
            if not tipo_unidade_fracionada:
                # Criar o tipo se não existir
                self.cursor.execute("""
                    INSERT INTO tipo_itens (nome, descricao) VALUES ('Unidade Fracionada', 'Porções fracionadas por volume')
                """)
                self.connection.commit()
                tipo_unidade_fracionada_id = self.cursor.lastrowid
            else:
                tipo_unidade_fracionada_id = tipo_unidade_fracionada['id']
            
            # 3. Verificar se já existe um item fracionado deste produto
            nome_item_fracionado = f"{item_original['nome']} (Unidades)"
            codigo_item_fracionado = f"{item_original['codigo']}-UN"
            
            self.cursor.execute("""
                SELECT id, quantidade_atual, custo_atual, custo_medio FROM itens_estoque 
                WHERE codigo = %s AND tipo_item_id = %s
            """, (codigo_item_fracionado, tipo_unidade_fracionada_id))
            
            item_fracionado_existente = self.cursor.fetchone()
            
            if item_fracionado_existente:
                # 4a. Se o item fracionado já existe, calcular novo custo médio ponderado
                quantidade_existente = float(item_fracionado_existente['quantidade_atual'] or 0)
                custo_medio_existente = float(item_fracionado_existente['custo_medio'] or 0)
                
                # Calcular novo custo médio ponderado
                # Fórmula: ((Qtd_Atual × Custo_Médio_Atual) + (Qtd_Entrada × Custo_Médio_Nova)) ÷ (Qtd_Atual + Qtd_Entrada)
                if quantidade_existente > 0 and custo_medio_existente > 0:
                    valor_total_existente = quantidade_existente * custo_medio_existente
                    valor_entrada = total_unidades * custo_medio_fracionado
                    quantidade_total = quantidade_existente + total_unidades
                    
                    if quantidade_total > 0:
                        novo_custo_medio = (valor_total_existente + valor_entrada) / quantidade_total
                    else:
                        novo_custo_medio = custo_medio_fracionado
                
                nova_quantidade_fracionada = quantidade_existente + total_unidades
                
                self.cursor.execute("""
                    UPDATE itens_estoque 
                    SET quantidade_atual = %s, custo_atual = %s, custo_medio = %s
                    WHERE id = %s
                """, (nova_quantidade_fracionada, custo_unitario_fracionado, novo_custo_medio, item_fracionado_existente['id']))
                
                item_fracionado_id = item_fracionado_existente['id']
                
                # Armazenar informações para o retorno
                custo_medio_anterior = custo_medio_existente
                quantidade_anterior = quantidade_existente
            else:
                # 4b. Se não existe, criar novo item fracionado
                query = """INSERT INTO itens_estoque (
                    nome, codigo, categoria_id, tipo_item_id, cor, quantidade_inicial, quantidade_atual, estoque_minimo,
                    unidades_por_pacote, unidade_medida_id, fornecedor_id, fabricante, localizacao_estoque, especificacoes_tecnicas, descricao,
                    largura, comprimento, espessura, volume, area, peso,
                    custo_atual, custo_medio
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                
                self.cursor.execute(query, (
                    nome_item_fracionado,
                    codigo_item_fracionado,
                    item_original['categoria_id'],
                    tipo_unidade_fracionada['id'],
                    item_original['cor'],
                    total_unidades,  # quantidade_inicial
                    total_unidades,  # quantidade_atual
                    item_original['estoque_minimo'],
                    1,  # unidades_por_pacote = 1 para item fracionado
                    item_original['unidade_medida_id'],
                    item_original['fornecedor_id'],
                    item_original['fabricante'],
                    item_original['localizacao_estoque'],
                    item_original['especificacoes_tecnicas'],
                    f"{item_original['descricao']} - Versão fracionada em unidades individuais" if item_original['descricao'] else "Versão fracionada em unidades individuais",
                    item_original['largura'],
                    item_original['comprimento'],
                    item_original['espessura'],
                    item_original['volume'],
                    item_original['area'],
                    item_original['peso'],
                    custo_unitario_fracionado,  # custo_atual
                    custo_medio_fracionado      # custo_medio
                ))
                
                item_fracionado_id = self.cursor.lastrowid
            
            # 5. Registrar a saída do item original (pacotes)
            self.cursor.execute("""
                INSERT INTO saidas_estoque (
                    item_id, quantidade, data_saida, motivo_saida, destino, observacoes
                ) VALUES (%s, %s, CURDATE(), %s, %s, %s)
            """, (
                item_id, 
                quantidade_pacotes, 
                'Fracionamento',
                'Conversão para unidades individuais',
                f'Fracionamento de {quantidade_pacotes} pacote(s) em {total_unidades} unidades individuais'
            ))
            
            # 6. Registrar a entrada do item fracionado (unidades) com custo unitário
            self.cursor.execute("""
                INSERT INTO entradas_estoque (
                    item_id, quantidade, data_entrada, custo_unitario, observacoes
                ) VALUES (%s, %s, CURDATE(), %s, %s)
            """, (
                item_fracionado_id,
                total_unidades,
                custo_unitario_fracionado,
                f'Entrada de {total_unidades} unidades individuais via fracionamento de {quantidade_pacotes} pacote(s) do item {item_original["nome"]}. Custo unitário: R$ {custo_unitario_fracionado:.4f}'
            ))
            
            self.connection.commit()
            
            # Preparar informações sobre o custo médio para o retorno
            if item_fracionado_existente:
                custo_info = {
                    "item_existia": True,
                    "quantidade_anterior": quantidade_anterior,
                    "custo_medio_anterior": custo_medio_anterior,
                    "nova_quantidade_total": nova_quantidade_fracionada,
                    "novo_custo_medio": novo_custo_medio,
                    "detalhes_calculo": f"Custo médio ponderado: ({quantidade_anterior:.0f} × R$ {custo_medio_anterior:.4f}) + ({total_unidades:.0f} × R$ {custo_medio_fracionado:.4f}) ÷ {nova_quantidade_fracionada:.0f} = R$ {novo_custo_medio:.4f}"
                }
            else:
                custo_info = {
                    "item_existia": False,
                    "quantidade_anterior": 0,
                    "custo_medio_anterior": 0,
                    "nova_quantidade_total": total_unidades,
                    "novo_custo_medio": custo_medio_fracionado,
                    "detalhes_calculo": f"Novo item criado com custo médio inicial de R$ {custo_medio_fracionado:.4f}"
                }
            
            return {
                "sucesso": f"Fracionamento realizado com sucesso! {quantidade_pacotes} pacote(s) convertido(s) em {total_unidades} unidades individuais. Custo unitário: R$ {custo_unitario_fracionado:.4f}",
                "pacotes_fracionados": quantidade_pacotes,
                "unidades_adicionadas": total_unidades,
                "item_original_id": item_id,
                "item_fracionado_id": item_fracionado_id,
                "item_fracionado_nome": nome_item_fracionado,
                "nova_quantidade_total": nova_quantidade_original,
                "custo_unitario_fracionado": custo_unitario_fracionado,
                "custo_medio_fracionado": custo_medio_fracionado,
                "custo_info": custo_info
            }
            
        except Error as e:
            self.connection.rollback()
            return {"erro": f"Erro ao fracionar pacote: {str(e)}"}
    
    # Método para fracionamento por volume (frascos/garrafas)
    def verificar_codigo_existente(self, codigo):
        """
        Verifica se um código já existe na tabela de itens_estoque
        """
        try:
            cursor = self.mysql.cursor()
            cursor.execute("SELECT COUNT(*) FROM itens_estoque WHERE codigo = %s", (codigo,))
            resultado = cursor.fetchone()[0]
            cursor.close()
            
            # Retorna True se existe (count > 0), False se não existe
            return resultado > 0
            
        except Exception as e:
            print(f"[ERROR] Erro ao verificar código existente: {str(e)}")
            return False  # Em caso de erro, assume que não existe

    def fracionar_volume(self, item_id, quantidade_recipientes, volume_por_porcao, total_porcoes):
        """
        Fraciona frascos/garrafas em porções menores baseado no volume
        """
        try:
            # Buscar dados completos do item original
            self.cursor.execute("""
                SELECT i.*, ti.nome as tipo_item_nome
                FROM itens_estoque i
                LEFT JOIN tipo_itens ti ON i.tipo_item_id = ti.id
                WHERE i.id = %s
            """, (item_id,))
            
            item_original = self.cursor.fetchone()
            if not item_original:
                return {"erro": "Item não encontrado"}
            
            # Verificar se é um frasco/garrafa (item com volume)
            tipo_item_nome = item_original['tipo_item_nome'] or ''
            volume_original = item_original['volume'] or 0
            
            # Converter volume_original para float para evitar problemas com Decimal
            volume_original = float(volume_original)
            
            if 'frasco' not in tipo_item_nome.lower() and 'garrafa' not in tipo_item_nome.lower():
                return {"erro": "Este item não é um frasco ou garrafa"}
            
            if volume_original <= 0:
                return {"erro": "Este item não tem volume definido"}
            
            # Verificar se há estoque suficiente
            quantidade_atual = item_original['quantidade_atual'] or 0
            quantidade_atual = float(quantidade_atual)
            
            if quantidade_atual < quantidade_recipientes:
                return {"erro": f"Estoque insuficiente. Disponível: {quantidade_atual} recipientes"}
            
            # Converter parâmetros para float para evitar problemas com Decimal
            print(f"[DEBUG VOLUME] Valores recebidos antes da conversão:")
            print(f"  - volume_por_porcao original: {volume_por_porcao} (tipo: {type(volume_por_porcao)})")
            print(f"  - quantidade_recipientes original: {quantidade_recipientes} (tipo: {type(quantidade_recipientes)})")
            print(f"  - total_porcoes original: {total_porcoes} (tipo: {type(total_porcoes)})")
            
            volume_por_porcao = float(volume_por_porcao)
            quantidade_recipientes = float(quantidade_recipientes)
            total_porcoes = float(total_porcoes)
            
            print(f"[DEBUG VOLUME] Valores após conversão:")
            print(f"  - volume_por_porcao: {volume_por_porcao}")
            print(f"  - quantidade_recipientes: {quantidade_recipientes}")
            print(f"  - total_porcoes: {total_porcoes}")
            
            # Verificar se o volume total necessário não excede o disponível
            volume_total_necessario = volume_por_porcao * total_porcoes
            volume_total_disponivel = quantidade_recipientes * volume_original
            
            if volume_total_necessario > volume_total_disponivel:
                return {"erro": f"Volume insuficiente. Necessário: {volume_total_necessario}ml, Disponível: {volume_total_disponivel}ml"}
            
            # Calcular custos para as porções fracionadas
            custo_atual_recipiente = float(item_original['custo_atual'] or 0)
            custo_medio_recipiente = float(item_original['custo_medio'] or 0)
            
            # O custo unitário da porção é proporcional ao volume
            if volume_original > 0:
                custo_unitario_porcao = (custo_atual_recipiente * volume_por_porcao) / volume_original
                custo_medio_porcao = (custo_medio_recipiente * volume_por_porcao) / volume_original
            else:
                custo_unitario_porcao = 0
                custo_medio_porcao = 0
            
            # 1. Reduzir a quantidade do item original (remover os recipientes)
            nova_quantidade_original = quantidade_atual - quantidade_recipientes
            self.cursor.execute("""
                UPDATE itens_estoque 
                SET quantidade_atual = %s
                WHERE id = %s
            """, (nova_quantidade_original, item_id))
            
            # 2. Buscar o ID do tipo "Porção Fracionada"
            self.cursor.execute("""
                SELECT id FROM tipo_itens WHERE nome = 'Porção Fracionada'
            """)
            tipo_porcao_fracionada = self.cursor.fetchone()
            if not tipo_porcao_fracionada:
                # Criar o tipo se não existir
                self.cursor.execute("""
                    INSERT INTO tipo_itens (nome, descricao) VALUES ('Porção Fracionada', 'Porções fracionadas por volume')
                """)
                self.connection.commit()
                tipo_porcao_fracionada_id = self.cursor.lastrowid
            else:
                tipo_porcao_fracionada_id = tipo_porcao_fracionada['id']
            
            # 3. Verificar se já existe um item fracionado deste produto
            # Converter volume de litros para mililitros para exibição
            volume_ml = volume_por_porcao * 1000
            
            # Formatar o volume em mililitros de forma inteligente (remove decimais desnecessárias)
            if volume_ml == int(volume_ml):
                volume_formatado = str(int(volume_ml))
            else:
                volume_formatado = f"{volume_ml:.1f}".rstrip('0').rstrip('.')
            
            nome_item_fracionado = f"{item_original['nome']} ({volume_formatado}ml)"
            codigo_item_fracionado = f"{item_original['codigo']}-{volume_formatado}ML"
            
            self.cursor.execute("""
                SELECT id, quantidade_atual, custo_atual, custo_medio FROM itens_estoque 
                WHERE codigo = %s AND tipo_item_id = %s
            """, (codigo_item_fracionado, tipo_porcao_fracionada_id))
            
            item_fracionado_existente = self.cursor.fetchone()
            
            if item_fracionado_existente:
                # 4a. Se o item fracionado já existe, calcular novo custo médio ponderado
                quantidade_existente = float(item_fracionado_existente['quantidade_atual'] or 0)
                custo_medio_existente = float(item_fracionado_existente['custo_medio'] or 0)
                
                if quantidade_existente > 0 and custo_medio_existente > 0:
                    valor_total_existente = quantidade_existente * custo_medio_existente
                    valor_entrada = total_porcoes * custo_medio_porcao
                    quantidade_total = quantidade_existente + total_porcoes
                    
                    if quantidade_total > 0:
                        novo_custo_medio = (valor_total_existente + valor_entrada) / quantidade_total
                    else:
                        novo_custo_medio = custo_medio_porcao
                
                nova_quantidade_fracionada = quantidade_existente + total_porcoes
                
                self.cursor.execute("""
                    UPDATE itens_estoque 
                    SET quantidade_atual = %s, custo_atual = %s, custo_medio = %s
                    WHERE id = %s
                """, (nova_quantidade_fracionada, custo_unitario_porcao, novo_custo_medio, item_fracionado_existente['id']))
                
                item_fracionado_id = item_fracionado_existente['id']
            else:
                # 4b. Se não existe, criar novo item fracionado
                query = """INSERT INTO itens_estoque (
                    nome, codigo, categoria_id, tipo_item_id, cor, quantidade_inicial, quantidade_atual, estoque_minimo,
                    unidades_por_pacote, unidade_medida_id, fornecedor_id, fabricante, localizacao_estoque, especificacoes_tecnicas, descricao,
                    largura, comprimento, espessura, volume, area, peso,
                    custo_atual, custo_medio
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                
                self.cursor.execute(query, (
                    nome_item_fracionado,
                    codigo_item_fracionado,
                    item_original['categoria_id'],
                    tipo_porcao_fracionada['id'],
                    item_original['cor'],
                    total_porcoes,  # quantidade_inicial
                    total_porcoes,  # quantidade_atual
                    item_original['estoque_minimo'],
                    1,  # unidades_por_pacote = 1 para porção fracionada
                    item_original['unidade_medida_id'],
                    item_original['fornecedor_id'],
                    item_original['fabricante'],
                    item_original['localizacao_estoque'],
                    item_original['especificacoes_tecnicas'],
                    f"{item_original['descricao']} - Porção fracionada de {volume_por_porcao * 1000:.0f}ml" if item_original['descricao'] else f"Porção fracionada de {volume_por_porcao * 1000:.0f}ml",
                    item_original['largura'],
                    item_original['comprimento'],
                    item_original['espessura'],
                    volume_por_porcao,  # volume da porção fracionada (ainda em litros)
                    item_original['area'],
                    item_original['peso'],
                    custo_unitario_porcao,  # custo_atual
                    custo_medio_porcao      # custo_medio
                ))
                
                item_fracionado_id = self.cursor.lastrowid
            
            # 5. Registrar a saída do item original
            self.cursor.execute("""
                INSERT INTO saidas_estoque (
                    item_id, quantidade, data_saida, motivo_saida, destino, observacoes
                ) VALUES (%s, %s, CURDATE(), %s, %s, %s)
            """, (
                item_id, 
                quantidade_recipientes, 
                'Fracionamento por Volume',
                'Conversão para porções menores',
                f'Fracionamento de {quantidade_recipientes} recipiente(s) em {total_porcoes} porções de {volume_por_porcao * 1000:.0f}ml cada'
            ))
            
            # 6. Registrar a entrada do item fracionado
            self.cursor.execute("""
                INSERT INTO entradas_estoque (
                    item_id, quantidade, data_entrada, custo_unitario, observacoes
                ) VALUES (%s, %s, CURDATE(), %s, %s)
            """, (
                item_fracionado_id,
                total_porcoes,
                custo_unitario_porcao,
                f'Entrada de {total_porcoes} porções de {volume_por_porcao * 1000:.0f}ml via fracionamento de {quantidade_recipientes} recipiente(s) do item {item_original["nome"]}. Volume utilizado: {volume_total_necessario * 1000:.0f}ml'
            ))
            
            self.connection.commit()
            
            return {
                "sucesso": f"Fracionamento por volume realizado com sucesso! {quantidade_recipientes} recipiente(s) convertido(s) em {total_porcoes} porções de {volume_por_porcao * 1000:.0f}ml cada",
                "recipientes_fracionados": quantidade_recipientes,
                "porcoes_adicionadas": total_porcoes,
                "volume_utilizado": volume_total_necessario,
                "volume_por_porcao": volume_por_porcao,
                "item_original_id": item_id,
                "item_fracionado_id": item_fracionado_id,
                "item_fracionado_nome": nome_item_fracionado,
                "nova_quantidade_total": nova_quantidade_original,
                "custo_unitario_porcao": custo_unitario_porcao
            }
            
        except Error as e:
            self.connection.rollback()
            return {"erro": f"Erro ao fracionar por volume: {str(e)}"}

    def fracionar_peso(self, item_id, quantidade_embalagens, peso_por_porcao, total_porcoes):
        """
        Fraciona embalagens em porções menores baseado no peso
        """
        try:
            # Buscar dados completos do item original
            self.cursor.execute("""
                SELECT i.*, ti.nome as tipo_item_nome
                FROM itens_estoque i
                LEFT JOIN tipo_itens ti ON i.tipo_item_id = ti.id
                WHERE i.id = %s
            """, (item_id,))
            
            item_original = self.cursor.fetchone()
            if not item_original:
                return {"erro": "Item não encontrado"}
            
            # Verificar se é uma embalagem (item com peso)
            tipo_item_nome = item_original['tipo_item_nome'] or ''
            peso_original = item_original['peso'] or 0
            
            # Converter peso_original para float para evitar problemas com Decimal
            peso_original = float(peso_original)
            
            if 'embalagem' not in tipo_item_nome.lower():
                return {"erro": "Este item não é uma embalagem"}
            
            if peso_original <= 0:
                return {"erro": "Este item não tem peso definido"}
            
            # Verificar se há estoque suficiente
            quantidade_atual = item_original['quantidade_atual'] or 0
            quantidade_atual = float(quantidade_atual)
            
            if quantidade_atual < quantidade_embalagens:
                return {"erro": f"Estoque insuficiente. Disponível: {quantidade_atual} embalagens"}
            
            # Converter parâmetros para float para evitar problemas com Decimal
            print(f"[DEBUG PESO] Valores recebidos antes da conversão:")
            print(f"  - peso_por_porcao original: {peso_por_porcao} (tipo: {type(peso_por_porcao)})")
            print(f"  - quantidade_embalagens original: {quantidade_embalagens} (tipo: {type(quantidade_embalagens)})")
            print(f"  - total_porcoes original: {total_porcoes} (tipo: {type(total_porcoes)})")
            
            peso_por_porcao = float(peso_por_porcao)
            quantidade_embalagens = float(quantidade_embalagens)
            total_porcoes = float(total_porcoes)
            
            print(f"[DEBUG PESO] Valores após conversão:")
            print(f"  - peso_por_porcao: {peso_por_porcao}")
            print(f"  - quantidade_embalagens: {quantidade_embalagens}")
            print(f"  - total_porcoes: {total_porcoes}")
            
            # Verificar se o peso total necessário não excede o disponível
            peso_total_necessario = peso_por_porcao * total_porcoes
            peso_total_disponivel = quantidade_embalagens * peso_original
            
            if peso_total_necessario > peso_total_disponivel:
                return {"erro": f"Peso insuficiente. Necessário: {peso_total_necessario}g, Disponível: {peso_total_disponivel}g"}
            
            # Verificar se o peso por porção não é maior que o peso original
            if peso_por_porcao >= peso_original:
                return {"erro": f"Peso por porção ({peso_por_porcao}g) deve ser menor que o peso da embalagem original ({peso_original}g)"}
            
            # Calcular custos para as porções fracionadas
            custo_atual_embalagem = float(item_original['custo_atual'] or 0)
            custo_medio_embalagem = float(item_original['custo_medio'] or 0)
            
            # O custo unitário da porção é proporcional ao peso
            if peso_original > 0:
                custo_unitario_porcao = (custo_atual_embalagem * peso_por_porcao) / peso_original
                custo_medio_porcao = (custo_medio_embalagem * peso_por_porcao) / peso_original
            else:
                custo_unitario_porcao = 0
                custo_medio_porcao = 0
            
            # 1. Reduzir a quantidade do item original (remover as embalagens)
            nova_quantidade_original = quantidade_atual - quantidade_embalagens
            self.cursor.execute("""
                UPDATE itens_estoque 
                SET quantidade_atual = %s
                WHERE id = %s
            """, (nova_quantidade_original, item_id))
            
            # 2. Buscar o ID do tipo "Porção Fracionada"
            self.cursor.execute("""
                SELECT id FROM tipo_itens WHERE nome = 'Porção Fracionada'
            """)
            tipo_porcao_fracionada = self.cursor.fetchone()
            if not tipo_porcao_fracionada:
                # Criar o tipo se não existir
                self.cursor.execute("""
                    INSERT INTO tipo_itens (nome, descricao) VALUES ('Porção Fracionada', 'Porções fracionadas por peso')
                """)
                self.connection.commit()
                tipo_porcao_fracionada_id = self.cursor.lastrowid
            else:
                tipo_porcao_fracionada_id = tipo_porcao_fracionada['id']
            
            # 3. Verificar se já existe um item fracionado deste produto
            # Formatar o peso de forma inteligente (remove decimais desnecessárias)
            if peso_por_porcao == int(peso_por_porcao):
                peso_formatado = str(int(peso_por_porcao))
            else:
                peso_formatado = f"{peso_por_porcao:.1f}".rstrip('0').rstrip('.')
            
            nome_item_fracionado = f"{item_original['nome']} ({peso_formatado}g)"
            codigo_item_fracionado = f"{item_original['codigo']}-{peso_formatado}G"
            
            self.cursor.execute("""
                SELECT id, quantidade_atual, custo_atual, custo_medio FROM itens_estoque 
                WHERE codigo = %s AND tipo_item_id = %s
            """, (codigo_item_fracionado, tipo_porcao_fracionada_id))
            
            item_fracionado_existente = self.cursor.fetchone()
            
            if item_fracionado_existente:
                # 4a. Se o item fracionado já existe, calcular novo custo médio ponderado
                quantidade_existente = float(item_fracionado_existente['quantidade_atual'] or 0)
                custo_medio_existente = float(item_fracionado_existente['custo_medio'] or 0)
                
                if quantidade_existente > 0 and custo_medio_existente > 0:
                    valor_total_existente = quantidade_existente * custo_medio_existente
                    valor_entrada = total_porcoes * custo_medio_porcao
                    quantidade_total = quantidade_existente + total_porcoes
                    
                    if quantidade_total > 0:
                        novo_custo_medio = (valor_total_existente + valor_entrada) / quantidade_total
                    else:
                        novo_custo_medio = custo_medio_porcao
                else:
                    novo_custo_medio = custo_medio_porcao
                
                nova_quantidade_fracionada = quantidade_existente + total_porcoes
                
                self.cursor.execute("""
                    UPDATE itens_estoque 
                    SET quantidade_atual = %s, custo_atual = %s, custo_medio = %s
                    WHERE id = %s
                """, (nova_quantidade_fracionada, custo_unitario_porcao, novo_custo_medio, item_fracionado_existente['id']))
                
                item_fracionado_id = item_fracionado_existente['id']
            else:
                # 4b. Se não existe, criar novo item fracionado
                query = """INSERT INTO itens_estoque (
                    nome, codigo, categoria_id, tipo_item_id, cor, quantidade_inicial, quantidade_atual, estoque_minimo,
                    unidades_por_pacote, unidade_medida_id, fornecedor_id, fabricante, localizacao_estoque, especificacoes_tecnicas, descricao,
                    largura, comprimento, espessura, volume, area, peso,
                    custo_atual, custo_medio
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                
                self.cursor.execute(query, (
                    nome_item_fracionado,
                    codigo_item_fracionado,
                    item_original['categoria_id'],
                    tipo_porcao_fracionada_id,
                    item_original['cor'],
                    total_porcoes,  # quantidade_inicial
                    total_porcoes,  # quantidade_atual
                    item_original['estoque_minimo'],
                    1,  # unidades_por_pacote = 1 para porção fracionada
                    item_original['unidade_medida_id'],
                    item_original['fornecedor_id'],
                    item_original['fabricante'],
                    item_original['localizacao_estoque'],
                    item_original['especificacoes_tecnicas'],
                    f"{item_original['descricao']} - Porção fracionada de {peso_por_porcao:.0f}g" if item_original['descricao'] else f"Porção fracionada de {peso_por_porcao:.0f}g",
                    item_original['largura'],
                    item_original['comprimento'],
                    item_original['espessura'],
                    item_original['volume'],
                    item_original['area'],
                    peso_por_porcao,  # peso da porção fracionada
                    custo_unitario_porcao,  # custo_atual
                    custo_medio_porcao      # custo_medio
                ))
                
                item_fracionado_id = self.cursor.lastrowid
            
            # 5. Registrar a saída do item original
            self.cursor.execute("""
                INSERT INTO saidas_estoque (
                    item_id, quantidade, data_saida, motivo_saida, destino, observacoes
                ) VALUES (%s, %s, CURDATE(), %s, %s, %s)
            """, (
                item_id, 
                quantidade_embalagens, 
                'Fracionamento por Peso',
                'Conversão para porções menores',
                f'Fracionamento de {quantidade_embalagens} embalagem(ns) em {total_porcoes} porções de {peso_por_porcao:.0f}g cada'
            ))
            
            # 6. Registrar a entrada do item fracionado
            self.cursor.execute("""
                INSERT INTO entradas_estoque (
                    item_id, quantidade, data_entrada, custo_unitario, observacoes
                ) VALUES (%s, %s, CURDATE(), %s, %s)
            """, (
                item_fracionado_id,
                total_porcoes,
                custo_unitario_porcao,
                f'Entrada de {total_porcoes} porções de {peso_por_porcao:.0f}g via fracionamento de {quantidade_embalagens} embalagem(ns) do item {item_original["nome"]}. Peso utilizado: {peso_total_necessario:.0f}g'
            ))
            
            self.connection.commit()
            
            return {
                "sucesso": f"Fracionamento por peso realizado com sucesso! {quantidade_embalagens} embalagem(ns) convertida(s) em {total_porcoes} porções de {peso_por_porcao:.0f}g cada",
                "embalagens_fracionadas": quantidade_embalagens,
                "porcoes_adicionadas": total_porcoes,
                "peso_utilizado": peso_total_necessario,
                "peso_por_porcao": peso_por_porcao,
                "item_original_id": item_id,
                "item_fracionado_id": item_fracionado_id,
                "item_fracionado_nome": nome_item_fracionado,
                "nova_quantidade_total": nova_quantidade_original,
                "custo_unitario_porcao": custo_unitario_porcao
            }
            
        except Error as e:
            self.connection.rollback()
            return {"erro": f"Erro ao fracionar por peso: {str(e)}"}

    # Métodos para Cálculo Proporcional de Materiais
    def calcular_custo_proporcional_material(self, material_id, dimensoes_necessarias):
        """
        Calcula o custo proporcional de um material baseado nas dimensões necessárias
        Parâmetros:
        - material_id: ID do material no estoque
        - dimensoes_necessarias: dict com as dimensões (ex: {'largura': 100, 'comprimento': 100, 'unidade': 'cm'})
        """
        try:
            # Buscar dados do material
            self.cursor.execute("""
                SELECT i.*, u.nome as unidade_medida_nome, ti.nome as tipo_item_nome
                FROM itens_estoque i
                LEFT JOIN unidades_de_medida u ON i.unidade_medida_id = u.id
                LEFT JOIN tipo_itens ti ON i.tipo_item_id = ti.id
                WHERE i.id = %s
            """, (material_id,))
            
            material = self.cursor.fetchone()
            if not material:
                return {"erro": "Material não encontrado"}
            
            # Obter dimensões do material
            largura_material = float(material['largura'] or 0)
            comprimento_material = float(material['comprimento'] or 0)
            area_material = float(material['area'] or 0)
            custo_atual = float(material['custo_atual'] or 0)
            custo_medio = float(material['custo_medio'] or 0)
            
            # Se não tem área calculada mas tem largura e comprimento, calcular
            if not area_material and largura_material > 0 and comprimento_material > 0:
                area_material = (largura_material * comprimento_material) / 10000  # cm² para m²
            
            if area_material <= 0:
                return {"erro": "Material não possui dimensões válidas para cálculo proporcional"}
            
            # Calcular área necessária
            largura_necessaria = float(dimensoes_necessarias.get('largura', 0))
            comprimento_necessario = float(dimensoes_necessarias.get('comprimento', 0))
            
            if largura_necessaria <= 0 or comprimento_necessario <= 0:
                return {"erro": "Dimensões necessárias inválidas"}
            
            # Converter para m² se necessário
            unidade = dimensoes_necessarias.get('unidade', 'cm').lower()
            if unidade == 'cm':
                area_necessaria = (largura_necessaria * comprimento_necessario) / 10000  # cm² para m²
            elif unidade == 'm':
                area_necessaria = largura_necessaria * comprimento_necessario  # já em m²
            else:
                return {"erro": f"Unidade '{unidade}' não suportada"}
            
            # Verificar se a área necessária não excede a área total do material
            if area_necessaria > area_material:
                return {"erro": f"Área necessária ({area_necessaria:.4f}m²) excede a área total do material ({area_material:.4f}m²)"}
            
            # Calcular custos proporcionais
            custo_por_m2_atual = custo_atual / area_material if area_material > 0 else 0
            custo_por_m2_medio = custo_medio / area_material if area_material > 0 else 0
            
            custo_proporcional_atual = custo_por_m2_atual * area_necessaria
            custo_proporcional_medio = custo_por_m2_medio * area_necessaria
            
            # Calcular eficiência de aproveitamento
            eficiencia = (area_necessaria / area_material) * 100
            
            return {
                "sucesso": "Cálculo realizado com sucesso",
                "material": {
                    "id": material_id,
                    "nome": material['nome'],
                    "area_total": area_material,
                    "custo_total_atual": custo_atual,
                    "custo_total_medio": custo_medio
                },
                "necessidades": {
                    "largura": largura_necessaria,
                    "comprimento": comprimento_necessario,
                    "area_necessaria": area_necessaria,
                    "unidade": unidade
                },
                "custos": {
                    "custo_por_m2_atual": custo_por_m2_atual,
                    "custo_por_m2_medio": custo_por_m2_medio,
                    "custo_proporcional_atual": custo_proporcional_atual,
                    "custo_proporcional_medio": custo_proporcional_medio
                },
                "eficiencia": {
                    "aproveitamento_percentual": eficiencia,
                    "area_desperdicada": area_material - area_necessaria,
                    "custo_desperdicado": (custo_atual / area_material) * (area_material - area_necessaria) if area_material > 0 else 0
                }
            }
            
        except Error as e:
            return {"erro": f"Erro ao calcular custo proporcional: {str(e)}"}
        except Exception as e:
            return {"erro": f"Erro inesperado: {str(e)}"}

    def calcular_custo_por_metros_lineares(self, material_id, metros_necessarios):
        """
        Calcula o custo proporcional baseado em metros lineares
        """
        try:
            # Buscar dados do material
            self.cursor.execute("""
                SELECT i.*, u.nome as unidade_medida_nome, ti.nome as tipo_item_nome
                FROM itens_estoque i
                LEFT JOIN unidades_de_medida u ON i.unidade_medida_id = u.id
                LEFT JOIN tipo_itens ti ON i.tipo_item_id = ti.id
                WHERE i.id = %s
            """, (material_id,))
            
            material = self.cursor.fetchone()
            if not material:
                return {"erro": "Material não encontrado"}
            
            comprimento_material = float(material['comprimento'] or 0)
            custo_atual = float(material['custo_atual'] or 0)
            custo_medio = float(material['custo_medio'] or 0)
            metros_necessarios = float(metros_necessarios)
            
            if comprimento_material <= 0:
                return {"erro": "Material não possui comprimento definido"}
            
            if metros_necessarios <= 0:
                return {"erro": "Metros necessários deve ser maior que zero"}
            
            # Converter comprimento para metros se estiver em cm
            comprimento_em_metros = comprimento_material / 100 if comprimento_material > 50 else comprimento_material
            
            if metros_necessarios > comprimento_em_metros:
                return {"erro": f"Metros necessários ({metros_necessarios}m) excedem o comprimento total ({comprimento_em_metros}m)"}
            
            # Calcular custos proporcionais
            custo_por_metro_atual = custo_atual / comprimento_em_metros
            custo_por_metro_medio = custo_medio / comprimento_em_metros
            
            custo_proporcional_atual = custo_por_metro_atual * metros_necessarios
            custo_proporcional_medio = custo_por_metro_medio * metros_necessarios
            
            # Calcular eficiência
            eficiencia = (metros_necessarios / comprimento_em_metros) * 100
            
            return {
                "sucesso": "Cálculo realizado com sucesso",
                "material": {
                    "id": material_id,
                    "nome": material['nome'],
                    "comprimento_total": comprimento_em_metros,
                    "custo_total_atual": custo_atual,
                    "custo_total_medio": custo_medio
                },
                "necessidades": {
                    "metros_necessarios": metros_necessarios
                },
                "custos": {
                    "custo_por_metro_atual": custo_por_metro_atual,
                    "custo_por_metro_medio": custo_por_metro_medio,
                    "custo_proporcional_atual": custo_proporcional_atual,
                    "custo_proporcional_medio": custo_proporcional_medio
                },
                "eficiencia": {
                    "aproveitamento_percentual": eficiencia,
                    "metros_desperdicados": comprimento_em_metros - metros_necessarios,
                    "custo_desperdicado": custo_por_metro_atual * (comprimento_em_metros - metros_necessarios)
                }
            }
            
        except Error as e:
            return {"erro": f"Erro ao calcular custo por metros lineares: {str(e)}"}
        except Exception as e:
            return {"erro": f"Erro inesperado: {str(e)}"}

    def registrar_consumo_proporcional(self, material_id, quantidade_consumida, tipo_consumo, dimensoes_consumidas, observacoes=None):
        """
        Registra o consumo proporcional de um material
        Parâmetros:
        - material_id: ID do material
        - quantidade_consumida: quantidade em unidade padrão (ex: m², metros lineares, etc.)
        - tipo_consumo: 'area', 'linear', 'volume', 'peso'
        - dimensoes_consumidas: dict com as dimensões consumidas
        - observacoes: observações opcionais
        """
        try:
            # Buscar dados do material
            self.cursor.execute("""
                SELECT i.*, ti.nome as tipo_item_nome
                FROM itens_estoque i
                LEFT JOIN tipo_itens ti ON i.tipo_item_id = ti.id
                WHERE i.id = %s
            """, (material_id,))
            
            material = self.cursor.fetchone()
            if not material:
                return {"erro": "Material não encontrado"}
            
            quantidade_atual = float(material['quantidade_atual'] or 0)
            
            # Para materiais em bobina/rolo, reduzir a quantidade baseada no tipo de consumo
            if tipo_consumo == 'area':
                # Verificar se ainda há material suficiente
                area_total = float(material['area'] or 0)
                if area_total <= 0:
                    return {"erro": "Material não possui área definida"}
                
                # Calcular quantas "unidades" foram consumidas
                percentual_consumido = quantidade_consumida / area_total
                quantidade_a_reduzir = quantidade_atual * percentual_consumido
                
            elif tipo_consumo == 'linear':
                comprimento_total = float(material['comprimento'] or 0) / 100  # cm para metros
                if comprimento_total <= 0:
                    return {"erro": "Material não possui comprimento definido"}
                
                percentual_consumido = quantidade_consumida / comprimento_total
                quantidade_a_reduzir = quantidade_atual * percentual_consumido
                
            else:
                return {"erro": f"Tipo de consumo '{tipo_consumo}' não suportado"}
            
            if quantidade_a_reduzir > quantidade_atual:
                return {"erro": "Quantidade a consumir excede o estoque disponível"}
            
            # Registrar a saída proporcional
            motivo_saida = f"Consumo {tipo_consumo} - {quantidade_consumida} {tipo_consumo}"
            destino = "Produção"
            observacoes_completas = f"Consumo proporcional: {dimensoes_consumidas}. {observacoes or ''}"
            
            # Inserir saída de estoque
            self.cursor.execute("""
                INSERT INTO saidas_estoque (
                    item_id, quantidade, data_saida, motivo_saida, destino, observacoes
                ) VALUES (%s, %s, CURDATE(), %s, %s, %s)
            """, (material_id, quantidade_a_reduzir, motivo_saida, destino, observacoes_completas))
            
            # Atualizar quantidade no estoque
            nova_quantidade = quantidade_atual - quantidade_a_reduzir
            self.cursor.execute("""
                UPDATE itens_estoque 
                SET quantidade_atual = %s
                WHERE id = %s
            """, (nova_quantidade, material_id))
            
            self.connection.commit()
            
            return {
                "sucesso": "Consumo registrado com sucesso",
                "quantidade_consumida": quantidade_consumida,
                "tipo_consumo": tipo_consumo,
                "quantidade_reduzida_estoque": quantidade_a_reduzir,
                "quantidade_restante": nova_quantidade,
                "percentual_consumido": (quantidade_a_reduzir / quantidade_atual) * 100
            }
            
        except Error as e:
            self.connection.rollback()
            return {"erro": f"Erro ao registrar consumo proporcional: {str(e)}"}
        except Exception as e:
            self.connection.rollback()
            return {"erro": f"Erro inesperado: {str(e)}"}

    # Métodos para Produtos - Buscar e Editar
    def buscar_produto_por_id(self, produto_id):
        """Busca um produto pelo ID com todos os dados relacionados"""
        try:
            # Buscar dados básicos do produto
            query_produto = """
                SELECT p.id, p.codigo, p.nome, p.categoria_id, 
                       cp.nome as categoria_nome, p.preco, p.margem_lucro, 
                       p.descricao, p.especificacoes_tecnicas, 
                       p.custo_materiais, p.custo_etapas, p.data_criacao
                FROM produtos p
                LEFT JOIN categoria_produtos cp ON p.categoria_id = cp.id
                WHERE p.id = %s
            """
            
            self.cursor.execute(query_produto, (produto_id,))
            produto = self.cursor.fetchone()
            
            if not produto:
                return {"erro": "Produto não encontrado"}
            
            # Buscar materiais do produto
            query_materiais = """
                SELECT pm.id, pm.material_id, ie.nome as material_nome, ie.codigo as material_codigo,
                       pm.quantidade_necessaria, pm.custo_unitario, pm.subtotal,
                       pm.largura, pm.altura, pm.area_utilizada
                FROM produtos_materiais pm
                LEFT JOIN itens_estoque ie ON pm.material_id = ie.id
                WHERE pm.produto_id = %s
            """
            
            self.cursor.execute(query_materiais, (produto_id,))
            materiais_raw = self.cursor.fetchall()
            
            # Converter campos problemáticos dos materiais
            materiais = []
            if materiais_raw:
                for material in materiais_raw:
                    material_dict = dict(material)
                    # Converter campos que podem causar problemas de serialização
                    for key, value in material_dict.items():
                        if hasattr(value, 'total_seconds'):  # timedelta
                            material_dict[key] = str(value)
                        elif hasattr(value, 'isoformat'):  # datetime/date
                            material_dict[key] = value.isoformat()
                    materiais.append(material_dict)
            
            # Buscar etapas do produto
            query_etapas = """
                SELECT pe.id, pe.nome, pe.tipo, equipamento_id, equipamento_nome,
                       material_id, material_nome, tempo_estimado, custo_estimado
                FROM produtos_etapas pe
                WHERE pe.produto_id = %s
            """
            
            self.cursor.execute(query_etapas, (produto_id,))
            etapas_raw = self.cursor.fetchall()
            
            # Converter campos problemáticos das etapas
            etapas = []
            if etapas_raw:
                for etapa in etapas_raw:
                    etapa_dict = dict(etapa)
                    # Converter campos que podem causar problemas de serialização
                    for key, value in etapa_dict.items():
                        if hasattr(value, 'total_seconds'):  # timedelta
                            etapa_dict[key] = str(value)
                        elif hasattr(value, 'isoformat'):  # datetime/date
                            etapa_dict[key] = value.isoformat()
                    etapas.append(etapa_dict)
            
            # Montar o resultado completo
            resultado = {
                "id": produto["id"],
                "codigo": produto["codigo"],
                "nome": produto["nome"],
                "categoria_id": produto["categoria_id"],
                "categoria": produto["categoria_nome"],
                "preco": produto["preco"],
                "margem_lucro": produto["margem_lucro"],
                "descricao": produto["descricao"],
                "especificacoes": produto["especificacoes_tecnicas"],
                "custoMateriais": produto["custo_materiais"],
                "custoEtapas": produto["custo_etapas"],
                "data_criacao": str(produto["data_criacao"]) if produto["data_criacao"] else None,
                "materiais": materiais or [],
                "etapas": etapas or []
            }
            
            print(f"[DEBUG] Produto encontrado: {produto['nome']} com {len(materiais)} materiais e {len(etapas)} etapas")
            return resultado
            
        except Error as e:
            print(f"[ERROR] Erro ao buscar produto por ID {produto_id}: {str(e)}")
            return {"erro": f"Erro ao buscar produto: {str(e)}"}

    def atualizar_produto(self, produto_id, dados):
        """Atualiza um produto existente"""
        try:
            # Debug: verificar se o produto existe
            check_query = "SELECT id, nome FROM produtos WHERE id = %s"
            self.cursor.execute(check_query, (produto_id,))
            produto_existente = self.cursor.fetchone()
            
            if not produto_existente:
                print(f"[DEBUG] Produto {produto_id} não encontrado no banco de dados")
                return {"erro": "Produto não encontrado"}
            
            print(f"[DEBUG] Produto encontrado: {produto_existente}")
            
            # Debug: verificar dados atuais do produto antes da atualização
            check_current_query = "SELECT codigo, nome, categoria_id, preco, margem_lucro, descricao, especificacoes_tecnicas, custo_materiais, custo_etapas FROM produtos WHERE id = %s"
            self.cursor.execute(check_current_query, (produto_id,))
            produto_atual = self.cursor.fetchone()
            print(f"[DEBUG] Dados atuais do produto: {produto_atual}")
            
            # Primeiro, buscar ou criar a categoria se necessário
            categoria_id = self.obter_categoria_id(dados['categoria'])
            
            if not categoria_id:
                print(f"[DEBUG] Erro: não foi possível obter categoria_id para: {dados['categoria']}")
                return {"erro": "Erro ao processar categoria"}
            
            print(f"[DEBUG] Atualizando produto {produto_id} com categoria_id: {categoria_id}")
            
            query = """
                UPDATE produtos 
                SET codigo = %s, nome = %s, categoria_id = %s, preco = %s, 
                    margem_lucro = %s, descricao = %s, especificacoes_tecnicas = %s,
                    custo_materiais = %s, custo_etapas = %s
                WHERE id = %s
            """
            
            valores = (
                dados['codigo'],
                dados['nome'], 
                categoria_id,
                dados['preco'],
                dados['margem'],
                dados['descricao'],
                dados['especificacoes'],
                dados['custo_materiais'],
                dados['custo_etapas'],
                produto_id
            )
            
            print(f"[DEBUG] Query: {query}")
            print(f"[DEBUG] Valores: {valores}")
            
            self.cursor.execute(query, valores)
            
            # Debug: verificar se há alguma mudança antes do commit
            linhas_afetadas = self.cursor.rowcount
            print(f"[DEBUG] Linhas afetadas antes do commit: {linhas_afetadas}")
            
            self.connection.commit()
            
            # Verificar se os dados foram realmente atualizados
            check_after_query = "SELECT codigo, nome, categoria_id, preco, margem_lucro, descricao, especificacoes_tecnicas, custo_materiais, custo_etapas FROM produtos WHERE id = %s"
            self.cursor.execute(check_after_query, (produto_id,))
            produto_apos_update = self.cursor.fetchone()
            print(f"[DEBUG] Produto após update: {produto_apos_update}")
            
            # Usar linhas_afetadas capturadas antes do commit, pois após commit pode ser resetado
            if linhas_afetadas > 0:
                print(f"[DEBUG] Produto {produto_id} atualizado com sucesso - {linhas_afetadas} linhas afetadas")
                return {"sucesso": "Produto atualizado com sucesso"}
            else:
                print(f"[DEBUG] Nenhuma linha foi afetada ao atualizar produto {produto_id}")
                # Verificar se realmente não foi atualizado comparando os dados
                # Se os dados são iguais aos enviados, considerar como sucesso (sem mudanças)
                if produto_apos_update:
                    print(f"[DEBUG] Produto existe após tentativa de update, considerando como sucesso")
                    return {"sucesso": "Produto atualizado com sucesso (sem alterações)"}
                else:
                    return {"erro": "Produto não encontrado ou nenhuma alteração foi feita"}
            
        except Error as e:
            print(f"[DEBUG] Erro ao atualizar produto {produto_id}: {str(e)}")
            import traceback
            traceback.print_exc()
            self.connection.rollback()
            return {"erro": f"Erro ao atualizar produto: {str(e)}"}

    def remover_materiais_produto(self, produto_id):
        """Remove todos os materiais associados a um produto"""
        try:
            query = "DELETE FROM produtos_materiais WHERE produto_id = %s"
            self.cursor.execute(query, (produto_id,))
            self.connection.commit()
            
            print(f"[DEBUG] Removidos {self.cursor.rowcount} materiais do produto {produto_id}")
            return {"sucesso": f"Materiais removidos: {self.cursor.rowcount}"}
            
        except Error as e:
            print(f"[DEBUG] Erro ao remover materiais do produto {produto_id}: {str(e)}")
            self.connection.rollback()
            return {"erro": f"Erro ao remover materiais: {str(e)}"}

    def remover_etapas_produto(self, produto_id):
        """Remove todas as etapas associadas a um produto"""
        try:
            query = "DELETE FROM produtos_etapas WHERE produto_id = %s"
            self.cursor.execute(query, (produto_id,))
            self.connection.commit()
            
            print(f"[DEBUG] Removidas {self.cursor.rowcount} etapas do produto {produto_id}")
            return {"sucesso": f"Etapas removidas: {self.cursor.rowcount}"}
            
        except Error as e:
            print(f"[DEBUG] Erro ao remover etapas do produto {produto_id}: {str(e)}")
            self.connection.rollback()
            return {"erro": f"Erro ao remover etapas: {str(e)}"}

    # Métodos para verificação de alterações de preços
    def verificar_alteracoes_custos(self, dias=7):
        """
        Verifica se houve alterações nos custos de materiais ou máquinas nos últimos X dias
        que possam impactar os preços dos produtos
        """
        try:
            alteracoes = {
                'materiais': [],
                'maquinas': []
            }
            
            # Verificar alterações em materiais (itens_estoque)
            # Buscar materiais que tiveram entradas recentes
            query_materiais_com_entradas = """
                SELECT DISTINCT ie.id, ie.nome, ie.custo_atual, ie.custo_medio
                FROM itens_estoque ie
                INNER JOIN entradas_estoque ee ON ie.id = ee.item_id
                WHERE ee.data_entrada >= DATE_SUB(NOW(), INTERVAL %s DAY)
                AND ee.custo_unitario IS NOT NULL
                ORDER BY ie.nome
            """
            
            self.cursor.execute(query_materiais_com_entradas, (dias,))
            materiais_com_entradas = self.cursor.fetchall()
            
            for material in materiais_com_entradas:
                # Para cada material, calcular o custo antes das entradas recentes
                custo_antes_alteracoes = self._calcular_custo_antes_periodo(material['id'], dias)
                custo_atual = float(material['custo_atual'] or material['custo_medio'] or 0)
                
                # Verificar se houve mudança significativa (maior que 1 centavo)
                if abs(custo_atual - custo_antes_alteracoes) > 0:
                    # Buscar a entrada mais recente para pegar a data
                    query_data_ultima_entrada = """
                        SELECT data_entrada, custo_unitario
                        FROM entradas_estoque 
                        WHERE item_id = %s 
                        AND data_entrada >= DATE_SUB(NOW(), INTERVAL %s DAY)
                        ORDER BY data_entrada DESC 
                        LIMIT 1
                    """
                    self.cursor.execute(query_data_ultima_entrada, (material['id'], dias))
                    ultima_entrada = self.cursor.fetchone()
                    
                    variacao_percentual = self._calcular_variacao_percentual(
                        custo_antes_alteracoes, custo_atual
                    )
                    
                    alteracoes['materiais'].append({
                        'id': material['id'],
                        'nome': material['nome'],
                        'custo_anterior': custo_antes_alteracoes,
                        'custo_novo': custo_atual,
                        'data_alteracao': ultima_entrada['data_entrada'].strftime('%Y-%m-%d %H:%M:%S') if ultima_entrada else 'N/A',
                        'variacao_percentual': variacao_percentual
                    })
            
            # Verificar alterações em máquinas usando o histórico
            query_maquinas_historico = """
                SELECT hcm.maquina_id, m.nome, hcm.hora_maquina_anterior, hcm.hora_maquina_nova,
                       hcm.metros_quadrados_anterior, hcm.metros_quadrados_nova, hcm.data_alteracao
                FROM historico_custos_maquinas hcm
                INNER JOIN maquinas m ON hcm.maquina_id = m.id
                WHERE hcm.data_alteracao >= DATE_SUB(NOW(), INTERVAL %s DAY)
                ORDER BY hcm.data_alteracao DESC
            """
            
            self.cursor.execute(query_maquinas_historico, (dias,))
            maquinas_historico = self.cursor.fetchall()
            
            for alteracao in maquinas_historico:
                # Calcular variação percentual no custo por hora
                custo_anterior = float(alteracao['hora_maquina_anterior'] or 0)
                custo_novo = float(alteracao['hora_maquina_nova'] or 0)
                
                if custo_anterior != custo_novo:
                    variacao_percentual = self._calcular_variacao_percentual(custo_anterior, custo_novo)
                    
                    alteracoes['maquinas'].append({
                        'id': alteracao['maquina_id'],
                        'nome': alteracao['nome'],
                        'custo_por_hora_anterior': custo_anterior,
                        'custo_por_hora': custo_novo,
                        'metros_quadrados_por_hora': float(alteracao['metros_quadrados_nova'] or 0),
                        'data_alteracao': alteracao['data_alteracao'].strftime('%Y-%m-%d %H:%M:%S'),
                        'variacao_percentual': variacao_percentual
                    })
            
            # Se não houver histórico, verificar máquinas alteradas recentemente (fallback)
            if not alteracoes['maquinas']:
                query_maquinas_fallback = """
                    SELECT m.id, m.nome, m.hora_maquina, m.metros_quadrados_por_hora, m.data_atualizacao
                    FROM maquinas m
                    WHERE m.data_atualizacao >= DATE_SUB(NOW(), INTERVAL %s DAY)
                """
                
                self.cursor.execute(query_maquinas_fallback, (dias,))
                maquinas_alteradas = self.cursor.fetchall()
                
                for maquina in maquinas_alteradas:
                    alteracoes['maquinas'].append({
                        'id': maquina['id'],
                        'nome': maquina['nome'],
                        'custo_por_hora': float(maquina['hora_maquina'] or 0),
                        'metros_quadrados_por_hora': float(maquina['metros_quadrados_por_hora'] or 0),
                        'data_alteracao': maquina['data_atualizacao'].strftime('%Y-%m-%d %H:%M:%S') if maquina['data_atualizacao'] else 'N/A',
                        'variacao_percentual': 0  # Sem histórico, não podemos calcular variação
                    })
            
            print(f"[DEBUG] Alterações detectadas: {len(alteracoes['materiais'])} materiais, {len(alteracoes['maquinas'])} máquinas")
            
            return alteracoes if (alteracoes['materiais'] or alteracoes['maquinas']) else None
            
        except Error as e:
            print(f"[ERROR] Erro ao verificar alterações de custos: {str(e)}")
            return None

    def calcular_impacto_alteracoes_precos(self, alteracoes):
        """
        Calcula o impacto das alterações de custos nos preços dos produtos
        """
        try:
            produtos_afetados = []
            produtos_processados = set()  # Para evitar duplicatas
            
            # Primeiro, coletar todos os produtos afetados por materiais
            for material in alteracoes['materiais']:
                query_produtos_material = """
                    SELECT DISTINCT p.id, p.nome, p.codigo, p.preco, p.margem_lucro,
                           cp.nome as categoria_nome
                    FROM produtos p
                    LEFT JOIN categoria_produtos cp ON p.categoria_id = cp.id
                    INNER JOIN produtos_materiais pm ON p.id = pm.produto_id
                    WHERE pm.material_id = %s
                """
                
                self.cursor.execute(query_produtos_material, (material['id'],))
                produtos_com_material = self.cursor.fetchall()
                
                for produto in produtos_com_material:
                    if produto['id'] not in produtos_processados:
                        produtos_processados.add(produto['id'])
                        
                        # Calcular novo custo do produto considerando TODAS as alterações
                        novo_custo_produto = self._calcular_novo_custo_produto(
                            produto['id'], alteracoes
                        )
                        
                        # Calcular novo preço com margem
                        margem_lucro = float(produto['margem_lucro'] or 0)
                        novo_preco = float(novo_custo_produto) * (1 + margem_lucro / 100)
                        
                        # Calcular variação de preço
                        preco_atual = float(produto['preco'] or 0)
                        variacao = self._calcular_variacao_percentual(preco_atual, novo_preco)
                        
                        # Filtrar apenas produtos com variação real (> 0%)
                        if abs(variacao) <= 0.0001:  # Tolerância mínima para erros de ponto flutuante
                            continue
                        
                        # Determinar nível de impacto
                        impacto = self._determinar_nivel_impacto(abs(variacao))
                        
                        # Identificar quais alterações afetam este produto
                        materiais_alterados = []
                        maquinas_alteradas = []
                        
                        # Verificar materiais alterados
                        for mat_alt in alteracoes['materiais']:
                            self.cursor.execute("""
                                SELECT COUNT(*) as count FROM produtos_materiais 
                                WHERE produto_id = %s AND material_id = %s
                            """, (produto['id'], mat_alt['id']))
                            if self.cursor.fetchone()['count'] > 0:
                                materiais_alterados.append(mat_alt['nome'])
                        
                        # Verificar máquinas alteradas
                        for maq_alt in alteracoes['maquinas']:
                            self.cursor.execute("""
                                SELECT COUNT(*) as count FROM produtos_etapas 
                                WHERE produto_id = %s AND equipamento_id = %s AND equipamento_tipo = 'maquina'
                            """, (produto['id'], maq_alt['id']))
                            if self.cursor.fetchone()['count'] > 0:
                                maquinas_alteradas.append(maq_alt['nome'])
                        
                        produtos_afetados.append({
                            'id': produto['id'],
                            'nome': produto['nome'],
                            'codigo': produto['codigo'],
                            'categoria': produto['categoria_nome'],
                            'preco_atual': float(produto['preco']),
                            'novo_preco': round(novo_preco, 2),
                            'diferenca': round(novo_preco - float(produto['preco']), 2),
                            'variacao_percentual': round(variacao, 2),
                            'impacto': impacto,
                            'causa': self._gerar_causa(materiais_alterados, maquinas_alteradas),
                            'materiais_alterados': materiais_alterados,
                            'maquinas_alteradas': maquinas_alteradas
                        })
            
            # Depois, verificar produtos afetados apenas por máquinas (que não foram processados ainda)
            for maquina in alteracoes['maquinas']:
                query_produtos_maquina = """
                    SELECT DISTINCT p.id, p.nome, p.codigo, p.preco, p.margem_lucro,
                           cp.nome as categoria_nome
                    FROM produtos p
                    LEFT JOIN categoria_produtos cp ON p.categoria_id = cp.id
                    INNER JOIN produtos_etapas pe ON p.id = pe.produto_id
                    WHERE pe.equipamento_id = %s AND pe.equipamento_tipo = 'maquina'
                """
                
                self.cursor.execute(query_produtos_maquina, (maquina['id'],))
                produtos_com_maquina = self.cursor.fetchall()
                
                for produto in produtos_com_maquina:
                    if produto['id'] not in produtos_processados:
                        produtos_processados.add(produto['id'])
                        
                        # Calcular novo custo e preço considerando TODAS as alterações
                        novo_custo_produto = self._calcular_novo_custo_produto(
                            produto['id'], alteracoes
                        )
                        margem_lucro = float(produto['margem_lucro'] or 0)
                        novo_preco = float(novo_custo_produto) * (1 + margem_lucro / 100)
                        preco_atual = float(produto['preco'] or 0)
                        variacao = self._calcular_variacao_percentual(preco_atual, novo_preco)
                        
                        # Filtrar apenas produtos com variação real (> 0%)
                        if abs(variacao) <= 0.0001:  # Tolerância mínima para erros de ponto flutuante
                            continue
                            
                        impacto = self._determinar_nivel_impacto(abs(variacao))
                        
                        # Identificar quais alterações afetam este produto
                        materiais_alterados = []
                        maquinas_alteradas = []
                        
                        # Verificar materiais alterados
                        for mat_alt in alteracoes['materiais']:
                            self.cursor.execute("""
                                SELECT COUNT(*) as count FROM produtos_materiais 
                                WHERE produto_id = %s AND material_id = %s
                            """, (produto['id'], mat_alt['id']))
                            if self.cursor.fetchone()['count'] > 0:
                                materiais_alterados.append(mat_alt['nome'])
                        
                        # Verificar máquinas alteradas
                        for maq_alt in alteracoes['maquinas']:
                            self.cursor.execute("""
                                SELECT COUNT(*) as count FROM produtos_etapas 
                                WHERE produto_id = %s AND equipamento_id = %s AND equipamento_tipo = 'maquina'
                            """, (produto['id'], maq_alt['id']))
                            if self.cursor.fetchone()['count'] > 0:
                                maquinas_alteradas.append(maq_alt['nome'])
                        
                        produtos_afetados.append({
                            'id': produto['id'],
                            'nome': produto['nome'],
                            'codigo': produto['codigo'],
                            'categoria': produto['categoria_nome'],
                            'preco_atual': float(produto['preco']),
                            'novo_preco': round(novo_preco, 2),
                            'diferenca': round(novo_preco - float(produto['preco']), 2),
                            'variacao_percentual': round(variacao, 2),
                            'impacto': impacto,
                            'causa': self._gerar_causa(materiais_alterados, maquinas_alteradas),
                            'materiais_alterados': materiais_alterados,
                            'maquinas_alteradas': maquinas_alteradas
                        })
            
            return {
                'produtos_afetados': produtos_afetados,
                'total': len(produtos_afetados)
            }
            
        except Error as e:
            print(f"[ERROR] Erro ao calcular impacto de alterações: {str(e)}")
            return {
                'produtos_afetados': [],
                'total': 0
            }

    def recalcular_precos_produtos(self, materiais_alterados, maquinas_alteradas):
        """
        Recalcula os preços dos produtos baseado em alterações de custos
        """
        try:
            alteracoes = {
                'materiais': materiais_alterados,
                'maquinas': maquinas_alteradas
            }
            
            return self.calcular_impacto_alteracoes_precos(alteracoes)
            
        except Error as e:
            print(f"[ERROR] Erro ao recalcular preços: {str(e)}")
            return []

    def aplicar_atualizacao_precos(self, produtos):
        """
        Aplica as atualizações de preços nos produtos selecionados
        """
        try:
            atualizados = 0
            erros = []
            
            for produto in produtos:
                try:
                    print(f"[DEBUG] Processando produto: {produto}")
                    produto_id = produto['id']
                    print(f"[DEBUG] Produto ID: {produto_id}")
                    
                    # Busca o preço atual do produto se preco_anterior não foi fornecido
                    preco_anterior = produto.get('preco_anterior')
                    if preco_anterior is None:
                        query_preco = "SELECT preco FROM produtos WHERE id = %s"
                        self.cursor.execute(query_preco, (produto_id,))
                        resultado = self.cursor.fetchone()
                        print(f"[DEBUG] Resultado da consulta de preço: {resultado}")
                        if resultado:
                            preco_anterior = float(resultado['preco'] if 'preco' in resultado else resultado[0])
                        else:
                            preco_anterior = 0.0
                    
                    print(f"[DEBUG] Preço anterior: {preco_anterior}")
                    print(f"[DEBUG] Novo preço: {produto['novo_preco']}")
                    
                    # Atualizar o preço do produto
                    query = """
                        UPDATE produtos 
                        SET preco = %s, 
                            data_atualizacao = NOW(),
                            preco_anterior = %s
                        WHERE id = %s
                    """
                    
                    self.cursor.execute(query, (
                        float(produto['novo_preco']),
                        float(preco_anterior),
                        produto_id
                    ))
                    
                    print(f"[DEBUG] Atualizando produto {produto_id}: preço {produto['novo_preco']}, linhas afetadas: {self.cursor.rowcount}")
                    
                    if self.cursor.rowcount > 0:
                        # Recalcular e atualizar os custos detalhados do produto
                        print(f"[DEBUG] Chamando _atualizar_custos_detalhados_produto para produto {produto_id}")
                        self._atualizar_custos_detalhados_produto(produto_id)
                        atualizados += 1
                    else:
                        erros.append(f"Produto ID {produto_id} não encontrado")
                        
                except Error as e:
                    erros.append(f"Erro ao atualizar produto ID {produto.get('id', 'N/A')}: {str(e)}")
                except KeyError as e:
                    erros.append(f"Campo obrigatório ausente para produto ID {produto.get('id', 'N/A')}: {str(e)}")
                    print(f"[DEBUG] KeyError details: {e}, produto: {produto}")
                except (ValueError, TypeError) as e:
                    erros.append(f"Erro de tipo/valor para produto ID {produto.get('id', 'N/A')}: {str(e)}")
                    print(f"[DEBUG] ValueError/TypeError details: {e}, produto: {produto}")
            
            self.connection.commit()
            
            return {
                'atualizados': atualizados,
                'erros': erros
            }
            
        except Error as e:
            self.connection.rollback()
            print(f"[ERROR] Erro ao aplicar atualizações de preços: {str(e)}")
            return {
                'atualizados': 0,
                'erros': [f"Erro geral: {str(e)}"]
            }

    def listar_produtos_com_custos_detalhados(self):
        """
        Lista todos os produtos com seus custos detalhados
        """
        try:
            query = """
                SELECT p.id, p.nome, p.codigo, p.preco, p.margem_lucro,
                       cp.nome as categoria_nome,
                       p.data_criacao, p.data_atualizacao
                FROM produtos p
                LEFT JOIN categoria_produtos cp ON p.categoria_id = cp.id
                ORDER BY p.nome
            """
            
            self.cursor.execute(query)
            produtos = self.cursor.fetchall()
            
            # Para cada produto, calcular custos detalhados
            for produto in produtos:
                custo_materiais = self._calcular_custo_materiais_produto(produto['id'])
                custo_etapas = self._calcular_custo_etapas_produto(produto['id'])
                custo_total = custo_materiais + custo_etapas
                
                # Convert Decimal values to float
                produto['preco'] = float(produto['preco']) if produto['preco'] else 0.0
                produto['margem_lucro'] = float(produto['margem_lucro']) if produto['margem_lucro'] else 0.0
                produto['custo_materiais'] = float(custo_materiais)
                produto['custo_etapas'] = float(custo_etapas)
                produto['custo_total'] = float(custo_total)
                
            return produtos
            
        except Error as e:
            print(f"[ERROR] Erro ao listar produtos com custos: {str(e)}")
            return []

    def recalcular_preco_produto_individual(self, produto_id):
        """
        Recalcula o preço de um produto específico baseado nos custos atuais
        """
        try:
            # Buscar dados do produto
            query = """
                SELECT p.id, p.nome, p.codigo, p.preco, p.margem_lucro
                FROM produtos p
                WHERE p.id = %s
            """
            
            self.cursor.execute(query, (produto_id,))
            produto = self.cursor.fetchone()
            
            if not produto:
                return None
            
            # Calcular custos atuais
            custo_materiais = self._calcular_custo_materiais_produto(produto_id)
            custo_etapas = self._calcular_custo_etapas_produto(produto_id)
            custo_total = float(custo_materiais) + float(custo_etapas)
            
            # Calcular novo preço com margem
            margem = float(produto['margem_lucro'] or 0)
            novo_preco = custo_total * (1 + margem / 100)
            
            # Atualizar preço no banco
            update_query = """
                UPDATE produtos 
                SET preco = %s, data_atualizacao = NOW()
                WHERE id = %s
            """
            
            self.cursor.execute(update_query, (novo_preco, produto_id))
            self.connection.commit()
            
            # Convert all numeric values to float
            produto['preco_anterior'] = float(produto['preco']) if produto['preco'] else 0.0
            produto['preco'] = float(novo_preco)
            produto['margem_lucro'] = margem
            produto['custo_materiais'] = float(custo_materiais)
            produto['custo_etapas'] = float(custo_etapas)
            produto['custo_total'] = float(custo_total)
            
            return produto
            
        except Error as e:
            print(f"[ERROR] Erro ao recalcular preço do produto {produto_id}: {str(e)}")
            return None

    # Métodos auxiliares privados
    def _calcular_variacao_percentual(self, valor_anterior, valor_novo):
        """Calcula a variação percentual entre dois valores"""
        # Convert to float to avoid Decimal/float arithmetic issues
        valor_anterior = float(valor_anterior) if valor_anterior is not None else 0.0
        valor_novo = float(valor_novo) if valor_novo is not None else 0.0
        
        if valor_anterior == 0:
            return 100.0 if valor_novo > 0 else 0.0
        return ((valor_novo - valor_anterior) / valor_anterior) * 100.0

    def _determinar_nivel_impacto(self, variacao_abs):
        """Determina o nível de impacto baseado na variação percentual"""
        if variacao_abs >= 20:
            return 'alto'
        elif variacao_abs >= 5:
            return 'medio'
        else:
            return 'baixo'

    def _calcular_novo_custo_produto(self, produto_id, alteracoes):
        """Calcula o novo custo total de um produto baseado nas alterações"""
        try:
            custo_materiais = float(self._calcular_custo_materiais_produto(produto_id, alteracoes['materiais']))
            custo_etapas = float(self._calcular_custo_etapas_produto(produto_id, alteracoes['maquinas']))
            return custo_materiais + custo_etapas
        except:
            return 0.0

    def _calcular_custo_materiais_produto(self, produto_id, materiais_alterados=None):
        """Calcula o custo total dos materiais de um produto com lógica inteligente"""
        try:
            query = """
                SELECT pm.material_id, pm.quantidade_necessaria, pm.area_utilizada,
                       ie.custo_atual, ie.custo_medio, ie.nome,
                       ie.unidade_medida_id, u.nome as unidade_nome, u.is_measurement,
                       ie.largura, ie.comprimento, ie.area, ie.unidades_por_pacote
                FROM produtos_materiais pm
                INNER JOIN itens_estoque ie ON pm.material_id = ie.id
                LEFT JOIN unidades_de_medida u ON ie.unidade_medida_id = u.id
                WHERE pm.produto_id = %s
            """
            
            self.cursor.execute(query, (produto_id,))
            materiais = self.cursor.fetchall()
            
            custo_total = 0.0
            
            for material in materiais:
                # Verificar se este material foi alterado
                custo_unitario = float(material['custo_atual'] or material['custo_medio'] or 0)
                
                if materiais_alterados:
                    material_alterado = next(
                        (m for m in materiais_alterados if m['id'] == material['material_id']), 
                        None
                    )
                    if material_alterado:
                        custo_unitario = float(material_alterado['custo_novo'] or 0)
                
                # Aplicar lógica inteligente para determinar o método de cálculo
                quantidade_necessaria = float(material['quantidade_necessaria'] or 0)
                area_utilizada = float(material['area_utilizada'] or 0)
                unidades_por_pacote = material['unidades_por_pacote']
                is_measurement = material['is_measurement']
                tem_dimensoes = material['largura'] and material['comprimento']
                
                custo_material = self._calcular_custo_material_inteligente(
                    material['nome'], custo_unitario, quantidade_necessaria, area_utilizada,
                    unidades_por_pacote, is_measurement, tem_dimensoes, material['area']
                )
                
                custo_total += custo_material
            
            return custo_total
            
        except Error as e:
            print(f"[ERROR] Erro ao calcular custo de materiais do produto {produto_id}: {str(e)}")
            return 0.0

    def _calcular_custo_material_inteligente(self, nome_material, custo_unitario, quantidade_necessaria, area_utilizada, unidades_por_pacote, is_measurement, tem_dimensoes, area_total_material=None):
        """
        Calcula o custo de um material aplicando lógica inteligente baseada nas características do material
        
        Para materiais dimensionais (chapa, bobina, etc):
        - Se quantidade >= 1 E área utilizada >= área total * quantidade, usar quantidade (chapa inteira)
        - Senão, usar área proporcional
        """
        
        # Regra 1: Materiais vendidos por pacote
        if unidades_por_pacote and unidades_por_pacote > 1:
            pacotes_necessarios = max(1, quantidade_necessaria / unidades_por_pacote)
            custo_material = custo_unitario * pacotes_necessarios
            print(f"[DEBUG] Material {nome_material}: PACOTE - {pacotes_necessarios:.3f} pacotes × R${custo_unitario:.2f} = R${custo_material:.2f}")
            return custo_material
        # Regra 2: Materiais dimensionais (bobinas, chapas, etc)
        if tem_dimensoes and is_measurement:
            area_total_material = float(area_total_material or 0)
            if quantidade_necessaria >= 1 and area_utilizada >= area_total_material * quantidade_necessaria * 0.99:
                custo_material = custo_unitario * quantidade_necessaria
                print(f"[DEBUG] Material {nome_material}: CHAPA INTEIRA - {quantidade_necessaria} × R${custo_unitario:.2f} = R${custo_material:.2f}")
                return custo_material

            elif area_utilizada > 0 and area_total_material > 0:
                custo_material = custo_unitario * (area_utilizada / area_total_material)
                print(f"[DEBUG] Material {nome_material}: ÁREA PROPORCIONAL - {area_utilizada:.4f} m² de {area_total_material:.4f} m² × R${custo_unitario:.2f} = R${custo_material:.2f}")
                return custo_material
        # Regra 3: Materiais unitários (quantidade >= 1)
        if quantidade_necessaria >= 1.0:
            custo_material = custo_unitario * quantidade_necessaria
            print(f"[DEBUG] Material {nome_material}: QUANTIDADE - {quantidade_necessaria:.3f} unidades × R${custo_unitario:.2f} = R${custo_material:.2f}")
            return custo_material
        # Fallback para área
        if area_utilizada > 0:
            custo_material = custo_unitario * area_utilizada
            print(f"[DEBUG] Material {nome_material}: ÁREA FALLBACK - {area_utilizada:.4f} m² × R${custo_unitario:.2f} = R${custo_material:.2f}")
            return custo_material
        # Último fallback: usar quantidade mesmo se < 1
        custo_material = custo_unitario * quantidade_necessaria
        print(f"[DEBUG] Material {nome_material}: QUANTIDADE FALLBACK - {quantidade_necessaria:.3f} × R${custo_unitario:.2f} = R${custo_material:.2f}")
        return custo_material

    def _calcular_custo_etapas_produto(self, produto_id, maquinas_alteradas=None):
        """Calcula o custo total das etapas de um produto"""
        try:
            query = """
                SELECT pe.tempo_estimado, pe.custo_estimado, pe.equipamento_id, pe.equipamento_tipo,
                       m.hora_maquina, m.metros_quadrados_por_hora
                FROM produtos_etapas pe
                LEFT JOIN maquinas m ON pe.equipamento_id = m.id AND pe.equipamento_tipo = 'maquina'
                WHERE pe.produto_id = %s
            """
            
            self.cursor.execute(query, (produto_id,))
            etapas = self.cursor.fetchall()
            
            custo_total = 0.0
            
            for etapa in etapas:
                # Se há custo estimado definido, usar ele apenas se não for máquina alterada
                usar_custo_estimado = True
                
                # Se for máquina e há alterações, recalcular
                if etapa['equipamento_tipo'] == 'maquina' and maquinas_alteradas:
                    maquina_alterada = next(
                        (m for m in maquinas_alteradas if m['id'] == etapa['equipamento_id']), 
                        None
                    )
                    if maquina_alterada:
                        usar_custo_estimado = False
                
                if usar_custo_estimado and etapa['custo_estimado'] and float(etapa['custo_estimado']) > 0:
                    custo_total += float(etapa['custo_estimado'])
                # Senão, calcular baseado no equipamento (se for máquina)
                elif etapa['equipamento_tipo'] == 'maquina' and etapa['hora_maquina']:
                    # Converter tempo estimado (HH:MM:SS) para horas
                    tempo_str = str(etapa['tempo_estimado']) if etapa['tempo_estimado'] else '00:00:00'
                    try:
                        if ':' in tempo_str:
                            parts = tempo_str.split(':')
                            horas = float(parts[0]) if len(parts) > 0 else 0
                            minutos = float(parts[1]) if len(parts) > 1 else 0
                            segundos = float(parts[2]) if len(parts) > 2 else 0
                            tempo_horas = horas + (minutos / 60.0) + (segundos / 3600.0)
                        else:
                            tempo_horas = float(tempo_str)
                    except (ValueError, IndexError):
                        tempo_horas = 0.0
                    
                    # Verificar se esta máquina foi alterada
                    custo_por_hora = float(etapa['hora_maquina'] or 0)  # hora_maquina é o custo por hora
                    if maquinas_alteradas:
                        maquina_alterada = next(
                            (m for m in maquinas_alteradas if m['id'] == etapa['equipamento_id']), 
                            None
                        )
                        if maquina_alterada:
                            custo_por_hora = float(maquina_alterada['custo_por_hora'] or 0)
                    
                    custo_etapa = custo_por_hora * tempo_horas
                    custo_total += custo_etapa
            
            return custo_total
            
        except Error as e:
            print(f"[ERROR] Erro ao calcular custo de etapas do produto {produto_id}: {str(e)}")
            return 0.0

    def _calcular_custo_antes_periodo(self, item_id, dias):
        """
        Calcula qual era o custo de um item antes do período especificado
        Simula o custo médio ponderado excluindo as entradas do período
        """
        try:
            # Buscar todas as entradas do item, exceto as do período recente
            query_entradas_anteriores = """
                SELECT ee.quantidade, ee.custo_unitario, ee.data_entrada
                FROM entradas_estoque ee
                WHERE ee.item_id = %s
                AND ee.data_entrada < DATE_SUB(NOW(), INTERVAL %s DAY)
                AND ee.custo_unitario IS NOT NULL
                ORDER BY ee.data_entrada ASC
            """
            
            self.cursor.execute(query_entradas_anteriores, (item_id, dias))
            entradas_anteriores = self.cursor.fetchall()
            
            if not entradas_anteriores:
                # Se não há entradas anteriores, buscar a primeira entrada do período como referência
                query_primeira_entrada = """
                    SELECT custo_unitario
                    FROM entradas_estoque
                    WHERE item_id = %s
                    AND custo_unitario IS NOT NULL
                    ORDER BY data_entrada ASC
                    LIMIT 1
                """
                self.cursor.execute(query_primeira_entrada, (item_id,))
                primeira_entrada = self.cursor.fetchone()
                return float(primeira_entrada['custo_unitario']) if primeira_entrada else 0.0
            
            # Calcular custo médio ponderado das entradas anteriores
            quantidade_total = 0.0
            valor_total = 0.0
            
            for entrada in entradas_anteriores:
                quantidade = float(entrada['quantidade'])
                custo = float(entrada['custo_unitario'])
                quantidade_total += quantidade
                valor_total += quantidade * custo
            
            if quantidade_total > 0:
                custo_medio_anterior = valor_total / quantidade_total
            else:
                custo_medio_anterior = 0.0
            
            return custo_medio_anterior
            
        except Exception as e:
            print(f"[ERROR] Erro ao calcular custo antes do período para item {item_id}: {str(e)}")
            return 0.0

    def _atualizar_custos_detalhados_produto(self, produto_id):
        """
        Atualiza os custos detalhados do produto nas tabelas relacionadas
        """
        try:
            # 1. Atualizar custos unitários e subtotais na tabela produtos_materiais
            query_materiais = """
                UPDATE produtos_materiais pm
                INNER JOIN itens_estoque ie ON pm.material_id = ie.id
                SET pm.custo_unitario = COALESCE(ie.custo_atual, ie.custo_medio, 0),
                    pm.subtotal = CASE 
                        WHEN pm.area_utilizada IS NOT NULL AND pm.area_utilizada > 0 
                        THEN COALESCE(ie.custo_atual, ie.custo_medio, 0) * pm.area_utilizada
                        ELSE COALESCE(ie.custo_atual, ie.custo_medio, 0) * pm.quantidade_necessaria
                    END
                WHERE pm.produto_id = %s
            """
            
            self.cursor.execute(query_materiais, (produto_id,))
            
            # 2. Atualizar custos individuais das etapas na tabela produtos_etapas
            self._atualizar_custos_etapas_individuais(produto_id)
            
            # 3. Recalcular custo total de materiais para o produto
            query_custo_materiais = """
                SELECT COALESCE(SUM(pm.subtotal), 0) as custo_total_materiais
                FROM produtos_materiais pm
                WHERE pm.produto_id = %s
            """
            
            self.cursor.execute(query_custo_materiais, (produto_id,))
            resultado = self.cursor.fetchone()
            custo_total_materiais = float(resultado['custo_total_materiais'] or 0)
            
            # 4. Recalcular custo total de etapas para o produto
            custo_etapas = self._calcular_custo_etapas_produto(produto_id)
            
            # 5. Atualizar coluna custo_materiais na tabela produtos
            query_update_produto = """
                UPDATE produtos 
                SET custo_materiais = %s,
                    custo_etapas = %s
                WHERE id = %s
            """
            
            self.cursor.execute(query_update_produto, (
                custo_total_materiais,
                float(custo_etapas),
                produto_id
            ))
            
            print(f"[DEBUG] Custos atualizados para produto {produto_id}: Materiais R${custo_total_materiais:.2f}, Etapas R${custo_etapas:.2f}")
            
        except Error as e:
            print(f"[ERROR] Erro ao atualizar custos detalhados do produto {produto_id}: {str(e)}")
            raise

    def _gerar_causa(self, materiais_alterados, maquinas_alteradas):
        """Gera a descrição da causa das alterações"""
        causas = []
        if materiais_alterados:
            causas.append(f"Material: {', '.join(materiais_alterados)}")
        if maquinas_alteradas:
            causas.append(f"Máquina: {', '.join(maquinas_alteradas)}")
        return ', '.join(causas) if causas else "Alteração de custos"

    def _atualizar_custos_etapas_individuais(self, produto_id):
        """
        Atualiza os custos individuais das etapas na tabela produtos_etapas
        """
        try:
            # Buscar todas as etapas do produto
            query_etapas = """
                SELECT pe.id, pe.tempo_estimado, pe.custo_estimado, pe.equipamento_id, pe.equipamento_tipo,
                       m.hora_maquina, m.metros_quadrados_por_hora
                FROM produtos_etapas pe
                LEFT JOIN maquinas m ON pe.equipamento_id = m.id AND pe.equipamento_tipo = 'maquina'
                WHERE pe.produto_id = %s
            """
            
            self.cursor.execute(query_etapas, (produto_id,))
            etapas = self.cursor.fetchall()
            
            print(f"[DEBUG] Atualizando custos de {len(etapas)} etapas para produto {produto_id}")
            
            for etapa in etapas:
                novo_custo = None
                
                # Se for etapa de máquina, recalcular baseado no valor/hora atual
                if etapa['equipamento_tipo'] == 'maquina' and etapa['hora_maquina'] and etapa['tempo_estimado']:
                    # Converter tempo estimado (HH:MM:SS) para horas
                    tempo_str = str(etapa['tempo_estimado']) if etapa['tempo_estimado'] else '00:00:00'
                    try:
                        if ':' in tempo_str:
                            parts = tempo_str.split(':')
                            horas = float(parts[0]) if len(parts) > 0 else 0
                            minutos = float(parts[1]) if len(parts) > 1 else 0
                            segundos = float(parts[2]) if len(parts) > 2 else 0
                            tempo_horas = horas + (minutos / 60.0) + (segundos / 3600.0)
                        else:
                            tempo_horas = float(tempo_str)
                    except (ValueError, IndexError):
                        tempo_horas = 0.0
                    
                    # Calcular novo custo baseado no valor/hora atual da máquina
                    custo_por_hora = float(etapa['hora_maquina'] or 0)
                    novo_custo = custo_por_hora * tempo_horas
                    
                    print(f"[DEBUG] Etapa ID {etapa['id']}: {tempo_horas:.6f}h × R${custo_por_hora:.2f} = R${novo_custo:.2f}")
                    
                    # Atualizar o custo da etapa na tabela
                    query_update_etapa = """
                        UPDATE produtos_etapas 
                        SET custo_estimado = %s
                        WHERE id = %s
                    """
                    
                    self.cursor.execute(query_update_etapa, (novo_custo, etapa['id']))
                    print(f"[DEBUG] Custo da etapa ID {etapa['id']} atualizado de R${float(etapa['custo_estimado'] or 0):.2f} para R${novo_custo:.2f}")
                
                # Para outros tipos de etapas (ferramentas, manual, etc.), manter o custo existente
                else:
                    print(f"[DEBUG] Etapa ID {etapa['id']} (tipo: {etapa['equipamento_tipo']}): mantendo custo R${float(etapa['custo_estimado'] or 0):.2f}")
            
        except Error as e:
            print(f"[ERROR] Erro ao atualizar custos das etapas individuais do produto {produto_id}: {str(e)}")
            raise

    def _determinar_nivel_impacto(self, variacao_abs):
        """Determina o nível de impacto baseado na variação percentual"""
        if variacao_abs >= 20:
            return 'alto'
        elif variacao_abs >= 5:
            return 'medio'
        else:
            return 'baixo'

    # Métodos para Anexos de Produtos
    def inserir_anexo_produto(self, produto_id, nome_original, conteudo_blob, tamanho, tipo_mime, caminho_fisico=None, descricao=None):
        """Insere um anexo para um produto"""
        try:
            # Gerar nome do arquivo (pode ser o mesmo que o nome original para anexos em BLOB)
            nome_arquivo = nome_original
            
            query = """
                INSERT INTO produtos_anexos (produto_id, nome_arquivo, nome_original, conteudo_blob, tamanho, tipo_mime, caminho_fisico, armazenar_em_blob, descricao)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            # Definir se vai armazenar em BLOB (TRUE) ou arquivo físico (FALSE)
            armazenar_em_blob = True if conteudo_blob else False
            
            self.cursor.execute(query, (produto_id, nome_arquivo, nome_original, conteudo_blob, tamanho, tipo_mime, caminho_fisico, armazenar_em_blob, descricao))
            self.connection.commit()
            
            anexo_id = self.cursor.lastrowid
            print(f"[DEBUG] Anexo inserido com sucesso. ID: {anexo_id}, Categoria: {descricao}")
            return anexo_id
            
        except Error as e:
            print(f"[ERROR] Erro ao inserir anexo do produto: {str(e)}")
            self.connection.rollback()
            return None

    def listar_anexos_produto(self, produto_id):
        """Lista todos os anexos de um produto"""
        try:
            query = """
                SELECT id, nome_original, tamanho, tipo_mime, data_upload, caminho_fisico, descricao
                FROM produtos_anexos 
                WHERE produto_id = %s 
                ORDER BY data_upload ASC
            """
            
            self.cursor.execute(query, (produto_id,))
            anexos = self.cursor.fetchall()
            
            # Converter tamanho para formato legível
            for anexo in anexos:
                anexo['tamanho_formatado'] = self._formatar_tamanho_arquivo(anexo['tamanho'])
            
            return anexos
            
        except Error as e:
            print(f"[ERROR] Erro ao listar anexos do produto: {str(e)}")
            return []

    def buscar_anexo_produto(self, anexo_id):
        """Busca um anexo específico pelo ID"""
        try:
            query = """
                SELECT id, produto_id, nome_original, conteudo_blob, tamanho, tipo_mime, data_upload, caminho_fisico
                FROM produtos_anexos 
                WHERE id = %s
            """
            
            self.cursor.execute(query, (anexo_id,))
            anexo = self.cursor.fetchone()
            
            return anexo
            
        except Error as e:
            print(f"[ERROR] Erro ao buscar anexo: {str(e)}")
            return None

    def remover_anexo_produto(self, anexo_id):
        """Remove um anexo de produto"""
        try:
            # Primeiro buscar informações do anexo
            anexo = self.buscar_anexo_produto(anexo_id)
            if not anexo:
                return False
            
            # Remover do banco de dados
            query = "DELETE FROM produtos_anexos WHERE id = %s"
            self.cursor.execute(query, (anexo_id,))
            self.connection.commit()
            
            print(f"[DEBUG] Anexo ID {anexo_id} removido com sucesso")
            return True
            
        except Error as e:
            print(f"[ERROR] Erro ao remover anexo: {str(e)}")
            self.connection.rollback()
            return False

    def deletar_produto(self, produto_id):
        """Deleta um produto e todos os seus dados relacionados"""
        try:
            # Verificar se o produto existe
            self.cursor.execute("SELECT id, nome FROM produtos WHERE id = %s", (produto_id,))
            produto = self.cursor.fetchone()
            
            if not produto:
                return {"erro": "Produto não encontrado"}
            
            nome_produto = produto['nome']
            
            # Remover anexos do produto
            self.cursor.execute("DELETE FROM produtos_anexos WHERE produto_id = %s", (produto_id,))
            anexos_removidos = self.cursor.rowcount
            
            # Remover materiais do produto
            self.cursor.execute("DELETE FROM produtos_materiais WHERE produto_id = %s", (produto_id,))
            materiais_removidos = self.cursor.rowcount
            
            # Remover etapas do produto
            self.cursor.execute("DELETE FROM produtos_etapas WHERE produto_id = %s", (produto_id,))
            etapas_removidas = self.cursor.rowcount
            
            # Remover o produto principal
            self.cursor.execute("DELETE FROM produtos WHERE id = %s", (produto_id,))
            
            if self.cursor.rowcount == 0:
                self.connection.rollback()
                return {"erro": "Erro ao deletar produto"}
            
            self.connection.commit()
            
            print(f"[DEBUG] Produto '{nome_produto}' (ID: {produto_id}) deletado com sucesso")
            print(f"[DEBUG] - Anexos removidos: {anexos_removidos}")
            print(f"[DEBUG] - Materiais removidos: {materiais_removidos}")
            print(f"[DEBUG] - Etapas removidas: {etapas_removidas}")
            
            return {
                "sucesso": f"Produto '{nome_produto}' deletado com sucesso",
                "detalhes": {
                    "anexos_removidos": anexos_removidos,
                    "materiais_removidos": materiais_removidos,
                    "etapas_removidas": etapas_removidas
                }
            }
            
        except Error as e:
            print(f"[ERROR] Erro ao deletar produto: {str(e)}")
            self.connection.rollback()
            return {"erro": f"Erro ao deletar produto: {str(e)}"}

    def atualizar_categoria_anexo_produto(self, anexo_id, categoria):
        """Atualiza a categoria (descrição) de um anexo de produto"""
        try:
            query = """
                UPDATE produtos_anexos 
                SET descricao = %s 
                WHERE id = %s
            """
            
            self.cursor.execute(query, (categoria, anexo_id))
            linhas_afetadas = self.cursor.rowcount
            self.connection.commit()
            
            print(f"[DEBUG] Categoria do anexo ID {anexo_id} atualizada para '{categoria}' - Linhas afetadas: {linhas_afetadas}")
            return linhas_afetadas > 0
            
        except Error as e:
            print(f"[ERROR] Erro ao atualizar categoria do anexo: {str(e)}")
            self.connection.rollback()
            return False

    # Métodos para Kits
    def criar_kit(self, codigo, nome, descricao=None, produtos=None):
        """Cria um novo kit com os produtos associados"""
        try:
            print(f"[DEBUG] Criando kit: codigo={codigo}, nome={nome}, descricao={descricao}")
            print(f"[DEBUG] Produtos recebidos: {produtos}")
            
            # Verificar se o código já existe
            self.cursor.execute("SELECT id FROM kits WHERE codigo = %s", (codigo,))
            if self.cursor.fetchone():
                return {"erro": "Código do kit já existe"}

            # Inserir o kit
            insert_kit_query = """
                INSERT INTO kits (codigo, nome, descricao, status) 
                VALUES (%s, %s, %s, 'Ativo')
            """
            self.cursor.execute(insert_kit_query, (codigo, nome, descricao))
            kit_id = self.cursor.lastrowid
            print(f"[DEBUG] Kit inserido com ID: {kit_id}")

            # Inserir produtos do kit se fornecidos
            if produtos and len(produtos) > 0:
                for i, produto in enumerate(produtos):
                    produto_id = produto.get('id')
                    quantidade = produto.get('quantidade', 1)
                    ordem = produto.get('ordem', i + 1)  # Use index as order if not provided
                    
                    print(f"[DEBUG] Inserindo produto {i}: id={produto_id}, quantidade={quantidade}, ordem={ordem}")
                    
                    if not produto_id:
                        print(f"[ERROR] Produto sem ID: {produto}")
                        continue
                    
                    insert_produto_query = """
                        INSERT INTO kits_produtos (kit_id, produto_id, quantidade, ordem) 
                        VALUES (%s, %s, %s, %s)
                    """
                    self.cursor.execute(insert_produto_query, (kit_id, produto_id, quantidade, ordem))

            self.connection.commit()
            print(f"[DEBUG] Kit criado com sucesso, ID: {kit_id}")
            return {"sucesso": "Kit criado com sucesso", "id": kit_id}

        except Error as e:
            print(f"[ERROR] Erro na criação do kit: {str(e)}")
            self.connection.rollback()
            return {"erro": f"Erro ao criar kit: {str(e)}"}

    def listar_kits(self):
        """Lista todos os kits com suas informações básicas"""
        try:
            query = """
                SELECT k.*, 
                       COUNT(kp.produto_id) as total_produtos
                FROM kits k
                LEFT JOIN kits_produtos kp ON k.id = kp.kit_id
                WHERE k.status = 'Ativo'
                GROUP BY k.id
                ORDER BY k.data_criacao DESC
            """
            self.cursor.execute(query)
            return self.cursor.fetchall()

        except Error as e:
            print(f"Erro ao listar kits: {e}")
            return []

    def buscar_kit_por_id(self, kit_id):
        """Busca um kit específico com todos os seus produtos"""
        try:
            # Buscar informações do kit
            kit_query = """
                SELECT * FROM kits WHERE id = %s
            """
            self.cursor.execute(kit_query, (kit_id,))
            kit = self.cursor.fetchone()

            if not kit:
                return None

            # Buscar produtos do kit
            produtos_query = """
                SELECT kp.*, p.nome, p.codigo as produto_codigo, p.preco, 
                       p.custo_materiais, p.custo_etapas, p.descricao,
                       cp.nome as categoria_nome
                FROM kits_produtos kp
                INNER JOIN produtos p ON kp.produto_id = p.id
                LEFT JOIN categoria_produtos cp ON p.categoria_id = cp.id
                WHERE kp.kit_id = %s
                ORDER BY kp.ordem ASC, kp.id ASC
            """
            self.cursor.execute(produtos_query, (kit_id,))
            produtos = self.cursor.fetchall()

            kit['produtos'] = produtos
            return kit

        except Error as e:
            print(f"Erro ao buscar kit: {e}")
            return None

    def atualizar_kit(self, kit_id, codigo=None, nome=None, descricao=None, produtos=None):
        """Atualiza um kit existente"""
        try:
            updates = []
            params = []

            if codigo is not None:
                # Verificar se o código já existe em outro kit
                self.cursor.execute("SELECT id FROM kits WHERE codigo = %s AND id != %s", (codigo, kit_id))
                if self.cursor.fetchone():
                    return {"erro": "Código do kit já existe"}
                updates.append("codigo = %s")
                params.append(codigo)

            if nome is not None:
                updates.append("nome = %s")
                params.append(nome)

            if descricao is not None:
                updates.append("descricao = %s")
                params.append(descricao)

            if updates:
                updates.append("data_atualizacao = CURRENT_TIMESTAMP")
                params.append(kit_id)
                
                update_query = f"UPDATE kits SET {', '.join(updates)} WHERE id = %s"
                self.cursor.execute(update_query, params)

            # Atualizar produtos se fornecidos
            if produtos is not None:
                # Remover produtos existentes
                self.cursor.execute("DELETE FROM kits_produtos WHERE kit_id = %s", (kit_id,))
                
                # Adicionar novos produtos
                for produto in produtos:
                    produto_id = produto.get('id')
                    quantidade = produto.get('quantidade', 1)
                    ordem = produto.get('ordem')
                    
                    insert_produto_query = """
                        INSERT INTO kits_produtos (kit_id, produto_id, quantidade, ordem) 
                        VALUES (%s, %s, %s, %s)
                    """
                    self.cursor.execute(insert_produto_query, (kit_id, produto_id, quantidade, ordem))

            self.connection.commit()
            return {"sucesso": "Kit atualizado com sucesso"}

        except Error as e:
            self.connection.rollback()
            return {"erro": f"Erro ao atualizar kit: {str(e)}"}

    def deletar_kit(self, kit_id):
        """Remove um kit (soft delete - altera status para Inativo)"""
        try:
            update_query = """
                UPDATE kits SET status = 'Inativo', data_atualizacao = CURRENT_TIMESTAMP 
                WHERE id = %s
            """
            self.cursor.execute(update_query, (kit_id,))
            
            if self.cursor.rowcount > 0:
                self.connection.commit()
                return {"sucesso": "Kit removido com sucesso"}
            else:
                return {"erro": "Kit não encontrado"}

        except Error as e:
            self.connection.rollback()
            return {"erro": f"Erro ao remover kit: {str(e)}"}

    def verificar_codigo_kit_existe(self, codigo):
        """Verifica se um código de kit já existe"""
        try:
            self.cursor.execute("SELECT id FROM kits WHERE codigo = %s", (codigo,))
            return self.cursor.fetchone() is not None
        except Error as e:
            print(f"Erro ao verificar código do kit: {e}")
            return False

    def _formatar_tamanho_arquivo(self, tamanho_bytes):
        """Formata o tamanho do arquivo em formato legível"""
        if tamanho_bytes < 1024:
            return f"{tamanho_bytes} B"
        elif tamanho_bytes < 1024 * 1024:
            return f"{tamanho_bytes / 1024:.1f} KB"
        elif tamanho_bytes < 1024 * 1024 * 1024:
            return f"{tamanho_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{tamanho_bytes / (1024 * 1024 * 1024):.1f} GB"

    # ====== MÉTODOS PARA ORÇAMENTOS ======
    
    def criar_orcamento(self, orcamento_data):
        """Cria um novo orçamento"""
        try:
            query = """
                INSERT INTO orcamentos (
                    numero, data_orcamento, cliente_id, vendedor_id, data_validade, 
                    validade_dias, prazo_entrega, data_hora_entrega, condicoes_pagamento, parcelas, observacoes, 
                    valor_total, subtotal, desconto, custo_total, margem_lucro, 
                    lucro_estimado, status, data_criacao
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
            """
            
            values = (
                orcamento_data['numero'],
                orcamento_data['data_orcamento'],
                orcamento_data['cliente_id'],
                orcamento_data.get('vendedor_id'),
                orcamento_data.get('validade'),  # Mapeia para data_validade
                orcamento_data.get('validade_dias', 30),  # Dias calculados
                orcamento_data.get('prazo_entrega'),  # Campo prazo_entrega
                orcamento_data.get('data_hora_entrega'),  # Nova coluna data_hora_entrega
                orcamento_data.get('condicoes_pagamento'),
                orcamento_data.get('parcelas'),
                orcamento_data.get('observacoes', ''),  # Observações do orçamento
                orcamento_data['valor_total'],
                orcamento_data.get('subtotal', 0),
                orcamento_data.get('desconto', 0),
                orcamento_data.get('custo_total', 0),
                orcamento_data.get('margem_lucro', 0),  # Margem de lucro média
                orcamento_data.get('lucro_estimado', 0),  # Lucro estimado
                orcamento_data.get('status', 'Pendente')
            )
            
            print(f"[DEBUG] Inserindo orçamento com margem_lucro: {orcamento_data.get('margem_lucro', 0)}")
            print(f"[DEBUG] Observações recebidas no database: '{orcamento_data.get('observacoes', '')}' (tipo: {type(orcamento_data.get('observacoes', ''))})")
            
            self.cursor.execute(query, values)
            self.connection.commit()
            return self.cursor.lastrowid
            
        except Error as e:
            print(f"Erro ao criar orçamento: {e}")
            return None

    def atualizar_orcamento(self, orcamento_id, orcamento_data):
        """Atualiza um orçamento existente"""
        try:
            # Primeiro, atualizar os dados principais do orçamento
            query = """
                UPDATE orcamentos SET 
                    cliente_id = %s, vendedor_id = %s, data_validade = %s, 
                    validade_dias = %s, prazo_entrega = %s, data_hora_entrega = %s, 
                    condicoes_pagamento = %s, parcelas = %s, observacoes = %s, 
                    valor_total = %s, subtotal = %s, desconto = %s, custo_total = %s, 
                    margem_lucro = %s, lucro_estimado = %s, status = %s, data_atualizacao = NOW()
                WHERE id = %s
            """
            
            values = (
                orcamento_data['cliente_id'],
                orcamento_data.get('vendedor_id'),
                orcamento_data.get('validade'),
                orcamento_data.get('validade_dias', 30),
                orcamento_data.get('prazo_entrega'),
                orcamento_data.get('data_hora_entrega'),
                orcamento_data.get('condicoes_pagamento'),
                orcamento_data.get('parcelas'),
                orcamento_data.get('observacoes', ''),
                orcamento_data['valor_total'],
                orcamento_data.get('subtotal', 0),
                orcamento_data.get('desconto', 0),
                orcamento_data.get('custo_total', 0),
                orcamento_data.get('margem_lucro', 0),
                orcamento_data.get('lucro_estimado', 0),
                orcamento_data.get('status', 'Pendente'),
                orcamento_id
            )
            
            print(f"[DEBUG] Atualizando orçamento ID {orcamento_id} com margem_lucro: {orcamento_data.get('margem_lucro', 0)}")
            print(f"[DEBUG] Observações atualizadas: '{orcamento_data.get('observacoes', '')}' (tipo: {type(orcamento_data.get('observacoes', ''))})")
            
            self.cursor.execute(query, values)
            
            # Deletar itens existentes do orçamento
            delete_query = "DELETE FROM orcamentos_itens WHERE orcamento_id = %s"
            self.cursor.execute(delete_query, (orcamento_id,))
            
            # Inserir novos itens
            itens = orcamento_data.get('itens', [])
            for item in itens:
                item['orcamento_id'] = orcamento_id
                self.criar_item_orcamento(item)
            
            self.connection.commit()
            print(f"[DEBUG] Orçamento ID {orcamento_id} atualizado com sucesso")
            return {'success': True, 'message': 'Orçamento atualizado com sucesso'}
            
        except Error as e:
            self.connection.rollback()
            print(f"Erro ao atualizar orçamento: {e}")
            return {'success': False, 'message': str(e)}
            return None

    def criar_item_orcamento(self, item_data):
        """Cria um item de orçamento"""
        try:
            # Calcular desconto e subtotal
            quantidade = item_data.get('quantidade', 1)
            preco_unitario = item_data.get('preco_unitario', 0)
            custo_unitario = item_data.get('custo_unitario', 0)
            desconto_item = item_data.get('desconto_item', 0)
            preco_total = item_data.get('preco_total', 0)
            
            # Se o subtotal não foi fornecido, calcular baseado no total
            subtotal = item_data.get('subtotal', preco_total)
            
            query = """
                INSERT INTO orcamentos_itens (
                    orcamento_id, produto_id, produto_nome, quantidade, 
                    preco_unitario, preco_total, descricao, kit_origem, kit_id,
                    custo_unitario, desconto_item, subtotal
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            values = (
                item_data['orcamento_id'],
                item_data.get('produto_id'),
                item_data['produto_nome'],
                quantidade,
                preco_unitario,
                preco_total,
                item_data.get('descricao', ''),
                item_data.get('kit_origem'),
                item_data.get('kit_id'),
                custo_unitario,
                desconto_item,
                subtotal
            )
            
            self.cursor.execute(query, values)
            self.connection.commit()
            return self.cursor.lastrowid
            
        except Error as e:
            print(f"Erro ao criar item de orçamento: {e}")
            return None

    def listar_orcamentos(self):
        """Lista todos os orçamentos"""
        try:
            query = """
                SELECT o.*, 
                       c.nome as cliente_nome,
                       u.nome as vendedor_nome,
                       COUNT(oi.id) as total_itens,
                       COALESCE(o.subtotal, SUM(oi.subtotal), 0) as subtotal,
                       COALESCE(o.desconto, 0) as desconto,
                       COALESCE(o.custo_total, 0) as custo_total,
                       COALESCE(o.margem_lucro, 0) as margem_lucro,
                       COALESCE(o.lucro_estimado, 0) as lucro_estimado,
                       COALESCE(o.valor_total, SUM(oi.preco_total), 0) as total,
                       COALESCE(o.validade_dias, 30) as validade_dias,
                       o.data_orcamento as data_orcamento_timestamp,
                       o.observacoes as observacoes_orcamento,
                       o.prazo_entrega as prazo_entrega_valor
                FROM orcamentos o
                LEFT JOIN clientes c ON o.cliente_id = c.id
                LEFT JOIN usuarios u ON o.vendedor_id = u.id
                LEFT JOIN orcamentos_itens oi ON o.id = oi.orcamento_id
                GROUP BY o.id, o.numero, o.data_orcamento, o.cliente_id, o.vendedor_id, 
                         o.data_validade, o.validade_dias, o.prazo_entrega, o.condicoes_pagamento, 
                         o.parcelas, o.observacoes, o.valor_total, o.subtotal, 
                         o.desconto, o.custo_total, o.margem_lucro, o.lucro_estimado, 
                         o.status, o.data_criacao, c.nome, u.nome
                ORDER BY o.data_criacao DESC
            """
            self.cursor.execute(query)
            return self.cursor.fetchall()

        except Error as e:
            print(f"Erro ao listar orçamentos: {e}")
            return []

    def buscar_orcamento_por_id(self, orcamento_id):
        """Busca um orçamento específico com seus itens"""
        try:
            # Buscar orçamento principal
            orcamento_query = """
                SELECT o.*, 
                       c.nome as cliente_nome, c.email as cliente_email,
                       u.nome as vendedor_nome
                FROM orcamentos o
                LEFT JOIN clientes c ON o.cliente_id = c.id
                LEFT JOIN usuarios u ON o.vendedor_id = u.id
                WHERE o.id = %s
            """
            self.cursor.execute(orcamento_query, (orcamento_id,))
            orcamento = self.cursor.fetchone()

            if not orcamento:
                return None

            # Buscar itens do orçamento com descrições reais dos produtos
            itens_query = """
                SELECT oi.*, p.descricao as produto_descricao_real
                FROM orcamentos_itens oi
                LEFT JOIN produtos p ON oi.produto_id = p.id
                WHERE oi.orcamento_id = %s
                ORDER BY oi.id
            """
            self.cursor.execute(itens_query, (orcamento_id,))
            itens = self.cursor.fetchall()
            
            # Corrigir descrições se necessário
            for item in itens:
                # Se a descrição atual é artificial (contém "Produto do kit"), usar a descrição real
                if item['descricao'] and 'Produto do kit' in item['descricao'] and item['produto_descricao_real']:
                    item['descricao'] = item['produto_descricao_real']
                elif not item['descricao'] and item['produto_descricao_real']:
                    item['descricao'] = item['produto_descricao_real']

            # Adicionar itens ao orçamento
            orcamento['itens'] = itens
            return orcamento

        except Error as e:
            print(f"Erro ao buscar orçamento: {e}")
            return None

    # Métodos para Vendas
    def criar_venda(self, venda_data):
        try:
            # Extrair itens antes de inserir a venda principal
            itens = venda_data.pop('itens', [])
            
            # Inserir venda principal
            venda_query = """
                INSERT INTO vendas (
                    usuario_id, subtotal, desconto, total, metodo_pagamento, 
                    parcelas, data_venda, status, observacoes
                ) VALUES (
                    %(usuario_id)s, %(subtotal)s, %(desconto)s, %(total)s, 
                    %(metodo_pagamento)s, %(parcelas)s, NOW(), 'Concluída', %(observacoes)s
                )
            """
            
            self.cursor.execute(venda_query, venda_data)
            venda_id = self.cursor.lastrowid
            
            # Inserir itens da venda
            for item in itens:
                item_query = """
                    INSERT INTO vendas_itens (
                        venda_id, produto_id, quantidade, preco_unitario, subtotal
                    ) VALUES (%s, %s, %s, %s, %s)
                """
                self.cursor.execute(item_query, (
                    venda_id, 
                    item['produto_id'], 
                    item['quantidade'], 
                    item['preco_unitario'], 
                    item['subtotal']
                ))
            
            self.connection.commit()
            return {"sucesso": "Venda criada com sucesso", "id": venda_id}
            
        except Error as e:
            self.connection.rollback()
            return {"erro": f"Erro ao criar venda: {str(e)}"}

    def listar_vendas(self, data_inicio=None, data_fim=None, usuario_id=None):
        try:
            where_conditions = []
            params = []
            
            if data_inicio:
                where_conditions.append("DATE(v.data_venda) >= %s")
                params.append(data_inicio)
            
            if data_fim:
                where_conditions.append("DATE(v.data_venda) <= %s")
                params.append(data_fim)
                
            if usuario_id:
                where_conditions.append("v.usuario_id = %s")
                params.append(usuario_id)
            
            where_clause = ""
            if where_conditions:
                where_clause = "WHERE " + " AND ".join(where_conditions)
            
            query = f"""
                SELECT 
                    v.id, v.usuario_id, u.nome as usuario_nome,
                    v.subtotal, v.desconto, v.total, v.metodo_pagamento,
                    v.parcelas, v.data_venda, v.status
                FROM vendas v
                LEFT JOIN usuarios u ON v.usuario_id = u.id
                {where_clause}
                ORDER BY v.data_venda DESC
            """
            
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
            
        except Error as e:
            return {"erro": f"Erro ao listar vendas: {str(e)}"}

    def buscar_venda_por_id(self, venda_id):
        try:
            # Buscar dados da venda
            venda_query = """
                SELECT 
                    v.id, v.usuario_id, u.nome as usuario_nome,
                    v.subtotal, v.desconto, v.total, v.metodo_pagamento,
                    v.parcelas, v.data_venda, v.status
                FROM vendas v
                LEFT JOIN usuarios u ON v.usuario_id = u.id
                WHERE v.id = %s
            """
            self.cursor.execute(venda_query, (venda_id,))
            venda = self.cursor.fetchone()
            
            if not venda:
                return None
            
            # Buscar itens da venda
            itens_query = """
                SELECT 
                    vi.produto_id, p.nome as produto_nome, 
                    vi.quantidade, vi.preco_unitario, vi.subtotal
                FROM vendas_itens vi
                LEFT JOIN produtos p ON vi.produto_id = p.id
                WHERE vi.venda_id = %s
                ORDER BY vi.id
            """
            self.cursor.execute(itens_query, (venda_id,))
            itens = self.cursor.fetchall()
            
            # Adicionar itens à venda
            venda['itens'] = itens
            return venda
            
        except Error as e:
            return {"erro": f"Erro ao buscar venda: {str(e)}"}
