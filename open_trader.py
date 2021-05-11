import requests
from bs4 import BeautifulSoup
import datetime
import yaml
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import time

import sys
import getopt

from stock_manager import StockManager
from index_manager import IndexManager

# wanted features
# - database to compare/notice changes
# - marketwatch for current price
# - marketbeat
# - auto stop loss and buy back at next elliot wave pivot
# - quiver quantitative
#   + delta of mentions
#   + congress
#   + insider trading
# - pretiming
# - flowalgo
# - seeking alpha
# - youtube analysts + transcription
# - google trends
# - tradingview 
# - iknowfirst
# - price target meet/exceed
# - bull trades ($50/mo)
#   + dark pool
#   + unusual/golden sweeps
#   + alpha ai
# stochastic RSI - captured in tradingview
# add futures and indices, commodities
# add market vs premarket for marketwatch


# for crypto
# https://s2f.hamal.nl/s2fcharts.html
# lookintobitcoin
# - private tradingview indicator scripts
# - indicator alerts

# https://digitalik.net/btc/


def main(argv):
  print("Open Trader 0.04")
  print()

  input_file = ''

  try:
    opts, args = getopt.getopt(argv, "hipmw", ["infile=", "--myportfolio", "--megacaps"])
  except getopt.GetoptError:
    print("open_trader.py -i <input_file>")
    sys.exit(2)

  manager = None
  for opt, arg in opts:
    if opt == "-h":
      print("open_trader.py -i <input_file>")
      sys.exit()
    elif opt in ["-i", "--infile"]:
      input_file = arg
      manager = StockManager(input_file)
    elif opt in ["-p", "--myportfolio"]:
      input_file = "Portfolios\MyPortfolio.yaml"
      manager = StockManager(input_file)
    elif opt in ["-m", "--megacaps"]:
      input_file = "Portfolios\MegaCaps.yaml"
      manager = StockManager(input_file)
    elif opt in ["-w", "--indices"]:
      input_file = "Portfolios\Indices.yaml"
      manager = IndexManager(input_file)

  if manager is not None:
    manager.run_battery()
    manager.close_browser()

  #stream = open("Portfolios\MyPortfolio.yaml", "r")
  #stream = open("Portfolios\MegaCaps.yaml", "r")
  #stream = open("Portfolios\Indices.yaml", "r")

  #commodities = ["Gold", "Silver", "Gas", "Copper"]
  #"10 yr"
  #"ETH"

if __name__ == "__main__":
    main(sys.argv[1:])
