import yfinance as yf
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

# -------------------------
# 設定（環境変数で管理）
# -------------------------
EMAIL_ADDRESS = os.environ.get("EMAIL_ADDRESS")       # 送信元メール
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")     # メールパスワード（環境変数）
TO_ADDRESS = os.environ.get("TO_ADDRESS")             # 送信先メール

STOCK_SYMBOL = "AAPL"      # 監視銘柄
DROP_PERCENT = 5           # 下落率（%）

# -------------------------
# 株価チェック
# -------------------------
def check_stock_drop():
    ticker = yf.Ticker(STOCK_SYMBOL)
    hist = ticker.history(period="2d")  # 直近2日分
    if len(hist) < 2:
        return False, 0

    high = hist['High'].iloc[-2]
    close = hist['Close'].iloc[-1]
    drop = (high - close) / high * 100

    if drop >= DROP_PERCENT:
        return True, drop
    return False, drop

# -------------------------
# メール送信
# -------------------------
def send_email(drop):
    subject = f"{STOCK_SYMBOL} has dropped {drop:.2f}%"
    body = f"{STOCK_SYMBOL} dropped {drop:.2f}% from its recent high."

    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = TO_ADDRESS
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP("smtp.office365.com", 587)  # Outlook SMTP
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        print("Email sent!")
    except Exception as e:
        print("Failed to send email:", e)

# -------------------------
# メイン
# -------------------------
if __name__ == "__main__":
    alert, drop = check_stock_drop()
    if alert:
        send_email(drop)
    else:
        print(f"No alert. {STOCK_SYMBOL} dropped {drop:.2f}%")
