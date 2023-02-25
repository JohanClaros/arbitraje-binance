import requests
import json
import time

# Hace la peticion al servidor y lista las monedas del exchange con toda la inf
def get_coin_tickers(url):
    req = requests.get(url)
    json_resp = json.loads(req.text)
    return json_resp


#retorna solamente las monedas disponibles
def collect_tradeables(json_obj):
    coin_list = []
    for coin in json_obj:
        is_frozen = json_obj[coin]["isFrozen"]
        is_post_only = json_obj[coin]["postOnly"]
        if is_frozen == '0' and is_post_only == '0':
            coin_list.append(coin)
    return coin_list


#hace los pares y las combinaciones trial para las monedas
def structure_triangular_pair(coin_list):

    triangular_pairs_list = []
    remove_duplicates_list = []
    pairs_list = coin_list[0:]

    # Obtener par A
    for pair_a in pairs_list:
        pair_a_split = pair_a.split("_")
        a_base = pair_a_split[0]
        a_quote = pair_a_split[1]

        # Asignar a la caja
        a_pair_box = [a_base, a_quote]

        # Obtener par B
        for pair_b in pairs_list:
            pair_b_split = pair_b.split("_")
            b_base = pair_b_split[0]
            b_quote = pair_b_split[1]

            # Corroborar par B
            if pair_b != pair_a:
                if b_base in a_pair_box or b_quote in a_pair_box:

                    # Obtener par A
                    for pair_c in pairs_list:
                        pair_c_split = pair_c.split("_")
                        c_base = pair_c_split[0]
                        c_quote = pair_c_split[1]

                        # contar el numero de item que estan en C
                        if pair_c != pair_a and pair_c != pair_b:
                            combine_all = [pair_a, pair_b, pair_c]
                            pair_box = [a_base, a_quote, b_base, b_quote, c_base, c_quote]

                            counts_c_base = 0
                            for i in pair_box:
                                if i == c_base:
                                    counts_c_base += 1

                            counts_c_quote = 0
                            for i in pair_box:
                                if i == c_quote:
                                    counts_c_quote += 1

                            # Determinar el triangulo de pares
                            if counts_c_base == 2 and counts_c_quote == 2 and c_base != c_quote:
                                combined = pair_a + "," + pair_b + "," + pair_c
                                unique_item = ''.join(sorted(combine_all))

                                if unique_item not in remove_duplicates_list:
                                    match_dict = {
                                        "a_base": a_base,
                                        "b_base": b_base,
                                        "c_base": c_base,
                                        "a_quote": a_quote,
                                        "b_quote": b_quote,
                                        "c_quote": c_quote,
                                        "pair_a": pair_a,
                                        "pair_b": pair_b,
                                        "pair_c": pair_c,
                                        "combined": combined
                                    }
                                    triangular_pairs_list.append(match_dict)
                                    remove_duplicates_list.append(unique_item)
    return triangular_pairs_list


#estructura de precios
def get_price_for_t_pair(t_pair,prices_json):
    
    #extraer la informacion del par
    pair_a = t_pair["pair_a"]
    pair_b = t_pair["pair_b"]
    pair_c = t_pair["pair_c"]


    #extraer la informacion por cada par
    pair_a_ask = float(prices_json[pair_a]["lowestAsk"])
    pair_a_bid = float(prices_json[pair_a]["highestBid"])
    pair_b_ask = float(prices_json[pair_b]["lowestAsk"])
    pair_b_bid = float(prices_json[pair_b]["highestBid"])
    pair_c_ask = float(prices_json[pair_c]["lowestAsk"])
    pair_c_bid = float(prices_json[pair_c]["highestBid"])

    #salida de diccionario 
    return {
        "pair_a_ask": pair_a_ask,
        "pair_a_bid": pair_a_bid,
        "pair_b_ask": pair_b_ask,
        "pair_b_bid": pair_b_bid,
        "pair_c_ask": pair_c_ask,
        "pair_c_bid": pair_c_bid
    }



