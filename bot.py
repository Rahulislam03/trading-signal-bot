import os
import time
import requests
import yfinance as yf
import pandas as pd
from flask import Flask
from threading import Thread

# --- ১. ওয়েব সার্ভার (Render-কে সচল রাখার জন্য) ---
app = Flask(__name__)

@app.route('/')
def home():
    return "<h1>Quotex VIP Bot is Active!</h1><p>Monitoring Market for @vipsignalsbd03...</p>"

# --- ২. আপনার কনফিগারেশন ---
BOT_TOKEN = "8659871069:AAEgPh6pwmLjB8nfrG1aBOLqsfsaGCUu3Kc"
CHAT_ID = "@vipsignalsbd03"  # আপনার চ্যানেলের ইউজারনেম সেট করা হয়েছে
AFFILIATE_LINK = "https://broker-qx.pro/sign-up/?lid=2022003" # আপনার কোটাক্স লিঙ্ক

# এসেট লিস্ট
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
        print(f"✅ Telegram Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Telegram Error: {e}")

# --- ৪. RSI ক্যালকুলেশন ---
def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# --- ৫. মেইন ট্রেডিং লুপ ---
def bot_loop():
    print("🚀 Monitoring Market...")
    # বোট চালু হওয়ার সাথে সাথে কনফার্মেশন মেসেজ
    send_telegram_msg("🔔 **বোট সফলভাবে চালু হয়েছে!**\nএখন USD/BDT এবং অন্যান্য পেয়ার স্ক্যান করা হচ্ছে।")
    
    while True:
        for symbol in SYMBOLS:
            try:
                # ডাটা ফেচ করা
                data = yf.download(tickers=symbol, period='1d', interval='5m', progress=False)
                
                if not data.empty and len(data) >= 15:
                    data['RSI'] = calculate_rsi(data['Close'])
                    last_price = round(float(data['Close'].iloc[-1]), 4)
                    last_rsi = round(float(data['RSI'].iloc[-1]), 2)
                    
                    # এসেট নাম সুন্দর করা
                    asset_display = "USD/BDT" if symbol == 'BDT=X' else symbol.replace('=X', '')

                    # সিগন্যাল কন্ডিশন
                    if last_rsi < 30: 
                        msg = (
                            f"🟢 **QUOTEX CALL (UP) SIGNAL**\n"
                            f"━━━━━━━━━━━━━━━\n"
                            f"📊 **ASSET:** {asset_display}\n"
                            f"🚀 **DIRECTION:** CALL ⬆️\n"
                            f"💰 **PRICE:** {last_price}\n"
                            f"⏰ **TIME:** 5 MIN\n"
                            f"━━━━━━━━━━━━━━━\n"
                            f"👉 [REGISTER ON QUOTEX]({AFFILIATE_LINK})"
                        )
                        send_telegram_msg(msg)
                        time.sleep(300) 
                        
                    elif last_rsi > 70: 
                        msg = (
                            f"🔴 **QUOTEX PUT (DOWN) SIGNAL**\n"
                            f"━━━━━━━━━━━━━━━\n"
                            f"📊 **ASSET:** {asset_display}\n"
                            f"📉 **DIRECTION:** PUT ⬇️\n"
                            f"💰 **PRICE:** {last_price}\n"
                            f"⏰ **TIME:** 5 MIN\n"
                            f"━━━━━━━━━━━━━━━\n"
                            f"👉 [REGISTER ON QUOTEX]({AFFILIATE_LINK})"
                        )
                        send_telegram_msg(msg)
                        time.sleep(300)

            except Exception as e:
                print(f"⚠️ Error with {symbol}: {e}")
        
        time.sleep(60)

# --- ৬. রানার ---
if __name__ == "__main__":
    t = Thread(target=bot_loop)
    t.daemon = True
    t.start()
    
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
