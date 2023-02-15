import MetaTrader5 as mt5
import pandas as pd
from trade.settings import SYMBOLS_WATHC, OPTIONS_WATHC


def conecta_mt5(conta):
    if conta == "XP-PRD":
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
    if not mt5.initialize(login=login, server=server, password=password):
        print("initialize() failed, error code =", mt5.last_error())
        mt5.shutdown()
    # request connection status and parameters
    # print('Informação: trade allowed -', mt5.terminal_info().trade_allowed)


def busca_carteira_teorica(indice):
    """busca_carteira_teorica returns a list of indexs ex. ibov, ibrx, smll"""
    url = "http://bvmf.bmfbovespa.com.br/indices/ResumoCarteiraTeorica.aspx?Indice={}&idioma=pt-br".format(
        indice.upper()
    )
    df = pd.read_html(url, decimal=",", thousands=".", index_col="Código")[0][
        :-1
    ]
    symbols = list(df.index)
    return symbols


def get_mt5_symbols(conta):
    """This function returns the list of symbols in mt5"""
    conecta_mt5(conta)
    symbols_mt5 = mt5.symbols_get()
    return symbols_mt5


def symbols_to_watch(symbols_mt5, symbols_watch):
    """This function receves a list of symbols to show in mt5 market watch"""
    symbols_list = []
    for watch in symbols_watch:
        for symbol in symbols_mt5:
            if symbol.name == watch:
                symbols_list.append(symbol.name)
    return symbols_list


def options_to_watch(symbols_mt5, options_watch, venc_call, venc_put):
    """This function receves a list of symbols to show in mt5 market watch
    also, receves a latter to options dedline"""
    options_list = []
    for watch in options_watch:
        for symbol in symbols_mt5:
            if symbol.name.startswith(
                watch + venc_call
            ) or symbol.name.startswith(watch + venc_put):
                options_list.append(symbol.name)
    return options_list


def market_watch(symbols_mt5, symbols_list):
    """Puts symbols and options in maket watch"""
    symbols = symbols_mt5
    for symbol in symbols:
        if symbol.name in symbols_list:
            symbol_info = mt5.symbol_info(symbol.name)
            if not symbol_info.visible:
                print(symbol.name, " náo está visível, tentando adicionar")
                # attempt to enable the display of the ativo in MarketWatch
                selected = mt5.symbol_select(symbol.name, True)
                if not selected:
                    print("Failed to select " + symbol.name)
                    mt5.shutdown()
                    quit()
            print(symbol.name + "... ok")
        else:
            selected = mt5.symbol_select(symbol.name, False)


def set_market_watch(conta):
    symbols_mt5 = get_mt5_symbols(conta)
    symbols_watch = SYMBOLS_WATHC
    options_watch = OPTIONS_WATHC
    symbols = symbols_to_watch(symbols_mt5, symbols_watch)
    options = options_to_watch(
        symbols_mt5, options_watch, venc_call="C", venc_put="O"
    )
    market_watch(symbols_mt5, symbols)
    market_watch(symbols_mt5, options)
    return symbols, options


def get_ohlc(symbol, timeframe, n=5):
    # get 10 symbol D1 bars from the current day
    symbol = mt5.copy_rates_from_pos(symbol, timeframe, 0, n)
    # create DataFrame out of the obtained data
    symbol = pd.DataFrame(symbol)
    # convert time in seconds into the datetime format
    symbol["time"] = pd.to_datetime(symbol["time"], unit="s")
    symbol.set_index("time", inplace=True)
    return symbol


def get_ohlc_close(symbols):
    close = pd.DataFrame()
    for symbol in symbols[0:10]:
        close[symbol] = get_ohlc(symbol, mt5.TIMEFRAME_D1, 10)["close"]
    close.index.names = ["Date"]
    return close


def get_book(symbol, data_inicio, n=5):
    # get 5 ativo ticks from the current day
    symbol = mt5.copy_ticks_from(symbol, data_inicio, n, mt5.COPY_TICKS_ALL)
    # create DataFrame out of the obtained data
    symbol = pd.DataFrame(symbol)
    # convert time in seconds into the datetime format
    symbol["time"] = pd.to_datetime(symbol["time"], unit="s")
    ativo.set_index("time", inplace=True)
    return symbol


def symbol_tick(symbols):
    """Recives a list of symbols and more eficiently
    Returns a real-time dict for last, bid and ask price"""
    tick = {}
    for symbol in symbols:
        bid, ask, last = mt5.symbol_info_tick(symbol)[1:4]
        tick[symbol] = bid, ask, last
    return tick


def last_bid_ask(*args):
    """Recives a list of symbols and
    Returns a real-time dict for last, bid and ask price"""
    last = {}
    bid = {}
    ask = {}
    for arg in args:
        last[arg] = mt5.symbol_info_tick(arg).last
        bid[arg] = mt5.symbol_info_tick(arg).bid
        ask[arg] = mt5.symbol_info_tick(arg).ask
    return last, bid, ask


def infotick(*symbols):
    """Recives a list of symbols and
    Returns a real-time df for last, bid and ask price"""
    last, bid, ask = last_bid_ask(*symbols)
    tick_last = pd.DataFrame(last, index=["last"])
    tick_bid = pd.DataFrame(bid, index=["bid"])
    tick_ask = pd.DataFrame(ask, index=["ask"])
    infotick = pd.concat([tick_last, tick_bid, tick_ask])
    return infotick


### Ordens em RealTime


def show_result_as_dict(result):
    # request the result as a dictionary and display it element by element
    result_dict = result._asdict()
    for field in result_dict.keys():
        if field != "request":
            print("   {}={}".format(field, result_dict[field]))
            # if this is a trading request structure, display it element by element as well
        if field == "request":
            traderequest_dict = result_dict[field]._asdict()
            for tradereq_filed in traderequest_dict:
                print(
                    "       traderequest: {}={}".format(
                        tradereq_filed, traderequest_dict[tradereq_filed]
                    )
                )


def request_market_order(lot, symbol, tipo):
    # prepare the request
    price = mt5.symbol_info_tick(symbol).ask
    point = mt5.symbol_info(symbol).point
    deviation = 10
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": float(lot),
        "type": tipo,
        "price": price,
        # "sl": mt5.symbol_info_tick(symbol).ask-50*point,
        # "tp": mt5.symbol_info_tick(symbol).ask+50*point,
        "deviation": deviation,
        "magic": 12345,
        "comment": "python script",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_RETURN,
    }
    return request


def send_market_order(lot, symbol, tipo):
    request = request_market_order(lot, symbol, tipo)

    # perform the check and display the result 'as is'
    result = mt5.order_check(request)

    print("=========== Order Check ============")
    show_result_as_dict(result)

    if result.retcode == 0:
        print("=========== Order Send ============")
        # enviamos a solicitação de negociação
        result = mt5.order_send(request)
        # verificamos o resultado da execução
        print("1. order_send(): by {} {} lots".format(symbol, lot))
        show_result_as_dict(result)

        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print("2. order_send failed, retcode={}".format(result.retcode))

        print("2. order_send done, ")
        print(
            "   opened position with POSITION_TICKET={}".format(result.order)
        )
    else:
        print("Order_check failed, retcode={}".format(result.retcode))

    return result
