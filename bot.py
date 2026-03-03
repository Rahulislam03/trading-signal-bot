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
    return "<h1>Candle-by-Candle Signal Bot is Active!</h1>"

# --- ১. কনফিগারেশন ---
BOT_TOKEN = "8659871069:AAEgPh6pwmLjB8nfrG1aBOLqsfsaGCUu3Kc"
CHAT_ID = "@vipsignalsbd03"
AFFILIATE_LINK = "https://broker-qx.pro/sign-up/?lid=2022003"

# সিগন্যাল বেশি পেতে এসেট সংখ্যা বাড়ানো হয়েছে
SYMBOLS = [
    'BDT=X', 'EURUSD=X', 'GBPUSD=X', 'USDJPY=X', 
    'AUDUSD=X', 'EURJPY=X', 'GBPJPY=X', 'USDCAD=X'
]

# --- ২. ইন্ডিকেটর ফাংশন ---
def add_indicators(df):
    # RSI (7) - দ্রুত সিগন্যালের জন্য পিরিয়ড কমানো হয়েছে
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=7).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=7).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
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
    send_msg("🔥 **Fast Signal Mode Activated!**\nএখন থেকে প্রতি ক্যান্ডেলের মুভমেন্ট অনুযায়ী সিগন্যাল আসবে।")
    
    while True:
        for symbol in SYMBOLS:
            try:
                # লেটেস্ট ৫ মিনিটের ডাটা
                data = yf.download(tickers=symbol, period='1d', interval='5m', progress=False)
                if not data.empty and len(data) >= 10:
                    data = add_indicators(data)
                    
                    last_candle = data.iloc[-1]
                    prev_candle = data.iloc[-2]
                    
                    price = round(float(last_candle['Close']), 4)
                    rsi = round(float(last_candle['RSI']), 2)
                    
                    asset = "USD/BDT" if symbol == 'BDT=X' else symbol.replace('=X', '')

                    # --- সিগন্যাল লজিক (প্রতি ক্যান্ডেলের জন্য শিথিল শর্ত) ---
                    
                    # ১. কল (UP) সিগন্যাল: যদি RSI ৪০ এর নিচে থাকে অথবা ক্যান্ডেলটি গ্রিন হওয়ার আভাস দেয়
                    if rsi < 45: 
                        msg = (
                            f"🔔 **QUOTEX CALL (UP) ALERT**\n"
                            f"━━━━━━━━━━━━━━━\n"
                            f"📊 **ASSET:** {asset}\n"
                            f"🚀 **DIRECTION:** CALL ⬆️\n"
                            f"💰 **PRICE:** {price}\n"
                            f"📈 **RSI:** {rsi}\n"
                            f"⏰ **EXPIRY:** 1-5 MIN\n"
                            f"━━━━━━━━━━━━━━━\n"
                            f"👉 [TRADE NOW]({AFFILIATE_LINK})"
                        )
                        send_msg(msg)
                        
                    # ২. পুট (DOWN) সিগন্যাল: যদি RSI ৫৫ এর উপরে থাকে
                    elif rsi > 55:
                        msg = (
                            f"🔔 **QUOTEX PUT (DOWN) ALERT**\n"
                            f"━━━━━━━━━━━━━━━\n"
                            f"📊 **ASSET:** {asset}\n"
                            f"📉 **DIRECTION:** PUT ⬇️\n"
                            f"💰 **PRICE:** {price}\n"
                            f"📈 **RSI:** {rsi}\n"
                            f"⏰ **EXPIRY:** 1-5 MIN\n"
                            f"━━━━━━━━━━━━━━━\n"
                            f"👉 [TRADE NOW]({AFFILIATE_LINK})"
                        )
                        send_msg(msg)

            except Exception as e:
                print(f"Error: {e}")
            
            # একটি এসেট চেক করার পর ২ সেকেন্ড গ্যাপ (টেলিগ্রাম স্প্যাম রোধে)
            time.sleep(2)
        
        # সব এসেট একবার চেক হলে ৫ মিনিট অপেক্ষা করবে (নতুন ক্যান্ডেলের জন্য)
        time.sleep(300) 

if __name__ == "__main__":
    t = Thread(target=bot_loop)
    t.daemon = True
    t.start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
