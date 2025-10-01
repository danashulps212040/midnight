#!/usr/bin/env python3
"""
Script para debugar problemas de login
"""

from database import Database
from werkzeug.security import check_password_hash

def verificar_usuarios():
    db = Database()
    try:
        # Listar todos os usuários
        db.cursor.execute("SELECT id, nome, email, cargo, senha FROM usuarios")
        usuarios = db.cursor.fetchall()
        
        print(f"Total de usuários no banco: {len(usuarios)}")
        
        for usuario in usuarios:
            print(f"\nUsuário ID: {usuario['id']}")
            print(f"Nome: {usuario['nome']}")
            print(f"Email: {usuario['email']}")
            print(f"Cargo: {usuario['cargo']}")
            print(f"Hash da senha: {usuario['senha'][:50]}...")
            
            # Testar se o hash é válido
            teste_senha = "123456"  # Senha comum para teste
            if check_password_hash(usuario['senha'], teste_senha):
                print(f"✅ Senha '123456' funciona para este usuário")
            else:
                print(f"❌ Senha '123456' NÃO funciona para este usuário")
                
    except Exception as e:
        print(f"Erro: {e}")
    finally:
        db.close()

def testar_autenticacao(email, senha):
    db = Database()
    try:
        print(f"\n🔍 Testando autenticação para: {email}")
        resultado = db.autenticar_usuario(email, senha)
        print(f"Resultado: {resultado}")
        
        # Testar busca manual
        db.cursor.execute("SELECT id, nome, email, senha FROM usuarios WHERE email = %s", (email,))
        usuario = db.cursor.fetchone()
        
        if usuario:
            print(f"✅ Usuário encontrado no banco: {usuario['nome']}")
            print(f"Email no banco: {usuario['email']}")
            print(f"Hash da senha: {usuario['senha'][:50]}...")
            
            # Testar verificação de senha
            if check_password_hash(usuario['senha'], senha):
                print("✅ Verificação de senha: SUCESSO")
            else:
                print("❌ Verificação de senha: FALHOU")
        else:
            print("❌ Usuário NÃO encontrado no banco")
            
    except Exception as e:
        print(f"❌ Erro na autenticação: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("=== DEBUG DO SISTEMA DE LOGIN ===")
    
    # Verificar todos os usuários
    verificar_usuarios()
    
    # Solicitar dados para teste
    print("\n" + "="*50)
    email = input("Digite o email para testar: ")
    senha = input("Digite a senha para testar: ")
    
    testar_autenticacao(email, senha)