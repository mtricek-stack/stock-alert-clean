import requests
import yfinance as yf

# Discord Webhook URL
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1416784239919235152/_4pHEPgqs8Jx3DbFEvFkbU_90cbyIQd0E8Elvypk5scV8asMUSYgkPRP4fPeeQ8W5jkb"

# 監視する銘柄リスト
SYMBOLS = [
    "NVDA","ISRG","TEM","SOUN","PLTR","IONQ",
    "QBTS","QUBT","RGTI","BBAI","LAES","PDYN",
    "OPTX","RKLB","CRCL"
]

# 下落通知する割合（%）
DROP_PERCENT = 10

def send_discord_message(message):
    data = {"content": message}
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=data)
        response.raise_for_status()
    except Exception as e:
        print(f"Failed to send Discord message: {e}")

def get_price(symbol):
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period="1mo")  # 直近1か月のデータ
        if hist.empty:
            return None, None
        recent_high = hist["High"].max()
        current_price = hist["Close"][-1]
        return current_price, recent_high
    except Exception as e:
        print(f"Failed to fetch price for {symbol}: {e}")
        return None, None

def main():
    print("Stock alert bot running!")
    for symbol in SYMBOLS:
        current_price, recent_high = get_price(symbol)
        if current_price is None or recent_high is None:
            print(f"No data for {symbol}")
            continue
        drop_rate = (recent_high - current_price) / recent_high * 100
        if drop_rate >= DROP_PERCENT:
            send_discord_message(
                f"🚨 {symbol} dropped {drop_rate:.2f}% from recent high!\n"
                f"Current: {current_price:.2f}, High: {recent_high:.2f}"
            )
        else:
            print(f"{symbol}: No alert. Drop {drop_rate:.2f}%")

if __name__ == "__main__":
    main()



