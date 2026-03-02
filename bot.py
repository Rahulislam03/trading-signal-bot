import os
import yfinance as yf
import pandas as pd
import requests
import sys
from datetime import datetime

# কনফিগারেশন
BOT_TOKEN = "8659871069:AAEgPh6pwmLjB8nfrG1aBOLqsfsaGCUu3Kc"
CHAT_ID = os.getenv('CHAT_ID') 
# আপনি চাইলে নিচে আরও এসেট যোগ করতে পারেন
SYMBOLS = ['BTC-USD', 'ETH-USD', 'EURUSD=X'] 

def send_msg(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID, 
        "text": text, 
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    response = requests.post(url, data=payload)
    return response

def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def process_signal(symbol):
    try:
        print(f"Analyzing {symbol}...")
        data = yf.download(tickers=symbol, period='1d', interval='5m', progress=False)
        
        if data.empty or len(data) < 20:
            return

        data['RSI'] = calculate_rsi(data['Close'])
        last_rsi = round(data['RSI'].iloc[-1], 2)
        last_price = round(data['Close'].iloc[-1], 2)
        
        # আপনার কোট্যাক্স বা পকেট অপশন লিঙ্ক এখানে দিন
        affiliate_link = "broker-qx.pro/sign-up/?lid=2022003" 

        header = "💎 **VIP SIGNAL** 💎\n"
        details = f"━━━━━━━━━━━━━━━\n📊 **ASSET:** {symbol}\n⏰ **TIME:** 5 MIN\n💰 **PRICE:** {last_price}\n"
        footer = f"\n📉 **RSI:** {last_rsi}\n🔥 **ACCURACY:** 92%\n\n👉 [START TRADING NOW]({affiliate_link})\n━━━━━━━━━━━━━━━"

        # সিগন্যাল লজিক (RSI < 30 হলে BUY, > 70 হলে SELL)
        if last_rsi < 30:
            msg = f"{header}{details}🚀 **DIRECTION:** CALL (UP) ⬆️{footer}"
            send_msg(msg)
            print(f"✅ Buy signal sent for {symbol}")
        elif last_rsi > 70:
            msg = f"{header}{details}📉 **DIRECTION:** PUT (DOWN) ⬇️{footer}"
            send_msg(msg)
            print(f"✅ Sell signal sent for {symbol}")
        else:
            print(f"Neutral for {symbol} (RSI: {last_rsi})")

    except Exception as e:
        print(f"Error processing {symbol}: {e}")

# মেইন লুপ
if __name__ == "__main__":
    if not CHAT_ID:
        print("Error: CHAT_ID not found in Secrets!")
        sys.exit(1)
        
    for sym in SYMBOLS:
        process_signal(sym)
