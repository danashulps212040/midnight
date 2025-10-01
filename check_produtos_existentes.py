from database import Database

db = Database()
db.cursor.execute('SELECT id, nome, codigo FROM produtos')
produtos = db.cursor.fetchall()
print('Produtos disponíveis:')
for p in produtos:
    print(f'ID: {p["id"]}, Nome: {p["nome"]}, Código: {p["codigo"]}')
db.close()
