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


def main():
  print("Open Trader 0.04")
  print()

  #run_my_portfolio()
  #run_mega_cap_portfolio()
  #run_tradingview_errors()
  run_indices()

  #stream = open("Portfolios\MyPortfolio.yaml", "r")
  #stream = open("Portfolios\MegaCaps.yaml", "r")
  #stream = open("Portfolios\Indices.yaml", "r")

  #commodities = ["Gold", "Silver", "Gas", "Copper"]
  #"10 yr"
  #"ETH"

def run_my_portfolio():
  stock_manager = StockManager("Portfolios\MyPortfolio.yaml")
  stock_manager.run_battery()
  stock_manager.close_browser()

def run_mega_cap_portfolio():
  stock_manager = StockManager("Portfolios\MegaCaps.yaml")
  stock_manager.run_battery()
  stock_manager.close_browser()

def run_tradingview_errors():
  stock_manager = StockManager("Portfolios\TradingviewErrors.yaml")
  stock_manager.run_battery()
  stock_manager.close_browser()

def run_indices():
  index_manager = IndexManager("Portfolios\Indices.yaml")
  index_manager.run_battery()
  index_manager.close_browser()

if __name__ == "__main__":
    main()
