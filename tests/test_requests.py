import requests

# IDs reais que já estão no banco de dados
payload = {
    'father_id':"046b2a9d-23a1-4a2a-9763-4b22acfd12ad",
    'mother_id':"0d02c699-3c8c-4b42-b651-6ee74e7dcf22"
}

response = requests.post('http://127.0.0.1:5000/cross', json=payload)

print("Status:", response.status_code)
print("Resposta:", response.text)