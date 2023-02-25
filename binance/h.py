import requests
import json
import time

# Define la dirección URL de la API de Binance
url = "https://api.binance.com/api/v3/ticker/bookTicker"


# Define el nombre del archivo JSON donde se guardarán los datos
filename = "binance/pares.json"
pares = []
# Realiza una solicitud HTTP a la API de Binance
response = requests.get(url)


# Carga el primer archivo JSON en un diccionario
with open("binance/pares.json") as f:
    file1 = json.load(f)

# Carga el segundo archivo JSON en un diccionario
with open("binance/monedas.json") as f:
    file2 = json.load(f)

data = []


for item in file1:
    for word in file2:
        monedas = word["moneda"]
        if monedas in item["symbol"]:
            symbol_value = item["symbol"]
            symbol_value = symbol_value.replace(
                word["moneda"], word["moneda"]+"_")
            if symbol_value.endswith("_"):
                symbol_value = symbol_value[:-1]
        sep = {
            "symbol": symbol_value
        }
        data.append(sep)


# Guarda los cambios en un archivo JSON
with open("binance/separados.json", "w") as file:
    json.dump(data, file)
