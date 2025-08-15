import requests

# IDs reais que já estão no banco de dados
payload = {
    'father_id':"bb8651f5-e3ae-404e-a936-d914e1e77e42",
    'mother_id':"d53be77c-fbc9-4ff5-b59a-7b2f1197175b"
}


response = requests.post('http://127.0.0.1:5000/cross', json=payload)

print("Status:", response.status_code)
print("Resposta:", response.text)
print(payload)