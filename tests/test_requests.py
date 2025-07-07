import requests

# IDs reais que já estão no banco de dados
# payload = {
#     'father_id':"046b2a9d-23a1-4a2a-9763-4b22acfd12ad",
#     'mother_id':"60ca0f2b-8b90-4a31-a718-f9a74abffee7"
# }
payload = {
    ''
}

response = requests.post('http://127.0.0.1:5000/cross', json=payload)

print("Status:", response.status_code)
print("Resposta:", response.text)
print(payload)