import requests
import json

# Test the price update API with correct product ID
url = 'http://localhost:5000/api/precos/atualizar'
test_data = {
    'produtos': [
        {
            'id': 29,
            'nome': 'Caixa Milk',
            'preco_atual': 28.99,
            'novo_preco': 30.00
        }
    ]
}

try:
    response = requests.post(url, json=test_data, headers={'Content-Type': 'application/json'})
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    # Verify the response format matches frontend expectations
    data = response.json()
    if 'status' in data:
        print(f"✅ Response has 'status' field: {data['status']}")
        if data['status'] == 'success':
            print("✅ Status is 'success' - frontend should work!")
        else:
            print(f"❌ Status is '{data['status']}' - not 'success'")
    else:
        print("❌ Response missing 'status' field")
        
except Exception as e:
    print(f"Error: {e}")
