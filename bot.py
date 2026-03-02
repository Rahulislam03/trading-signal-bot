import os
import yfinance as yf
import pandas as pd
import requests
import time
from threading import Thread
from flask import Flask
from datetime import datetime

# Render-এর জন্য ছোট ওয়েব সার্ভার
app = Flask('')
@app.route('/')
def home():
    return "Trading Bot is Alive!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

# --- কনফিগারেশন ---
BOT_TOKEN = "8659871069:AAEgPh6pwmLjB8nfrG1aBOLqsfsaGCUu3Kc"
CHAT_ID = "@vipsignalsbd03" # আপনার চ্যানেলের নাম দিন
SYMBOLS = ['BTC-USD', 'ETH-USD', 'EURUSD=X'] 
AFFILIATE_LINK = "https://your-link.com"

def send_msg(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown", "disable_web_page_preview": True}
    requests.post(url, data=payload)

def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def bot_loop():
    print("🚀 Monitoring started...")
    while True:
        for symbol in SYMBOLS:
            try:
                data = yf.download(tickers=symbol, period='1d', interval='5m', progress=False)
                if not data.empty and len(data) >= 20:
                    data['RSI'] = calculate_rsi(data['Close'])
                    last_rsi = round(data['RSI'].iloc[-1], 2)
                    last_price = round(data['Close'].iloc[-1], 2)
                    
                    if last_rsi < 30:
                        msg = f"🟢 **BUY SIGNAL**\n━━━━━━━━━━━━━━\n📊 **ASSET:** {symbol}\n🚀 **DIRECTION:** CALL (UP)\n💰 **PRICE:** {last_price}\n📉 **RSI:** {last_rsi}\n\n👉 [TRADE NOW]({AFFILIATE_LINK})"
                        send_msg(msg)
                    elif last_rsi > 70:
                        msg = f"🔴 **SELL SIGNAL**\n━━━━━━━━━━━━━━\n📊 **ASSET:** {symbol}\n📉 **DIRECTION:** PUT (DOWN)\n💰 **PRICE:** {last_price}\n📈 **RSI:** {last_rsi}\n\n👉 [TRADE NOW]({AFFILIATE_LINK})"
                        send_msg(msg)
            except Exception as e:
                print(f"Error: {e}")
        
        time.sleep(300) # ঠিক ৫ মিনিট পর পর চেক করবে

if __name__ == "__main__":
    # বোট এবং ওয়েব সার্ভার একসাথে চালু করা
    Thread(target=bot_loop).start()
    run_flask()
