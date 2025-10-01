#!/usr/bin/env python3
"""
Teste para verificar exatamente o que está acontecendo com o cálculo e formatação
"""

import requests
import json
from database import Database

# Configuração do servidor Flask
BASE_URL = "http://localhost:8000"

def debug_calculo_detalhado():
    print("=== DEBUG DETALHADO DO CÁLCULO ===\n")
    
    try:
        db = Database()
        
        # 1. Verificar dados atuais no banco
        produto_id = 61
        
        query = """
            SELECT p.*, pe.tempo_estimado, pe.custo_estimado, m.hora_maquina, m.nome as maquina_nome
            FROM produtos p
            LEFT JOIN produtos_etapas pe ON p.id = pe.produto_id AND pe.equipamento_tipo = 'maquina'
            LEFT JOIN maquinas m ON pe.equipamento_id = m.id
            WHERE p.id = %s
        """
        
        db.cursor.execute(query, (produto_id,))
        produto = db.cursor.fetchone()
        
        print("📊 DADOS DO BANCO:")
        print(f"  Preço atual registrado: R$ {produto['preco']:.2f}")
        print(f"  Custo materiais: R$ {produto['custo_materiais'] or 0:.2f}")
        print(f"  Custo etapas: R$ {produto['custo_etapas'] or 0:.2f}")
        print(f"  Margem: {produto['margem_lucro'] or 0:.1f}%")
        print(f"  Máquina: {produto['maquina_nome']}")
        print(f"  Hora/máquina: R$ {produto['hora_maquina']:.2f}")
        print(f"  Tempo estimado: {produto['tempo_estimado']}")
        print(f"  Custo estimado da etapa: R$ {produto['custo_estimado'] or 0:.2f}")
        
        # 2. Calcular manualmente
        if produto['tempo_estimado']:
            tempo_horas = produto['tempo_estimado'].total_seconds() / 3600
            custo_etapa_atual = float(produto['hora_maquina']) * tempo_horas
            custo_materiais = float(produto['custo_materiais'] or 0)
            custo_total = custo_materiais + custo_etapa_atual
            margem = float(produto['margem_lucro'] or 0)
            preco_calculado = custo_total * (1 + margem / 100)
            
            print(f"\n🧮 CÁLCULO MANUAL:")
            print(f"  Tempo em horas: {tempo_horas:.6f}")
            print(f"  Custo etapa: R$ {produto['hora_maquina']:.2f} × {tempo_horas:.6f} = R$ {custo_etapa_atual:.6f}")
            print(f"  Custo materiais: R$ {custo_materiais:.6f}")
            print(f"  Custo total: R$ {custo_total:.6f}")
            print(f"  Margem: {margem:.1f}%")
            print(f"  Preço final: R$ {preco_calculado:.6f}")
            print(f"  Preço final formatado: R$ {preco_calculado:.2f}")
        
        # 3. Testar API do sistema
        print(f"\n🌐 TESTE VIA API:")
        response = requests.get(f'{BASE_URL}/api/produtos/{produto_id}/detalhes-calculo')
        
        if response.status_code == 200:
            data = response.json()
            produto_api = data.get('produto', {})
            
            print(f"  Preço API: R$ {produto_api.get('preco', 0):.6f}")
            print(f"  Custo materiais API: R$ {produto_api.get('custo_materiais', 0):.6f}")
            print(f"  Custo etapas API: R$ {produto_api.get('custo_etapas', 0):.6f}")
            print(f"  Custo total API: R$ {produto_api.get('custo_total', 0):.6f}")
            
            # Formatação como seria no frontend
            preco_formatado = f"{produto_api.get('preco', 0):.2f}".replace('.', ',')
            print(f"  Preço formatado (BR): R$ {preco_formatado}")
        else:
            print(f"  ❌ Erro API: {response.status_code}")
        
        # 4. Testar verificação de alterações
        print(f"\n🔍 TESTE VERIFICAÇÃO DE ALTERAÇÕES:")
        response = requests.post(
            f'{BASE_URL}/api/produtos/verificar-alteracoes-precos',
            json={'dias': 7}
        )
        
        if response.status_code == 200:
            data = response.json()
            produtos_afetados = data.get('produtos_afetados', [])
            
            if produtos_afetados:
                produto_afetado = produtos_afetados[0]
                print(f"  Produto: {produto_afetado['nome']}")
                print(f"  Preço atual: R$ {produto_afetado['preco_atual']:.6f}")
                print(f"  Novo preço: R$ {produto_afetado['novo_preco']:.6f}")
                print(f"  Variação: {produto_afetado['variacao_percentual']:.6f}%")
                
                # Formatação como seria exibida
                preco_exibido = f"{produto_afetado['novo_preco']:.2f}".replace('.', ',')
                print(f"  Preço que deveria aparecer: R$ {preco_exibido}")
            else:
                print("  ❌ Nenhum produto detectado nas alterações")
        else:
            print(f"  ❌ Erro API: {response.status_code}")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        import traceback
        traceback.print_exc()

