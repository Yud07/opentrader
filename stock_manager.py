import requests
from bs4 import BeautifulSoup
import datetime
import yaml
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import time

class StockManager:
  RANKS  = ["Error", "Great", "Good", "Neutral", "Bad" , "Terrible"]
  HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    
  
  def __init__(self, file_path):
    self.file_path = file_path
    self.browser = self.initialize_firefox()
    self.dictionary = self.load_portfolio()
    #print (dictionary.items())

  # setup headless firefox
  def initialize_firefox(self):
    opts = Options()
    opts.add_argument("--headless")
    return Firefox(options=opts)

  # load yaml portfolio
  def load_portfolio(self):
    stream = stream = open(self.file_path)
    return yaml.load(stream, Loader=yaml.CLoader)

  def run_battery(self):
    browser = self.browser
    dictionary = self.dictionary

    self.check_premarket()
    print("---------------------------")
    for t, content in dictionary.items():
      exchange = content['exchange']
      print(t + " " + str(self.check_marketwatch_price(t)) + "\t" + self.check_marketwatch_daily_change(t))

      tradingview_result = -1
      try:
        tradingview_exchange = content['tradingview_exchange']
        tradingview_result = self.check_tradingview_with_retry(t, tradingview_exchange)
      except:
        tradingview_result = self.check_tradingview_with_retry(t, exchange)

      #print("tradingViewResult: " + str(tradingview_result))
      print("TradingView has " + t + "\t" + self.RANKS[1 + tradingview_result])

      try:
        t = content['alternate_ticker']
        exchange = content['alternate_exchange']
      except:
        None

      self.check_marketbeat_analysts(t, exchange)
      self.check_pretiming_by_ticker(t)
      print("Zacks thinks " + t + " is\t" + self.RANKS[self.check_zacks(t)])
      

      print()

  def close_browser(self):
    self.browser.close()

  def check_zacks(self, ticker):
    zacks_url = "https://www.zacks.com/stock/quote/" + ticker
    html_text = requests.get(zacks_url, headers=self.HEADERS).text
    soup = BeautifulSoup(html_text, 'html.parser')

    result = "0"
    ranks = [1, 2, 3, 4, 5]
    for r in ranks:
      span = soup.find("span", {"class":"rank_chip rankrect_" + str(r)})
      if span is None:
        break
      #print(span)
      rank = str(span).split(">")[1][:1]
      #print(rank)
      if ord(rank) != 160: # 160 is the blank character code
        result = rank
        break

    return int(result)

  def check_marketbeat_analysts(self, ticker, exchange):
    # OTC -> OTCMKTS
    marketbeat_analysts_url = "http://www.marketbeat.com/stocks/" + exchange + "/" + ticker + "/price-target/"
    html_text = requests.get(marketbeat_analysts_url, headers=self.HEADERS).text
    soup = BeautifulSoup(html_text, 'html.parser')

    result = 0.0
    ranks = [1, 2, 3, 4]
    #<div class="scroll-table-wrapper"
    # <div id="cphPrimaryContent_tabAnalystRatings" class="tab-pane active"
    div = soup.find("div", {"id":"cphPrimaryContent_tabAnalystRatings", "class":"tab-pane active"})
    #print(div)

    # (0-1.5 = Sell, 1.5-2.5 = Hold, 2.5-3.5 = Buy, >3.5 = Strong Buy)

    i = 0
    if div is not None:
      rating_string = "Error"
      rating_val_string = "Error"
      num_ratings = "Error"
      for l in div:
        if i == 6:
          tds = l.find_all("td")
          j = 0
          rating_string = "Error"
          rating_val_string = "Error"
          num_rating_string = "Error"
          price_target_string = "Error"
          upside_string = "Error"
          num_tds = len(tds)
          if num_tds == 25:
            for td in tds:
              td_string = str(td)[4:-5]
              if j == 1:
                rating_string = td_string
              elif j == 6:
                rating_val_string = td_string
                #print("Rating val string: " + rating_val_string)
                result = float(rating_val_string)
              elif j == 11:
                num_rating_string = td_string
                num_sell_ratings = num_rating_string[0]
                num_rating_string_split = num_rating_string.split("<br/>")
                num_hold_ratings = num_rating_string_split[1][0]
                num_buy_ratings = num_rating_string_split[2][0]
                num_strong_buy_ratings = num_rating_string_split[3][0]
                #print(num_rating_string)
                #print(num_sell_ratings)
                #print(num_hold_ratings)
                #print(num_buy_ratings)
                #print(num_strong_buy_ratings)
                num_ratings = int(num_sell_ratings) + int(num_hold_ratings) + int(num_buy_ratings) + int(num_strong_buy_ratings)
              elif j == 16:
                price_target_string = td_string
              elif j == 21:
                upside_string = td_string
              #print(td_string)
              j = j + 1
        i = i + 1

      print(ticker + " has a rating of\t" + rating_string + " from " + str(num_ratings) + " ratings. Target: " + price_target_string + " " + upside_string)

    return result

  #def check_tradingview(ticker, exchange):
  #  if exchange == "OTC":
  #    if ticker == "GBTC" or ticker == "ETHE":
  #      check_tradingview(ticker)
  #  else:
  #    check_tradingview_large_caps(ticker, exchange)

  def check_tradingview_large_caps(self, ticker, exchange):
    url = "https://www.tradingview.com/markets/stocks-usa/market-movers-large-cap/"
    html_text = requests.get(url, headers=self.HEADERS).text
    soup = BeautifulSoup(html_text, 'html.parser')

    result = -1
    row = soup.find("tr", {"class":"tv-data-table__row tv-data-table__stroke tv-screener-table__result-row", "data-symbol":exchange + ":" + ticker})
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

  def check_tradingview_with_retry(self, ticker, exchange):
    tradingview_result = -1
    i = 0
    while (tradingview_result == -1 or tradingview_result == 0) and i < 2:
      tradingview_result = self.check_tradingview(ticker, exchange)
      if tradingview_result == -1 or tradingview_result == 0:
        time.sleep(5 * i)
      i = i + 1
    return tradingview_result


  def check_tradingview(self, ticker, exchange):
    browser = self.browser

    browser.get("https://www.tradingview.com/symbols/" + exchange + "-" + ticker + "/technicals/")
    #browser.save_screenshot("screenshot.png")
    #img = mpimg.imread("screenshot.png")
    #imgplot = plt.imshow(img)
    #plt.show()
    time.sleep(2)
    #name = "tv-content-header"
    name = "speedometersContainer-DPgs-R4s"
    #name = "speedometerSignal-DPgs-R4s buyColor-DPgs-R4s"
    result = -1
    try:
      element = browser.find_element_by_class_name(name)
    except:
      #print("Couldn't find element")
      return result

    if element is not None:
      text = element.text
      #location = element.location
      #size = element.size

      #print(text)

      split_text = text.split("\n")

      ranks = ["STRONG BUY", "BUY", "NEUTRAL", "SELL", "STRONG SELL"]

      oscillators = split_text[6]
      summary = split_text[19]
      #print("summary: " + summary)
      moving_averages = split_text[32]

      i = 0
      #print("summary: " + str(summary))
      for r in ranks:
        #print("i: " + str(i))
        if r == summary:
          result = i
        i = i + 1

    #print("result: " + str(result))
    return result

  def show_element(self, element):
    element.screenshot("element.png")
    img = mpimg.imread("element.png")
    imgplot = plt.imshow(img)
    plt.show()

  def check_marketwatch_price(self, ticker):
    url = "https://www.marketwatch.com/investing/stock/" + ticker
    html_text = requests.get(url, headers=self.HEADERS).text
    soup = BeautifulSoup(html_text, 'html.parser')
    #print(soup)

    result = -1
    header = soup.find("h3", {"class":"intraday__price"})
    quote = header.find("bg-quote")
    split_quote = str(quote).split(">")
    if len(split_quote) > 1:
      price = split_quote[1].split("<")[0]
      #print(price)
      return float(price.replace(",", ""))
    else:
      return -1

  def check_marketwatch_daily_change(self, ticker):
    url = "https://www.marketwatch.com/investing/stock/" + ticker
    html_text = requests.get(url, headers=self.HEADERS).text
    soup = BeautifulSoup(html_text, 'html.parser')
    #print(soup)

    result = -1
    span = soup.find("span", {"class":"change--percent--q"})
    percent_string = str(span).split(">")[2].split("<")[0]
    #print(percent_string)

    return percent_string

  def check_pretiming_by_ticker(self, ticker):
    url = "https://www.pretiming.com/search?q=" + ticker
    self.check_pretiming(url)

  def check_pretiming(self, url):
    html_text = requests.get(url, headers=self.HEADERS).text
    soup = BeautifulSoup(html_text, 'html.parser')

    post = soup.find("div", {"class":"post-body entry-content"})
    if post is not None:
      post_string = str(post)
      if post_string.find("10 days") > 0:
        date_loc_index = post_string.find("2021")
        substring = post_string[date_loc_index - 20:date_loc_index + 4]
        split = substring.split(">")
        # old posts had only 1 body
        #print("post len: " + str(len(split)))
        if len(split) > 1:
          date_string = split[1]
          post_date = datetime.datetime.strptime(date_string, "%b %d, %Y").date()
          date_delta = datetime.datetime.today().date() - post_date
          # if the post is 3 days old or less
          if(date_delta > datetime.timedelta(3)):
            print("Pretiming is old: " + str(date_delta))
          if(date_delta <= datetime.timedelta(5)):
            summary_index = post_string.find("Suitable")
            summary_blob = post_string[summary_index: summary_index + 2500]
            summary = summary_blob.split(">")[8].split(";")[1].split("<")[0][1:]
            change_index = post_string.find("% Change:")
            substring = post_string[change_index:change_index + 2500]
            #print(substring)
            lower_band_change = substring.split(">")[6].split("<")[0]
            upper_band_change = substring.split(">")[18].split("<")[0]
            print("Pretiming predicts\t" + summary + " " + lower_band_change + " to " + upper_band_change + " over 10 days")
        else:
          #print("Pretiming post seems old style")
          return
      else:
        print("Pretiming seems not 10 day span")

  def check_premarket(self):
    browser = self.browser

    browser.get("https://www.cnn.com/business/markets/premarkets")
    element = browser.find_element_by_id("featured-ribbon-markets-section")

    split = element.text.split("\n")
    dow = split[5]
    print("DOW " + dow)

    sp = split[9]
    print("SP500 " + sp)

    nasdaq = split[13]
    print("NASDAQ " + nasdaq)
    print()

    element = browser.find_element_by_name("anchor-futures")
    #print(element.text)
    split = element.text.split("\n")

    dow_futures = split[2]
    decimal_index = dow_futures.find(".")
    dow_futures = dow_futures[decimal_index + 3:]
    print("DOW Futures " + dow_futures)

    sp_futures = split[10]
    decimal_index = sp_futures.find(".")
    sp_futures = sp_futures[decimal_index + 3:]
    print("SP500 Futures " + sp_futures)

    nasdaq_futures = split[18]
    decimal_index = nasdaq_futures.find(".")
    nasdaq_futures = nasdaq_futures[decimal_index + 3:]
    print("NASDAQ Futures " + nasdaq_futures)
    print()

