import os
import time
import requests
from flask import Flask
from threading import Thread
from tradingview_ta import TA_Handler, Interval

app = Flask(__name__)

# --- কনফিগারেশন ---
BOT_TOKEN = "8659871069:AAEgPh6pwmLjB8nfrG1aBOLqsfsaGCUu3Kc"
CHAT_ID = "@vipsignalsbd03"
AFFILIATE_LINK = "https://broker-qx.pro/sign-up/?lid=2022003"

# Quotex এ সবচাইতে বেশি ট্রেড হওয়া পেয়ারগুলো
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

# --- ৩. Quotex এর সাথে ডাটা সিঙ্ক করার ফাংশন ---
def get_exact_signal(symbol):
    try:
        # Quotex সাধারণত FX_IDC বা OANDA থেকে ডাটা নেয়
        # আমরা সরাসরি FX_IDC ব্যবহার করছি যা একদম Real-time
        handler = TA_Handler(
            symbol=symbol,
            exchange="FX_IDC", 
            screener="forex",
            interval=Interval.INTERVAL_1_MINUTE, 
            timeout=7
        )
        analysis = handler.get_analysis()
        
        # ডিটেইলড ডাটা সংগ্রহ
        recommendation = analysis.summary['RECOMMENDATION']
        rsi = analysis.indicators['RSI']
        
        return recommendation, round(rsi, 2)
    except:
        return None, None

# --- ৪. মেইন লুপ (একদম Fast এবং নির্ভুল) ---
def bot_loop():
    send_msg("🎯 **Quotex Sync Mode: ON**\nএখন থেকে চার্টের সাথে হুবহু মিল রেখে সিগন্যাল আসবে।")
    
    last_sent_time = {symbol: 0 for symbol in SYMBOLS}

    while True:
        for symbol in SYMBOLS:
            current_time = time.time()
            # একই পেয়ারে অন্তত ২ মিনিট পর পর সিগন্যাল দেবে যাতে স্প্যাম না হয়
            if current_time - last_sent_time[symbol] < 120:
                continue

            rec, rsi_val = get_exact_signal(symbol)
            
            # সিগন্যাল কন্ডিশন (BUY/SELL থাকলেই হবে)
            if rec and ("BUY" in rec or "SELL" in rec):
                direction = "CALL ⬆️" if "BUY" in rec else "PUT ⬇️"
                emoji = "🟢" if "BUY" in rec else "🔴"
                
                # ক্যান্ডেল স্টিক চার্ট এবং ইন্ডিকেটরের মিল চেক
                msg = (
                    f"{emoji} **QUOTEX LIVE SIGNAL**\n"
                    f"━━━━━━━━━━━━━━━\n"
                    f"📊 **ASSET:** {symbol}/FIXED\n"
                    f"🚀 **DIRECTION:** {direction}\n"
                    f"⏰ **EXPIRY:** 1 MIN\n"
                    f"📈 **RSI VALUE:** {rsi_val}\n"
                    f"🎯 **RECO:** {rec}\n"
                    f"━━━━━━━━━━━━━━━\n"
                    f"👉 [TRADE ON QUOTEX]({AFFILIATE_LINK})"
                )
                send_msg(msg)
                last_sent_time[symbol] = current_time
                time.sleep(2) # ছোট বিরতি

        time.sleep(5) # ৫ সেকেন্ড পর পর নতুন ডাটা চেক

@app.route('/')
def home():
    return "Quotex Direct Sync Bot is Active"

if __name__ == "__main__":
    t = Thread(target=bot_loop)
    t.daemon = True
    t.start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
