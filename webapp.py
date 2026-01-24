import os
import json
import requests
import yfinance as yf

DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1416784239919235152/_4pHEPgqs8Jx3DbFEvFkbU_90cbyIQd0E8Elvypk5scV8asMUSYgkPRP4fPeeQ8W5jkb"
STATE_FILE = "state.json"

SYMBOLS = [
    "NVDA","ISRG","TEM","SOUN","PLTR","IONQ",
    "QBTS","QUBT","RGTI","BBAI","LAES","PDYN",
    "OPTX","RKLB","CRCL","KRMN","NVTS","ENVX","MIAX","BTQ"
]

DROP_PERCENT = 10  # 下落通知閾値(%)

# state.json をロード（なければ作成）
if not os.path.exists(STATE_FILE):
    with open(STATE_FILE, "w") as f:
        json.dump({}, f)

with open(STATE_FILE, "r") as f:
    try:
        state = json.load(f)
    except:
        state = {}

def save_state():
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def send_discord_message(message):
    try:
        requests.post(DISCORD_WEBHOOK_URL, json={"content": message})
    except Exception as e:
        print(f"Failed to send Discord message: {e}")

def get_price(symbol):
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(start="2025-10-01")  # 2025/10/1以降のデータ
        if hist.empty:
            return None, None
        recent_high = hist["High"].max()
        current_price = hist["Close"].iloc[-1]
        return current_price, recent_high
    except Exception as e:
        print(f"Failed to fetch price for {symbol}: {e}")
        return None, None

def main():
    print("Stock alert bot running!")
    for symbol in SYMBOLS:
        current_price, recent_high = get_price(symbol)
        if current_price is None:
            print(f"No data for {symbol}")
            continue

        # state.json に初期値設定
        if symbol not in state:
            state[symbol] = {"notified": False, "high": recent_high}

        # 過去最高値更新
        if recent_high > state[symbol]["high"]:
            state[symbol]["high"] = recent_high
            state[symbol]["notified"] = False  # 最高値更新で通知リセット

        drop_rate = (state[symbol]["high"] - current_price) / state[symbol]["high"] * 100

        if drop_rate >= DROP_PERCENT and not state[symbol]["notified"]:
            send_discord_message(
                f"🚨 {symbol} dropped {drop_rate:.2f}% from recent high!\n"
                f"Current: {current_price:.2f}, High: {state[symbol]['high']:.2f}"
            )
            state[symbol]["notified"] = True
        elif drop_rate < DROP_PERCENT and state[symbol]["notified"]:
            # 回復したら通知フラグリセット
            state[symbol]["notified"] = False
            print(f"{symbol}: recovered. Drop {drop_rate:.2f}%")

        else:
            print(f"{symbol}: No alert. Drop {drop_rate:.2f}%")

    save_state()

if __name__ == "__main__":
    main()
