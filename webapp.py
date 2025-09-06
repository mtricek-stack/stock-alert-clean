import os
import yfinance as yf
import smtplib
from email.mime.text import MIMEText
from flask import Flask

app = Flask(__name__)

# 株情報
TICKER = "AAPL"
DROP_THRESHOLD = 2

# メール情報（Yahooメール用）
EMAIL_ADDRESS = "outlook_313AA6D1A08AC2BC@outlook.com"
EMAIL_PASSWORD = "ntoko2940"
TO_EMAIL = "mtrice.k@gmail.com"

def send_email(subject, body):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = TO_EMAIL

    with smtplib.SMTP_SSL("smtp.mail.yahoo.co.jp", 465) as server:
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)

def check_stock_drop():
    stock = yf.Ticker(TICKER)
    hist = stock.history(period="5d")
    high_price = hist['Close'].max()
    current_price = hist['Close'][-1]
    drop_percent = (high_price - current_price) / high_price * 100

    if drop_percent >= DROP_THRESHOLD:
        send_email(f"{TICKER} 株価下落アラート",
                   f"{TICKER} が直近高値から {drop_percent:.2f}% 下落しました！")
    return f"{TICKER}: 現在 {current_price}, 直近高値 {high_price}, 下落率 {drop_percent:.2f}%"

@app.route("/")
def home():
    return "Stock alert bot is running!\n" + check_stock_drop()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
