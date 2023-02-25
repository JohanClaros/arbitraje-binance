import requests
import time
import json

# Define la dirección URL de la API de Binance
url = "https://api.binance.com/api/v3/ticker/price"

# Define el nombre del archivo JSON donde se guardarán los datos
filename = "binance/prices.json"

while True:
    # Realiza una solicitud GET a la API de Binance
    response = requests.get(url)

    # Verifica si la solicitud fue exitosa
    if response.status_code == 200:
        # Obtiene los datos de precios en formato JSON
        prices = response.json()

        # Guarda los datos de precios en el archivo JSON
        with open(filename, "w") as file:
            json.dump(prices, file)

        # Imprime un mensaje para indicar que los datos se han actualizado
        print("Datos actualizados a las", time.ctime())
    else:
        # Imprime un mensaje de error si la solicitud falla
        print("Error al obtener datos de precios:", response.status_code)

    # Espera 60 segundos antes de hacer una nueva solicitud
    time.sleep(60)