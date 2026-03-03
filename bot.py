import os
import time
import requests
from flask import Flask
from threading import Thread
from tradingview_ta import TA_Handler, Interval, Exchange

app = Flask(__name__)

@app.route('/')
def home():
    return "<h1>TradingView Analysis Bot is Online!</h1>"

# --- ১. কনফিগারেশন ---
BOT_TOKEN = "8659871069:AAEgPh6pwmLjB8nfrG1aBOLqsfsaGCUu3Kc"
CHAT_ID = "@vipsignalsbd03"
AFFILIATE_LINK = "https://broker-qx.pro/sign-up/?lid=2022003"

# TradingView এর জন্য পেয়ার লিস্ট
SYMBOLS = ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'BTCUSD', 'ETHUSD']

# --- ২. টেলিগ্রাম ফাংশন ---
def send_msg(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown", "disable_web_page_preview": True}
    try:
        requests.post(url, data=payload, timeout=10)
    except:
        pass

# --- ৩. TradingView অ্যানালাইসিস লজিক ---
def get_tv_signal(symbol):
    try:
        handler = TA_Handler(
            symbol=symbol,
            exchange="FX_IDC", # ফরেক্সের জন্য IDC এক্সচেঞ্জ সবচেয়ে ভালো
            screener="forex",
            interval=Interval.INTERVAL_5_MINUTES, # ৫ মিনিটের ক্যান্ডেল অ্যানালাইসিস
            timeout=10
        )
        analysis = handler.get_analysis()
        return analysis.summary['RECOMMENDATION']
    except Exception as e:
        print(f"Error fetching TV data for {symbol}: {e}")
        return None

# --- ৪. মেইন বোট লুপ ---
def bot_loop():
    send_msg("🚀 **TradingView Analysis Mode Active!**\nএখন সরাসরি TradingView সার্ভার থেকে সিগন্যাল আসবে।")
    
    while True:
        for symbol in SYMBOLS:
            recommendation = get_tv_signal(symbol)
            print(f"🔍 {symbol}: {recommendation}")

            if recommendation:
                # সিগন্যাল কন্ডিশন
                if "STRONG_BUY" in recommendation or "BUY" in recommendation:
                    msg = (
                        f"🟢 **VIP CALL (UP) SIGNAL**\n"
                        f"━━━━━━━━━━━━━━━\n"
                        f"📊 **ASSET:** {symbol}\n"
                        f"🚀 **DIRECTION:** CALL ⬆️\n"
                        f"⚡ **STRENGTH:** {recommendation}\n"
                        f"⏰ **TIME:** 5 MIN\n"
                        f"━━━━━━━━━━━━━━━\n"
                        f"👉 [TRADE ON QUOTEX]({AFFILIATE_LINK})"
                    )
                    send_msg(msg)
                    time.sleep(10) # স্প্যাম প্রোটেকশন

                elif "STRONG_SELL" in recommendation or "SELL" in recommendation:
                    msg = (
                        f"🔴 **VIP PUT (DOWN) SIGNAL**\n"
                        f"━━━━━━━━━━━━━━━\n"
                        f"📊 **ASSET:** {symbol}\n"
                        f"📉 **DIRECTION:** PUT ⬇️\n"
                        f"⚡ **STRENGTH:** {recommendation}\n"
                        f"⏰ **TIME:** 5 MIN\n"
                        f"━━━━━━━━━━━━━━━\n"
                        f"👉 [TRADE ON QUOTEX]({AFFILIATE_LINK})"
                    )
                    send_msg(msg)
                    time.sleep(10)

        time.sleep(60) # প্রতি ১ মিনিট পর পর সব পেয়ার আবার চেক করবে

if __name__ == "__main__":
    t = Thread(target=bot_loop)
    t.daemon = True
    t.start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
