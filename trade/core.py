from trade import pymt5


def start_options():
    """Entry piont to  Starts MetaTrader5 and set market watch
    also returns symbol lisr and an option list"""
    symbols = pymt5.set_market_watch_symbols("BTG")
    options = pymt5.set_market_watch_options("BTG")

    options.reset_index(inplace=True)
    print(options)


