import os
import yfinance as yf
import pandas as pd
import requests
import time
from threading import Thread
from flask import Flask
from datetime import datetime

app = Flask('')

@app.route('/')
def home():
    return "AI Precision Bot is Online!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- কনফিগারেশন ---
BOT_TOKEN = "8659871069:AAEgPh6pwmLjB8nfrG1aBOLqsfsaGCUu3Kc"
CHAT_ID = "@vipsignalsbd03" 
SYMBOLS = ['BTC-USD', 'ETH-USD', 'EURUSD=X', 'GBPUSD=X', 'AUDUSD=X']
AFFILIATE_LINK = "broker-qx.pro/sign-up/?lid=2022003"

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
    print("🚀 Precision Monitoring Started...")
    while True:
        for symbol in SYMBOLS:
            try:
                # ১ মিনিটের ডাটা নিয়ে ৫ মিনিটের এনালাইসিস (যাতে দেরি না হয়)
                data = yf.download(tickers=symbol, period='1d', interval='1m', progress=False)
                
                if not data.empty and len(data) >= 30:
                    data['RSI'] = calculate_rsi(data['Close'])
                    
                    # ডাটা ক্লিনআপ (Ticker বা Name এরর দূর করার জন্য .item() ব্যবহার)
                    last_price = round(float(data['Close'].iloc[-1]), 5)
                    last_rsi = round(float(data['RSI'].iloc[-1]), 2)
                    
                    # সিগন্যাল লজিক (৩০/৭০ এর বদলে ২৫/৭৫ ব্যবহার করছি আরও শিউর শট সিগন্যালের জন্য)
                    if last_rsi < 25: # Oversold - High probability Buy
                        direction = "CALL (UP) ⬆️"
                        msg = f"💎 **VIP WINNING SIGNAL** 💎\n━━━━━━━━━━━━━━━\n📊 **ASSET:** {symbol}\n🚀 **DIRECTION:** {direction}\n💰 **PRICE:** {last_price}\n📉 **RSI:** {last_rsi}\n⏰ **EXPIRY:** 5 MIN\n\n👉 [TRADE ON QUOTEX]({AFFILIATE_LINK})\n━━━━━━━━━━━━━━━"
                        send_msg(msg)
                        time.sleep(300) # একটি সিগন্যাল দিলে ৫ মিনিট বিরতি (ডাবল মেসেজ এড়াতে)
                        
                    elif last_rsi > 75: # Overbought - High probability Sell
                        direction = "PUT (DOWN) ⬇️"
                        msg = f"💎 **VIP WINNING SIGNAL** 💎\n━━━━━━━━━━━━━━━\n📊 **ASSET:** {symbol}\n📉 **DIRECTION:** {direction}\n💰 **PRICE:** {last_price}\n📈 **RSI:** {last_rsi}\n⏰ **EXPIRY:** 5 MIN\n\n👉 [TRADE ON QUOTEX]({AFFILIATE_LINK})\n━━━━━━━━━━━━━━━"
                        send_msg(msg)
                        time.sleep(300)

            except Exception as e:
                print(f"Error on {symbol}: {e}")
        
        time.sleep(30) # প্রতি ৩০ সেকেন্ড পর পর মার্কেট চেক করবে

if __name__ == "__main__":
    t = Thread(target=bot_loop)
    t.start()
    run_flask()
