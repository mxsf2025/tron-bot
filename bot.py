
from flask import Flask, request
import requests
import config

app = Flask(__name__)
TELEGRAM_API = f"https://api.telegram.org/bot{config.BOT_TOKEN}"

@app.route('/', methods=['GET'])
def index():
    return 'Bot is running!'

@app.route('/', methods=['POST'])
def webhook():
    data = request.get_json()
    if 'message' in data:
        chat_id = data['message']['chat']['id']
        text = data['message'].get('text', '')
        if text.startswith('T'):
            reply = get_tron_balance(text.strip())
        else:
            reply = '请输入有效的 TRON 地址'
        send_message(chat_id, reply)
    return 'ok'

def send_message(chat_id, text):
    requests.post(f"{TELEGRAM_API}/sendMessage", json={
        "chat_id": chat_id,
        "text": text
    })

def get_tron_balance(address):
    try:
        url = f"https://apilist.tronscan.org/api/account?address={address}"
        resp = requests.get(url)
        data = resp.json()
        trx = int(data.get("balance", 0)) / 1_000_000
        result = [f"地址：{address}", "主链余额：", f"   TRX: {trx:.2f}"]

        for token in data.get("tokenBalances", []):
            if token.get("tokenId") == "TXLAQ63Xg1NAzckPwKHvzw7CSEmLMEqcdj":
                usdt = int(token["balance"]) / (10 ** int(token.get("tokenDecimal", 6)))
                result.append(f"   USDT：{usdt:.0f}")
        return "\n".join(result)
    except Exception as e:
        return f"查询失败：{e}"

def set_webhook():
    url = f"{TELEGRAM_API}/setWebhook"
    requests.post(url, json={"url": config.WEBHOOK_URL})

if __name__ == '__main__':
    set_webhook()
    app.run(host='0.0.0.0', port=10000)
