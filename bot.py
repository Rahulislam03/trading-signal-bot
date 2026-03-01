import os
import yfinance as yf
import pandas_ta as ta
import requests
import sys

# আপনার দেওয়া টোকেন সরাসরি কোডে দেওয়া হলো
BOT_TOKEN = "8659871069:AAEgPh6pwmLjB8nfrG1aBOLqsfsaGCUu3Kc"
CHAT_ID = os.getenv('CHAT_ID') 
SYMBOL = 'BTC-USD' # ক্রিপ্টো মার্কেট সবসময় খোলা থাকে

def send_msg(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID, 
        "text": text, 
        "parse_mode": "Markdown",
        "disable_web_page_preview": False
    }
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        print("✅ Signal sent to Telegram!")
    else:
        print(f"❌ Telegram Error: {response.text}")

try:
    print(f"Fetching data for {SYMBOL}...")
    data = yf.download(tickers=SYMBOL, period='1d', interval='15m', progress=False)
    
    if data.empty or len(data) < 20:
        print("⚠️ Not enough market data available right now.")
        sys.exit(0)

    # RSI ক্যালকুলেশন
    data['RSI'] = ta.rsi(data['Close'], length=14)
    last_rsi = data['RSI'].iloc[-1]
    
    # আপনার কোট্যাক্স পার্টনার লিঙ্কটি এখানে দিন
    affiliate_link = "broker-qx.pro/sign-up/?lid=2022003" 

    print(f"📊 Current RSI: {round(last_rsi, 2)}")

    # সিগন্যাল লজিক (RSI < 30 হলে বাই, > 70 হলে সেল)
    if last_rsi < 30:
        msg = (f"🟢 **BUY SIGNAL (CALL)**\n\n"
               f"📊 Asset: {SYMBOL}\n"
               f"📉 RSI: {round(last_rsi, 2)}\n"
               f"⏰ Time: 15 min\n\n"
               f"👉 [এখানে ক্লিক করে ট্রেড করুন]({affiliate_link})")
        send_msg(msg)
    elif last_rsi > 70:
        msg = (f"🔴 **SELL SIGNAL (PUT)**\n\n"
               f"📊 Asset: {SYMBOL}\n"
               f"📈 RSI: {round(last_rsi, 2)}\n"
               f"⏰ Time: 15 min\n\n"
               f"👉 [এখানে ক্লিক করে ট্রেড করুন]({affiliate_link})")
        send_msg(msg)
    else:
        print("😴 Market is stable. No signal generated.")

except Exception as e:
    print(f"🚨 Error: {e}")
    sys.exit(1)
