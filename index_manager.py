from stock_manager import StockManager
import requests
from bs4 import BeautifulSoup

class IndexManager(StockManager):
  def run_battery(self):
    browser = self.browser
    dictionary = self.dictionary

    #self.check_premarket()
    print("---------------------------")
    for t, content in dictionary.items():
      name = content['name']
      pretiming_text = content['pretiming']

      tradingview_result = -1
      try:
        exchange = content['exchange']
        #print("exchange: " + str(exchange))
      except:
        None

      if t == "RUT":
        tradingview_result = self.check_tradingview(t, exchange)
      else:
        tradingview_result = self.check_tradingview_index(t, exchange)

      print("TradingView has " + name + "\t" + self.RANKS[1 + tradingview_result])
      self.check_pretiming_index(t, name, pretiming_text)
      print()

  def check_tradingview_index(self, ticker, exchange):
    url = "https://www.tradingview.com/markets/indices/quotes-major/"
    html_text = requests.get(url, headers=self.HEADERS).text
    soup = BeautifulSoup(html_text, 'html.parser')

    result = -1
    row = soup.find("tr", {"class":"tv-data-table__row tv-data-table__stroke tv-screener-table__result-row", "data-symbol":exchange + ":" + ticker})
    #print("row: " + str(row))
    if row is not None:
      #print(ticker)
      ranks = ["strong-sell", "sell", "neutral", "buy", "strong-buy"]
      rating_val = -1
      i = 0
      for rank in ranks:
        rating = row.find("span", {"class":"tv-screener-table__signal tv-screener-table__signal--" + rank})
        if rating is not None:
          break
        i = i + 1
      result = i
      #print(str(i) + " " + str(rating))
    return result

  def check_pretiming_index(self, t, name, pretiming):
    browser = self.browser

    browser.get("https://www.pretiming.com/")

    try:
      element = browser.find_element_by_link_text(pretiming)
    except:
      element = None
    #print (element.text)
    if element is not None:
      #show_element(element)
      url = element.get_attribute("href")
      #print(url)
      self.check_pretiming(url)