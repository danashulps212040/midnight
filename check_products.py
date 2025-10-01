from database import Database

db = Database()
produtos = db.listar_produtos()
print(f'Produtos encontrados: {len(produtos)}')
for i, p in enumerate(produtos[:5]):
    print(f'ID: {p["id"]}, Nome: {p["nome"]}, Preço: {p["preco"]}')
db.close()
