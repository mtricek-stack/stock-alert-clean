import json
import os
import requests
import yfinance as yf

DISCORD_WEBHOOK_URL = "ここはそのまま"

SYMBOLS = [
    "NVDA","ISRG","TEM","SOUN","PLTR","IONQ",
    "QBTS","QUBT","RGTI","BBAI","LAES","PDYN",
    "OPTX","RKLB","CRCL","KRMN","NVTS","ENVX","MIAX","BTQ"
]

DROP_PERCENT = 10
STATE_FILE = "state.json"


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {}


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def send_discord_message(message):
    requests.post(DISCORD_WEBHOOK_URL, json={"content": message})


def get_price(symbol):
    stock = yf.Ticker(symbol)
    price = stock.fast_info.get("last_price")
    return price


def main():
    print("Stock alert bot running!")
    state = load_state()

    for symbol in SYMBOLS:
        price = get_price(symbol)
        if price is None:
            print(f"No data for {symbol}")
            continue

        s = state.get(symbol, {
            "recent_high": price,
            "in_alert": False
        })

        # 高値更新
        if price > s["recent_high"]:
            s["recent_high"] = price
            s["in_alert"] = False
            state[symbol] = s
            continue

        drop_rate = (s["recent_high"] - price) / s["recent_high"] * 100

        if drop_rate >= DROP_PERCENT:
            if not s["in_alert"]:
                send_discord_message(
                    f"🚨 {symbol} dropped {drop_rate:.2f}% from recent high!\n"
                    f"Current: {price:.2f}, High: {s['recent_high']:.2f}"
                )
                s["in_alert"] = True
        else:
            s["in_alert"] = False

        state[symbol] = s

    save_state(state)


if __name__ == "__main__":
    main()
