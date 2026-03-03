import os
import time
import requests
import yfinance as yf
import pandas as pd
from flask import Flask
from threading import Thread

app = Flask(__name__)

@app.route('/')
def home():
    return "<h1>VIP Signal Bot with RSI & Bollinger Bands</h1>"

# --- ১. কনফিগারেশন ---
BOT_TOKEN = "8659871069:AAEgPh6pwmLjB8nfrG1aBOLqsfsaGCUu3Kc"
CHAT_ID = "@vipsignalsbd03"
AFFILIATE_LINK = "https://broker-qx.pro/sign-up/?lid=2022003"

SYMBOLS = ['BDT=X', 'EURUSD=X', 'GBPUSD=X', 'USDJPY=X', 'BTC-USD']

# --- ২. টেকনিক্যাল ইন্ডিকেটর ফাংশন ---
def add_indicators(df):
    # RSI (14)
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # Bollinger Bands (20, 2)
    df['MA20'] = df['Close'].rolling(window=20).mean()
    df['STD'] = df['Close'].rolling(window=20).std()
    df['Upper_Band'] = df['MA20'] + (df['STD'] * 2)
    df['Lower_Band'] = df['MA20'] - (df['STD'] * 2)
    return df

# --- ৩. টেলিগ্রাম ফাংশন ---
def send_msg(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown", "disable_web_page_preview": True}
    try:
        requests.post(url, data=payload, timeout=10)
    except:
        pass

# --- ৪. মেইন লজিক ---
def bot_loop():
    send_msg("🚀 **ইন্ডিকেটর আপডেট করা হয়েছে!**\nএখন থেকে RSI + Bollinger Bands এর সমন্বয়ে সিগন্যাল আসবে।")
    
    while True:
        for symbol in SYMBOLS:
            try:
                data = yf.download(tickers=symbol, period='1d', interval='5m', progress=False)
                if not data.empty and len(data) >= 20:
                    data = add_indicators(data)
                    
                    last = data.iloc[-1]
                    price = round(float(last['Close']), 4)
                    rsi = round(float(last['RSI']), 2)
                    upper = float(last['Upper_Band'])
                    lower = float(last['Lower_Band'])
                    
                    asset = "USD/BDT" if symbol == 'BDT=X' else symbol.replace('=X', '')

                    # 🟢 CALL Signal: RSI < 30 AND প্রাইস লোয়ার ব্যান্ড টাচ করেছে
                    if rsi < 30 and price <= lower:
                        msg = (
                            f"🔥 **VIP STRONG CALL (UP)**\n"
                            f"━━━━━━━━━━━━━━━\n"
                            f"📊 **ASSET:** {asset}\n"
                            f"🚀 **DIRECTION:** CALL ⬆️\n"
                            f"💰 **ENTRY:** {price}\n"
                            f"📉 **RSI:** {rsi} | **BB:** Lower\n"
                            f"⏰ **TIME:** 5 MIN\n"
                            f"━━━━━━━━━━━━━━━\n"
                            f"👉 [REGISTER NOW]({AFFILIATE_LINK})"
                        )
                        send_msg(msg)
                        time.sleep(300)

                    # 🔴 PUT Signal: RSI > 70 AND প্রাইস আপার ব্যান্ড টাচ করেছে
                    elif rsi > 70 and price >= upper:
                        msg = (
                            f"🔥 **VIP STRONG PUT (DOWN)**\n"
                            f"━━━━━━━━━━━━━━━\n"
                            f"📊 **ASSET:** {asset}\n"
                            f"📉 **DIRECTION:** PUT ⬇️\n"
                            f"💰 **ENTRY:** {price}\n"
                            f"📈 **RSI:** {rsi} | **BB:** Upper\n"
                            f"⏰ **TIME:** 5 MIN\n"
                            f"━━━━━━━━━━━━━━━\n"
                            f"👉 [REGISTER NOW]({AFFILIATE_LINK})"
                        )
                        send_msg(msg)
                        time.sleep(300)

            except Exception as e:
                print(f"Error: {e}")
        time.sleep(60)

if __name__ == "__main__":
    t = Thread(target=bot_loop)
    t.daemon = True
    t.start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
