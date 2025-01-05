# WallStreetBets Inverse Trader

A trading bot that analyzes posts on r/wallstreetbets and simulates inverse trading strategies.

## Features
- Analyzes Reddit posts by flair.
- Backtests trading strategies using `backtrader`.
- Fetches financial data using `yfinance`.

## Prerequisites
- Python 3.9+
- Reddit API credentials (see below).

## **Setup Instructions**

To fetch posts from Reddit, you need to set up Reddit API credentials. Follow these steps:

1. **Log in to your Reddit account** and go to the [App Preferences](https://www.reddit.com/prefs/apps) page.

2. **Create a new app**:
   - Click the **"Create App"** or **"Create Another App"** button.
   - Select **"script"** as the app type.


### **1. Clone the Repository**
Run the following command to clone the repository to your local machine:
```bash
git clone https://github.com/YourUsername/wsb-inverse-trader.git
cd wsb-inverse-trader
```
### **2. Setup venv and dependencies**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```
### **3. Setup credentials**

Copy .env.example to .env and fill in your Reddit API credentials.

### **4. Run script**

python main.py

