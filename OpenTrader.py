import requests
from bs4 import BeautifulSoup
import datetime
import yaml
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

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


# for crypto
# https://s2f.hamal.nl/s2fcharts.html
# lookintobitcoin
# - private tradingview indicator scripts
# - indicator alerts

# https://digitalik.net/btc/


def main():
  print("Open Trader 0.02")

  # load yaml portfolio
  #stream = open("Portfolios\MyPortfolio.yaml", "r")
  stream = open("Portfolios\MegaCaps.yaml", "r")
  dictionary = yaml.load(stream, Loader=yaml.CLoader)
  #print (dictionary.items())

  my_portfolio = ["ETHE", "GBTC", "TSLA", "AMZN", "FB", "GOOGL", "ASML", "NVDA", "NFLX", "MSFT", "BABA", "AAPL", "TCEHY", "AMD", "PLTR"]
  megacaps = ["AAPL", "MSFT", "AMZN", "GOOGL", "FB", "TCEHY", "TSLA", "BABA", "TSM", "V", "JPM", "JNJ", "WMT", "UNH", "LVMUY", "MA", "HD", "NVDA", "BAC", "NSRGY", "DIS", "PG", "PYPL", "RHHBY", "CMCSA", "ASML", "XOM", "VZ", "ADBE", "KO", "MPNGF", "T", "INTC", "ORCL", "PFE", "CSCO", "ABT", "TM", "NKE", "ABBV", "CVX", "PEP", "CRM", "PNGAY", "CICHY", "MRK", "NVS", "WFC", "UPS", "ACN", "BHP"]
  
  #indices = ["DOWJ", "SP500", "NASDAQ", "RUT2000", "STOXX 50 Euro", "DAX Germ", "SP/TSX Can", "NIFTY 50 Ind", "BOVESPA Brazil", "NIKKEI Japan", "Shanghai Ind", "Hong Kong Hang Seng", "KOSPI South Korea"]
  #commodities = ["Gold", "Silver", "Gas", "Copper"]
  #"10 yr"
  #"ETH"

  zacks_ranks = ["Error", "Great", "Good", "Neutral", "Bad" , "Terrible"]

  # setup headless firefox
  opts = Options()
  opts.add_argument("--headless")
  browser = Firefox(options=opts)

  #check_marketbeat_analysts("AMC", "NYSE")
  #check_tradingview_large_caps(tickers)
  #check_marketwatch_price("AMC")
  #check_marketwatch_daily_change("AMC")
  #check_pretiming("PLTR")
  #check_tradingview("PLTR", "NYSE")
  #check_tradingview_sector("GBTC", "miscellaneous")

  #check_tradingview(browser, "ETHE", "OTC")
  #check_tradingview(browser, "PLTR", "NYSE")
  #check_tradingview(browser, "FB", "NASDAQ")

  if True:
    for t, content in dictionary.items():
      exchange = content['exchange']
      print(t + " " + str(check_marketwatch_price(t)) + "\t" + check_marketwatch_daily_change(t))
      tradingview_result = -1
      try:
        tradingview_exchange = content['tradingview_exchange']
        tradingview_result = check_tradingview(browser, t, tradingview_exchange)
      except:
        tradingview_result = check_tradingview(browser, t, exchange)
      print("TradingView has " + t + "\t" + zacks_ranks[1 + tradingview_result])
      check_marketbeat_analysts(t, exchange)
      check_pretiming(t)
      print("Zacks thinks " + t + " is\t" + zacks_ranks[check_zacks(t)])
      print()

  browser.close()

def check_zacks(ticker):
  zacks_url = "https://www.zacks.com/stock/quote/" + ticker
  headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
  html_text = requests.get(zacks_url, headers=headers).text
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

def check_marketbeat_analysts(ticker, exchange):
  # OTC -> OTCMKTS
  marketbeat_analysts_url = "http://www.marketbeat.com/stocks/" + exchange + "/" + ticker + "/price-target/"
  headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
  html_text = requests.get(marketbeat_analysts_url, headers=headers).text
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

