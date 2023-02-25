import itertools
import json
import requests

url = "https://api.binance.com/api/v3/ticker/bookTicker"


# Realiza una solicitud GET a la API de Binance
response = requests.get(url)

# Verifica si la solicitud fue exitosa
if response.status_code == 200:
    # Obtiene los datos de precios en formato JSON
    prices = response.json()
 
# Carga el primer archivo JSON en un diccionario
with open("binance/jsonbusd_.json") as f:
    pares = json.load(f)


filename = "binance/sacar_0_.json"

new_list = []
for item in pares:
    
    symbol = (item['symbol']).replace("_","")
    for red in prices:
        if symbol == red['symbol']:
            if red['bidPrice'] != "0.00000000" and red['askPrice']!= "0.00000000":
                pa = item['symbol']
                n = {
                    'symbol': pa,
                    'bidPrice':red['bidPrice'],
                    'askPrice':red['askPrice']
                }
                

                new_list.append(n)


# Guarda los cambios en un archivo JSON
with open(filename, "w") as file:
    json.dump(new_list, file)


