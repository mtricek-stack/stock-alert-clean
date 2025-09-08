import yfinance as yf
import requests
import time

# ----------------- 設定 -----------------
TICKER = "AAPL"              # 監視したい銘柄
DROP_PERCENT = 1.0           # 下落率（％）
CHECK_INTERVAL = 60          # チェック間隔（秒）
WEBHOOK_URL = "https://discord.com/api/webhooks/1414617578915233852/s_ZyYQwSdy3fs1xJRewshlvU7Xjor1BT3hmFwmS__ahLxDklUw8YG2Rt44mPUCqrEm7f"
# ----------------------------------------

def get_price():
    data = yf.Ticker(TICKER)
    hist = data.history(period="1d", interval="1m")
    if hist.empty:
        return None
    current_price = hist["Close"][-1]
    high_price = hist["Close"].max()
    drop_rate = (high_price - current_price) / high_price * 100
    return current_price, high_price, drop_rate

def send_discord_alert(message):
    payload = {"content": message}
    try:
        requests.post(WEBHOOK_URL, json=payload)
    except Exception as e:
        print("Failed to send alert:", e)

def main():
    while True:
        result = get_price()
        if result:
            current, high, drop = result
            print(f"{TICKER}: 現在 {current}, 直近高値 {high}, 下落率 {drop:.2f}%")
            if drop >= DROP_PERCENT:
                send_discord_alert(f"{TICKER} dropped {drop:.2f}%! Current: {current}, High: {high}")
        else:
            print("Failed to fetch price.")
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    print("Stock alert bot is running!")
    main()
