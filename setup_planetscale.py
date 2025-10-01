#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de configuração e migração do banco de dados para PlanetScale
Este script deve ser executado após configurar as variáveis de ambiente
"""

import os
import sys
from pathlib import Path

# Adicionar o diretório atual ao path para imports
sys.path.append(str(Path(__file__).parent))

def configurar_ambiente():
    """Configura as variáveis de ambiente necessárias"""
    print("🔧 Configurando ambiente...")
    
    # Verificar se arquivo .env existe
    env_file = Path('.env')
    if not env_file.exists():
        print("⚠️  Arquivo .env não encontrado. Usando variáveis de ambiente do sistema.")
    else:
        # Carregar variáveis do arquivo .env se existir
        try:
            from dotenv import load_dotenv
            load_dotenv()
            print("✅ Arquivo .env carregado com sucesso")
        except ImportError:
            print("⚠️  python-dotenv não instalado. Usando apenas variáveis do sistema.")
    
    # Verificar variáveis necessárias
    required_vars = [
        'PLANETSCALE_HOST',
        'PLANETSCALE_USERNAME', 
        'PLANETSCALE_PASSWORD',
        'PLANETSCALE_DATABASE'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ ERRO: Variáveis de ambiente não configuradas: {', '.join(missing_vars)}")
        print("\n📋 Configure as seguintes variáveis:")
        for var in missing_vars:
            print(f"   export {var}=valor_aqui")
        return False
    
    print("✅ Todas as variáveis de ambiente estão configuradas")
    return True

def testar_conexao():
    """Testa a conexão com o banco de dados"""
    print("\n🔌 Testando conexão com PlanetScale...")
    
    try:
        # Importar usando o database.py modificado
        from database_cloud import Database
        
        # Tentar conectar
        db = Database()
        
        # Testar conexão
        resultado = db.testar_conexao()
        
        if 'erro' in resultado:
            print(f"❌ Erro na conexão: {resultado['erro']}")
            return False
        
        print("✅ Conexão com PlanetScale estabelecida com sucesso!")
        
        # Listar tabelas para verificar
        tabelas_result = db.verificar_tabelas()
        if 'tabelas' in tabelas_result:
            print(f"📊 Tabelas encontradas: {len(tabelas_result['tabelas'])}")
            for tabela in tabelas_result['tabelas']:
                print(f"   - {tabela}")
        
        db.close()
        return True
        
    except ImportError as e:
        print(f"❌ Erro ao importar módulos: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def executar_migracao():
    """Executa a migração do banco de dados"""
    print("\n📦 Executando migração do banco de dados...")
    
    try:
        import mysql.connector
        from mysql.connector import Error
        
        # Configuração de conexão
        config = {
            'host': os.getenv('PLANETSCALE_HOST'),
            'user': os.getenv('PLANETSCALE_USERNAME'),
            'password': os.getenv('PLANETSCALE_PASSWORD'),
            'database': os.getenv('PLANETSCALE_DATABASE'),
            'port': int(os.getenv('PLANETSCALE_PORT', 3306)),
            'ssl_disabled': False,
            'autocommit': True
        }
        
        # Conectar e executar migração
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        
        # Ler arquivo de migração
        migration_file = Path('planetscale_migration.sql')
        if not migration_file.exists():
            print("❌ Arquivo planetscale_migration.sql não encontrado")
            return False
        
        # Executar migração
        with open(migration_file, 'r', encoding='utf-8') as f:
            migration_sql = f.read()
        
        # Dividir em comandos individuais (removendo comentários)
        commands = []
        for line in migration_sql.split('\n'):
            line = line.strip()
            if line and not line.startswith('--'):
                commands.append(line)
        
        sql_script = ' '.join(commands)
        
        # Executar comandos SQL
        for statement in sql_script.split(';'):
            statement = statement.strip()
            if statement:
                try:
                    cursor.execute(statement)
                    print(f"✅ Executado: {statement[:50]}...")
                except Error as e:
                    # Ignorar erros de "table already exists"
                    if "already exists" in str(e).lower():
                        print(f"⚠️  Tabela já existe: {statement[:50]}...")
                    else:
                        print(f"❌ Erro SQL: {e}")
                        print(f"   Statement: {statement}")
        
        cursor.close()
        connection.close()
        
        print("✅ Migração executada com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro durante migração: {e}")
        return False

def main():
    """Função principal"""
    print("🚀 CONFIGURAÇÃO PLANETSCALE + RENDER")
    print("=" * 50)
    
    # Etapa 1: Configurar ambiente
    if not configurar_ambiente():
        sys.exit(1)
    
    # Etapa 2: Testar conexão
    if not testar_conexao():
        print("\n💡 DICA: Verifique suas credenciais do PlanetScale")
        sys.exit(1)
    
    # Etapa 3: Executar migração
    response = input("\n❓ Deseja executar a migração do banco? (s/N): ")
    if response.lower() in ['s', 'sim', 'y', 'yes']:
        if not executar_migracao():
            sys.exit(1)
    
    print("\n🎉 CONFIGURAÇÃO CONCLUÍDA!")
    print("=" * 50)
    print("✅ Banco de dados configurado e pronto para uso")
    print("✅ Aplicação pronta para deploy no Render")
    print("\n📋 PRÓXIMOS PASSOS:")
    print("1. Fazer upload do código para GitHub usando o uploader")
    print("2. Criar serviço no Render conectado ao repositório")
    print("3. Configurar as variáveis de ambiente no Render")
    print("4. Fazer o deploy!")

if __name__ == "__main__":
    main()