#calcular la oportunidad de arbitraje de tasa de superficie
def calc_triangular_arb_surface_rate(t_pair, prices_dict):
    
    starting_amount = 1000
    min_surface_rate = 0
    surface_dict = {}
    contract_2 = ""
    contract_3 = ""
    direction_trade_1 = ""
    direction_trade_2 = ""
    direction_trade_3 = ""
    acquired_coin_t2 = 0
    acquired_coin_t3 = 0
    calculated = 0


    #extraer el par de la variable
    a_base = t_pair["a_base"]
    a_quote = t_pair["a_quote"]
    b_base = t_pair["b_base"]
    b_quote = t_pair["b_quote"]
    c_base = t_pair["c_base"]
    c_quote = t_pair["c_quote"]
    pair_a = t_pair["pair_a"]
    pair_b = t_pair["pair_b"]
    pair_c = t_pair["pair_c"]

    #extrae la informacion del precio 
    a_ask = prices_dict["pair_a_ask"]
    a_bid = prices_dict["pair_a_bid"]
    b_ask = prices_dict["pair_b_ask"]
    b_bid = prices_dict["pair_b_bid"]
    c_ask = prices_dict["pair_c_ask"]
    c_bid = prices_dict["pair_c_bid"]


    # Declara la variable y la recorre
    direction_list = ["forward", "reverse"]
    for direction in direction_list:

        # declara variables adicionales para el intercambio de informacion
        swap_1 = 0
        swap_2 = 0
        swap_3 = 0
        swap_1_rate = 0
        swap_2_rate = 0
        swap_3_rate = 0

        """
        Reglas de Poloniex !!
             Si estamos intercambiando la moneda de la izquierda (Base) a la derecha (Cotización) entonces * (1 / Ask)
             Si estamos intercambiando la moneda de la derecha (Cotización) a la izquierda (Base), entonces * Oferta
            
        """

       # Asume el inicio con a_base y intercambio por a_quote
        if direction == "forward":
            swap_1 = a_base
            swap_2 = a_quote
            swap_1_rate = 1 / a_ask
            direction_trade_1 = "base_to_quote"

        # Asume el inicio con a_base y intercambio a_quote
        if direction == "reverse":
            swap_1 = a_quote
            swap_2 = a_base
            swap_1_rate = a_bid
            direction_trade_1 = "quote_to_base"

        # Lugar del primer trade
        contract_1 = pair_a
        acquired_coin_t1 = starting_amount * swap_1_rate


        """  FORWARD """

        # Primer stado verificar si a_quote (acquired_coin) coincide b_quote
        if direction == "forward":
            if a_quote == b_quote and calculated == 0:
                swap_2_rate = b_bid
                acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
                direction_trade_2 = "quote_to_base"
                contract_2 = pair_b

                # Si b_base (acquired coin) Coincide c_base
                if b_base == c_base:
                    swap_3 = c_base
                    swap_3_rate = 1 / c_ask
                    direction_trade_3 = "base_to_quote"
                    contract_3 = pair_c

                # Si b_base (acquired coin) Coincide c_quote
                if b_base == c_quote:
                    swap_3 = c_quote
                    swap_3_rate = c_bid
                    direction_trade_3 = "quote_to_base"
                    contract_3 = pair_c

                acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                calculated = 1

        # Primer estado verificar si a_quote (acquired_coin) Intercambiar b_base
        error=0
        if direction == "forward":
            if a_quote == b_base and calculated == 0:
                if b_ask>0:
                    error = 0
                if(b_ask==0.0):
                    b_ask=1
                    error = 1
                swap_2_rate = 1 / b_ask
                acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
                direction_trade_2 = "base_to_quote"
                contract_2 = pair_b

                # Si b_quote (acquired coin) Intercambio c_base
                if b_quote == c_base:
                    swap_3 = c_base
                    swap_3_rate = 1 / c_ask
                    direction_trade_3 = "base_to_quote"
                    contract_3 = pair_c

                # Si b_quote (acquired coin) Intercambio c_quote
                if b_quote == c_quote:
                    swap_3 = c_quote
                    swap_3_rate = c_bid
                    direction_trade_3 = "quote_to_base"
                    contract_3 = pair_c

                acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                calculated = 1

        # Tercer estado verificar si a_quote (acquired_coin) intercambia c_quote
        if direction == "forward":
            if a_quote == c_quote and calculated == 0:
                swap_2_rate = c_bid
                acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
                direction_trade_2 = "quote_to_base"
                contract_2 = pair_c

                # si c_base (acquired coin) intercambia b_base
                if c_base == b_base:
                    swap_3 = b_base
                    swap_3_rate = 1 / b_ask
                    direction_trade_3 = "base_to_quote"
                    contract_3 = pair_b

                # si c_base (acquired coin) intercambia b_quote
                if c_base == b_quote:
                    swap_3 = b_quote
                    swap_3_rate = b_bid
                    direction_trade_3 = "quote_to_base"
                    contract_3 = pair_b

                acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                calculated = 1

        # Cuarto estado verificar si a_quote (acquired_coin) intercambio c_base
        if direction == "forward":
            if a_quote == c_base and calculated == 0:
                swap_2_rate = 1 / c_ask
                acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
                direction_trade_2 = "base_to_quote"
                contract_2 = pair_c

                # Si c_quote (acquired coin) Intercambia b_base
                if c_quote == b_base:
                    swap_3 = b_base
                    swap_3_rate = 1 / b_ask
                    direction_trade_3 = "base_to_quote"
                    contract_3 = pair_b

                # si c_quote (acquired coin) Intercambia b_quote
                if c_quote == b_quote:
                    swap_3 = b_quote
                    swap_3_rate = b_bid
                    direction_trade_3 = "quote_to_base"
                    contract_3 = pair_b

                acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                calculated = 1

        """  Inversa """
        # Primer estado verificar si a_base (acquired_coin) intercambio b_quote
        if direction == "reverse":
            if a_base == b_quote and calculated == 0:
                swap_2_rate = b_bid
                acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
                direction_trade_2 = "quote_to_base"
                contract_2 = pair_b

                # si b_base (acquired coin) intercambio c_base
                if b_base == c_base:
                    swap_3 = c_base
                    swap_3_rate = 1 / c_ask
                    direction_trade_3 = "base_to_quote"
                    contract_3 = pair_c

                # si b_base (acquired coin) intercambio c_quote
                if b_base == c_quote:
                    swap_3 = c_quote
                    swap_3_rate = c_bid
                    direction_trade_3 = "quote_to_base"
                    contract_3 = pair_c

                acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                calculated = 1

        #  2 estado verificar si a_base (acquired_coin) intercambio b_base
        if direction == "reverse":
            if a_base == b_base and calculated == 0:
                swap_2_rate = 1 / b_ask
                acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
                direction_trade_2 = "base_to_quote"
                contract_2 = pair_b

                # si b_quote (acquired coin) intercambio c_base
                if b_quote == c_base:
                    swap_3 = c_base
                    swap_3_rate = 1 / c_ask
                    direction_trade_3 = "base_to_quote"
                    contract_3 = pair_c

                # si b_quote (acquired coin) intercambio c_quote
                if b_quote == c_quote:
                    swap_3 = c_quote
                    swap_3_rate = c_bid
                    direction_trade_3 = "quote_to_base"
                    contract_3 = pair_c

                acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                calculated = 1

        #  3 estado verificar si a_base (acquired_coin) intercambio c_quote
        if direction == "reverse":
            if a_base == c_quote and calculated == 0:
                swap_2_rate = c_bid
                acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
                direction_trade_2 = "quote_to_base"
                contract_2 = pair_c

                # si c_base (acquired coin) intercambio b_base
                if c_base == b_base:
                    swap_3 = b_base
                    swap_3_rate = 1 / b_ask
                    direction_trade_3 = "base_to_quote"
                    contract_3 = pair_b

                # si c_base (acquired coin) intercambio b_quote
                if c_base == b_quote:
                    swap_3 = b_quote
                    swap_3_rate = b_bid
                    direction_trade_3 = "quote_to_base"
                    contract_3 = pair_b

                acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                calculated = 1

        #  4 estado verificar si a_base (acquired_coin) intercambio c_base
        if direction == "reverse":
            if a_base == c_base and calculated == 0:
                swap_2_rate = 1 / c_ask
                acquired_coin_t2 = acquired_coin_t1 * swap_2_rate
                direction_trade_2 = "base_to_quote"
                contract_2 = pair_c

                # si c_quote (acquired coin) intercambio b_base
                if c_quote == b_base:
                    swap_3 = b_base
                    swap_3_rate = 1 / b_ask
                    direction_trade_3 = "base_to_quote"
                    contract_3 = pair_b

                # si c_quote (acquired coin) intercambio b_quote
                if c_quote == b_quote:
                    swap_3 = b_quote
                    swap_3_rate = b_bid
                    direction_trade_3 = "quote_to_base"
                    contract_3 = pair_b

                acquired_coin_t3 = acquired_coin_t2 * swap_3_rate
                calculated = 1


        # Profit and Loss Calculations
        profit_loss = acquired_coin_t3 - starting_amount
        profit_loss_perc = (profit_loss / starting_amount) * 100 if profit_loss != 0 else 0

        # Trade Descriptions
        trade_description_1 = f"Inicio con {swap_1} de {starting_amount}. intercambio a {swap_1_rate} por {swap_2} adquirido {acquired_coin_t1}."
        trade_description_2 = f"intercambio {acquired_coin_t1} de {swap_2} a {swap_2_rate} por {swap_3} adquirido {acquired_coin_t2}."
        trade_description_3 = f"intercambio {acquired_coin_t2} de {swap_3} a {swap_3_rate} por {swap_1} adquirido {acquired_coin_t3}."

        pair_trian = pair_a+" "+ pair_b+" "+ pair_c


        # Salida de resultados Results
        if profit_loss_perc > min_surface_rate:
            surface_dict = {
                "swap_1": swap_1,
                "swap_2": swap_2,
                "swap_3": swap_3,
                "contract_1": contract_1,
                "contract_2": contract_2,
                "contract_3": contract_3,
                "direction_trade_1": direction_trade_1,
                "direction_trade_2": direction_trade_2,
                "direction_trade_3": direction_trade_3,
                "starting_amount": starting_amount,
                "acquired_coin_t1": acquired_coin_t1,
                "acquired_coin_t2": acquired_coin_t2,
                "acquired_coin_t3": acquired_coin_t3,
                "swap_1_rate": swap_1_rate,
                "swap_2_rate": swap_2_rate,
                "swap_3_rate": swap_3_rate,
                "profit_loss": profit_loss,
                "profit_loss_perc": profit_loss_perc,
                "direction": direction,
                "trade_description_1": trade_description_1,
                "trade_description_2": trade_description_2,
                "trade_description_3": trade_description_3,
                "pair_trian":pair_trian,
                "error": error
            }
            

            return surface_dict

    return surface_dict

        # if profit_loss>0:
        #     print('nuevo trade')
        #     print(trade_description_1)
        #     print(trade_description_2)
        #     print(trade_description_3)
        #     print(direction,pair_a,pair_b,pair_c, "\n")




