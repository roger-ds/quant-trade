import MetaTrader5 as mt5
import pandas as pd
import numpy as np
import requests
import pprint
from scipy.stats import norm
from py_vollib.black_scholes import black_scholes as bs
from py_vollib.black_scholes.greeks.analytical import vega, theta, rho

pd.set_option('display.max_columns', 20)  # or 1000
pd.set_option('display.max_rows', 400)  # or 1000
pd.set_option('display.max_colwidth', 20)  # or 199
pd.set_option('expand_frame_repr', False)


def list_options(symbol, expiration):
    """List options from https://opcoes.net.br/ API by expiration date"""
    url = f"https://opcoes.net.br/listaopcoes/completa?idAcao={symbol}&listarVencimentos=false&cotacoes=true&vencimentos={expiration}"
    r = requests.get(url).json()
    l = [ 
        [i[3], i[0].split("_")[0], i[2], expiration, i[5]] 
        for i in r["data"]["cotacoesOpcoes"]
        ]
    return pd.DataFrame(
        l, columns=["model", "option",  "type", "expiration", "strike"]
        )


def list_all_options(symbol):
    """List all options from https://opcoes.net.br/ API """
    url = f"https://opcoes.net.br/listaopcoes/completa?idAcao={symbol}&listarVencimentos=true&cotacoes=true"
    r = requests.get(url).json()
    expirations = [i["value"] for i in r["data"]["vencimentos"]]
    df = pd.concat([list_options(symbol, expiration) for expiration in expirations])
    return df


def get_options_net_br(symbol, spot_price, call_expire = "C", put_expire = "O"):
    """Returns a df with options that strike is aroud 10 % spot price on
    given expirations dates"""
    option = symbol[0:4]
    delta = spot_price * 0.1
    df = list_all_options(symbol)
    df['type'] = df.apply(lambda x: "c" if x.type == "CALL" else "p", axis=1)
    df['symbol'] = symbol
    df = df[(df['option'].str.contains(option + call_expire)) |
    (df['option'].str.contains(option + put_expire))]
    df = df[(df['strike'] > spot_price - delta) &
    (df['strike'] < spot_price + delta)]
    df = df[df['model'] == 'E']
    df = df[df['symbol'] == 'PETR4']
    return df




def implied_vol(S0, K, market_price, flag="c", T=15/252, r=0.1365, tol=0.00001):
    """Compute the implied volatility of a European Option
        S0: initial stock price
        K:  strike price
        T:  maturity
        r:  risk-free rate
        market_price: market observed price
        tol: user choosen tolerance
    """
    max_iter = 200 #max number of iterations
    vol_old = 0.30 #initial guess
    for k in range(max_iter):
        bs_price = bs(flag, S0, K, T, r, vol_old)
        Cprime =  vega(flag, S0, K, T, r, vol_old)*100
        C = bs_price - market_price
        if Cprime != 0.0: 
            vol_new = vol_old - C/Cprime
        else: return None
        bs_new = bs(flag, S0, K, T, r, vol_new)
        if (abs(vol_old - vol_new) < tol or abs(bs_new - market_price) < tol):
            break
        vol_old = vol_new
    implied_vol = vol_old
    return implied_vol


def delta_calc(S, K, sigma, type_="c", T=15/252, r=0.1365):
    "Calculate delta of an option"
    d1 = (np.log(S/K) + (r + sigma**2/2)*T)/(sigma*np.sqrt(T))
    if type_ == "c":
        delta_calc = norm.cdf(d1, 0, 1)
    elif type_ == "p":
        delta_calc = -norm.cdf(-d1, 0, 1)
    return delta_calc 


def gamma_calc(S, K, sigma, type_="c", T=15/252, r=0.1365):
    "Calculate gamma of a option"
    d1 = (np.log(S/K) + (r + sigma**2/2)*T)/(sigma*np.sqrt(T))
    d2 = d1 - sigma*np.sqrt(T)
    gamma_calc = norm.pdf(d1, 0, 1)/(S*sigma*np.sqrt(T))
    return gamma_calc


