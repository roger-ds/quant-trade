import MetaTrader5 as mt5
import pandas as pd
import requests


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


def options(symbol, spot_price, call_expire = "C", put_expire = "O"):
    """Returns a df with options that strike is aroud 10 % spot price on
    given expirations dates"""
    option = symbol[0:4]
    delta = spot_price * 0.1
    df = list_all_options(symbol)
    df = df[(df['option'].str.contains(option + call_expire)) |
    (df['option'].str.contains(option + put_expire))]
    df = df[(df['strike'] > spot_price - delta) &
    (df['strike'] < spot_price + delta)]
    return df


def add_realtime_columns(options):
    """Add RealTime columns to options df"""
    options["last"] = options.apply(
        lambda x: mt5.symbol_info_tick(x.option).last, axis =1)
    options["bid"] = options.apply(
        lambda x: mt5.symbol_info_tick(x.option).bid, axis =1)
    options["ask"] = options.apply(
        lambda x: mt5.symbol_info_tick(x.option).ask, axis =1)
