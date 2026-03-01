import os
import yfinance as yf
import pandas_ta as ta
import requests

# আপনার দেওয়া টোকেন সরাসরি এখানে দেওয়া হলো
BOT_TOKEN = "8659871069:AAEgPh6pwmLjB8nfrG1aBOLqsfsaGCUu3Kc"
CHAT_ID = os.getenv('CHAT_ID') 
SYMBOL = 'EURUSD=X'

def send_msg(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
    requests.post(url, data=payload)

# মার্কেট ডাটা এনালাইসিস
data = yf.download(tickers=SYMBOL, period='1d', interval='15m')
data['RSI'] = ta.rsi(data['Close'], length=14)
last_rsi = data['RSI'].iloc[-1]

affiliate_link = "broker-qx.pro/sign-up/?lid=2022003" # <--- এখানে আপনার লিঙ্ক দিন

if last_rsi < 30:
    msg = f"🟢 **BUY SIGNAL (CALL)**\n\n📊 Asset: {SYMBOL}\n📉 RSI: {round(last_rsi, 2)}\n⏰ Time: 15 min\n\n👉 [ট্রেড শুরু করুন]({affiliate_link})"
    send_msg(msg)
elif last_rsi > 70:
    msg = f"🔴 **SELL SIGNAL (PUT)**\n\n📊 Asset: {SYMBOL}\n📈 RSI: {round(last_rsi, 2)}\n⏰ Time: 15 min\n\n👉 [ট্রেড শুরু করুন]({affiliate_link})"
    send_msg(msg)
else:
    print("No strong signal right now.")