def testar_edicao_produto():
    """Testa a edição de um produto específico"""
    
    # Primeiro, vamos listar os produtos existentes para escolher um
    print("=== Listando produtos existentes ===")
    response = requests.get(f"{BASE_URL}/api/produtos")
    if response.status_code == 200:
        produtos = response.json()
        if produtos.get('produtos'):
            print(f"Encontrados {len(produtos['produtos'])} produtos")
            for produto in produtos['produtos'][:5]:  # Mostrar apenas os primeiros 5
                print(f"- ID: {produto['id']}, Nome: {produto['nome']}, Código: {produto['codigo']}")
        else:
            print("Nenhum produto encontrado")
            return
    else:
        print(f"Erro ao buscar produtos: {response.status_code}")
        return
    
    # Escolher o primeiro produto para teste
    produto_id = produtos['produtos'][0]['id']
    print(f"\n=== Testando edição do produto ID: {produto_id} ===")
    
    # Buscar dados completos do produto
    response = requests.get(f"{BASE_URL}/api/produtos/{produto_id}")
    if response.status_code != 200:
        print(f"Erro ao buscar produto {produto_id}: {response.status_code}")
        return
    
    produto_original = response.json()
    if produto_original.get('status') != 'success':
        print(f"Erro no retorno do produto: {produto_original}")
        return
    
    produto = produto_original['produto']
    print(f"Produto original: {produto['nome']}")
    
    # Criar dados para edição (alterando apenas o nome)
    dados_edicao = {
        'nome': produto['nome'] + ' (EDITADO)',
        'codigo': produto['codigo'],
        'categoria': produto['categoria'],
        'preco': produto['preco'],
        'margem': produto.get('margem', 0),
        'descricao': produto.get('descricao', ''),
        'especificacoes': produto.get('especificacoes', ''),
        'materiais': produto.get('materiais', []),
        'etapas': produto.get('etapas', []),
        'custoMateriais': produto.get('custoMateriais', 0),
        'custoEtapas': produto.get('custoEtapas', 0)
    }
    
    print(f"\nDados a serem enviados:")
    print(json.dumps(dados_edicao, indent=2, ensure_ascii=False))
    
    # Enviar edição
    response = requests.put(
        f"{BASE_URL}/api/produtos/{produto_id}",
        json=dados_edicao,
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"\nResposta do servidor:")
    print(f"Status: {response.status_code}")
    print(f"Conteúdo: {response.text}")
    
    # Verificar se a edição foi bem-sucedida
    if response.status_code == 200:
        print("\n✅ Edição realizada com sucesso!")
        
        # Verificar se o produto foi realmente atualizado
        response_check = requests.get(f"{BASE_URL}/api/produtos/{produto_id}")
        if response_check.status_code == 200:
            produto_atualizado = response_check.json()
            if produto_atualizado.get('status') == 'success':
                produto_novo = produto_atualizado['produto']
                print(f"Nome antes: {produto['nome']}")
                print(f"Nome depois: {produto_novo['nome']}")
                
                if produto_novo['nome'] != produto['nome']:
                    print("✅ Produto foi realmente atualizado no banco!")
                else:
                    print("❌ Produto não foi atualizado no banco de dados")
            else:
                print(f"Erro ao verificar produto atualizado: {produto_atualizado}")
        else:
            print(f"Erro ao verificar produto atualizado: {response_check.status_code}")
    else:
        print(f"❌ Erro na edição: {response.status_code}")

if __name__ == "__main__":
    debug_calculo_detalhado()
