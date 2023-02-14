import time

from trade.garch import *
from trade.mt5 import *


def main():
    conecta_mt5("BTG")


garch_symbols, options = set_market_watch("BTG")

tempo = time.time() + 10
while time.time() < tempo:
    print(volatilitys_df(garch_symbols))
