
import sqlite3
from datetime import datetime

DB_FILE = "bot_data.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        join_date TEXT,
        ai_uses INTEGER DEFAULT 0
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS invites (
        referrer_id INTEGER,
        invited_id INTEGER PRIMARY KEY
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS vip_users (
        user_id INTEGER PRIMARY KEY
    )""")

        # جدول پروکسی‌ها
    c.execute("""CREATE TABLE IF NOT EXISTS proxies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        proxy TEXT
    )""")

    # جدول کاربران فعال (برای user_ids)
    c.execute("""CREATE TABLE IF NOT EXISTS bot_users (
        user_id INTEGER PRIMARY KEY
    )""")


    conn.commit()
    conn.close()

def save_user(user_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (user_id, join_date) VALUES (?, ?)", 
              (user_id, datetime.now().strftime("%Y-%m-%d")))
    conn.commit()
    conn.close()

def increment_ai_usage(user_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE users SET ai_uses = ai_uses + 1 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def get_user_info(user_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT join_date, ai_uses FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row

def save_invite(referrer_id, invited_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO invites (referrer_id, invited_id) VALUES (?, ?)", 
              (referrer_id, invited_id))
    conn.commit()
    conn.close()

def get_invite_count(referrer_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM invites WHERE referrer_id = ?", (referrer_id,))
    count = c.fetchone()[0]
    conn.close()
    return count

def add_vip(user_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO vip_users (user_id) VALUES (?)", (user_id,))
    conn.commit()
    conn.close()

def is_vip(user_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT 1 FROM vip_users WHERE user_id = ?", (user_id,))
    result = c.fetchone()
    conn.close()
    return bool(result)

def add_proxy_to_db(proxy):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO proxies (proxy) VALUES (?)", (proxy,))
    conn.commit()
    conn.close()

def remove_proxy_from_db(proxy):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM proxies WHERE proxy=?", (proxy,))
    conn.commit()
    conn.close()

def get_all_proxies():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT proxy FROM proxies")
    proxies = [row[0] for row in c.fetchall()]
    conn.close()
    return proxies

def save_user_id(user_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO bot_users (user_id) VALUES (?)", (user_id,))
    conn.commit()
    conn.close()

def get_all_user_ids():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT user_id FROM bot_users")
    users = {row[0] for row in c.fetchall()}
    conn.close()
    return users

def get_all_vip_users():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS vip_users (user_id INTEGER PRIMARY KEY)")
    c.execute("SELECT user_id FROM vip_users")
    result = {row[0] for row in c.fetchall()}
    conn.close()
    return result


def get_all_bot_users():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS bot_users (user_id INTEGER PRIMARY KEY)")
    c.execute("SELECT user_id FROM bot_users")
    result = {row[0] for row in c.fetchall()}
    conn.close()
    return result
