import requests
import sqlite3
from datetime import datetime, timedelta

# Configuración de la conexión a la base de datos SQLite
conn = sqlite3.connect('tokens.db')
c = conn.cursor()

# Método para obtener el access_token y refresh_token de la base de datos
def get_tokens():
    c.execute("SELECT * FROM tokens")
    tokens = c.fetchone()
    if tokens is None:
        return None
    access_token, refresh_token, expiration_date = tokens
    expiration_date = datetime.strptime(expiration_date, '%Y-%m-%d %H:%M:%S')
    return access_token, refresh_token, expiration_date

# Método para guardar el access_token y refresh_token en la base de datos
def save_tokens(access_token, refresh_token, expiration_date):
    c.execute("DELETE FROM tokens")
    c.execute("INSERT INTO tokens VALUES (?, ?, ?)",
            (access_token, refresh_token, expiration_date))
    conn.commit()

# Método para obtener un nuevo access_token y refresh_token
def get_new_tokens(refresh_token):
    url = "https://api.mercadolibre.com/oauth/token"
    payload = {
        "grant_type": "refresh_token",
        "client_id": "5030313997317379",
        "client_secret": "zTJax3dLAiog35gQdaOVEhTSwxXxbTTY",
        "refresh_token": refresh_token
    }
    response = requests.post(url, data=payload)
    response.raise_for_status()
    data = response.json()
    access_token = data['access_token']
    refresh_token = data['refresh_token']
    expires_in = data['expires_in']
    expiration_date = datetime.now() + timedelta(seconds=expires_in)
    expiration_date_str = expiration_date.strftime('%Y-%m-%d %H:%M:%S')
    save_tokens(access_token, refresh_token, expiration_date_str)
    return access_token, refresh_token, expiration_date_str

# Método para hacer la petición con el access_token
def make_request(access_token, url):
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()
    return data

# Método para hacer una petición a la main
def do_request(url):
    tokens = get_tokens()
    if tokens is None or tokens[2] < datetime.now():
        refresh_token = tokens[1] if tokens is not None else input("Ingrese refresh_token: ")
        access_token, refresh_token, expiration_date = get_new_tokens(refresh_token)
    else:
        access_token, refresh_token, expiration_date = tokens
    data = make_request(access_token, url)
    return data

url = "https://api.mercadolibre.com/trends/MLC"
url2 = "https://api.mercadolibre.com/sites/MLC/search?category=MLC82067"
url3 = "https://api.mercadolibre.com/sites/MLC/search?category=MLC1648&offset=50"
url4 = "https://api.mercadolibre.com/sites/MLC/search?category=MLC1648&offset=100"
url5 = "https://api.mercadolibre.com/highlights/$SITE_ID/category/$CATEGORY_ID"

datos_json = do_request(url2)['results']
for producto in datos_json:
    print("Nombre del producto:", producto["title"])
    print("Precio del producto:", producto["price"])
    print("Precio Original del Producto:", producto["original_price"])
    
# Cerrar la conexión a la base de datos al terminar
conn.close()