# Importa as bibliotecas
from datetime import datetime, timedelta, date 
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from arch import arch_model # roda o modelo garch
import MetaTrader5 as mt5


def ohlc_to_ascending_df(ativo):
    ohlc = get_ohlc(ativo, mt5.TIMEFRAME_D1, 101)["close"]
    ohlc = ohlc.to_frame()
    ohlc.index.names = ['Date']
    ohlc.sort_values('Date', ascending=False, inplace=True)
    return ohlc


def get_log_return(df):
    data = df.copy()
    # Transforma em retornos contínuos
    data['log_return'] = np.log( data['close'].shift(-1) / data['close'])
    data.dropna(inplace=True)
    data.sort_values('Date', inplace=True)
    return(data)


def get_std_dev(df):
    # compute sample standard deviation of returns
    data = df.copy()
    data['std_dev'] = data['log_return'].rolling(50).std()
    return(data)


def hist_volatility(df):
    # hystorycal annualized volatilty
    data = df.copy()
    data['hist_volatility'] = data['std_dev'] * ((252)**0.5)
    # Retira os dados faltantes
    data = data.dropna()
    return(data)


def garch_model(df):
    # Especifica o modelo
    gm = arch_model(df['log_return'], p = 1, q = 1,
                        mean = 'constant', vol = 'GARCH', dist = 'normal', rescale=False)
    # Roda o modelo
    gm_fit = gm.fit(disp = 'off')
    print(gm_fit.summary())
    return gm_fit


def gm_volatility(gm_fit):
    """Volatilidade dada por garch"""
    gm_volatility = gm_fit.conditional_volatility * 252 ** 0.5
    gm_volatility = pd.DataFrame({'gm_volatility':gm_volatility.values}, index=gm_volatility.index)
    gm_volatility.sort_index(ascending=False, inplace=True)
    return(gm_volatility)


def forecast_vol(gm_fit, horizon = 1):
    # Previsão
    forecast = gm_fit.forecast(horizon = 5, reindex = False)
    forecast_vol = (forecast.variance ** 0.5) * 252 ** 0.5
    return(forecast_vol)


def volatilites():





    forecast_data = data.sort_index(ascending=False)
    garch_vol = forecast_data.join(gm_volatility).join(forecast_vol).fillna('-')
    vols = garch_vol.iloc[0,:].to_frame().T
    return vols


