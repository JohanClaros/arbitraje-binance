import json
import datos_json
import time


coin_prince_url="https://api.binance.com/api/v3/ticker/bookTicker"

def step_2():


    datos_json.actual()

    #obtener la actualizacion del precio
    with open("binance/sacar_0.json") as json_file:
        prices_json = json.load(json_file)


    #cargar el json creado para cargar los pares y combinaciones
    with open("binance/structura_binance.json") as json_file:
        structured_pairs = json.load(json_file)



    #iterar la estructura para encontrar precio del par
    for t_pair in structured_pairs:
        prices_dict = datos_json.get_price_for_t_pair(t_pair, prices_json)
        surface_arb = datos_json.calc_triangular_arb_surface_rate(t_pair, prices_dict)
        if len(surface_arb) > 0:
            print("surfear mercado",surface_arb)
            real_rate_arb = datos_json.get_depth_from_orderbook(surface_arb)
            print(real_rate_arb)



step_2()