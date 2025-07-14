import requests

# IDs reais que já estão no banco de dados
payload = {
    'father_id':"18ffc125-a67e-439f-94d3-6ac981f33f14",
    'mother_id':"c6a2f63a-ba86-4ec9-9c7d-8c57a20e08bc"
}


response = requests.post('http://127.0.0.1:5000/cross', json=payload)

print("Status:", response.status_code)
print("Resposta:", response.text)
print(payload)