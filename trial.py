import trial_funtion
import json
import time

coin_prince_url = "https://poloniex.com/public?command=returnTicker"

def step_0():
    #Extrae la lista de pares y precios del exchange
    coin_json = trial_funtion.get_coin_tickers(coin_prince_url) 
    coin_list = trial_funtion.collect_tradeables(coin_json)
    return(coin_list)


def step_1(coin_list):

    #estructura de lista de pares para triangular arbitraje     
    structured_list = trial_funtion.structure_triangular_pair(coin_list)
    
    #guardar el json para luego utilizarlo
    with open("structured_triangular_pairs.json", "w") as fp:
        json.dump(structured_list, fp)
   


def step_2():

    #cargar el json creado para cargar los pares y combinaciones
    with open("structured_triangular_pairs.json") as json_file:
        structured_pairs = json.load(json_file)

    #obtener la actualizacion del precio
    prices_json = trial_funtion.get_coin_tickers(coin_prince_url)

    #iterar la estructura para encontrar precio del par
    for t_pair in structured_pairs:
        time.sleep(0.3)
        prices_dict = trial_funtion.get_price_for_t_pair(t_pair, prices_json)
        surface_arb = trial_funtion.calc_triangular_arb_surface_rate(t_pair, prices_dict)
        if len(surface_arb) > 0:
            real_rate_arb = trial_funtion.get_depth_from_orderbook(surface_arb)
            print(real_rate_arb)
            time.sleep(20)


        






if __name__ == "__main__":
    # coin_list = step_0()
    # structure = step_1(coin_list)
    while True:
        step_2()

