import yfinance as yf
import json
import os
import requests

# ===== 設定 =====
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1416784239919235152/_4pHEPgqs8Jx3DbFEvFkbU_90cbyIQd0E8Elvypk5scV8asMUSYgkPRP4fPeeQ8W5jkb"

SYMBOLS = [
    "NVDA", "ISRG", "TEM", "SOUN", "PLTR", "IONQ", "QBTS", "QUBT",
    "RGTI", "BBAI", "LAES", "PDYN", "OPTX", "RKLB", "CRCL",
    "NVTS", "ENVX", "MIAX", "BTQ"
]

DROP_THRESHOLD = 10.0  # %
STATE_FILE = "state.json"


# ===== state 読み込み =====
if os.path.exists(STATE_FILE):
    with open(STATE_FILE, "r") as f:
        state = json.load(f)
else:
    state = {}


def save_state():
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def send_discord(message: str):
    requests.post(
        DISCORD_WEBHOOK_URL,
        json={"content": message}
    )


print("Stock alert bot running!")


for symbol in SYMBOLS:
    ticker = yf.Ticker(symbol)

    hist = ticker.history(period="6mo")
    if hist.empty:
        continue

    high_price = hist["High"].max()
    current_price = hist["Close"].iloc[-1]

    drop_pct = (high_price - current_price) / high_price * 100

    # ===== 下落率が閾値未満なら state をリセット =====
    if drop_pct < DROP_THRESHOLD:
        if symbol in state:
            del state[symbol]
        print(f"{symbol}: No alert. Drop {drop_pct:.2f}%")
        continue

    # ===== 下落監視開始（初回）=====
    if symbol not in state:
        state[symbol] = {
            "low_since_drop": current_price
        }

    # ===== 最安値更新 =====
    if current_price < state[symbol]["low_since_drop"]:
        state[symbol]["low_since_drop"] = current_price

    low_price = state[symbol]["low_since_drop"]

    # ===== 正しい回復率 =====
    # (Current - Low) / (High - Low)
    if high_price > low_price:
        recovery_pct = (current_price - low_price) / (high_price - low_price) * 100
    else:
        recovery_pct = 0.0

    # ===== 通知（毎回必ず送る）=====
    message = (
        f"🚨 {symbol}\n"
        f"Current: {current_price:.2f}\n"
        f"High: {high_price:.2f}\n"
        f"Low: {low_price:.2f}\n"
        f"Drop: {drop_pct:.2f}%\n"
        f"Recovery: {recovery_pct:.2f}%"
    )

    send_discord(message)
    print(f"{symbol}: Alert sent")


save_state()

