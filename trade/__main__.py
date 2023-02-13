import time 
from trade.mt5 import *
from trade.garch import *


def main():
    conecta_mt5("BTG")


if __name__ == "__main__":
    main()

symbols, options = set_market_watch()

tempo = time.time() + 30
while time.time() < tempo:
    for symbol in symbols:
        print(symbol)
        vols = garch(symbol)
        print(vols)
    time.sleep(1)


