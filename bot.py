import os
import time
from flask import Flask
from threading import Thread
import requests
# লাইব্রেরি ইমপোর্ট করার সময় ট্রাই-ক্যাচ ব্যবহার করছি যাতে এরর হ্যান্ডেল করা যায়
try:
    from quotexapi.stable_api import Quotex
except ImportError:
    Quotex = None

app = Flask(__name__)

# --- কনফিগারেশন ---
BOT_TOKEN = "8659871069:AAEgPh6pwmLjB8nfrG1aBOLqsfsaGCUu3Kc"
CHAT_ID = "@vipsignalsbd03"
EMAIL = "hmia9878@gmail.com"
PASSWORD = "RRahul@2002"

def send_msg(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
    requests.post(url, data=payload)

def bot_loop():
    if Quotex is None:
        print("API Library not found!")
        return

    # Quotex কানেকশন
    client = Quotex(email=EMAIL, password=PASSWORD)
    check, reason = client.connect()
    
    if check:
        send_msg("✅ **Quotex API Connected Successfully!**\nসরাসরি ব্রোকার ডাটা থেকে সিগন্যাল আসছে।")
        
        while True:
            # USD/BDT (OTC) বা অন্য যেকোনো এসেট
            asset = "USD/BDT_otc" 
            candles = client.get_candles(asset, 60) # ১ মিনিটের ডাটা
            
            if candles:
                last = candles[-1]
                # আপনার সিগন্যাল লজিক এখানে (যেমন RSI বা Candle Pattern)
                # ... 
            time.sleep(10)
    else:
        print(f"Connection Error: {reason}")

@app.route('/')
def home():
    return "API Bot is Running"

if __name__ == "__main__":
    t = Thread(target=bot_loop)
    t.daemon = True
    t.start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
