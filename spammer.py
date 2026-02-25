import os
import random
import string
import threading
import time
from flask import Flask, jsonify

app = Flask(__name__)

SPAM_FREQUENCY = int(os.getenv('SPAM_FREQUENCY', '5'))


def generate_random_log():
    """Generate a 200 character log with '-' every 5 characters."""
    chars = []
    for i in range(34):  # 34 groups of 5 = 170 chars + 33 dashes = 203 chars, we'll trim to 200
        group = ''.join(random.choices(string.ascii_letters + string.digits, k=5))
        chars.append(group)
    log = '-'.join(chars)
    return log[:200]  # Ensure exactly 200 characters


def spam_logger():
    """Background thread that prints random logs every SPAM_FREQUENCY seconds."""
    while True:
        time.sleep(SPAM_FREQUENCY)
        print(generate_random_log(), flush=True)


@app.route('/')
def index():
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append({
            'endpoint': rule.endpoint,
            'methods': list(rule.methods - {'HEAD', 'OPTIONS'}),
            'path': str(rule)
        })
    return jsonify({
        'message': 'hello world',
        'routes': routes
    })


@app.route('/health')
def health():
    return jsonify({'status': 'healthy'})


if __name__ == '__main__':
    # Start the spam logger thread
    logger_thread = threading.Thread(target=spam_logger, daemon=True)
    logger_thread.start()

    app.run(host='0.0.0.0', port=5000)
