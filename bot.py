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

# এসেট লিস্ট (এগুলো রিয়েল মার্কেটে হুবহু মিলবে)
SYMBOLS = ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD']

def send_msg(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown", "disable_web_page_preview": True}
    try: requests.post(url, data=payload, timeout=10)
    except: pass

# --- ২. ডাটা অ্যানালাইসিস ---
def get_signal(symbol):
    try:
        handler = TA_Handler(
            symbol=symbol,
            exchange="FX_IDC", # এটি রিয়েল চার্টের জন্য সবচাইতে নির্ভুল
            screener="forex",
            interval=Interval.INTERVAL_1_MINUTE, # ১ মিনিটের ক্যান্ডেল
            timeout=10
        )
        analysis = handler.get_analysis().summary['RECOMMENDATION']
        return analysis
    except:
        return None

# --- ৩. মেইন লুপ ---
def bot_loop():
    send_msg("🔥 **VIP Bot is Online!**\nDirect Sync with Live Market Charts.")
    
    while True:
        for symbol in SYMBOLS:
            rec = get_signal(symbol)
            if rec and "STRONG" in rec:
                direction = "CALL ⬆️" if "BUY" in rec else "PUT ⬇️"
                emoji = "🟢" if "BUY" in rec else "🔴"
                
                msg = (
                    f"{emoji} **QUOTEX LIVE SIGNAL**\n"
                    f"━━━━━━━━━━━━━━━\n"
                    f"📊 **ASSET:** {symbol}\n"
                    f"🚀 **DIRECTION:** {direction}\n"
                    f"⏰ **EXPIRY:** 1-2 MIN\n"
                    f"🎯 **CONFIDENCE:** High\n"
                    f"━━━━━━━━━━━━━━━\n"
                    f"👉 [TRADE NOW ON QUOTEX]({AFFILIATE_LINK})"
                )
                send_msg(msg)
                time.sleep(60) # ১ মিনিট বিরতি

        time.sleep(30) # প্রতি ৩০ সেকেন্ডে নতুন সিগন্যাল খুঁজবে

@app.route('/')
def home(): return "Bot is Running"

if __name__ == "__main__":
    t = Thread(target=bot_loop)
    t.daemon = True
    t.start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