# Volver a formatear el libro de pedidos para el cálculo de la profundidad
def reformated_orderbook(prices, c_direction):
    price_list_main = []
    if c_direction == "base_to_quote":
        for p in prices["asks"]:
            ask_price = float(p[0])
            adj_price = 1 / ask_price if ask_price != 0 else 0
            adj_quantity = float(p[1]) * ask_price
            price_list_main.append([adj_price, adj_quantity])
    if c_direction == "quote_to_base":
        for p in prices["bids"]:
            bid_price = float(p[0])
            adj_price = bid_price if bid_price != 0 else 0
            adj_quantity = float(p[1])
            price_list_main.append([adj_price, adj_quantity])
    return price_list_main






# Obtenga la moneda adquirida, también conocida como cálculo de profundidad
def calculate_acquired_coin(amount_in, orderbook):

    # Variables iniciales
    trading_balance = amount_in
    quantity_bought = 0
    acquired_coin = 0
    counts = 0
    for level in orderbook:

        # Extraer el nivel de precio y cantidad.
        level_price = level[0]
        level_available_quantity = level[1]

        # monto entrante es <= importe total del primer nivel
        if trading_balance <= level_available_quantity:
            quantity_bought = trading_balance
            trading_balance = 0
            amount_bought = quantity_bought * level_price

        # La cantidad entrante es > una cantidad total de nivel dado
        if trading_balance > level_available_quantity:
            quantity_bought = level_available_quantity
            trading_balance -= quantity_bought
            amount_bought = quantity_bought * level_price

        # Acumular monedas adquiridas
        acquired_coin = acquired_coin + amount_bought

        # Trade con exito
        if trading_balance == 0:
            return acquired_coin

        # Salir si no hay suficientes niveles de cartera de pedidos
        counts += 1
        if counts == len(orderbook):
            return 0



