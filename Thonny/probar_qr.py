import requests

# URL de tu backend FastAPI
API_URL = "http://localhost:8000/api/asistencias/qr"

# Pide el texto base64 por consola
base64_str = input("Pega el texto base64 del QR: ")

# Envía el texto al backend
res = requests.post(API_URL, json={"qr_texto": base64_str})

# Muestra la respuesta
print("Respuesta del backend:")
print("Código de estado:", res.status_code)
print("Texto de respuesta:", res.text)
print(res.json())  # Solo si el código es 200 y el texto es JSON