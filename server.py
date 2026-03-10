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
    # Secure fallback key (64 chars = 32 bytes)
    SECRET_KEY = '903d58e3638c082faffae0e63dcee4df9b62d4ca23702da723f9c78cdf460f3e'
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

    # Seed initial settings
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('whitelist_required', '0')")


    # Pricing table (our selling prices, not provider cost)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS pricing (
        service_id TEXT NOT NULL,
        country_id TEXT NOT NULL,
        price_kes REAL NOT NULL,
        price_usd REAL NOT NULL,
        PRIMARY KEY (service_id, country_id)
    )
    ''')

    # Seed default prices (KES) — based on provider cost + margin
    default_prices = [
        # service, country, KES price, USD price
        ('wa', 'US', 600, 4.60),
        ('wa', 'CA', 600, 4.60),
        ('wa', 'GB', 600, 4.60),
        ('wa', 'KE', 600, 4.60),
        ('wa', 'TZ', 600, 4.60),
        ('wa', 'ZA', 600, 4.60),
        ('wa', 'NG', 600, 4.60),
        ('wa', 'UG', 600, 4.60),
        ('wa', 'TR', 600, 4.60),
        ('wa', 'IT', 600, 4.60),
        ('wa', 'DE', 600, 4.60),
        ('wa', 'NL', 600, 4.60),
        ('wa', 'PL', 600, 4.60),
        ('wa', 'SA', 600, 4.60),
        ('wa', 'JP', 600, 4.60),
        ('wa', 'AU', 600, 4.60),
        ('wa', 'SE', 600, 4.60),
        ('wa', 'SG', 600, 4.60),
        ('wa', 'RU', 600, 4.60),
        ('wa', 'IN', 600, 4.60),
        ('wa', 'ID', 600, 4.60),
        ('tg', 'CA', 600, 4.60),
        ('tg', 'US', 600, 4.60),
        ('tg', 'BR', 600, 4.60),
        ('tg', 'TR', 600, 4.60),
        ('tg', 'KE', 600, 4.60),
        ('tg', 'GB', 600, 4.60),
        ('tg', 'DE', 600, 4.60),
        ('tg', 'NG', 600, 4.60),
        ('ig', 'BR', 600, 4.60),
        ('ig', 'CA', 600, 4.60),
        ('ig', 'US', 600, 4.60),
        ('ig', 'KE', 600, 4.60),
        ('ig', 'GB', 600, 4.60),
        ('fb', 'BR', 600, 4.60),
        ('fb', 'CA', 600, 4.60),
        ('fb', 'US', 600, 4.60),
        ('fb', 'KE', 600, 4.60),
        ('goo', 'CA', 600, 4.60),
        ('goo', 'US', 600, 4.60),
        ('goo', 'KE', 600, 4.60),
        ('goo', 'DE', 600, 4.60),
        ('goo', 'NG', 600, 4.60),
    ]
    for svc, cid, kes, usd in default_prices:
        cursor.execute(
            'INSERT OR IGNORE INTO pricing (service_id, country_id, price_kes, price_usd) VALUES (?, ?, ?, ?)',
            (svc, cid, kes, usd)
        )

    conn.commit()

    # Seed initial mappings based on constants.tsx and common SMS-Activate IDs
    initial_country_mappings = {
        'KE': '8',   'US': '187', 'GB': '16',  'CA': '36',  'ZA': '31',
        'AE': '95',  'CN': '3',   'DE': '43',  'IN': '22',  'NG': '19',
        'AU': '175', 'FR': '78',  'NL': '48',  'BR': '73',  'RU': '0',
        'TZ': '9',   'UG': '75',  'SA': '53',  'QA': '111', 'JP': '182',
        'SG': '196', 'TR': '62',  'ES': '56',  'IT': '86',  'SE': '46',
        'CH': '173', 'PL': '15',  'ID': '6',   'PH': '4'
    }
    initial_service_mappings = {
        'wa': 'wa', 'tg': 'tg', 'ig': 'ig', 'fb': 'fb', 'goo': 'go',
        'tt': 'lf', 'tw': 'tw', 'li': 'ot', 'pp': 'pp', 'airbnb': 'am', 'bolt': 'ol'
    }

    for fid, pid in initial_country_mappings.items():
        cursor.execute('INSERT OR IGNORE INTO mappings (frontend_id, provider_id, type) VALUES (?, ?, ?)', (fid, pid, 'country'))
    for fid, pid in initial_service_mappings.items():
        cursor.execute('INSERT OR IGNORE INTO mappings (frontend_id, provider_id, type) VALUES (?, ?, ?)', (fid, pid, 'service'))

    # Fix any wrong country IDs from previous seeds
    cursor.execute("UPDATE mappings SET provider_id='187' WHERE frontend_id='US' AND type='country'")
    cursor.execute("UPDATE mappings SET provider_id='9'   WHERE frontend_id='TZ' AND type='country'")
    cursor.execute("UPDATE mappings SET provider_id='182' WHERE frontend_id='JP' AND type='country'")
    cursor.execute("UPDATE mappings SET provider_id='196' WHERE frontend_id='SG' AND type='country'")
    cursor.execute("UPDATE mappings SET provider_id='86'  WHERE frontend_id='IT' AND type='country'")
    cursor.execute("UPDATE mappings SET provider_id='173' WHERE frontend_id='CH' AND type='country'")
    cursor.execute("DELETE FROM mappings WHERE frontend_id='KR' AND type='country'")

    # Patch existing quotas that might have the old default of 600
    cursor.execute("UPDATE quotas SET allowed_numbers = 0 WHERE allowed_numbers = 600")

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
    if quota is None:
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO quotas (user_id, allowed_numbers, used_numbers) VALUES (?, 0, 0)',
            (current_user['id'],)
        )
        conn.commit()
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

@app.route('/api/services', methods=['GET'])
@token_required
def get_services(current_user):
    if not HERO_SMS_API_KEY:
        # Simulation
        return jsonify([
            {"id": "wa", "name": "WhatsApp"},
            {"id": "tg", "name": "Telegram"},
            {"id": "ig", "name": "Instagram"},
            {"id": "fb", "name": "Facebook"},
            {"id": "go", "name": "Google"}
        ])

    res = call_hero_api('getServicesList')
    if isinstance(res, dict):
        services = [
            {"id": k, "name": v.get("en", k)}
            for k, v in res.items()
        ]
        return jsonify(services)
    return jsonify({'error': 'Could not fetch services', 'details': str(res)}), 500

@app.route('/api/countries', methods=['GET'])
@token_required
def get_countries(current_user):
    if not HERO_SMS_API_KEY:
        # Simulation
        return jsonify([
            {"id": "8", "name": "Kenya"},
            {"id": "12", "name": "USA"},
            {"id": "16", "name": "United Kingdom"},
            {"id": "36", "name": "Canada"}
        ])

    res = call_hero_api('getCountries')
    if isinstance(res, list):
        countries = [
            {"id": str(c.get("id")), "name": c.get("eng", str(c.get("id")))}
            for c in res
        ]
        return jsonify(countries)
    return jsonify({'error': 'Could not fetch countries', 'details': str(res)}), 500

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
        # Try to parse as JSON first, fallback to text
        try:
            return response.json()
        except:
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

def get_number_with_smart_pricing(p_service, p_country):
    """Try price tiers from cheapest to most expensive. Return first success."""
    price_tiers = [0.5, 1.0, 2.0, 3.0, 5.0, 10.0, 15.0]
    last_res = None
    for max_p in price_tiers:
        res = call_hero_api('getNumberV2', service=p_service, country=p_country, maxPrice=max_p)
        if isinstance(res, dict) and 'activationId' in res:
            return res
        last_res = res
        # Stop escalating if error is not "no numbers at this price"
        if isinstance(res, str) and 'NO_NUMBER' not in res.upper():
            break
        if isinstance(res, dict) and res.get('status') not in (None, 'NO_NUMBERS'):
            break
    return last_res

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
    setting = conn.execute("SELECT value FROM settings WHERE key = 'whitelist_required'").fetchone()
    whitelist_required = setting and setting['value'] == '1'

    if whitelist_required:
        whitelisted = conn.execute('SELECT 1 FROM user_whitelist WHERE user_id = ? AND service_id = ? AND country_id = ?',
                                  (current_user['id'], service_id, country_id)).fetchone()
        if not whitelisted:
            conn.close()
            return jsonify({'message': f'Service {service_id} for country {country_id} is not whitelisted for your account.'}), 403

    quota = conn.execute('SELECT * FROM quotas WHERE user_id = ?', (current_user['id'],)).fetchone()
    if quota is None:
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO quotas (user_id, allowed_numbers, used_numbers) VALUES (?, 0, 0)',
            (current_user['id'],)
        )
        conn.commit()
        quota = conn.execute('SELECT * FROM quotas WHERE user_id = ?', (current_user['id'],)).fetchone()

    if quota['used_numbers'] >= quota['allowed_numbers']:
        conn.close()
        return jsonify({'message': 'Quota exceeded! Please contact admin to increase your limit.'}), 403

    # Map frontend IDs to Provider IDs
    p_service = get_mapping(service_id, 'service')
    p_country = get_mapping(country_id, 'country')

    # For testing without real API key, allow simulation
    if not HERO_SMS_API_KEY:
        import random
        res = {
            "activationId": str(random.randint(100000, 999999)),
            "phoneNumber": f"1{random.randint(2000000000, 9999999999)}"
        }
    else:
        # Call Hero-SMS API V2
        res = get_number_with_smart_pricing(p_service, p_country)

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

    # For testing without real API key, allow simulation
    if not HERO_SMS_API_KEY:
        import random
        res = {
            "activationId": str(random.randint(100000, 999999)),
            "phoneNumber": f"1{random.randint(2000000000, 9999999999)}"
        }
    else:
        # Call Hero-SMS API V2
        res = get_number_with_smart_pricing(p_service, p_country)

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

    # Simulation for testing
    if not HERO_SMS_API_KEY:
        import random
        if random.random() > 0.7:
             res = {"sms": {"code": str(random.randint(100000, 999999))}}
        else:
             res = "STATUS_WAIT_CODE"
    else:
        # Reuse status logic
        res = call_hero_api('getStatusV2', id=order_id)

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
    if not HERO_SMS_API_KEY:
        res = "ACCESS_CANCEL"
    else:
        # cancelActivation — cancel activation (return money)
        res = call_hero_api('cancelActivation', id=order_id)

    if res == "ACCESS_CANCEL" or (isinstance(res, dict) and res.get('status') == 'SUCCESS'): # Allow simulation
        conn = get_db_connection()
        order = conn.execute('SELECT * FROM orders WHERE order_id_provider = ? AND user_id = ?', (order_id, current_user['id'])).fetchone()
        if order:
            cursor = conn.cursor()
            cursor.execute('UPDATE orders SET status = ? WHERE order_id_provider = ?', ('cancelled', order_id))
            if order['status'] == 'waiting':
                cursor.execute('UPDATE quotas SET used_numbers = used_numbers - 1 WHERE user_id = ?', (current_user['id'],))
            conn.commit()
        conn.close()
        return jsonify({'message': 'Order cancelled.'})
    else:
        return jsonify({'message': f'Failed to cancel order: {res}'}), 400

@app.route('/api/admin/order/<order_id>/cancel', methods=['POST'])
@token_required
def admin_cancel_order(current_user, order_id):
    if current_user.get('username') != 'admin':
        return jsonify({'message': 'Unauthorized'}), 403
    conn = get_db_connection()
    order = conn.execute('SELECT * FROM orders WHERE order_id_provider = ?', (order_id,)).fetchone()
    if not order:
        conn.close()
        return jsonify({'message': 'Order not found'}), 404
    res = call_hero_api('cancelActivation', id=order_id) if HERO_SMS_API_KEY else "ACCESS_CANCEL"
    if res == "ACCESS_CANCEL" or (isinstance(res, dict) and res.get('status') == 'SUCCESS'):
        cursor = conn.cursor()
        cursor.execute('UPDATE orders SET status = ? WHERE order_id_provider = ?', ('cancelled', order_id))
        if order['status'] == 'waiting' and order['user_id']:
            cursor.execute('UPDATE quotas SET used_numbers = used_numbers - 1 WHERE user_id = ?', (order['user_id'],))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Cancelled by admin.'})
    conn.close()
    return jsonify({'message': f'Provider cancel failed: {res}'}), 400

@app.route('/api/direct/cancel', methods=['POST'])
def direct_cancel():
    data = request.get_json()
    token = data.get('token')
    order_id = data.get('order_id')

    if not token or not order_id:
        return jsonify({'message': 'Missing parameters!'}), 400

    if not HERO_SMS_API_KEY:
        res = "ACCESS_CANCEL"
    else:
        # cancelActivation — cancel activation (return money)
        res = call_hero_api('cancelActivation', id=order_id)

    if res == "ACCESS_CANCEL" or (isinstance(res, dict) and res.get('status') == 'SUCCESS'): # Allow simulation
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
    # Simulation for testing
    if not HERO_SMS_API_KEY:
        import random
        if random.random() > 0.7:
             res = {"sms": {"code": str(random.randint(100000, 999999))}}
        else:
             res = "STATUS_WAIT_CODE"
    else:
        # Call Hero-SMS API V2
        res = call_hero_api('getStatusV2', id=order_id)

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

    COUNTRY_FLAGS = {
        'AE':'🇦🇪','AU':'🇦🇺','BR':'🇧🇷','CA':'🇨🇦','CH':'🇨🇭','CN':'🇨🇳',
        'DE':'🇩🇪','ES':'🇪🇸','FR':'🇫🇷','GB':'🇬🇧','ID':'🇮🇩','IN':'🇮🇳',
        'IT':'🇮🇹','JP':'🇯🇵','KE':'🇰🇪','NL':'🇳🇱','NG':'🇳🇬','PH':'🇵🇭',
        'PL':'🇵🇱','QA':'🇶🇦','RU':'🇷🇺','SA':'🇸🇦','SE':'🇸🇪','SG':'🇸🇬',
        'TR':'🇹🇷','TZ':'🇹🇿','UG':'🇺🇬','US':'🇺🇸','ZA':'🇿🇦'
    }

    @bot.message_handler(commands=['start', 'menu'])
    def send_welcome(message):
        if str(message.from_user.id) != ADMIN_TELEGRAM_ID:
            bot.reply_to(message, "Unauthorized.")
            return

        conn = get_db_connection()
        setting = conn.execute("SELECT value FROM settings WHERE key = 'whitelist_required'").fetchone()
        conn.close()
        wl_mode = setting and setting['value'] == '1'
        wl_label = '🔒 Whitelist: ON' if wl_mode else '🔓 Whitelist: OFF (open)'

        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("👥 Manage Users", callback_data="list_users"))
        markup.add(
            InlineKeyboardButton("📋 List Services", callback_data="list_services_0"),
            InlineKeyboardButton("🌍 List Countries", callback_data="list_countries_0")
        )
        markup.add(InlineKeyboardButton("💰 HeroSMS Balance", callback_data="check_balance"))
        markup.add(InlineKeyboardButton("🏷️ Check Prices", callback_data="view_prices"))
        markup.add(InlineKeyboardButton(wl_label, callback_data="toggle_whitelist"))
        markup.add(InlineKeyboardButton("🎟️ Direct Purchase Tokens", callback_data="manage_tokens"))
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

        elif call.data.startswith("user_orders_"):
            user_id = call.data.split("_")[2]
            conn = get_db_connection()
            orders = conn.execute(
                "SELECT * FROM orders WHERE user_id = ? AND status IN ('waiting','received') ORDER BY timestamp DESC LIMIT 10",
                (user_id,)
            ).fetchall()
            conn.close()
            markup = InlineKeyboardMarkup()
            if not orders:
                text = f"No active orders for user {user_id}."
            else:
                text = f"📋 Active orders (user {user_id}):\n\n"
                for o in orders:
                    text += f"• #{o['order_id_provider']} | {o['service_id']}@{o['country_id']} | {o['status']}\n  {o['phone_number']}\n\n"
                    markup.add(
                        InlineKeyboardButton(f"❌ Cancel #{o['order_id_provider'][:6]}", callback_data=f"adm_cancel_{o['order_id_provider']}_{user_id}"),
                        InlineKeyboardButton(f"🔄 Regen #{o['order_id_provider'][:6]}", callback_data=f"adm_regen_{o['order_id_provider']}_{user_id}_{o['service_id']}_{o['country_id']}")
                    )
            markup.add(InlineKeyboardButton("« Back to User", callback_data=f"user_{user_id}"))
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)

        elif call.data.startswith("user_"):
            user_id = call.data.split("_")[1]
            conn = get_db_connection()
            user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
            quota = conn.execute('SELECT * FROM quotas WHERE user_id = ?', (user_id,)).fetchone()

            if user and not quota:
                # Auto-create missing quota row
                conn.execute('INSERT INTO quotas (user_id, allowed_numbers, used_numbers) VALUES (?, 0, 0)', (user_id,))
                conn.commit()
                quota = conn.execute('SELECT * FROM quotas WHERE user_id = ?', (user_id,)).fetchone()

            conn.close()

            if not user:
                bot.answer_callback_query(call.id, "❌ User not found.")
                return

            text = f"👤 User: {user['username']}\n📊 Quota: {quota['used_numbers']} used / {quota['allowed_numbers']} allowed"
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("⚙️ Set Quota (replace)", callback_data=f"askquota_{user_id}"))
            markup.add(InlineKeyboardButton("➕ Add to Quota", callback_data=f"askquota_add_{user_id}"))
            markup.add(InlineKeyboardButton("📋 View Active Orders", callback_data=f"user_orders_{user_id}"))
            markup.add(InlineKeyboardButton("🛡️ Manage Whitelist", callback_data=f"whitelist_{user_id}"))
            markup.add(InlineKeyboardButton("« Back to Users", callback_data="list_users"))
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)

        elif call.data.startswith("adm_cancel_"):
            parts = call.data.split("_")
            order_id = parts[2]
            user_id = parts[3]
            conn = get_db_connection()
            order = conn.execute('SELECT * FROM orders WHERE order_id_provider = ?', (order_id,)).fetchone()
            res = call_hero_api('cancelActivation', id=order_id) if HERO_SMS_API_KEY else "ACCESS_CANCEL"
            if res == "ACCESS_CANCEL" or (isinstance(res, dict) and res.get('status') == 'SUCCESS'):
                cursor = conn.cursor()
                cursor.execute('UPDATE orders SET status = ? WHERE order_id_provider = ?', ('cancelled', order_id))
                if order and order['status'] == 'waiting' and order['user_id']:
                    cursor.execute('UPDATE quotas SET used_numbers = used_numbers - 1 WHERE user_id = ?', (order['user_id'],))
                conn.commit()
                bot.answer_callback_query(call.id, f"✅ Order {order_id[:8]} cancelled.")
            else:
                bot.answer_callback_query(call.id, f"❌ Failed: {str(res)[:80]}")
            conn.close()
            # Navigate back to orders list
            class Obj: pass
            new_call = Obj()
            new_call.data = f"user_orders_{user_id}"
            new_call.from_user = call.from_user
            new_call.message = call.message
            new_call.id = call.id
            callback_query(new_call)

        elif call.data.startswith("adm_regen_"):
            parts = call.data.split("_")
            old_order_id = parts[2]
            user_id = parts[3]
            service_id = parts[4]
            country_id = parts[5]
            # Cancel old
            if HERO_SMS_API_KEY:
                call_hero_api('cancelActivation', id=old_order_id)
            conn = get_db_connection()
            conn.execute('UPDATE orders SET status = ? WHERE order_id_provider = ?', ('cancelled', old_order_id))
            conn.commit()
            conn.close()
            # Get new
            p_service = get_mapping(service_id, 'service')
            p_country = get_mapping(country_id, 'country')
            if HERO_SMS_API_KEY:
                res = get_number_with_smart_pricing(p_service, p_country)
            else:
                import random
                res = {"activationId": str(random.randint(100000,999999)), "phoneNumber": f"1{random.randint(2000000000,9999999999)}"}
            if isinstance(res, dict) and 'activationId' in res:
                conn = get_db_connection()
                conn.execute(
                    'INSERT INTO orders (user_id, service_id, country_id, phone_number, order_id_provider, status) VALUES (?,?,?,?,?,?)',
                    (user_id, service_id, country_id, res['phoneNumber'], res['activationId'], 'waiting')
                )
                conn.commit()
                conn.close()
                bot.answer_callback_query(call.id, f"✅ New: {res['phoneNumber']}")
            else:
                bot.answer_callback_query(call.id, f"❌ No number: {str(res)[:100]}")
            # Navigate back to orders list
            class Obj: pass
            new_call = Obj()
            new_call.data = f"user_orders_{user_id}"
            new_call.from_user = call.from_user
            new_call.message = call.message
            new_call.id = call.id
            callback_query(new_call)

        elif call.data.startswith("askquota_add_"):
            user_id = call.data.split("_")[2]
            msg = bot.send_message(call.message.chat.id, "How many numbers to ADD to this user's quota?")
            bot.register_next_step_handler(msg, process_add_quota, user_id)

        elif call.data.startswith("askquota_"):
            user_id = call.data.split("_")[1]
            msg = bot.send_message(call.message.chat.id, "Enter the TOTAL number of allowed generations for this user:")
            bot.register_next_step_handler(msg, process_set_quota, user_id)

        elif call.data.startswith("whitelist_"):
            user_id = int(call.data.split("_")[1])
            page = int(call.data.split("_")[2]) if len(call.data.split("_")) > 2 else 0
            per_page = 5

            conn = get_db_connection()
            whitelist = conn.execute('SELECT * FROM user_whitelist WHERE user_id = ? LIMIT ? OFFSET ?',
                                   (user_id, per_page, page * per_page)).fetchall()
            total = conn.execute('SELECT COUNT(*) FROM user_whitelist WHERE user_id = ?', (user_id,)).fetchone()[0]
            conn.close()

            text = f"🛡️ Whitelist for User ID {user_id} (Page {page+1}):\n"
            markup = InlineKeyboardMarkup()
            for entry in whitelist:
                markup.add(InlineKeyboardButton(f"❌ Remove {entry['service_id']}@{entry['country_id']}",
                                               callback_data=f"rmwl_{entry['id']}_{page}"))

            nav_buttons = []
            if page > 0:
                nav_buttons.append(InlineKeyboardButton("« Prev", callback_data=f"whitelist_{user_id}_{page-1}"))
            if (page + 1) * per_page < total:
                nav_buttons.append(InlineKeyboardButton("Next »", callback_data=f"whitelist_{user_id}_{page+1}"))
            if nav_buttons:
                markup.add(*nav_buttons)

            markup.add(InlineKeyboardButton("➕ Add New Pair", callback_data=f"addwl_{user_id}"))
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
            page = call.data.split("_")[2] if len(call.data.split("_")) > 2 else 0
            conn = get_db_connection()
            row = conn.execute('SELECT user_id FROM user_whitelist WHERE id = ?', (wl_id,)).fetchone()
            user_id = row['user_id']
            conn.execute('DELETE FROM user_whitelist WHERE id = ?', (wl_id,))
            conn.commit()
            conn.close()
            bot.answer_callback_query(call.id, "✅ Removed from whitelist")
            # Stay on the same page
            callback_query(type('obj', (object,), {'data': f'whitelist_{user_id}_{page}', 'from_user': call.from_user, 'message': call.message, 'id': call.id}))

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
            conn = get_db_connection()
            setting = conn.execute("SELECT value FROM settings WHERE key = 'whitelist_required'").fetchone()
            conn.close()
            wl_mode = setting and setting['value'] == '1'
            wl_label = '🔒 Whitelist: ON' if wl_mode else '🔓 Whitelist: OFF (open)'

            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("👥 Manage Users", callback_data="list_users"))
            markup.add(
                InlineKeyboardButton("📋 List Services", callback_data="list_services_0"),
                InlineKeyboardButton("🌍 List Countries", callback_data="list_countries_0")
            )
            markup.add(InlineKeyboardButton("💰 HeroSMS Balance", callback_data="check_balance"))
            markup.add(InlineKeyboardButton("🏷️ Check Prices", callback_data="view_prices"))
            markup.add(InlineKeyboardButton(wl_label, callback_data="toggle_whitelist"))
            markup.add(InlineKeyboardButton("🎟️ Direct Purchase Tokens", callback_data="manage_tokens"))
            bot.edit_message_text("SMSKenya Admin Panel:", call.message.chat.id, call.message.message_id, reply_markup=markup)

        elif call.data.startswith("list_services_"):
            page = int(call.data.split("_")[2])
            per_page = 10
            conn = get_db_connection()
            services = conn.execute(
                "SELECT frontend_id, provider_id FROM mappings WHERE type='service' ORDER BY frontend_id LIMIT ? OFFSET ?",
                (per_page, page * per_page)
            ).fetchall()
            total = conn.execute("SELECT COUNT(*) FROM mappings WHERE type='service'").fetchone()[0]
            conn.close()
            lines = [f"  {s['frontend_id']} → {s['provider_id']}" for s in services]
            text = "📋 Service Mappings:\n\n" + "\n".join(lines)
            markup = InlineKeyboardMarkup()
            nav = []
            if page > 0:
                nav.append(InlineKeyboardButton("« Prev", callback_data=f"list_services_{page-1}"))
            if (page + 1) * per_page < total:
                nav.append(InlineKeyboardButton("Next »", callback_data=f"list_services_{page+1}"))
            if nav:
                markup.add(*nav)
            markup.add(InlineKeyboardButton("« Back", callback_data="main_menu"))
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)

        elif call.data.startswith("list_countries_"):
            page = int(call.data.split("_")[2])
            per_page = 10
            conn = get_db_connection()
            countries = conn.execute(
                "SELECT frontend_id, provider_id FROM mappings WHERE type='country' ORDER BY frontend_id LIMIT ? OFFSET ?",
                (per_page, page * per_page)
            ).fetchall()
            total = conn.execute("SELECT COUNT(*) FROM mappings WHERE type='country'").fetchone()[0]
            conn.close()
            lines = [f"  {COUNTRY_FLAGS.get(c['frontend_id'],'')} {c['frontend_id']} → {c['provider_id']}" for c in countries]
            text = "🌍 Country Mappings:\n\n" + "\n".join(lines)
            markup = InlineKeyboardMarkup()
            nav = []
            if page > 0:
                nav.append(InlineKeyboardButton("« Prev", callback_data=f"list_countries_{page-1}"))
            if (page + 1) * per_page < total:
                nav.append(InlineKeyboardButton("Next »", callback_data=f"list_countries_{page+1}"))
            if nav:
                markup.add(*nav)
            markup.add(InlineKeyboardButton("« Back", callback_data="main_menu"))
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)

        elif call.data == "toggle_whitelist":
            conn = get_db_connection()
            setting = conn.execute("SELECT value FROM settings WHERE key = 'whitelist_required'").fetchone()
            new_val = '0' if (setting and setting['value'] == '1') else '1'
            conn.execute("UPDATE settings SET value = ? WHERE key = 'whitelist_required'", (new_val,))
            conn.commit()
            conn.close()
            state = 'ENABLED (restricted)' if new_val == '1' else 'DISABLED (open to all)'
            bot.answer_callback_query(call.id, f'Whitelist mode: {state}')
            # Refresh menu
            callback_query(type('obj', (object,), {'data': 'main_menu', 'from_user': call.from_user, 'message': call.message, 'id': call.id}))

        elif call.data == "view_prices":
            markup = InlineKeyboardMarkup()
            svcs = ['wa', 'tg', 'ig', 'fb', 'goo', 'tt', 'pp', 'go']
            row = []
            for svc in svcs:
                row.append(InlineKeyboardButton(svc.upper(), callback_data=f"price_svc_{svc}"))
                if len(row) == 4:
                    markup.add(*row)
                    row = []
            if row:
                markup.add(*row)
            markup.add(InlineKeyboardButton("« Back", callback_data="main_menu"))
            bot.edit_message_text("Select service:", call.message.chat.id, call.message.message_id, reply_markup=markup)

        elif call.data.startswith("price_svc_"):
            svc = call.data.split("_")[2]
            conn = get_db_connection()
            countries = conn.execute("SELECT frontend_id, provider_id FROM mappings WHERE type='country' ORDER BY frontend_id").fetchall()
            conn.close()
            markup = InlineKeyboardMarkup()
            row = []
            for c in countries:
                flag = COUNTRY_FLAGS.get(c['frontend_id'], '')
                row.append(InlineKeyboardButton(f"{flag}{c['frontend_id']}", callback_data=f"pchk_{svc}_{c['frontend_id']}_{c['provider_id']}"))
                if len(row) == 3:
                    markup.add(*row)
                    row = []
            if row:
                markup.add(*row)
            markup.add(InlineKeyboardButton("« Back", callback_data="view_prices"))
            bot.edit_message_text(f"Select country for {svc.upper()}:", call.message.chat.id, call.message.message_id, reply_markup=markup)

        elif call.data.startswith("pchk_"):
            parts = call.data.split("_")
            svc = parts[1]
            fe_country = parts[2]
            prov_country = parts[3]
            res = call_hero_api('getPrices', service=svc, country=prov_country)
            if isinstance(res, dict) and str(prov_country) in res:
                sd = res[str(prov_country)].get(svc, {})
                cost = sd.get('cost', 'N/A')
                count = sd.get('count', 'N/A')
                text = f"🏷️ {svc.upper()} @ {fe_country} (ID:{prov_country})\n💰 Cost: ${cost}\n📦 Stock: {count}"
            else:
                text = f"No data for {svc}@{prov_country}.\nRaw: {str(res)[:300]}"
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("« Back to Countries", callback_data=f"price_svc_{svc}"))
            markup.add(InlineKeyboardButton("« Main Menu", callback_data="main_menu"))
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)

    def process_set_quota(message, user_id):
        try:
            amount = int(message.text.strip())
            conn = get_db_connection()
            existing = conn.execute('SELECT user_id FROM quotas WHERE user_id = ?', (user_id,)).fetchone()
            if existing:
                conn.execute('UPDATE quotas SET allowed_numbers = ? WHERE user_id = ?', (amount, user_id))
            else:
                conn.execute('INSERT INTO quotas (user_id, allowed_numbers, used_numbers) VALUES (?, ?, 0)', (user_id, amount))
            conn.commit()
            conn.close()
            bot.reply_to(message, f"✅ Quota set to {amount} for user {user_id}")
        except ValueError:
            bot.reply_to(message, "❌ Enter a valid number.")

    def process_add_quota(message, user_id):
        try:
            amount = int(message.text.strip())
            conn = get_db_connection()
            existing = conn.execute('SELECT * FROM quotas WHERE user_id = ?', (user_id,)).fetchone()
            if existing:
                new_total = existing['allowed_numbers'] + amount
                conn.execute('UPDATE quotas SET allowed_numbers = ? WHERE user_id = ?', (new_total, user_id))
                msg = f"✅ Added {amount}. New total: {new_total}"
            else:
                conn.execute('INSERT INTO quotas (user_id, allowed_numbers, used_numbers) VALUES (?, ?, 0)', (user_id, amount))
                msg = f"✅ Created quota: {amount}"
            conn.commit()
            conn.close()
            bot.reply_to(message, msg)
        except ValueError:
            bot.reply_to(message, "❌ Enter a valid number.")

    def process_check_prices(message):
        try:
            parts = message.text.split()
            if len(parts) == 2:
                service, country = parts
                res = call_hero_api('getPrices', service=service, country=country)

                if isinstance(res, dict) and str(country) in res:
                    service_data = res[str(country)].get(service, {})
                    cost = service_data.get('cost', 'N/A')
                    count = service_data.get('count', 'N/A')
                    text = f"🏷️ {service}@{country}: ${cost}, {count} available"
                else:
                    text = f"📝 Provider Response: {res}"

                bot.reply_to(message, text)
            else:
                bot.reply_to(message, "❌ Format: `service country` (e.g., `wa 8`)")
        except Exception as e:
            bot.reply_to(message, f"❌ Error: {str(e)}")

    def process_add_whitelist(message, user_id):
        try:
            parts = message.text.split()
            if len(parts) == 2:
                service, country = parts
                conn = get_db_connection()
                conn.execute('INSERT OR IGNORE INTO user_whitelist (user_id, service_id, country_id) VALUES (?, ?, ?)',
                             (user_id, service, country))
                conn.commit()
                conn.close()
                bot.reply_to(message, f"✅ Added {service}@{country} to whitelist.")
            else:
                bot.reply_to(message, "❌ Format: `service country` (e.g., `wa KE`)")
        except Exception as e:
            bot.reply_to(message, f"❌ Error: {str(e)}")

    def run_bot():
        print("Starting Telegram Bot...")
        bot.infinity_polling()

    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()

# --- Static Files & Single Page App Handling ---

@app.route('/api/prices', methods=['GET'])
def get_prices():
    """Returns live prices from HeroSMS for all our mapped countries."""
    if not HERO_SMS_API_KEY:
        return jsonify({'error': 'No API key configured'}), 503

    res = call_hero_api('getPrices')
    if not isinstance(res, dict):
        return jsonify({'error': 'Failed to fetch prices', 'raw': str(res)}), 500

    our_countries = {
        'AE':'95','AU':'175','BR':'73','CA':'36','CH':'173','CN':'3',
        'DE':'43','ES':'56','FR':'78','GB':'16','ID':'6','IN':'22',
        'IT':'86','JP':'182','KE':'8','NG':'19','NL':'48','PH':'4',
        'PL':'15','QA':'111','RU':'0','SA':'53','SE':'46','SG':'196',
        'TR':'62','TZ':'9','UG':'75','US':'187','ZA':'31'
    }
    id_to_code = {v: k for k, v in our_countries.items()}

    # Restructure: service -> country_code -> {cost, count}
    summary = {}
    for cid, services in res.items():
        code = id_to_code.get(cid)
        if not code:
            continue
        for svc, info in services.items():
            if svc not in summary:
                summary[svc] = {}
            summary[svc][code] = {
                'cost': info.get('cost'),
                'count': info.get('count', 0)
            }

    return jsonify(summary)




@app.route('/api/pricing', methods=['GET'])
def get_pricing():
    """Return our selling prices (KES + USD) for all service/country combos."""
    conn = get_db_connection()
    rows = conn.execute('SELECT * FROM pricing').fetchall()
    conn.close()

    result = {}
    for row in rows:
        svc = row['service_id']
        cid = row['country_id']
        if svc not in result:
            result[svc] = {}
        result[svc][cid] = {
            'kes': row['price_kes'],
            'usd': row['price_usd']
        }
    return jsonify(result)


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
