#!/usr/bin/env python3
from database import Database

db = Database()

print("=== HISTÓRICO DE CUSTOS ===")
db.cursor.execute("SELECT * FROM historico_custos_maquinas ORDER BY data_alteracao DESC LIMIT 5")
historico = db.cursor.fetchall()
for h in historico:
    print(f"  Data: {h['data_alteracao']}, Máquina: {h['maquina_id']}, Valor anterior: R${h['hora_maquina_anterior']}, Valor novo: R${h['hora_maquina_nova']}")
    
print("\n=== MÁQUINAS ATUAIS ===")
db.cursor.execute("SELECT id, nome, hora_maquina FROM maquinas WHERE nome LIKE '%Router%'")
maquinas = db.cursor.fetchall()
for m in maquinas:
    print(f"  ID: {m['id']}, Nome: {m['nome']}, Hora atual: R${m['hora_maquina']}")

db.close()
