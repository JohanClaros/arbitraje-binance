import requests
import json

filename = "binance/busd.json"
url = "https://api.binance.com/api/v3/ticker/bookTicker"


def dictionary_busd():
    response = requests.get(url)
    data = response.json()
    result = []
    for item in data:
        if 'BUSD"' in item["symbol"] or '"BUSD' in item["symbol"]:
            result.append({
                "symbol": item["symbol"],
                "bidPrice": item["bidPrice"],
                "bidQty": item["bidQty"],
                "askPrice": item["askPrice"],
                "askQty": item["askQty"],
            })
        # Guarda los datos de precios en el archivo JSON
    with open(filename, "w") as file:
        json.dump(result, file)

