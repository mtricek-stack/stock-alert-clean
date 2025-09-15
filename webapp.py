import requests
import yfinance as yf
from datetime import datetime
import pytz

# ===== 設定 =====
DISCORD_WEBHOOK_URL = "https://canary.discord.com/api/webhooks/1416784239919235152/_4pHEPgqs8Jx3DbFEvFkbU_90cbyIQd0E8Elvypk5scV8asMUSYgkPRP4fPeeQ8W5jkb"
STOCKS = [
    "NVDA","ISRG","TEM","SOUN","PLTR","IONQ","QBTS","QUBT","RGTI",
    "BBAI","LAES","PDYN","OPTX","RKLB","CRCL"
]
DROP_PERCENT = 20.0  # 20%以上下落で通知

# ===== 米国市場判定 =====
def is_market_open():
    eastern = pytz.timezone('US/Eastern')
    now_et = datetime.now(eastern)
    if now_et.weekday() >= 5:  # 土日
        return False
    market_open = now_et.replace(hour=9, minute=30, second=0, microsecond=0)
    market_close = now_et.replace(hour=16, minute=0, second=0, microsecond=0)
    return market_open <= now_et <= market_close

# ===== Discord通知 =====
def send_discord_message(message):
    data = {"content": message}
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=data)
        response.raise_for_status()
    except Exception as e:
        print("Failed to send message:", e)

# ===== 株価チェック =====
def check_stocks():
    for symbol in STOCKS:
        try:
            data = yf.Ticker(symbol)
            hist = data.history(period="1mo")
            if hist.empty:
                print(f"No data for {symbol}")
                continue
            recent_high = hist['High'].max()
            current_price = hist['Close'][-1]
            drop_rate = (recent_high - current_price) / recent_high * 100

            if drop_rate >= DROP_PERCENT:
                send_discord_message(
                    f"🚨 {symbol} dropped {drop_rate:.2f}% from recent high!\n"
                    f"Current: {current_price:.2f}, High: {recent_high:.2f}"
                )
            else:
                print(f"{symbol}: No alert. Drop {drop_rate:.2f}%")
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")

# ===== メイン =====
if __name__ == "__main__":
    if is_market_open():
        print("Market is open, checking stocks...")
        check_stocks()
    else:
        print("Market closed, skipping.")

