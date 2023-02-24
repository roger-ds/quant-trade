from time import sleep
from trade import pymt5, pyoptions


def start_options():
    """Entry piont to  Starts MetaTrader5 and set market watch
    also returns symbol lisr and an option list"""
    symbols = pymt5.set_market_watch_symbols("BTG")
    options_net_br = pymt5.set_market_watch_options("BTG")


    while True:
        options = pyoptions.add_realtime_columns(options_net_br)
        sleep(.1)


