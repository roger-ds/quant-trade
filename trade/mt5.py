import MetaTrader5 as mt5


def conecta_mt5(conta):
    if conta ==  "XP-PRD":
        login = 359995
        server = "XPMT5-PRD"
        password = "Fiscal960"
    elif conta == "XP-Demo":
        login = 50359995
        server = "XPMT5-Demo"
        password = "W2585KgI"
    elif conta == "modalmais":
        login = 43292
        server = "mt5-DMA4.modalmais.com.br"
        password = "Fiscal96"
    elif conta == "MetaQuotes-Demo":
        login = 5010116048
        server = "MetaQuotes-Demo"
        password = "jpy6bivn"
    elif conta == "BTG":
        login = 2378472
        server = "BancoBTGPactual-PRD"
        password = "Fiscal960"
        
    # connect to MetaTrader 5
    if not mt5.initialize(login=login, server=server ,password=password):
        print("initialize() failed, error code =",mt5.last_error())
        mt5.shutdown()

    # request connection status and parameters
    print('Informação: trade allowed -', mt5.terminal_info().trade_allowed)


def get_ohlc(ativo, timeframe, n=5):
    # get 10 ativo D1 bars from the current day
    ativo = mt5.copy_rates_from_pos(ativo, timeframe, 0, n)
    # create DataFrame out of the obtained data
    ativo = pd.DataFrame(ativo)
    # convert time in seconds into the datetime format
    ativo['time'] = pd.to_datetime(ativo['time'], unit='s')
    ativo.set_index('time', inplace=True)
    return ativo


