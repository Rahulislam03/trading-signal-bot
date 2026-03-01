import os
import yfinance as yf
import pandas_ta as ta
import requests
import sys

# আপনার দেওয়া টোকেন সরাসরি এখানে দেওয়া হয়েছে
BOT_TOKEN = "8659871069:AAEgPh6pwmLjB8nfrG1aBOLqsfsaGCUu3Kc"
CHAT_ID = os.getenv('CHAT_ID') 
SYMBOL = 'BTC-USD' # ক্রিপ্টো সবসময় খোলা থাকে তাই টেস্ট করার জন্য এটি ভালো

def send_msg(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID, 
        "text": text, 
        "parse_mode": "Markdown",
        "disable_web_page_preview": False
    }
    response = requests.post(url, data=payload)
    if response.status_code != 200:
        print(f"Telegram Error: {response.text}")
    else:
        print("Signal sent to Telegram!")

try:
    # ডাটা ডাউনলোড করা হচ্ছে
    data = yf.download(tickers=SYMBOL, period='1d', interval='15m', progress=False)
    
    if len(data) < 20:
        print("Not enough data. Waiting for more candles...")
        sys.exit(0)

    # RSI ক্যালকুলেশন
    data['RSI'] = ta.rsi(data['Close'], length=14)
    last_rsi = data['RSI'].iloc[-1]
    
    # আপনার অ্যাফিলিয়েট লিঙ্ক এখানে দিন
    affiliate_link = "broker-qx.pro/sign-up/?lid=2022003" 

    print(f"Current RSI for {SYMBOL}: {round(last_rsi, 2)}")

    # সিগন্যাল লজিক
    if last_rsi < 30:
        msg = f"🟢 **BUY SIGNAL (CALL)**\n\n📊 Asset: {SYMBOL}\n📉 RSI: {round(last_rsi, 2)}\n⏰ Time: 15 min\n\n👉 [ট্রেড শুরু করুন]({affiliate_link})"
        send_msg(msg)
    elif last_rsi > 70:
        msg = f"🔴 **SELL SIGNAL (PUT)**\n\n📊 Asset: {SYMBOL}\n📈 RSI: {round(last_rsi, 2)}\n⏰ Time: 15 min\n\n👉 [ট্রেড শুরু করুন]({affiliate_link})"
        send_msg(msg)
    else:
        print("Market is neutral. No signal.")

except Exception as e:
    print(f"An Error Occurred: {e}")
    sys.exit(1)
