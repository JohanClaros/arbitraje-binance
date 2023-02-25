import requests
import json

filename = "binance/sinbusd.json"
url = "https://api.binance.com/api/v3/ticker/bookTicker"


def dictionary_busd():
    response = requests.get(url)
    data = response.json()
    result = []
    for item in data:
        if "BUSD" in item["symbol"]:
            symbol_value = item["symbol"]
            symbol_value = symbol_value.replace(
                "BUSD", "").replace("_","")
            if symbol_value.endswith("_"):
                symbol_value = symbol_value[:-1]
            if symbol_value.startswith("_"):
                symbol_value = symbol_value[1:]
            result.append({
                "symbol": symbol_value,
            })
        # Guarda los datos de precios en el archivo JSON
    with open(filename, "w") as file:
        json.dump(result, file)


dictionary_busd()
