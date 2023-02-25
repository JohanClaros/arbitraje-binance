import trial_funtion
import json

coin_prince_url = "https://poloniex.com/public?command=returnTicker"

def step_0():
    #Extrae la lista de pares y precios del exchange
    coin_json = trial_funtion.get_coin_tickers(coin_prince_url) 
    coin_list = trial_funtion.collect_tradeables(coin_json)
    return(coin_list)





uwu = step_0()
pairs_list = uwu[0:]
print(pairs_list)
   
   