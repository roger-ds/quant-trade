# Importa as bibliotecas
import time
import matplotlib.pyplot as plt
import MetaTrader5 as mt5
import numpy as np
import pandas as pd
import seaborn as sns
from trade.pymt5 import get_ohlc
from datetime import date, datetime, timedelta
from arch import arch_model  # roda o modelo garch


def ohlc_to_ascending_df(symbol):
    """Returns 101 closes prices df in TIMEFRAME_D1"""
    ohlc = get_ohlc(symbol, mt5.TIMEFRAME_D1, 101)["close"]
    ohlc = ohlc.to_frame()
    ohlc.index.names = ["Date"]
    ohlc.sort_values("Date", ascending=False, inplace=True)
    ohlc["symbol"] = symbol
    ohlc = ohlc[["symbol", "close"]]
    return ohlc


def get_log_return(df):
    data = df.copy()
    # Transforma em retornos contínuos
    data["log_return"] = np.log(data["close"].shift(-1) / data["close"])
    data.dropna(inplace=True)
    data.sort_values("Date", inplace=True)
    return data


def get_std_dev(df):
    # compute sample standard deviation of returns
    data = df.copy()
    data["std_dev"] = data["log_return"].rolling(50).std()
    return data


def hist_volatility(df):
    # hystorycal annualized volatilty
    data = df.copy()
    data["hist_volatility"] = data["std_dev"] * ((252) ** 0.5)
    # Retira os dados faltantes
    data = data.dropna()
    return data


def garch_model(df):
    # Especifica o modelo
    gm = arch_model(
        df["log_return"],
        p=1,
        q=1,
        mean="constant",
        vol="GARCH",
        dist="normal",
        rescale=False,
    )
    # Roda o modelo
    gm_fit = gm.fit(disp="off")
    # print(gm_fit.summary())
    return gm_fit


def gm_volatility(gm_fit):
    """Volatilidade dada por garch"""
    gm_vol = gm_fit.conditional_volatility * 252**0.5
    gm_vol = pd.DataFrame({"gm_volatility": gm_vol.values}, index=gm_vol.index)
    gm_vol.sort_index(ascending=False, inplace=True)
    return gm_vol


def forecast_volatility(gm_fit, horizon=1):
    # Previsão
    forecast = gm_fit.forecast(horizon=3, reindex=False)
    forecast_vol = (forecast.variance**0.5) * 252**0.5
    return forecast_vol


def volatilites(data, gm_vol, forecast_vol):
    forecast_data = data.sort_index(ascending=False)
    garch_vol = forecast_data.join(gm_vol).join(forecast_vol).fillna("-")
    vols = garch_vol.iloc[0, :].to_frame().T
    return vols


def garch(symbol):
    close_prices = ohlc_to_ascending_df(symbol)
    data = get_log_return(close_prices)
    data = get_std_dev(data)
    data = hist_volatility(data)
    gm_fit = garch_model(data)
    gm_vol = gm_volatility(gm_fit)
    forecast_vol = forecast_volatility(gm_fit)
    vols = volatilites(data, gm_vol, forecast_vol)
    vols = vols[["symbol", "close", "hist_volatility", "gm_volatility", "h.1"]]

    vols["hist_volatility"] = vols["hist_volatility"].astype(float).round(4) * 100
    vols["gm_volatility"] = vols["gm_volatility"].astype(float).round(4) * 100
    vols["h.1"] = vols["h.1"].astype(float).round(4) * 100
    return vols


def volatilitys_df(garch_symbols):
    vols_list = []
    for symbol in garch_symbols:
        vols = garch(symbol)
        vols_list.append(vols)
        volatilitys = pd.concat(vols_list)
    vols_list = []
    time.sleep(3)
    return volatilitys
