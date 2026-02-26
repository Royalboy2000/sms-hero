import os
import sys
import sqlite3
import jwt
import datetime
import threading
import requests
from flask import Flask, send_from_directory, request, jsonify, make_response
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from dotenv import load_dotenv
import telebot

# Load environment variables
load_dotenv()

def setup_env():
    env_vars = {
        'SECRET_KEY': 'Enter a secret key for JWT (e.g., a long random string): ',
        'HERO_SMS_API_KEY': 'Enter your Hero-SMS API Key: ',
        'TELEGRAM_BOT_TOKEN': 'Enter your Telegram Bot Token: ',
        'ADMIN_TELEGRAM_ID': 'Enter your Admin Telegram User ID: '
    }

    updated = False
    for var, prompt in env_vars.items():
        if not os.environ.get(var):
            try:
                val = input(prompt).strip()
                if val:
                    os.environ[var] = val
                    with open('.env', 'a') as f:
                        f.write(f"{var}={val}\n")
                    updated = True
            except EOFError:
                break
    if updated:
        print("\nEnvironment variables updated in .env and current session.")

if __name__ == '__main__':
    # Only run setup if not in a non-interactive shell or specifically requested
    if sys.stdin.isatty():
        setup_env()

app = Flask(__name__, static_folder='dist' if os.path.exists('dist') else '.')
CORS(app)

SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    if os.environ.get('FLASK_ENV') == 'production':
        raise RuntimeError("SECRET_KEY must be set in production!")
    SECRET_KEY = 'dev-key-smskenya-2026'
HERO_SMS_API_KEY = os.environ.get('HERO_SMS_API_KEY', '')
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')
ADMIN_TELEGRAM_ID = os.environ.get('ADMIN_TELEGRAM_ID', '')

