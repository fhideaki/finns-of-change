import requests

# IDs reais que já estão no banco de dados
payload = {
    'father_id':'5569b031-18ff-4405-8036-5ef218b9fd65',
    'mother_id':'5569b031-18ff-4405-8036-5ef218b9fd65'
}

response = requests.post('http://127.0.0.1:5000/cross', json=payload)

print("Status:", response.status_code)
print("Resposta:", response.text)