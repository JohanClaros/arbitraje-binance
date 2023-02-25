import requests
import json

# Define la dirección URL de la API de Binance
url = "https://api.binance.com/api/v3/ticker/bookTicker"

# Realiza una solicitud GET a la API de Binance
response = requests.get(url)

# Verifica si la solicitud fue exitosa
if response.status_code == 200:
    # Obtiene los datos de precios en formato JSON
    prices = response.json()

all_prices = [price for price in prices]
bol_prices = [price for price in prices if price["symbol"].endswith("BUSD") or price["symbol"].startswith("BUSD") ]



# Analiza cada combinación de tres criptomonedas para determinar si existe una oportunidad de arbitraje
for i in range(len(bol_prices)):
    for j in range(i + 1, len(all_prices)):
        for k in range(j + 1, len(bol_prices)):
            # Obtiene los precios de compra y venta de la primera criptomoneda
            symbol1 = bol_prices[i]["symbol"]
            bid_price1 = float(bol_prices[i]["bidPrice"])
            ask_price1 = float(bol_prices[i]["askPrice"])

            # Obtiene los precios de compra y venta de la segunda criptomoneda
            symbol2 = all_prices[j]["symbol"]
            bid_price2 = float(all_prices[j]["bidPrice"])
            ask_price2 = float(all_prices[j]["askPrice"])

            # Obtiene los precios de compra y venta de la tercera criptomoneda
            symbol3 = bol_prices[k]["symbol"]
            bid_price3 = float(bol_prices[k]["bidPrice"])
            ask_price3 = float(bol_prices[k]["askPrice"])
            
            #print( symbol1," ", symbol2," ",symbol3)

            # Verifica si el primer símbolo comienza con "USDT" y el tercer símbolo termina con "BTC"
            if symbol1.endswith("BUSD") and symbol3.endswith("BUSD") and ask_price2!=0 and ask_price3!=0:

                
                # Calcula el margen de ganancia entre las tres criptomonedas
                profit = (bid_price1 / ask_price2) * (bid_price2 / ask_price3) - 1

                # Imprime un mensaje si existe una oportunidad de arbitraje
                if profit > 0:
                    print("Existe una oportunidad de arbitraje entre", symbol1, symbol2, symbol3)
                    print("Comprar", symbol1, "a", ask_price1)
                    print("Vender", symbol2, "a", bid_price2)
                    print("Vender", symbol3, "a", bid_price3)
                    print("Margen de ganancia:", profit, "\n")