# def vega(S, K, sigma, type_="c", T=16/252, r=0.1365):
#     "Calculate BS price of call/put"
#     d1 = (np.log(S/K) + (r + sigma**2/2)*T)/(sigma*np.sqrt(T))
#     d2 = d1 - sigma*np.sqrt(T)
#     vega_calc = S*norm.pdf(d1, 0, 1)*np.sqrt(T)
#     return vega_calc*0.01, vega(type_, S, K, T, r, sigma)


# def theta(S, K, sigma, type_="c", T=16/252, r=0.1365):
#     "Calculate BS price of call/put"
#     d1 = (np.log(S/K) + (r + sigma**2/2)*T)/(sigma*np.sqrt(T))
#     d2 = d1 - sigma*np.sqrt(T)
#     if type_ == "c":
#         theta_calc = -S*norm.pdf(d1, 0, 1)*sigma/(2*np.sqrt(T)) - r*K*np.exp(-r*T)*norm.cdf(d2, 0, 1)
#     elif type_ == "p":
#         theta_calc = -S*norm.pdf(d1, 0, 1)*sigma/(2*np.sqrt(T)) + r*K*np.exp(-r*T)*norm.cdf(-d2, 0, 1)
#     return theta_calc/365, theta(type_, S, K, T, r, sigma)


def add_realtime_columns(options):
    """Add RealTime columns to options df"""
    options["bid"] = options.apply(
        lambda x: mt5.symbol_info_tick(x.option).bid if mt5.symbol_info_tick(x.option).bid != 0 else None, axis=1)
    options["ask"] = options.apply(
        lambda x: mt5.symbol_info_tick(x.option).ask if mt5.symbol_info_tick(x.option).ask != 0 else None, axis=1)
    options.dropna(inplace=True)
    options["med"] = round((options["bid"] + options["ask"]) / 2, 2)
    options["last"] = options.apply(
        lambda x: mt5.symbol_info_tick(x.option).last, axis=1)
    options["spot_bid"] = options.apply(
        lambda x: mt5.symbol_info_tick(x.symbol).bid, axis=1)
    options["spot_ask"] = options.apply(
        lambda x: mt5.symbol_info_tick(x.symbol).ask, axis=1)
    options["spot_med"] = round(
        (options["spot_bid"] + options["spot_ask"]) / 2, 2)
    options["spot_last"] = options.apply(
        lambda x: mt5.symbol_info_tick(x.symbol).last, axis=1)
    options["vol_bid"] = round(options.apply(
        lambda x: implied_vol(x.spot_med, x.strike, x.bid,x.type),axis=1)*100,2)
    options["vol_ask"] = round(options.apply(
        lambda x: implied_vol(x.spot_med, x.strike, x.ask,x.type),axis=1)*100,2)
    options.dropna(inplace=True)
    options["vol_med"] = round(
        (options["vol_bid"] + options["vol_ask"]) / 2, 2)
    options["delta"] = round(options.apply(
        lambda x: delta_calc(x.spot_med, x.strike, x.vol_med, x.type),axis=1)*100,2)
    options["gamma"] = round(options.apply(
        lambda x: gamma_calc(x.spot_med,x.strike,x.vol_med,x.type),axis=1)*100,2)
    # options["vega"] = round(options.apply(
    #     lambda x: vega(x.spot_med,x.strike,x.vol_med,x.type)[0],axis=1)*100,2)
    options = options[
        ['model','option','type','expiration','strike','bid','ask','med',
        'last','symbol','spot_bid','spot_ask','spot_med','spot_last',
        'vol_bid','vol_ask','vol_med','delta','gamma']
        ]
    #options.reset_index(drop=True, inplace=True)
    print(options)
    return(options)
