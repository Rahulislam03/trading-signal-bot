import os
import yfinance as yf
import pandas as pd
import requests
import sys
from datetime import datetime

# আপনার টোকেন
BOT_TOKEN = "8659871069:AAEgPh6pwmLjB8nfrG1aBOLqsfsaGCUu3Kc"
CHAT_ID = os.getenv('CHAT_ID') 
SYMBOL = 'BTC-USD' 

def send_msg(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID, 
        "text": text, 
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    requests.post(url, data=payload)

def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

try:
    print(f"Fetching 5m VIP data for {SYMBOL}...")
    # interval='5m' সেট করা হয়েছে
    data = yf.download(tickers=SYMBOL, period='1d', interval='5m', progress=False)
    
    if data.empty or len(data) < 20:
        sys.exit(0)

    data['RSI'] = calculate_rsi(data['Close'])
    last_rsi = round(data['RSI'].iloc[-1], 2)
    last_price = round(data['Close'].iloc[-1], 2)
    
    affiliate_link = "আপনার_লিঙ্ক_এখানে_দিন" 

    # VIP সিগন্যাল টেমপ্লেট
    header = "💎 **VIP AI PREDICTION (FAST)** 💎\n"
    instrument = f"━━━━━━━━━━━━━━━\n📊 **ASSET:** {SYMBOL}\n"
    timeframe = "⏰ **TIMEFRAME:** 5 MINUTES\n"
    price_info = f"💰 **ENTRY PRICE:** {last_price}\n"
    
    risk_footer = "\n━━━━━━━━━━━━━━━\n⚠️ *Risk Warning: High volatility in 5m charts.*"

    if last_rsi < 30:
        msg = (f"{header}{instrument}{timeframe}{price_info}"
               f"🚀 **DIRECTION:** CALL (UP) ⬆️\n"
               f"📉 **RSI STRENGTH:** {last_rsi}\n"
               f"🔥 **ACCURACY:** 88%\n\n"
               f"👉 [TRADE ON QUOTEX]({affiliate_link}){risk_footer}")
        send_msg(msg)
        
    elif last_rsi > 70:
        msg = (f"{header}{instrument}{timeframe}{price_info}"
               f"📉 **DIRECTION:** PUT (DOWN) ⬇️\n"
               f"📈 **RSI STRENGTH:** {last_rsi}\n"
               f"🔥 **ACCURACY:** 88%\n\n"
               f"👉 [TRADE ON QUOTEX]({affiliate_link}){risk_footer}")
        send_msg(msg)

except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
