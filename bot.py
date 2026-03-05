import os
import time
import requests
from flask import Flask
from threading import Thread
from quotexapi.stable_api import Quotex

app = Flask(__name__)

# --- ১. কনফিগারেশন ---
BOT_TOKEN = "8659871069:AAEgPh6pwmLjB8nfrG1aBOLqsfsaGCUu3Kc"
CHAT_ID = "@vipsignalsbd03"
AFFILIATE_LINK = "https://broker-qx.pro/sign-up/?lid=2022003"

# গুরুত্বপূর্ণ: Quotex অ্যাকাউন্টের তথ্য (Render-এর Env Variables-এ সেট করা ভালো)
# যদি সরাসরি দিতে চান তবে এখানে দিন:
EMAIL = "rahulislam124@yahoo.com" 
PASSWORD = "RRahul@2002"

# এসেট লিস্ট (Real এবং OTC উভয়ই কাজ করবে)
SYMBOLS = ['EURUSD', 'USD/BDT_otc', 'GBPUSD', 'USDJPY_otc']

# --- ২. টেলিগ্রাম ফাংশন ---
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
        print(f"Telegram Error: {e}")

# --- ৩. মেইন লজিক ও WebSocket কানেকশন ---
def bot_loop():
    client = Quotex(email=EMAIL, password=PASSWORD)
    check, reason = client.connect()
    
    if not check:
        print(f"❌ Connection Failed: {reason}")
        return

    send_msg("🚀 **Quotex Live WebSocket Active!**\nসরাসরি ব্রোকার সার্ভার থেকে ডাটা সিঙ্ক করা হচ্ছে।\nসহজেই চার্টের সাথে সিগন্যাল মিলবে।")

    while True:
        for asset in SYMBOLS:
            try:
                # ১ মিনিটের ক্যান্ডেল ডাটা সংগ্রহ (বোটের জন্য এটিই সেরা)
                candles = client.get_candles(asset, 60) 
                
                if candles and len(candles) >= 5:
                    last = candles[-1]
                    prev = candles[-2]
                    
                    price = last['close']
                    # একটি সাধারণ RSI-ভিত্তিক বা ক্যান্ডেল প্যাটার্ন লজিক
                    # উদাহরণ: যদি ক্যান্ডেল অনেক বেশি নিচে নেমে যায় (Oversold)
                    
                    # ক্যান্ডেল বডি সাইজ চেক
                    is_red = last['close'] < last['open']
                    is_green = last['close'] > last['open']

                    # --- সিগন্যাল অ্যালগরিদম ---
                    if is_red and (last['open'] - last['close']) > 0.0005: # বড় লাল ক্যান্ডেল
                        msg = (
                            f"🟢 **QUOTEX CALL (UP)**\n"
                            f"━━━━━━━━━━━━━━━\n"
                            f"📊 **ASSET:** {asset}\n"
                            f"🚀 **DIRECTION:** CALL ⬆️\n"
                            f"💰 **PRICE:** {price}\n"
                            f"⏰ **EXPIRY:** 1 MIN\n"
                            f"📊 **TYPE:** WebSocket Live\n"
                            f"━━━━━━━━━━━━━━━\n"
                            f"👉 [TRADE ON QUOTEX]({AFFILIATE_LINK})"
                        )
                        send_msg(msg)
                        time.sleep(60) # একই এসেটে বারবার সিগন্যাল রোধে

                    elif is_green and (last['close'] - last['open']) > 0.0005: # বড় সবুজ ক্যান্ডেল
                        msg = (
                            f"🔴 **QUOTEX PUT (DOWN)**\n"
                            f"━━━━━━━━━━━━━━━\n"
                            f"📊 **ASSET:** {asset}\n"
                            f"📉 **DIRECTION:** PUT ⬇️\n"
                            f"💰 **PRICE:** {price}\n"
                            f"⏰ **EXPIRY:** 1 MIN\n"
                            f"📊 **TYPE:** WebSocket Live\n"
                            f"━━━━━━━━━━━━━━━\n"
                            f"👉 [TRADE ON QUOTEX]({AFFILIATE_LINK})"
                        )
                        send_msg(msg)
                        time.sleep(60)

            except Exception as e:
                print(f"Error on {asset}: {e}")
            
        time.sleep(5) # প্রতি ৫ সেকেন্ড পর পর সব এসেট চেক করবে

# --- ৪. ওয়েব সার্ভার ---
@app.route('/')
def home():
    return "Quotex WebSocket Engine is Running"

if __name__ == "__main__":
    t = Thread(target=bot_loop)
    t.daemon = True
    t.start()
    
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
