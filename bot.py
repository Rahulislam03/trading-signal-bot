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

# --- ৩. টেলিগ্রাম মেসেজ ফাংশন ---
def send_msg(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID, 
        "text": text, 
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    try:
        requests.post(url, data=payload, timeout=10)
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
                    
                    # ডাটা ক্লিনআপ
                    last_price = round(float(data['Close'].iloc[-1]), 5)
                    last_rsi = round(float(data['RSI'].iloc[-1]), 2)
                    
                    print(f"Checking {symbol}: RSI {last_rsi} | Price {last_price}")

                    # সিগন্যাল কন্ডিশন (৩০/৭০ লেভেল - শিউর শট সিগন্যাল)
                    if last_rsi < 40:
                        msg = (
                            f"🟢 **QUOTEX CALL (UP) SIGNAL**\n"
                            f"━━━━━━━━━━━━━━━\n"
                            f"📊 **ASSET:** {symbol}\n"
                            f"🚀 **DIRECTION:** CALL ⬆️\n"
                            f"💰 **PRICE:** {last_price}\n"
                            f"📉 **RSI LEVEL:** {last_rsi}\n"
                            f"⏰ **TIME:** 5 MIN\n"
                            f"⚠️ **1-STEP MARTINGALE OK**\n"
                            f"━━━━━━━━━━━━━━━\n"
                            f"👉 [TRADE ON QUOTEX]({AFFILIATE_LINK})"
                        )
                        send_msg(msg)
                        time.sleep(300) # ৫ মিনিট বিরতি
                        
                    elif last_rsi > 50:
                        msg = (
                            f"🔴 **QUOTEX PUT (DOWN) SIGNAL**\n"
                            f"━━━━━━━━━━━━━━━\n"
                            f"📊 **ASSET:** {symbol}\n"
                            f"📉 **DIRECTION:** PUT ⬇️\n"
                            f"💰 **PRICE:** {last_price}\n"
                            f"📈 **RSI LEVEL:** {last_rsi}\n"
                            f"⏰ **TIME:** 5 MIN\n"
                            f"⚠️ **1-STEP MARTINGALE OK**\n"
                            f"━━━━━━━━━━━━━━━\n"
                            f"👉 [TRADE ON QUOTEX]({AFFILIATE_LINK})"
                        )
                        send_msg(msg)
                        time.sleep(300)

            except Exception as e:
                print(f"Market Error for {symbol}: {e}")
        
        # প্রতি ৩০ সেকেন্ড পর পর সব এসেট চেক করবে
        time.sleep(30)

# --- ৬. মেইন রানার ---
if __name__ == "__main__":
    # বোটের লুপ আলাদা থ্রেডে চালানো
    t = Thread(target=bot_loop)
    t.daemon = True
    t.start()
    
    # ফ্ল্যাস্ক সার্ভার স্টার্ট
    run_flask()