def check_tradingview_large_caps(ticker, exchange):
  url = "https://www.tradingview.com/markets/stocks-usa/market-movers-large-cap/"
  headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
  html_text = requests.get(url, headers=headers).text
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

def check_tradingview(browser, ticker, exchange):
  browser.get("https://www.tradingview.com/symbols/" + exchange + "-" + ticker + "/technicals/")
  #browser.save_screenshot("screenshot.png")
  #img = mpimg.imread("screenshot.png")
  #imgplot = plt.imshow(img)
  #plt.show()

  #name = "tv-content-header"
  name = "speedometersContainer-DPgs-R4s"
  #name = "speedometerSignal-DPgs-R4s buyColor-DPgs-R4s"
  try:
    element = browser.find_element_by_class_name(name)
  except:
    return -1
  if element is not None:
    text = element.text
    #location = element.location
    #size = element.size

    #print(text)

    split_text = text.split("\n")

    ranks = ["STRONG BUY", "BUY", "NEUTRAL", "SELL", "STRONG SELL"]

    oscillators = split_text[6]
    summary = split_text[19]
    moving_averages = split_text[32]

    i = 0
    #print("summary: " + str(summary))
    for r in ranks:
      if r == summary:
        break
      i = i + 1

    result = i
  else:
    result = -1
  #print("result: " + str(result))
  return result

    #print("text: " + str(text))
    #print("location: " + str(location))
    #print("size: " + str(size))

    #element.screenshot("element.png")
    #img = mpimg.imread("element.png")
    #imgplot = plt.imshow(img)
    #plt.show()

def check_marketwatch_price(ticker):
  url = "https://www.marketwatch.com/investing/stock/" + ticker
  headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
  html_text = requests.get(url, headers=headers).text
  soup = BeautifulSoup(html_text, 'html.parser')
  #print(soup)

  result = -1
  header = soup.find("h3", {"class":"intraday__price"})
  quote = header.find("bg-quote")
  price = str(quote).split(">")[1].split("<")[0]
  #print(price)
  return(float(price.replace(",", "")))

def check_marketwatch_daily_change(ticker):
  url = "https://www.marketwatch.com/investing/stock/" + ticker
  headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
  html_text = requests.get(url, headers=headers).text
  soup = BeautifulSoup(html_text, 'html.parser')
  #print(soup)

  result = -1
  span = soup.find("span", {"class":"change--percent--q"})
  percent_string = str(span).split(">")[2].split("<")[0]
  #print(percent_string)

  return percent_string

def check_pretiming(ticker):
  url = "https://www.pretiming.com/search?q=" + ticker
  headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
  html_text = requests.get(url, headers=headers).text
  soup = BeautifulSoup(html_text, 'html.parser')

  post = soup.find("div", {"class":"post-body entry-content"})
  if post is not None:
    post_string = str(post)
    if post_string.find("10 days") > 0:
      date_loc_index = post_string.find("2021")
      substring = post_string[date_loc_index - 20:date_loc_index + 4]
      split = substring.split(">")
      # old posts had only 1 body
      if len(split) > 1:
        date_string = split[1]
        post_date = datetime.datetime.strptime(date_string, "%b %d, %Y").date()
        date_delta = datetime.datetime.today().date() - post_date
        # if the post is 3 days old or less
        if(date_delta <= datetime.timedelta(3)):
          summary_index = post_string.find("Suitable")
          summary_blob = post_string[summary_index: summary_index + 2500]
          summary = summary_blob.split(">")[8].split(";")[1].split("<")[0][1:]
          change_index = post_string.find("% Change:")
          substring = post_string[change_index:change_index + 2500]
          #print(substring)
          lower_band_change = substring.split(">")[6].split("<")[0]
          upper_band_change = substring.split(">")[18].split("<")[0]
          print("Pretiming predicts\t" + summary + " " + lower_band_change + " to " + upper_band_change + " over 10 days")

if __name__ == "__main__":
    main()
