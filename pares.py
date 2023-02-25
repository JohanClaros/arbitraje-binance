import ccxt

# Crear una instancia de la clase poloniex
exchange = ccxt.poloniex({
    'rateLimit': 1500,
    'enableRateLimit': True,
})

# Cargar los mercados disponibles
markets = exchange.load_markets()

# Imprimir todos los pares de trading disponibles
for market in markets:
    print(market)
