from database import Database

db = Database()

# Verificar antes
print("=== ANTES DA ATUALIZAÇÃO ===")
query = """
    SELECT p.id, p.nome, p.preco, p.custo_materiais, p.custo_etapas,
           pm.material_id, pm.custo_unitario, pm.subtotal, pm.quantidade_necessaria,
           ie.nome as material_nome, ie.custo_atual
    FROM produtos p
    LEFT JOIN produtos_materiais pm ON p.id = pm.produto_id
    LEFT JOIN itens_estoque ie ON pm.material_id = ie.id
    WHERE p.id = 32
"""

db.cursor.execute(query)
resultado = db.cursor.fetchall()

for row in resultado:
    print(f"Produto: {row['nome']}")
    print(f"  Preço: R$ {row['preco']:.2f}")
    print(f"  Custo materiais: R$ {row['custo_materiais'] or 0:.2f}")
    print(f"  Material: {row['material_nome']}")
    print(f"  Custo unitário produtos_materiais: R$ {row['custo_unitario'] or 0:.2f}")
    print(f"  Subtotal produtos_materiais: R$ {row['subtotal'] or 0:.2f}")
    print(f"  Custo atual no estoque: R$ {row['custo_atual'] or 0:.2f}")

# Executar atualização
print("\n=== EXECUTANDO ATUALIZAÇÃO ===")
db._atualizar_custos_detalhados_produto(32)

# Verificar depois
print("\n=== DEPOIS DA ATUALIZAÇÃO ===")
db.cursor.execute(query)
resultado = db.cursor.fetchall()

for row in resultado:
    print(f"Produto: {row['nome']}")
    print(f"  Preço: R$ {row['preco']:.2f}")
    print(f"  Custo materiais: R$ {row['custo_materiais'] or 0:.2f}")
    print(f"  Material: {row['material_nome']}")
    print(f"  Custo unitário produtos_materiais: R$ {row['custo_unitario'] or 0:.2f}")
    print(f"  Subtotal produtos_materiais: R$ {row['subtotal'] or 0:.2f}")
    print(f"  Custo atual no estoque: R$ {row['custo_atual'] or 0:.2f}")

db.connection.commit()
db.close()
