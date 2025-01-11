from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

# Standard library imports
import os
import re
from datetime import datetime
from dataclasses import dataclass
from typing import List

# Third-party imports
import pandas as pd
import praw
import pytesseract
import yfinance as yf
import backtrader as bt
from dotenv import load_dotenv

# Local imports
from graph import get_data

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
load_dotenv()

reddit = praw.Reddit(
    client_id=os.getenv("PRAW_CLIENT_ID"),
    client_secret=os.getenv("PRAW_CLIENT_SECRET"),
    username=os.getenv("PRAW_USERNAME"),
    password=os.getenv("PRAW_PASSWORD"),
    user_agent=os.getenv("PRAW_USER_AGENT"),
)

# Spoof headers
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

cerebro = bt.Cerebro()


@dataclass
class SubmissionInfo:
    tickers: List[str]
    position: str


def check_ticker(ticker: str) -> bool:
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        if not info or 'symbol' not in info:
            print(
                f"Error: Ticker {ticker} not found or no market data available.")
            return False
        return True
    except Exception as e:
        print(f"Unexpected error occurred for ticker {ticker}: {e}")
        return False


def extract_data(text, title: bool) -> SubmissionInfo:
    ticker_pattern = r"\b(?!JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC|INC|CAD|USD|FHSA|TFSA|RRSP|RESP|MAX|YOLO|STOP|CLOSE|AND|LOSS|OMG|USA|OPEN|NOT|LTE|BY|ANY|NO|CALL|PUT|EXP|TRADE|MONEY|HELD|CLASS|YTD|POS|CST|BSS|UTC|GMT|PST|EST|CET|BST|IST|MST|JST|AEDT|ACDT|AWST)[A-Z]{2,5}\b"
    ticker_position = r"(?i)\b(call|put|\sC\s|\sP\s)\b"

    tickers = re.findall(ticker_pattern, text)
    position = re.search(ticker_position, text)

    updated_tickers = []
    for ticker in tickers:
        if check_ticker(ticker) and ticker not in updated_tickers:
            updated_tickers.append(ticker)

    if position:
        # Abbreviate all positions to "C" or "P"
        position = position.group()[0]
    elif position is None and title:  # Assume position to call since majority of YOLOs are calls
        position = "C"
    else:
        position = ""
    return SubmissionInfo(tickers=updated_tickers, position=position)


def main():
    # subreddit = reddit.subreddit("wallstreetbets")
    # gain_flair = "YOLO"
    # image_only_counter, has_text = 0, 0
    # json_data = []

    # for submission in subreddit.search(query=f'flair:"{gain_flair}"', sort="new", time_filter="month", limit=10):
    #     image_url = submission.url
    #     submission_data = None
    #     if submission.url.endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp')):
    #         image_only_counter += 1
    #         try:
    #             r = requests.get(image_url, headers=headers)
    #         except requests.exceptions.Timeout:
    #             print("No image found")
    #         if r:
    #             img = Image.open(io.BytesIO(r.content))
    #             text = pytesseract.image_to_string(img)
    #             img.close()
    #             submission_data = extract_data(text, False)
    #     else:
    #         has_text += 1
    #         submission_data = extract_data(submission.title, True)

    #     if submission_data:
    #         for ticker in submission_data.tickers:
    #             entry = {
    #                 "date": datetime.fromtimestamp(submission.created_utc).strftime('%Y-%m-%d'),
    #                 "ticker": ticker,
    #                 "position": submission_data.position
    #             }
    #             json_data.append(entry)
    #     print(f"URL: {submission.url}\n")

    # folder_path = './weekly_data'
    # if not os.path.exists(folder_path):
    #     os.makedirs(folder_path)

    # datafiles = [f for f in os.listdir(folder_path) if os.path.isfile(
    #     os.path.join(folder_path, f))]
    # if len(datafiles) > 20:
    #     oldest_file_path = os.path.join(folder_path, datafiles[0])
    #     os.remove(oldest_file_path)

    # current_date = datetime.today().strftime('%Y-%m-%d')
    # filename = os.path.join(folder_path, f'{current_date}.json')
    # with open(filename, 'w') as file:
    #     json.dump(json_data, file, indent=4)

    # filedata = get_data(current_date)

    # ticker_count = {}

    # for item in json_data:
    #     ticker = item['ticker']
    #     position = item["position"]
    #     if position == '':
    #         continue

    #     key = (ticker, position)
    #     if key in ticker_count:
    #         ticker_count[key] += 1
    #     else:
    #         ticker_count[key] = 1
    # print(ticker_count)
    # top_ticker = max(ticker_count, key=ticker_count.get)
    # print(top_ticker)

    # print("image only: ", image_only_counter)
    # print("has text too: ", has_text)

    ticker_name = 'AAPL'
    position = 'C'
    data = yf.download('AAPL', start='2000-01-01', end='2000-12-31')
    data_feed = bt.feeds.PandasData(dataname=data)

    cerebro.adddata(data_feed)
    cerebro.broker.setcash(100000.0)
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    cerebro.addstrategy(Strategy, stock_ticker=ticker_name, position=position)
    cerebro.run()
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    cerebro.datas.clear()


class Strategy(bt.Strategy):
    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()}, {txt}')

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.entry_price = None
        self.sell_percentage = 0.1
        self.buy_date = None
        self.max_days = 30

    def next(self):
        if self.entry_price is None:
            if not self.position:
                if self.p.position == 'P':
                    self.buy()
                    self.entry_price = self.dataclose[0]
                    self.buy_date = self.datas[0].datetime.date(0)
                    self.log(
                        f'Bought at {self.entry_price :.2f} on {self.buy_date}')
                elif self.p.position == 'C':
                    self.sell()
                    self.entry_price = self.dataclose[0]
                    self.buy_date = self.datas[0].datetime.date(0)
                    self.log(
                        f'Short sold at {self.entry_price :.2f} on {self.buy_date}')
                else:
                    self.log('Invalid position')
        else:
            days_since_buy = (
                self.datas[0].datetime.date(0) - self.buy_date).days
            price_change_up = self.dataclose[0] >= self.entry_price * (
                1 + self.sell_percentage)
            price_change_down = self.dataclose[0] <= self.entry_price * (
                1 + self.sell_percentage)
            if price_change_down or price_change_up or (days_since_buy >= self.max_days):
                if self.p.position == 'P':
                    self.sell()
                    self.log(
                        f'Sold at {self.dataclose[0]:.2f} after {days_since_buy} days')
                    self.entry_price = None
                elif self.p.position == 'C':
                    self.buy()
                    self.log(
                        f'Covered Short at {self.dataclose[0]:.2f} after {days_since_buy} days')
                    self.entry_price = None
                    self.entry_date = None


if __name__ == "__main__":
    # schedule.every().week.do(main)  # Schedule weekly task
    # while True:
    #     schedule.run_pending()  # Run scheduled tasks and check every second
    #     time.sleep(1)
    main()
