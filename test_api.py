import requests
import json

# Teste da API de listagem de itens
print("Testando API de listagem de itens...")
response = requests.get('http://127.0.0.1:5000/api/itens_estoque/lista')
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")

# Teste criando um item se a lista estiver vazia
if response.status_code == 200:
    data = response.json()
    if data.get('status') == 'success' and len(data.get('items', [])) == 0:
        print("\nNenhum item encontrado. Criando item de teste...")
        
        # Criar item de teste
        item_data = {
            'itemName': 'Material Teste',
            'itemCode': 'MT001',
            'itemCategory': 'Categoria Teste',
            'itemColor': 'Azul',
            'itemInitialQuantity': '10',
            'itemMinStock': '5',
            'itemUnit': 'UN',
            'itemSupplier': 'Fornecedor Teste',
            'itemLocation': 'Estoque A'
        }
        
        create_response = requests.post('http://127.0.0.1:5000/api/itens_estoque', data=item_data)
        print(f"Criação - Status: {create_response.status_code}")
        print(f"Criação - Response: {create_response.text}")
        
        # Testar novamente a listagem
        print("\nTestando listagem novamente...")
        response2 = requests.get('http://127.0.0.1:5000/api/itens_estoque/lista')
        print(f"Status: {response2.status_code}")
        print(f"Response: {response2.text}")