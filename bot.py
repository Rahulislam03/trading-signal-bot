import os
import yfinance as yf
import pandas as pd
import requests
import time
from threading import Thread
from flask import Flask

# --- ১. Render Web Server ---
app = Flask('')

@app.route('/')
def home():
    return "USD/BDT Signal Bot is Online!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- ২. কনফিগারেশন ---
BOT_TOKEN = "8659871069:AAEgPh6pwmLjB8nfrG1aBOLqsfsaGCUu3Kc"
CHAT_ID = "@vipsignalsbd03" 
AFFILIATE_LINK = "broker-qx.pro/sign-up/?lid=2022003"

# শুধু USD/BDT এর সিম্বল (Yahoo Finance-এ এটি 'BDT=X')
SYMBOL = 'BDT=X'

# --- ৩. টেলিগ্রাম ফাংশন ---
def send_msg(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
    try:
        requests.post(url, data=payload, timeout=10)
    except Exception as e:
        print(f"Error: {e}")

# --- ৪. RSI ক্যালকুলেশন ---
def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# --- ৫. মেইন বোট লজিক ---
def bot_loop():
    print(f"🚀 Monitoring {SYMBOL} for Signals...")
    while True:
        try:
            # USD/BDT এর জন্য ৫ মিনিটের ডাটা বেশি নির্ভুল হয়
            data = yf.download(tickers=SYMBOL, period='2d', interval='5m', progress=False)
            
            if not data.empty and len(data) >= 20:
                data['RSI'] = calculate_rsi(data['Close'])
                
                last_price = round(float(data['Close'].iloc[-1]), 2)
                last_rsi = round(float(data['RSI'].iloc[-1]), 2)
                
                print(f"Update: {SYMBOL} Price: {last_price} | RSI: {last_rsi}")

                # সিগন্যাল কন্ডিশন (৩০/৭০ লেভেল)
                if last_rsi < 40:
                    msg = (
                        f"🟢 **USD/BDT CALL (UP)**\n"
                        f"━━━━━━━━━━━━━━━\n"
                        f"📊 **ASSET:** USD/BDT\n"
                        f"🚀 **DIRECTION:** CALL ⬆️\n"
                        f"💰 **PRICE:** {last_price} BDT\n"
                        f"📉 **RSI:** {last_rsi}\n"
                        f"⏰ **EXPIRY:** 5-15 MIN\n"
                        f"━━━━━━━━━━━━━━━\n"
                        f"👉 [TRADE ON QUOTEX]({AFFILIATE_LINK})"
                    )
                    send_msg(msg)
                    time.sleep(900) # ১৫ মিনিট বিরতি
                    
                elif last_rsi > 50:
                    msg = (
                        f"🔴 **USD/BDT PUT (DOWN)**\n"
                        f"━━━━━━━━━━━━━━━\n"
                        f"📊 **ASSET:** USD/BDT\n"
                        f"📉 **DIRECTION:** PUT ⬇️\n"
                        f"💰 **PRICE:** {last_price} BDT\n"
                        f"📈 **RSI:** {last_rsi}\n"
                        f"⏰ **EXPIRY:** 5-15 MIN\n"
                        f"━━━━━━━━━━━━━━━\n"
                        f"👉 [TRADE ON QUOTEX]({AFFILIATE_LINK})"
                    )
                    send_msg(msg)
                    time.sleep(900)

        except Exception as e:
            print(f"Market Error: {e}")
        
        time.sleep(60) # প্রতি ১ মিনিটে চেক করবে

if __name__ == "__main__":
    t = Thread(target=bot_loop)
    t.daemon = True
    t.start()
    run_flask()
