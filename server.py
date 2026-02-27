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

    # Create tables if not exist
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
        user_id INTEGER,
        service_id TEXT NOT NULL,
        country_id TEXT NOT NULL,
        phone_number TEXT,
        order_id_provider TEXT,
        status TEXT DEFAULT 'waiting',
        sms_code TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        token TEXT,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')

    # Whitelist table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_whitelist (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        service_id TEXT NOT NULL,
        country_id TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id),
        UNIQUE(user_id, service_id, country_id)
    )
    ''')

    # Direct purchase tokens
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS purchase_tokens (
        token TEXT PRIMARY KEY,
        service_id TEXT,
        country_id TEXT,
        is_used INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Mapping table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS mappings (
        frontend_id TEXT NOT NULL,
        provider_id TEXT NOT NULL,
        type TEXT NOT NULL, -- 'service' or 'country'
        PRIMARY KEY (frontend_id, type)
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

    # Seed initial mappings based on constants.tsx and common SMS-Activate IDs
    initial_country_mappings = {
        'KE': '8', 'US': '12', 'GB': '16', 'CA': '36', 'ZA': '31',
        'AE': '95', 'CN': '3', 'DE': '43', 'IN': '22', 'NG': '19',
        'AU': '175', 'FR': '78', 'NL': '48', 'BR': '73', 'RU': '0',
        'TZ': '51', 'UG': '75', 'SA': '53', 'QA': '111', 'JP': '112',
        'KR': '113', 'SG': '47', 'TR': '62', 'ES': '56', 'IT': '88',
        'SE': '46', 'CH': '42', 'PL': '15', 'ID': '6', 'PH': '4'
    }
    initial_service_mappings = {
        'wa': 'wa', 'tg': 'tg', 'ig': 'ig', 'fb': 'fb', 'goo': 'go',
        'tt': 'lf', 'tw': 'tw', 'li': 'ot', 'pp': 'pp', 'airbnb': 'am', 'bolt': 'ol'
    }

    for fid, pid in initial_country_mappings.items():
        cursor.execute('INSERT OR IGNORE INTO mappings (frontend_id, provider_id, type) VALUES (?, ?, ?)', (fid, pid, 'country'))
    for fid, pid in initial_service_mappings.items():
        cursor.execute('INSERT OR IGNORE INTO mappings (frontend_id, provider_id, type) VALUES (?, ?, ?)', (fid, pid, 'service'))

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
        if action.endswith('V2') or action in ['getCountries', 'getServicesList', 'getPrices']:
            try:
                return response.json()
            except:
                return response.text
        return response.text
    except Exception as e:
        return {"error": str(e)} if action.endswith('V2') else f"ERROR: {str(e)}"

def get_mapping(frontend_id, mapping_type):
    conn = get_db_connection()
    row = conn.execute('SELECT provider_id FROM mappings WHERE frontend_id = ? AND type = ?', (frontend_id, mapping_type)).fetchone()
    conn.close()
    return row['provider_id'] if row else frontend_id

def set_mapping(frontend_id, provider_id, mapping_type):
    conn = get_db_connection()
    conn.execute('INSERT OR REPLACE INTO mappings (frontend_id, provider_id, type) VALUES (?, ?, ?)',
                 (frontend_id, provider_id, mapping_type))
    conn.commit()
    conn.close()

@app.route('/api/generate-number', methods=['POST'])
@token_required
def generate_number(current_user):
    data = request.get_json()
    service_id = data.get('service_id') # e.g. 'wa'
    country_id = data.get('country_id') # e.g. 'KE'

    if not service_id or not country_id:
        return jsonify({'message': 'Service ID and Country ID are required!'}), 400

    conn = get_db_connection()
    # Check Whitelist
    whitelisted = conn.execute('SELECT 1 FROM user_whitelist WHERE user_id = ? AND service_id = ? AND country_id = ?',
                              (current_user['id'], service_id, country_id)).fetchone()
    if not whitelisted:
        conn.close()
        return jsonify({'message': f'Service {service_id} for country {country_id} is not whitelisted for your account.'}), 403

    quota = conn.execute('SELECT * FROM quotas WHERE user_id = ?', (current_user['id'],)).fetchone()

    if quota['used_numbers'] >= quota['allowed_numbers']:
        conn.close()
        return jsonify({'message': 'Quota exceeded! Please contact admin to increase your limit.'}), 403

    # Map frontend IDs to Provider IDs
    p_service = get_mapping(service_id, 'service')
    p_country = get_mapping(country_id, 'country')

    # Call Hero-SMS API V2
    res = call_hero_api('getNumberV2', service=p_service, country=p_country)

    # For testing without real API key, allow simulation
    if not HERO_SMS_API_KEY:
        import random
        res = {
            "activationId": str(random.randint(100000, 999999)),
            "phoneNumber": f"123456789{random.randint(10, 99)}"
        }

    if isinstance(res, dict) and 'activationId' in res:
        order_id = res['activationId']
        phone_number = res['phoneNumber']

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
        msg = res.get('details', 'Failed to generate number from provider') if isinstance(res, dict) else str(res)
        return jsonify({'message': msg, 'provider_response': res}), 500

@app.route('/api/orders', methods=['GET'])
@token_required
def get_orders(current_user):
    conn = get_db_connection()
    orders = conn.execute('SELECT * FROM orders WHERE user_id = ? ORDER BY timestamp DESC', (current_user['id'],)).fetchall()
    conn.close()

    return jsonify([dict(order) for order in orders])

@app.route('/api/direct/generate', methods=['POST'])
def direct_generate():
    data = request.get_json()
    token = data.get('token')
    service_id = data.get('service_id')
    country_id = data.get('country_id')

    if not token or not service_id or not country_id:
        return jsonify({'message': 'Missing parameters!'}), 400

    conn = get_db_connection()
    # Validate token
    p_token = conn.execute('SELECT * FROM purchase_tokens WHERE token = ? AND is_used = 0', (token,)).fetchone()
    if not p_token:
        conn.close()
        return jsonify({'message': 'Invalid or expired token!'}), 403

    # Map frontend IDs to Provider IDs
    p_service = get_mapping(service_id, 'service')
    p_country = get_mapping(country_id, 'country')

    # Call Hero-SMS API V2
    res = call_hero_api('getNumberV2', service=p_service, country=p_country)

    # For testing without real API key, allow simulation
    if not HERO_SMS_API_KEY:
        import random
        res = {
            "activationId": str(random.randint(100000, 999999)),
            "phoneNumber": f"123456789{random.randint(10, 99)}"
        }

    if isinstance(res, dict) and 'activationId' in res:
        order_id = res['activationId']
        phone_number = res['phoneNumber']

        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO orders (service_id, country_id, phone_number, order_id_provider, status, token)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (service_id, country_id, phone_number, order_id, 'waiting', token))

        # Mark token as used
        cursor.execute('UPDATE purchase_tokens SET is_used = 1, service_id = ?, country_id = ? WHERE token = ?',
                       (service_id, country_id, token))
        conn.commit()
        conn.close()

        return jsonify({
            'order_id': order_id,
            'phone_number': phone_number,
            'status': 'waiting'
        })
    else:
        conn.close()
        msg = res.get('details', 'Failed to generate number from provider') if isinstance(res, dict) else str(res)
        return jsonify({'message': msg, 'provider_response': res}), 500

@app.route('/api/direct/status', methods=['GET'])
def direct_status():
    token = request.args.get('token')
    order_id = request.args.get('order_id')

    if not token or not order_id:
        return jsonify({'message': 'Missing parameters!'}), 400

    # Verify order belongs to token
    conn = get_db_connection()
    order = conn.execute('SELECT * FROM orders WHERE order_id_provider = ? AND token = ?', (order_id, token)).fetchone()
    conn.close()

    if not order:
        return jsonify({'message': 'Order not found for this token!'}), 404

    # Reuse status logic
    res = call_hero_api('getStatusV2', id=order_id)

    # Simulation for testing
    if not HERO_SMS_API_KEY:
        import random
        if random.random() > 0.7:
             res = {"sms": {"code": str(random.randint(100000, 999999))}}
        else:
             res = "STATUS_WAIT_CODE"

    status = 'waiting'
    sms_code = None

    if isinstance(res, dict) and res.get('sms') and res['sms'].get('code'):
        status = 'received'
        sms_code = res['sms']['code']
    elif res == "STATUS_WAIT_CODE":
        status = 'waiting'
    elif res == "STATUS_CANCEL" or (isinstance(res, dict) and res.get('title') == 'CANCELED'):
        status = 'cancelled'

    # Update local DB
    conn = get_db_connection()
    conn.execute('UPDATE orders SET status = ?, sms_code = ? WHERE order_id_provider = ? AND token = ?',
                 (status, sms_code, order_id, token))
    conn.commit()
    conn.close()

    return jsonify({
        'order_id': order_id,
        'status': status,
        'sms_code': sms_code
    })

@app.route('/api/order/<order_id>/cancel', methods=['POST'])
@token_required
def cancel_order(current_user, order_id):
    # status 8 — cancel activation (return money)
    res = call_hero_api('setStatus', id=order_id, status=8)

    if res == "ACCESS_CANCEL" or not HERO_SMS_API_KEY: # Allow simulation
        conn = get_db_connection()
        order = conn.execute('SELECT * FROM orders WHERE order_id_provider = ? AND user_id = ?', (order_id, current_user['id'])).fetchone()
        if order and order['status'] == 'waiting':
             cursor = conn.cursor()
             cursor.execute('UPDATE orders SET status = ? WHERE order_id_provider = ?', ('cancelled', order_id))
             cursor.execute('UPDATE quotas SET used_numbers = used_numbers - 1 WHERE user_id = ?', (current_user['id'],))
             conn.commit()
        conn.close()
        return jsonify({'message': 'Order cancelled and quota refunded.'})
    else:
        return jsonify({'message': f'Failed to cancel order: {res}'}), 400

@app.route('/api/direct/cancel', methods=['POST'])
def direct_cancel():
    data = request.get_json()
    token = data.get('token')
    order_id = data.get('order_id')

    if not token or not order_id:
        return jsonify({'message': 'Missing parameters!'}), 400

    # status 8 — cancel activation (return money)
    res = call_hero_api('setStatus', id=order_id, status=8)

    if res == "ACCESS_CANCEL" or not HERO_SMS_API_KEY: # Allow simulation
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE orders SET status = ? WHERE order_id_provider = ? AND token = ?', ('cancelled', order_id, token))
        cursor.execute('UPDATE purchase_tokens SET is_used = 0 WHERE token = ?', (token,))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Order cancelled. You can try another number.'})
    else:
        return jsonify({'message': f'Failed to cancel order: {res}'}), 400

@app.route('/api/order/<order_id>/status', methods=['GET'])
@token_required
def get_order_status(current_user, order_id):
    # Call Hero-SMS API V2
    res = call_hero_api('getStatusV2', id=order_id)

    # Simulation for testing
    if not HERO_SMS_API_KEY:
        import random
        if random.random() > 0.7:
             res = {"sms": {"code": str(random.randint(100000, 999999))}}
        else:
             res = "STATUS_WAIT_CODE"

    status = 'waiting'
    sms_code = None

    if isinstance(res, dict) and res.get('sms') and res['sms'].get('code'):
        status = 'received'
        sms_code = res['sms']['code']
    elif res == "STATUS_WAIT_CODE":
        status = 'waiting'
    elif res == "STATUS_CANCEL" or (isinstance(res, dict) and res.get('title') == 'CANCELED'):
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

if TELEGRAM_BOT_TOKEN and ":" in TELEGRAM_BOT_TOKEN:
    bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
    from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

    @bot.message_handler(commands=['start', 'menu'])
    def send_welcome(message):
        if str(message.from_user.id) != ADMIN_TELEGRAM_ID:
            bot.reply_to(message, "Unauthorized.")
            return

        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("Manage Users", callback_data="list_users"))
        markup.add(InlineKeyboardButton("Direct Purchase Tokens", callback_data="manage_tokens"))
        bot.send_message(message.chat.id, "SMSKenya Admin Panel:", reply_markup=markup)

    @bot.callback_query_handler(func=lambda call: True)
    def callback_query(call):
        if str(call.from_user.id) != ADMIN_TELEGRAM_ID:
            bot.answer_callback_query(call.id, "Unauthorized")
            return

        if call.data == "check_balance":
            res = call_hero_api('getBalance')
            bot.answer_callback_query(call.id, f"Balance: {res}")
            # Refresh menu to show balance in text maybe? Or just alert.

        elif call.data == "list_users":
            conn = get_db_connection()
            users = conn.execute('SELECT id, username FROM users').fetchall()
            conn.close()

            markup = InlineKeyboardMarkup()
            for user in users:
                markup.add(InlineKeyboardButton(user['username'], callback_data=f"user_{user['id']}"))
            markup.add(InlineKeyboardButton("« Back", callback_data="main_menu"))
            bot.edit_message_text("Select a user:", call.message.chat.id, call.message.message_id, reply_markup=markup)

        elif call.data.startswith("user_"):
            user_id = call.data.split("_")[1]
            conn = get_db_connection()
            user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
            quota = conn.execute('SELECT * FROM quotas WHERE user_id = ?', (user_id,)).fetchone()
            conn.close()

            text = f"User: {user['username']}\nQuota: {quota['used_numbers']}/{quota['allowed_numbers']}"
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("Add Quota (+5)", callback_data=f"quota_{user_id}_5"))
            markup.add(InlineKeyboardButton("Whitelist Service/Country", callback_data=f"whitelist_{user_id}"))
            markup.add(InlineKeyboardButton("« Back to Users", callback_data="list_users"))
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)

        elif call.data.startswith("quota_"):
            _, user_id, amount = call.data.split("_")
            conn = get_db_connection()
            conn.execute('UPDATE quotas SET allowed_numbers = allowed_numbers + ? WHERE user_id = ?', (amount, user_id))
            conn.commit()
            conn.close()
            bot.answer_callback_query(call.id, f"Added {amount} to quota")
            # Refresh user view
            callback_query(type('obj', (object,), {'data': f'user_{user_id}', 'from_user': call.from_user, 'message': call.message, 'id': call.id}))

        elif call.data.startswith("whitelist_"):
            user_id = call.data.split("_")[1]
            # Show existing whitelist and option to add
            conn = get_db_connection()
            whitelist = conn.execute('SELECT * FROM user_whitelist WHERE user_id = ?', (user_id,)).fetchall()
            conn.close()

            text = "Current Whitelist:\n"
            markup = InlineKeyboardMarkup()
            for entry in whitelist:
                text += f"- {entry['service_id']} in {entry['country_id']}\n"
                markup.add(InlineKeyboardButton(f"❌ {entry['service_id']}@{entry['country_id']}", callback_data=f"rmwl_{entry['id']}"))

            markup.add(InlineKeyboardButton("➕ Add Pair", callback_data=f"addwl_{user_id}"))
            markup.add(InlineKeyboardButton("« Back to User", callback_data=f"user_{user_id}"))
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)

        elif call.data.startswith("addwl_"):
            # Instead of asking for text, let's offer buttons for common services/countries or ask for text if preferred
            # For brevity and flexibility, let's stick to text but improve the prompt
            user_id = call.data.split("_")[1]
            msg = bot.send_message(call.message.chat.id, "Send service and country ID (frontend IDs) separated by space (e.g., `wa KE` or `tg US`).\n\nCommon Services: `wa`, `tg`, `ig`, `fb`, `goo`, `tt`, `pp`.\nCommon Countries: `KE`, `US`, `GB`, `CA`, `DE`.", parse_mode="Markdown")
            bot.register_next_step_handler(msg, process_add_whitelist, user_id)

        elif call.data.startswith("rmwl_"):
            wl_id = call.data.split("_")[1]
            conn = get_db_connection()
            row = conn.execute('SELECT user_id FROM user_whitelist WHERE id = ?', (wl_id,)).fetchone()
            user_id = row['user_id']
            conn.execute('DELETE FROM user_whitelist WHERE id = ?', (wl_id,))
            conn.commit()
            conn.close()
            bot.answer_callback_query(call.id, "Removed from whitelist")
            callback_query(type('obj', (object,), {'data': f'whitelist_{user_id}', 'from_user': call.from_user, 'message': call.message, 'id': call.id}))

        elif call.data == "manage_tokens":
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("Generate New Token", callback_data="gen_token"))
            markup.add(InlineKeyboardButton("« Back", callback_data="main_menu"))
            bot.edit_message_text("Manage Direct Purchase Tokens:", call.message.chat.id, call.message.message_id, reply_markup=markup)

        elif call.data == "gen_token":
            import secrets
            token = secrets.token_urlsafe(16)
            conn = get_db_connection()
            conn.execute('INSERT INTO purchase_tokens (token) VALUES (?)', (token,))
            conn.commit()
            conn.close()
            bot.send_message(call.message.chat.id, f"Generated Token:\n`{token}`", parse_mode="Markdown")
            bot.answer_callback_query(call.id, "Token Generated")

        elif call.data == "main_menu":
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("Manage Users", callback_data="list_users"))
            markup.add(InlineKeyboardButton("Direct Purchase Tokens", callback_data="manage_tokens"))
            markup.add(InlineKeyboardButton("💰 Check HeroSMS Balance", callback_data="check_balance"))
            markup.add(InlineKeyboardButton("🏷️ View Provider Prices", callback_data="view_prices"))
            bot.edit_message_text("SMSKenya Admin Panel:", call.message.chat.id, call.message.message_id, reply_markup=markup)

    def process_add_whitelist(message, user_id):
        try:
            service, country = message.text.split()
            conn = get_db_connection()
            conn.execute('INSERT OR IGNORE INTO user_whitelist (user_id, service_id, country_id) VALUES (?, ?, ?)',
                         (user_id, service, country))
            conn.commit()
            conn.close()
            bot.reply_to(message, f"Added {service}@{country} to whitelist.")
        except Exception as e:
            bot.reply_to(message, f"Error: {str(e)}. Use format: service country")

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
