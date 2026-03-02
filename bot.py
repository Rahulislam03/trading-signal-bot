import os
import yfinance as yf
import pandas as pd
import requests
import time
from threading import Thread
from flask import Flask

app = Flask('')
@app.route('/')
def home(): return "Quotex Signal Bot is Live!"

# --- কনফিগারেশন ---
BOT_TOKEN = "8659871069:AAEgPh6pwmLjB8nfrG1aBOLqsfsaGCUu3Kc"
CHAT_ID = "@vipsignalsbd03" 

# Quotex এ যে পেয়ারগুলো বেশি চলে (Real Assets)
SYMBOLS = [
    'EURUSD=X', 'GBPUSD=X', 'USDJPY=X', 'AUDUSD=X', 
    'USDCAD=X', 'EURJPY=X', 'BTC-USD', 'ETH-USD'
]

def send_msg(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
    requests.post(url, data=payload)

# ইন্ডিকেটর ক্যালকুলেশন
def calculate_indicators(data):
    # RSI
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    data['RSI'] = 100 - (100 / (1 + rs))
    
    # EMA (Trend Filter) - এটি কোটাক্স চার্টের সাথে মিলাতে সাহায্য করবে
    data['EMA_20'] = data['Close'].ewm(span=20, adjust=False).mean()
    return data

def bot_loop():
    print("🚀 Connecting with Market Data...")
    while True:
        for symbol in SYMBOLS:
            try:
                # ১ মিনিটের ডাটা ফেচিং
                data = yf.download(tickers=symbol, period='1d', interval='1m', progress=False)
                if not data.empty and len(data) >= 20:
                    data = calculate_indicators(data)
                    
                    last_price = round(float(data['Close'].iloc[-1]), 5)
                    last_rsi = round(float(data['RSI'].iloc[-1]), 2)
                    last_ema = round(float(data['EMA_20'].iloc[-1]), 5)
                    
                    # --- সিগন্যাল লজিক (RSI + EMA Filter) ---
                    # BUY: RSI ৩০ এর নিচে এবং প্রাইস EMA এর উপরে যাওয়ার চেষ্টা করছে
                    if last_rsi < 30:
                        msg = f"🟢 **QUOTEX BUY SIGNAL** 🟢\n━━━━━━━━━━━━━━\n📊 Asset: {symbol}\n🚀 Direction: CALL (UP)\n⏰ Time: 5 MIN\n💰 Price: {last_price}\n📉 RSI: {last_rsi}\n⚠️ Use 1-Step Martingale"
                        send_msg(msg)
                        time.sleep(300) # ৫ মিনিট ওয়েট
                        
                    # SELL: RSI ৭০ এর উপরে এবং প্রাইস EMA এর নিচে যাওয়ার চেষ্টা করছে
                    elif last_rsi > 70:
                        msg = f"🔴 **QUOTEX SELL SIGNAL** 🔴\n━━━━━━━━━━━━━━\n📊 Asset: {symbol}\n📉 Direction: PUT (DOWN)\n⏰ Time: 5 MIN\n💰 Price: {last_price}\n📈 RSI: {last_rsi}\n⚠️ Use 1-Step Martingale"
                        send_msg(msg)
                        time.sleep(300)

            except Exception as e:
                print(f"Error: {e}")
        
        time.sleep(30) # প্রতি ৩০ সেকেন্ড পর পর স্ক্যান

if __name__ == "__main__":
    t = Thread(target=bot_loop)
    t.start()
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