# Obtenga la profundidad del libro de pedidos
def get_depth_from_orderbook(surface_arb):

    # Extraer variables iniciales
    swap_1 = surface_arb["swap_1"]
    starting_amount = 100
    starting_amount_dict = {
        "USDT": 100,
        "USDC": 100,
        "BTC": 0.05,
        "ETH": 0.1
    }
    if swap_1 in starting_amount_dict:
        starting_amount = starting_amount_dict[swap_1]

    # Definir los pares
    contract_1 = surface_arb["contract_1"]
    contract_2 = surface_arb["contract_2"]
    contract_3 = surface_arb["contract_3"]

    # Definir la direccion de los trades
    contract_1_direction = surface_arb["direction_trade_1"]
    contract_2_direction = surface_arb["direction_trade_2"]
    contract_3_direction = surface_arb["direction_trade_3"]

    # Obtener el libro de pedidos para la primera evaluación comercial
    url1 = f"https://poloniex.com/public?command=returnOrderBook&currencyPair={contract_1}&depth=20"
    depth_1_prices = get_coin_tickers(url1)
    depth_1_reformatted_prices = reformated_orderbook(depth_1_prices, contract_1_direction)
    time.sleep(0.3)
    url2 = f"https://poloniex.com/public?command=returnOrderBook&currencyPair={contract_2}&depth=20"
    depth_2_prices = get_coin_tickers(url2)
    depth_2_reformatted_prices = reformated_orderbook(depth_2_prices, contract_2_direction)
    time.sleep(0.3)
    url3 = f"https://poloniex.com/public?command=returnOrderBook&currencyPair={contract_3}&depth=20"
    depth_3_prices = get_coin_tickers(url3)
    depth_3_reformatted_prices = reformated_orderbook(depth_3_prices, contract_3_direction)

    # Obtener las monedas
    acquired_coin_t1 = calculate_acquired_coin(starting_amount, depth_1_reformatted_prices)
    acquired_coin_t2 = calculate_acquired_coin(acquired_coin_t1, depth_2_reformatted_prices)
    acquired_coin_t3 = calculate_acquired_coin(acquired_coin_t2, depth_3_reformatted_prices)

    # Calcule la pérdida o ganancias, también conocida como tasa real
    profit_loss = acquired_coin_t3 - starting_amount
    real_rate_perc = (profit_loss / starting_amount) * 100 if profit_loss != 0 else 0

    if real_rate_perc > -1:
        return_dict = {
            "profit_loss": profit_loss,
            "real_rate_perc": real_rate_perc,
            "contract_1": contract_1,
            "contract_2": contract_2,
            "contract_3": contract_3,
            "contract_1_direction": contract_1_direction,
            "contract_2_direction": contract_2_direction,
            "contract_3_direction": contract_3_direction
        }
        return return_dict
    else:
        return {}


