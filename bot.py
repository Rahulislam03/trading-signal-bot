import os
import time
import requests
from flask import Flask
from threading import Thread
from tradingview_ta import TA_Handler, Interval

app = Flask(__name__)

# --- ১. কনফিগারেশন ---
BOT_TOKEN = "8659871069:AAEgPh6pwmLjB8nfrG1aBOLqsfsaGCUu3Kc"
CHAT_ID = "@vipsignalsbd03"
AFFILIATE_LINK = "https://broker-qx.pro/sign-up/?lid=2022003"

# এসেট লিস্ট
SYMBOLS = [
    'EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD', 
    'EURJPY', 'GBPJPY', 'NZDUSD', 'EURGBP'
]

def send_msg(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown", "disable_web_page_preview": True}
    try:
        requests.post(url, data=payload, timeout=10)
    except:
        pass

# --- ২. ডাটা অ্যানালাইসিস ---
def get_signal(symbol):
    try:
        handler = TA_Handler(
            symbol=symbol,
            exchange="FX_IDC",
            screener="forex",
            interval=Interval.INTERVAL_1_MINUTE, 
            timeout=5
        )
        analysis = handler.get_analysis().summary['RECOMMENDATION']
        return analysis
    except:
        return None

# --- ৩. মেইন লুপ (প্রতি ক্যান্ডেলে সিগন্যাল দেওয়ার জন্য) ---
def bot_loop():
    send_msg("🔥 **Every Candle Signal Mode: ON**\nএখন প্রতিটি ক্যান্ডেলের মুভমেন্ট অনুযায়ী সিগন্যাল আসবে।")
    
    while True:
        for symbol in SYMBOLS:
            rec = get_signal(symbol)
            
            # শর্ত আরও শিথিল করা হয়েছে (BUY/SELL/STRONG যেকোনো একটা হলেই সিগন্যাল যাবে)
            if rec and ("BUY" in rec or "SELL" in rec):
                direction = "CALL ⬆️" if "BUY" in rec else "PUT ⬇️"
                emoji = "🟢" if "BUY" in rec else "🔴"
                
                msg = (
                    f"{emoji} **QUOTEX LIVE**\n"
                    f"━━━━━━━━━━━━━━━\n"
                    f"📊 **ASSET:** {symbol}\n"
                    f"🚀 **DIRECTION:** {direction}\n"
                    f"⏰ **EXPIRY:** 1 MIN\n"
                    f"🔥 **STATUS:** {rec}\n"
                    f"━━━━━━━━━━━━━━━\n"
                    f"👉 [TRADE NOW]({AFFILIATE_LINK})"
                )
                send_msg(msg)
                # মেসেজ পাঠানোর পর খুব সামান্য বিরতি (০.৫ সেকেন্ড) যাতে টেলিগ্রাম ব্লক না করে
                time.sleep(0.5) 

        # এক রাউন্ড শেষ করে মাত্র ৫ সেকেন্ড অপেক্ষা করবে পরবর্তী স্ক্যানের জন্য
        time.sleep(5)

@app.route('/')
def home():
    return "Every Candle Bot is Active"

if __name__ == "__main__":
    t = Thread(target=bot_loop)
    t.daemon = True
    t.start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
