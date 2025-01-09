import io
import re
import os
import json
import requests

from dotenv import load_dotenv
from datetime import datetime
from dataclasses import dataclass
from typing import List
from graph import get_data
from PIL import Image
import backtrader as bt
import praw
import yfinance as yf
import pytesseract
# import schedule
# import  time

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

# cerebro = bt.Cerebro()


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
        position = position.group()[0] # Abbreviate all positions to "C" or "P"
    elif position is None and title:  # Assume position to call since majority of YOLOs are calls
        position = "C"
    else:
        position = ""
    return SubmissionInfo(tickers=updated_tickers, position=position)


def main():
    subreddit = reddit.subreddit("wallstreetbets")
    gain_flair = "YOLO"
    image_only_counter, has_text = 0, 0
    json_data = []

    for submission in subreddit.search(query=f'flair:"{gain_flair}"', sort="new", time_filter="month", limit=50):
        image_url = submission.url
        submission_data = None
        if submission.url.endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp')):
            image_only_counter += 1
            try:
                r = requests.get(image_url, headers=headers)
            except requests.exceptions.Timeout:
                print("No image found")
            if r:
                img = Image.open(io.BytesIO(r.content))
                text = pytesseract.image_to_string(img)
                img.close()
                submission_data = extract_data(text, False)
        else:
            has_text += 1
            submission_data = extract_data(submission.title, True)

        if submission_data:
            for ticker in submission_data.tickers:
                entry = {
                    "date": datetime.fromtimestamp(submission.created_utc).strftime('%Y-%m-%d'),
                    "ticker": ticker,
                    "position": submission_data.position
                }
                json_data.append(entry)
        print(f"URL: {submission.url}\n")

    folder_path = './weekly_data'
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    datafiles = [f for f in os.listdir(folder_path) if os.path.isfile(
        os.path.join(folder_path, f))]
    if len(datafiles) > 20:
        oldest_file_path = os.path.join(folder_path, datafiles[0])
        os.remove(oldest_file_path)

    current_date = datetime.today().strftime('%Y-%m-%d')
    filename = os.path.join(folder_path, f'{current_date}.json')
    with open(filename, 'w') as file:
        json.dump(json_data, file, indent=4)
    
    filedata = get_data(current_date)
    
    ticker_count = {}

    for item in json_data:
        ticker = item['ticker']
        position = item["position"]
        if position == '':
            continue

        key = (ticker, position)
        if key in ticker_count:
            ticker_count[key] += 1
        else:
            ticker_count[key] = 1
    print(ticker_count)
    print(max(ticker_count, key=ticker_count.get))
    
    print("image only: ", image_only_counter)
    print("has text too: ", has_text)


if __name__ == "__main__":
    # schedule.every().week.do(main)  # Schedule weekly task
    # while True:
    #     schedule.run_pending()  # Run scheduled tasks and check every second
    #     time.sleep(1)
    main()
