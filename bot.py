import os
import time
from threading import Thread

# লাইব্রেরিগুলো ইমপোর্ট করার চেষ্টা করা হচ্ছে
try:
    from flask import Flask
    import yfinance as yf
    import pandas as pd
    import requests
except ImportError:
    print("❌ Error: Modules are missing! Make sure requirements.txt is correct.")

# --- ১. ওয়েব সার্ভার সেটআপ (Render-এর জন্য) ---
app = Flask(__name__)

@app.route('/')
def home():
    return "<h1>Quotex VIP Bot is Online!</h1><p>Monitoring USD/BDT and Forex Market...</p>"

def run_flask():
    # Render সাধারণত পোর্ট ১০০০০ বা এনভায়রনমেন্ট পোর্ট ব্যবহার করে
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- ২. কনফিগারেশন (এখানে আপনার তথ্য দিন) ---
BOT_TOKEN = "8659871069:AAEgPh6pwmLjB8nfrG1aBOLqsfsaGCUu3Kc"
CHAT_ID = "@vipsignalsbd03" # আপনার চ্যানেলের ইউজারনেম (যেমন: @my_trading_signals)
AFFILIATE_LINK = "broker-qx.pro/sign-up/?lid=2022003" # আপনার কোটাক্স লিঙ্ক

# এসেট লিস্ট (USD/BDT সহ অন্যান্য গুরুত্বপূর্ণ পেয়ার)
SYMBOLS = ['BDT=X', 'EURUSD=X', 'GBPUSD=X', 'BTC-USD']

# --- ৩. টেলিগ্রাম মেসেজ ফাংশন ---
def send_telegram_msg(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    try:
        response = requests.post(url, data=payload, timeout=10)
        print(f"✅ Telegram Sent: {response.status_code}")
    except Exception as e:
        print(f"❌ Telegram Error: {e}")

# --- ৪. RSI ইন্ডিকেটর ক্যালকুলেশন ---
def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# --- ৫. মেইন বোট লজিক (সিগন্যাল জেনারেটর) ---
def bot_loop():
    print("🚀 Starting Market Scan for Signals...")
    while True:
        for symbol in SYMBOLS:
            try:
                # ৫ মিনিটের ইন্টারভ্যালে ডাটা নেওয়া (USD/BDT এর জন্য ভালো)
                data = yf.download(tickers=symbol, period='1d', interval='5m', progress=False)
                
                if not data.empty and len(data) >= 20:
                    data['RSI'] = calculate_rsi(data['Close'])
                    
                    last_price = round(float(data['Close'].iloc[-1]), 2 if 'BDT' in symbol else 5)
                    last_rsi = round(float(data['RSI'].iloc[-1]), 2)
                    
                    print(f"🔍 Checking {symbol}: Price {last_price} | RSI {last_rsi}")

                    # সিগন্যাল কন্ডিশন (RSI ৩০ এর নিচে মানে CALL, ৭০ এর উপরে মানে PUT)
                    if last_rsi < 40:
                        msg = (
                            f"🟢 **QUOTEX CALL (UP) SIGNAL**\n"
                            f"━━━━━━━━━━━━━━━\n"
                            f"📊 **ASSET:** {symbol.replace('=X', '')}\n"
                            f"🚀 **DIRECTION:** CALL ⬆️\n"
                            f"💰 **PRICE:** {last_price}\n"
                            f"📉 **RSI LEVEL:** {last_rsi}\n"
                            f"⏰ **TIME:** 5-10 MIN\n"
                            f"⚠️ **1-STEP MARTINGALE OK**\n"
                            f"━━━━━━━━━━━━━━━\n"
                            f"👉 [TRADE ON QUOTEX]({AFFILIATE_LINK})"
                        )
                        send_telegram_msg(msg)
                        time.sleep(300) # একটি সিগন্যাল দিলে ৫ মিনিট বিরতি
                        
                    elif last_rsi > 50:
                        msg = (
                            f"🔴 **QUOTEX PUT (DOWN) SIGNAL**\n"
                            f"━━━━━━━━━━━━━━━\n"
                            f"📊 **ASSET:** {symbol.replace('=X', '')}\n"
                            f"📉 **DIRECTION:** PUT ⬇️\n"
                            f"💰 **PRICE:** {last_price}\n"
                            f"📈 **RSI LEVEL:** {last_rsi}\n"
                            f"⏰ **TIME:** 5-10 MIN\n"
                            f"⚠️ **1-STEP MARTINGALE OK**\n"
                            f"━━━━━━━━━━━━━━━\n"
                            f"👉 [TRADE ON QUOTEX]({AFFILIATE_LINK})"
                        )
                        send_telegram_msg(msg)
                        time.sleep(300)

            except Exception as e:
                print(f"⚠️ Error scanning {symbol}: {e}")
        
        time.sleep(60) # প্রতি ১ মিনিট পর পর সব এসেট পুনরায় চেক করবে

# --- ৬. রানার ---
if __name__ == "__main__":
    # বোটের লুপ আলাদা থ্রেডে চালানো
    t = Thread(target=bot_loop)
    t.daemon = True
    t.start()
    
    # ফ্ল্যাস্ক সার্ভার স্টার্ট করা
    run_flask()