# Database setup
DB_PATH = 'smskenya.db'

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        telegram_id TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Quotas table (admin approves how many numbers)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS quotas (
        user_id INTEGER PRIMARY KEY,
        allowed_numbers INTEGER DEFAULT 0,
        used_numbers INTEGER DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')

    # Orders table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        service_id TEXT NOT NULL,
        country_id TEXT NOT NULL,
        phone_number TEXT,
        order_id_provider TEXT,
        status TEXT DEFAULT 'waiting',
        sms_code TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')

    # Settings table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )
    ''')

    conn.commit()
    conn.close()

init_db()

# --- JWT Decorator ---
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            conn = get_db_connection()
            current_user = conn.execute('SELECT * FROM users WHERE id = ?', (data['user_id'],)).fetchone()
            conn.close()
            if not current_user:
                 return jsonify({'message': 'User not found!'}), 401
        except Exception as e:
            return jsonify({'message': 'Token is invalid!', 'error': str(e)}), 401

        return f(current_user, *args, **kwargs)

    return decorated

# --- API Endpoints ---

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Username and password are required!'}), 400

    hashed_password = generate_password_hash(password)

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', (username, hashed_password))
        user_id = cursor.lastrowid
        # Initialize quota
        cursor.execute('INSERT INTO quotas (user_id, allowed_numbers, used_numbers) VALUES (?, ?, ?)', (user_id, 0, 0))
        conn.commit()
    except sqlite3.IntegrityError:
        return jsonify({'message': 'Username already exists!'}), 400
    finally:
        conn.close()

    # Notify admin on Telegram
    if TELEGRAM_BOT_TOKEN and ADMIN_TELEGRAM_ID:
        try:
            bot.send_message(ADMIN_TELEGRAM_ID, f"New user registered: {username}. Use /approve {username} <amount> to give quota.")
        except Exception as e:
            print(f"Failed to send telegram notification: {e}")

    return jsonify({'message': 'User registered successfully!'}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Username and password are required!'}), 400

    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()

    if not user or not check_password_hash(user['password_hash'], password):
        return jsonify({'message': 'Invalid username or password!'}), 401

    token = jwt.encode({
        'user_id': user['id'],
        'username': user['username'],
        'exp': datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=24)
    }, SECRET_KEY)

    return jsonify({
        'token': token,
        'user': {
            'id': user['id'],
            'username': user['username']
        }
    })

@app.route('/api/me', methods=['GET'])
@token_required
def get_me(current_user):
    conn = get_db_connection()
    quota = conn.execute('SELECT * FROM quotas WHERE user_id = ?', (current_user['id'],)).fetchone()
    conn.close()

    return jsonify({
        'id': current_user['id'],
        'username': current_user['username'],
        'quota': {
            'allowed': quota['allowed_numbers'],
            'used': quota['used_numbers']
        }
    })

# --- Hero-SMS API Integration (Mocked/Generic SMS-Activate protocol) ---

BASE_API_URL = "https://hero-sms.com/stubs/handler_api.php"

def call_hero_api(action, **kwargs):
    params = {
        'api_key': HERO_SMS_API_KEY,
        'action': action
    }
    params.update(kwargs)
    try:
        response = requests.get(BASE_API_URL, params=params)
        return response.text
    except Exception as e:
        return f"ERROR: {str(e)}"

@app.route('/api/generate-number', methods=['POST'])
@token_required
def generate_number(current_user):
    data = request.get_json()
    service_id = data.get('service_id')
    country_id = data.get('country_id')

    if not service_id or not country_id:
        return jsonify({'message': 'Service ID and Country ID are required!'}), 400

    conn = get_db_connection()
    quota = conn.execute('SELECT * FROM quotas WHERE user_id = ?', (current_user['id'],)).fetchone()

    if quota['used_numbers'] >= quota['allowed_numbers']:
        conn.close()
        return jsonify({'message': 'Quota exceeded! Please contact admin to increase your limit.'}), 403

    # Call Hero-SMS API
    # action=getNumber, service=service_id, country=country_id
    # Result format: ACCESS_NUMBER:ID:NUMBER
    res = call_hero_api('getNumber', service=service_id, country=country_id)

    # For testing without real API key, allow simulation
    if not HERO_SMS_API_KEY:
        import random
        order_id = str(random.randint(100000, 999999))
        phone_number = f"+123456789{random.randint(10, 99)}"
        res = f"ACCESS_NUMBER:{order_id}:{phone_number}"

    if res.startswith('ACCESS_NUMBER'):
        parts = res.split(':')
        order_id = parts[1]
        phone_number = parts[2]

        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO orders (user_id, service_id, country_id, phone_number, order_id_provider, status)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (current_user['id'], service_id, country_id, phone_number, order_id, 'waiting'))

        cursor.execute('UPDATE quotas SET used_numbers = used_numbers + 1 WHERE user_id = ?', (current_user['id'],))
        conn.commit()
        conn.close()

        return jsonify({
            'order_id': order_id,
            'phone_number': phone_number,
            'status': 'waiting'
        })
    else:
        conn.close()
        return jsonify({'message': 'Failed to generate number from provider', 'provider_response': res}), 500

@app.route('/api/orders', methods=['GET'])
@token_required
def get_orders(current_user):
    conn = get_db_connection()
    orders = conn.execute('SELECT * FROM orders WHERE user_id = ? ORDER BY timestamp DESC', (current_user['id'],)).fetchall()
    conn.close()

    return jsonify([dict(order) for order in orders])

@app.route('/api/order/<order_id>/status', methods=['GET'])
@token_required
def get_order_status(current_user, order_id):
    # Call Hero-SMS API to check status
    # action=getStatus, id=order_id
    res = call_hero_api('getStatus', id=order_id)

    # Simulation for testing
    if not HERO_SMS_API_KEY:
        import random
        if random.random() > 0.7:
             res = f"STATUS_OK:{random.randint(100000, 999999)}"
        else:
             res = "STATUS_WAIT_CODE"

    # STATUS_WAIT_CODE, STATUS_OK:CODE, etc.
    status = 'waiting'
    sms_code = None

    if res.startswith('STATUS_OK'):
        status = 'received'
        sms_code = res.split(':')[1]
    elif res.startswith('STATUS_WAIT_CODE'):
        status = 'waiting'
    elif res.startswith('STATUS_CANCEL'):
        status = 'cancelled'

    # Update local DB
    conn = get_db_connection()
    conn.execute('UPDATE orders SET status = ?, sms_code = ? WHERE order_id_provider = ? AND user_id = ?',
                 (status, sms_code, order_id, current_user['id']))
    conn.commit()
    conn.close()

    return jsonify({
        'order_id': order_id,
        'status': status,
        'sms_code': sms_code
    })

# --- Telegram Bot ---

if TELEGRAM_BOT_TOKEN:
    bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

    @bot.message_handler(commands=['start', 'help'])
    def send_welcome(message):
        bot.reply_to(message, "SMSKenya Admin Bot. Use /approve <username> <amount> to increase quota.")

    @bot.message_handler(commands=['approve'])
    def approve_quota(message):
        # Security: only admin can use this command
        if str(message.from_user.id) != ADMIN_TELEGRAM_ID:
            bot.reply_to(message, "Unauthorized.")
            return

        try:
            args = message.text.split()
            if len(args) != 3:
                bot.reply_to(message, "Usage: /approve <username> <amount>")
                return

            username = args[1]
            amount = int(args[2])

            conn = get_db_connection()
            user = conn.execute('SELECT id FROM users WHERE username = ?', (username,)).fetchone()
            if user:
                conn.execute('UPDATE quotas SET allowed_numbers = allowed_numbers + ? WHERE user_id = ?', (amount, user['id']))
                conn.commit()
                bot.reply_to(message, f"Approved {amount} more numbers for {username}.")
            else:
                bot.reply_to(message, f"User {username} not found.")
            conn.close()
        except Exception as e:
            bot.reply_to(message, f"Error: {str(e)}")

    def run_bot():
        print("Starting Telegram Bot...")
        bot.infinity_polling()

    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()

# --- Static Files & Single Page App Handling ---

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    default_port = 8000
    if len(sys.argv) > 1:
        try:
            default_port = int(sys.argv[1])
        except ValueError:
            pass

    port = default_port
    if sys.stdin.isatty():
        try:
            port_input = input(f"Enter the port you want to use (default {default_port}): ").strip()
            if port_input:
                port = int(port_input)
        except (ValueError, EOFError):
            print(f"Using port {default_port}")
            port = default_port

    print(f"\nSMSKenya Server starting...")
    print(f"Serving from: {os.path.abspath(app.static_folder)}")
    print(f"URL: http://localhost:{port}")

    app.run(host='0.0.0.0', port=port)
