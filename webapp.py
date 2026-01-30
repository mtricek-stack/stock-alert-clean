import yfinance as yf
import json
import os
import requests
from datetime import datetime

# ===== 設定 =====
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1416784239919235152/_4pHEPgqs8Jx3DbFEvFkbU_90cbyIQd0E8Elvypk5scV8asMUSYgkPRP4fPeeQ8W5jkb"

SYMBOLS = [
    "NVDA", "ISRG", "TEM", "SOUN", "PLTR", "IONQ", "QBTS", "QUBT",
    "RGTI", "BBAI", "LAES", "PDYN", "OPTX", "RKLB", "CRCL",
    "NVTS", "ENVX", "MIAX", "BTQ"
]

DROP_THRESHOLD = 10.0  # %
STATE_FILE = "state.json"
BASE_DATE = "2025-10-01"  # ← 10月基準


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

    hist = ticker.history(start=BASE_DATE)
    if hist.empty:
        continue

    high_price = hist["High"].max()
    low_price_hist = hist["Low"].min()
    current_price = hist["Close"].iloc[-1]

    drop_pct = (high_price - current_price) / high_price * 100

    # ---- 閾値未満は何もしない ----
    if drop_pct < DROP_THRESHOLD:
        print(f"{symbol}: No alert. Drop {drop_pct:.2f}%")
        continue

    # ---- state 初期化（10月以降の最安値・高値を固定）----
    if symbol not in state:
        state[symbol] = {
            "high_since_oct": float(high_price),
            "low_since_oct": float(low_price_hist),
            "alerted": False
        }

    # ---- 念のため更新（10月内で高値・安値が伸びた場合）----
    state[symbol]["high_since_oct"] = max(
        state[symbol]["high_since_oct"], high_price
    )
    state[symbol]["low_since_oct"] = min(
        state[symbol]["low_since_oct"], low_price_hist
    )

    high_price = state[symbol]["high_since_oct"]
    low_price = state[symbol]["low_since_oct"]

    drop_pct = (high_price - current_price) / high_price * 100
    recovery_pct = (current_price - low_price) / low_price * 100

    # ---- 通知文（常に同じ意味）----
    message = (
    f"{symbol}\n"
    f"C {current_price:.2f} | "
    f"H {high_price:.2f} | "
    f"L {low_price:.2f} | "
    f"D {drop_pct:.2f}% | "
    f"R {recovery_pct:.2f}%"
)

    # ---- 初回だけ 🚨 ----
    if not state[symbol]["alerted"]:
        message = "🚨 " + message
        state[symbol]["alerted"] = True

    send_discord(message)
    print(f"{symbol}: Alert sent")

save_state()
