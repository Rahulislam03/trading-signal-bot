import os
import yfinance as yf
import pandas as pd
import requests
import sys

# আপনার টোকেন
BOT_TOKEN = "8659871069:AAEgPh6pwmLjB8nfrG1aBOLqsfsaGCUu3Kc"
CHAT_ID = os.getenv('CHAT_ID') 
SYMBOL = 'BTC-USD' 

def send_msg(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
    requests.post(url, data=payload)

# লাইব্রেরি ছাড়া RSI বের করার ফাংশন
def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

try:
    print(f"Fetching data for {SYMBOL}...")
    data = yf.download(tickers=SYMBOL, period='2d', interval='15m', progress=False)
    
    if data.empty or len(data) < 20:
        print("⚠️ Data short. Waiting...")
        sys.exit(0)

    # RSI ক্যালকুলেশন (ম্যানুয়ালি)
    data['RSI'] = calculate_rsi(data['Close'])
    last_rsi = data['RSI'].iloc[-1]
    
    affiliate_link = "broker-qx.pro/sign-up/?lid=2022003" 

    print(f"📊 Current RSI: {round(last_rsi, 2)}")

    if last_rsi < 30:
        msg = f"🟢 **BUY SIGNAL**\nAsset: {SYMBOL}\nRSI: {round(last_rsi, 2)}\n👉 [ট্রেড করুন]({affiliate_link})"
        send_msg(msg)
    elif last_rsi > 70:
        msg = f"🔴 **SELL SIGNAL**\nAsset: {SYMBOL}\nRSI: {round(last_rsi, 2)}\n👉 [ট্রেড করুন]({affiliate_link})"
        send_msg(msg)
    else:
        print("Market Neutral.")

except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
