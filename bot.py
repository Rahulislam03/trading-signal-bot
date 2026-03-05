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

# এসেট লিস্ট বাড়ানো হয়েছে যাতে সিগন্যাল বেশি আসে
SYMBOLS = [
    'EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD', 
    'EURJPY', 'GBPJPY', 'NZDUSD', 'EURGBP', 'AUDJPY'
]

def send_msg(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown", "disable_web_page_preview": True}
    try:
        requests.post(url, data=payload, timeout=10)
    except:
        pass

# --- ২. ডাটা অ্যানালাইসিস (১ মিনিট টাইমফ্রেম) ---
def get_signal(symbol):
    try:
        handler = TA_Handler(
            symbol=symbol,
            exchange="FX_IDC",
            screener="forex",
            interval=Interval.INTERVAL_1_MINUTE, 
            timeout=10
        )
        # এখানে summary থেকে সরাসরি রিকমেন্ডেশন নেওয়া হচ্ছে
        analysis = handler.get_analysis().summary['RECOMMENDATION']
        return analysis
    except:
        return None

# --- ৩. মেইন লুপ ---
def bot_loop():
    send_msg("🔥 **Fast Signal Mode Activated!**\nএখন থেকে ঘনঘন সিগন্যাল পাঠানো হবে। প্রস্তুত থাকুন!")
    
    # লাস্ট সিগন্যাল ট্র্যাক করার জন্য ডিকশনারি (যাতে একই পেয়ারে বারবার মেসেজ না যায়)
    last_sent = {symbol: "" for symbol in SYMBOLS}

    while True:
        for symbol in SYMBOLS:
            rec = get_signal(symbol)
            
            # শর্ত শিথিল করা হয়েছে: BUY বা SELL থাকলেই সিগন্যাল যাবে
            if rec and ("BUY" in rec or "SELL" in rec):
                
                # একই সিগন্যাল বারবার পাঠানো বন্ধ করতে চেক
                if last_sent[symbol] != rec:
                    direction = "CALL ⬆️" if "BUY" in rec else "PUT ⬇️"
                    emoji = "🟢" if "BUY" in rec else "🔴"
                    
                    msg = (
                        f"{emoji} **QUOTEX SIGNAL**\n"
                        f"━━━━━━━━━━━━━━━\n"
                        f"📊 **ASSET:** {symbol}\n"
                        f"🚀 **DIRECTION:** {direction}\n"
                        f"⏰ **EXPIRY:** 1 MIN\n"
                        f"⚡ **STRENGTH:** {rec}\n"
                        f"━━━━━━━━━━━━━━━\n"
                        f"👉 [TRADE NOW]({AFFILIATE_LINK})"
                    )
                    send_msg(msg)
                    last_sent[symbol] = rec
                    time.sleep(2) # মেসেজের মাঝে গ্যাপ

        # চেক করার বিরতি কমিয়ে ১০ সেকেন্ড করা হয়েছে
        time.sleep(10)

@app.route('/')
def home():
    return "High Frequency Bot is Running"

if __name__ == "__main__":
    t = Thread(target=bot_loop)
    t.daemon = True
    t.start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
