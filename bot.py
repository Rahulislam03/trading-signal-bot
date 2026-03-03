import os
import time
import requests
from flask import Flask
from threading import Thread
from tradingview_ta import TA_Handler, Interval

app = Flask(__name__)

@app.route('/')
def home():
    return "<h1>VIP Bot: Real Market Analysis Live</h1>"

# --- ১. কনফিগারেশন ---
BOT_TOKEN = "8659871069:AAEgPh6pwmLjB8nfrG1aBOLqsfsaGCUu3Kc"
CHAT_ID = "@vipsignalsbd03"
AFFILIATE_LINK = "https://broker-qx.pro/sign-up/?lid=2022003"

# রিয়েল মার্কেট এসেট লিস্ট (এগুলো Quotex এর Real চার্টের সাথে মিলবে)
SYMBOLS = ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD', 'GBPCHF']

# --- ২. টেলিগ্রাম ফাংশন ---
def send_msg(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown", "disable_web_page_preview": True}
    try:
        requests.post(url, data=payload, timeout=10)
    except:
        pass

# --- ৩. TradingView অ্যানালাইসিস (৫ মিনিট টাইমফ্রেম) ---
def get_analysis(symbol):
    try:
        handler = TA_Handler(
            symbol=symbol,
            exchange="FX_IDC", 
            screener="forex",
            interval=Interval.INTERVAL_5_MINUTES, # আপনার চার্টের ৫ মিনিটের সাথে মিলবে
            timeout=10
        )
        return handler.get_analysis().summary['RECOMMENDATION']
    except:
        return None

# --- ৪. মেইন লুপ ---
def bot_loop():
    send_msg("📡 **Real Market Scanner Active!**\nচ্যানেলে এখন থেকে শুধুমাত্র Real Assets (Non-OTC) সিগন্যাল আসবে।\n**Timeframe:** 5 Minutes")
    
    while True:
        for symbol in SYMBOLS:
            rec = get_analysis(symbol)
            
            if rec and ("STRONG" in rec): # শুধুমাত্র স্ট্রং সিগন্যাল পাঠাবে
                direction = "CALL ⬆️" if "BUY" in rec else "PUT ⬇️"
                emoji = "🟢" if "BUY" in rec else "🔴"
                
                msg = (
                    f"{emoji} **VIP {direction} SIGNAL**\n"
                    f"━━━━━━━━━━━━━━━\n"
                    f"📊 **ASSET:** {symbol} (Real)\n"
                    f"⏰ **TIMEFRAME:** 5 MIN\n"
                    f"⚡ **STRATEGY:** TradingView AI\n"
                    f"🎯 **RECO:** {rec}\n"
                    f"━━━━━━━━━━━━━━━\n"
                    f"👉 [TRADE ON REAL CHART]({AFFILIATE_LINK})"
                )
                send_msg(msg)
                time.sleep(300) # একটি পেয়ারে সিগন্যাল দিলে ৫ মিনিট বিরতি

        time.sleep(60)

if __name__ == "__main__":
    t = Thread(target=bot_loop)
    t.daemon = True
    t.start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
