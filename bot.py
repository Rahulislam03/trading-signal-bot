import os
import yfinance as yf
import pandas as pd
import requests
import time
from threading import Thread
from flask import Flask
from datetime import datetime

# --- ১. Render Web Server (To keep bot alive) ---
app = Flask('')

@app.route('/')
def home():
    return "Quotex Precision Bot is Live!"

def run_flask():
    # Render uses 'PORT' environment variable
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- ২. কনফিগারেশন (এখানে আপনার তথ্য দিন) ---
BOT_TOKEN = "8659871069:AAEgPh6pwmLjB8nfrG1aBOLqsfsaGCUu3Kc"
CHAT_ID = "@vipsignalsbd03"  # অবশ্যই @ সহ দিন
AFFILIATE_LINK = "broker-qx.pro/sign-up/?lid=2022003" # আপনার কোটাক্স লিঙ্ক

# রিয়েল এসেট লিস্ট (Quotex এর সাথে মিলবে)
SYMBOLS = [
    'EURUSD=X', 'GBPUSD=X', 'USDJPY=X', 'AUDUSD=X', 
    'USDCAD=X', 'EURJPY=X', 'BTC-USD', 'ETH-USD', 'SOL-USD'
]

# --- ৩. টেলিগ্রাম ফাংশন ---
def send_msg(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID, 
        "text": text, 
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Error sending message: {e}")

# --- ৪. RSI ক্যালকুলেশন ---
def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# --- ৫. মেইন বোট লজিক ---
def bot_loop():
    print("🚀 Monitoring Market for Quotex Signals...")
    while True:
        for symbol in SYMBOLS:
            try:
                # ১ মিনিটের ইন্টারভাল ডাটা ফেচিং
                data = yf.download(tickers=symbol, period='1d', interval='1m', progress=False)
                
                if not data.empty and len(data) >= 20:
                    data['RSI'] = calculate_rsi(data['Close'])
                    
                    # ডাটা ফরম্যাটিং (Clean Price & RSI)
                    last_price = round(float(data['Close'].iloc[-1]), 5)
                    last_rsi = round(float(data['RSI'].iloc[-1]), 2)
                    
                    # সিগন্যাল কন্ডিশন (৩০/৭০ লেভেল)
                    # BUY SIGNAL
                    if last_rsi < 30:
                        msg = (
                            f"🟢 **QUOTEX CALL (UP) SIGNAL** 🟢\n"
                            f"━━━━━━━━━━━━━━━━━━━━\n"
                            f"📊 **ASSET:** {symbol}\n"
                            f"🚀 **DIRECTION:** CALL (UP) ⬆️\n"
                            f"💰 **PRICE:** {last_price}\n"
                            f"📉 **RSI LEVEL:** {last_rsi}\n"
                            f"⏰ **EXPIRY:** 5 MIN\n"
                            f"⚠️ **USE 1-STEP MARTINGALE**\n"
                            f"━━━━━━━━━━━━━━━━━━━━\n"
                            f"👉 [START TRADING NOW]({AFFILIATE_LINK})"
                        )
                        send_msg(msg)
                        print(f"✅ Signal Sent: {symbol} - BUY")
                        time.sleep(300) # একটি এসেটে সিগন্যাল দিলে ৫ মিনিট বিরতি
                    
                    # SELL SIGNAL
                    elif last_rsi > 70:
                        msg = (
                            f"🔴 **QUOTEX PUT (DOWN) SIGNAL** 🔴\n"
                            f"━━━━━━━━━━━━━━━━━━━━\n"
                            f"📊 **ASSET:** {symbol}\n"
                            f"📉 **DIRECTION:** PUT (DOWN) ⬇️\n"
                            f"💰 **PRICE:** {last_price}\n"
                            f"📈 **RSI LEVEL:** {last_rsi}\n"
                            f"⏰ **EXPIRY:** 5 MIN\n"
                            f"⚠️ **USE 1-STEP MARTINGALE**\n"
                            f"━━━━━━━━━━━━━━━━━━━━\n"
                            f"👉 [START TRADING NOW]({AFFILIATE_LINK})"
                        )
                        send_msg(msg)
                        print(f"✅ Signal Sent: {symbol} - SELL")
                        time.sleep(300) # একটি এসেটে সিগন্যাল দিলে ৫ মিনিট বিরতি

            except Exception as e:
                print(f"Error on {symbol}: {e}")
        
        # প্রতি ৩০ সেকেন্ড পর পর সব এসেট চেক করবে
        time.sleep(30)

# --- ৬. রানার ---
if __name__ == "__main__":
    # আলাদা থ্রেডে বোট চালানো
    t = Thread(target=bot_loop)
    t.daemon = True
    t.start()
    
    # মেইন থ্রেডে ফ্ল্যাস্ক সার্ভার চালানো
    run_flask()
