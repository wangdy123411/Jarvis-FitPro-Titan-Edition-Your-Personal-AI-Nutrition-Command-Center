import sqlite3
import pandas as pd
import shutil
import os
from .config import DB_FILE, get_current_time

# === 🛠️ 实时备份逻辑 (不变) ===
def _trigger_realtime_backup():
    backup_dir = "backups"
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    mirror_path = os.path.join(backup_dir, "jarvis_latest_mirror.db")
    try:
        shutil.copy2(DB_FILE, mirror_path)
    except Exception as e:
        print(f"❌ Backup Failed: {e}")

# === 🏗️ 数据库初始化 (V3 架构) ===
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # 1. 用户表 (新增)
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  username TEXT UNIQUE, 
                  password TEXT, 
                  created_at TEXT)''')
                  
    # 2. 饮食表 (增加 user_id)
    c.execute('''CREATE TABLE IF NOT EXISTS meals 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  user_id INTEGER,  -- 👈 新增归属人ID
                  date TEXT, time TEXT, food_name TEXT, 
                  calories REAL, protein REAL, carbs REAL, fat REAL, advice TEXT)''')
                  
    # 3. 身体数据表 (增加 user_id)
    c.execute('''CREATE TABLE IF NOT EXISTS body_stats 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  user_id INTEGER,  -- 👈 新增
                  date TEXT, weight REAL, body_fat REAL, muscle REAL, 
                  water_rate REAL, bmr INTEGER, visceral_fat INTEGER)''')
                  
    # 4. 战报表 (增加 user_id)
    c.execute('''CREATE TABLE IF NOT EXISTS daily_reports 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  user_id INTEGER,  -- 👈 新增
                  date TEXT, content TEXT, created_at TEXT)''')
                  
    conn.commit()
    conn.close()

# === 写入函数 (必须传入 user_id) ===

def save_meal(user_id, data):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    date_str, time_str = get_current_time()
    c.execute("INSERT INTO meals (user_id, date, time, food_name, calories, protein, carbs, fat, advice) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
              (user_id, date_str, time_str, data['food_name'], data['calories'], data['protein'], data['carbs'], data['fat'], data['advice']))
    conn.commit()
    conn.close()
    _trigger_realtime_backup()

def save_body_stats(user_id, w, f, m):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    date_str, _ = get_current_time()
    # 只删除该用户当天的旧数据
    c.execute("DELETE FROM body_stats WHERE user_id=? AND date=?", (user_id, date_str))
    c.execute("INSERT INTO body_stats (user_id, date, weight, body_fat, muscle, water_rate, bmr, visceral_fat) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", 
              (user_id, date_str, w, f, m, 0, 0, 0))
    conn.commit()
    conn.close()
    _trigger_realtime_backup()

def save_report(user_id, content):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    date_str, time_str = get_current_time()
    created_at = f"{date_str} {time_str}"
    c.execute("INSERT INTO daily_reports (user_id, date, content, created_at) VALUES (?, ?, ?, ?)", 
              (user_id, date_str, content, created_at))
    conn.commit()
    conn.close()
    _trigger_realtime_backup()

def delete_meal(meal_id):
    # 删除逻辑暂时不需要 user_id，因为 id 是唯一的，但为了安全其实应该校验
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM meals WHERE id=?", (meal_id,))
    conn.commit()
    conn.close()
    _trigger_realtime_backup()

# === 读取函数 (只读取当前用户的数据) ===

def get_today_meals(user_id):
    conn = sqlite3.connect(DB_FILE)
    date_str, _ = get_current_time()
    # WHERE user_id = ?
    df = pd.read_sql_query(f"SELECT * FROM meals WHERE user_id={user_id} AND date='{date_str}' ORDER BY id DESC", conn)
    conn.close()
    return df

def get_body_history(user_id, days=14):
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query(f"SELECT * FROM body_stats WHERE user_id={user_id} ORDER BY date ASC LIMIT {days}", conn)
    conn.close()
    return df

def get_report_history(user_id):
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query(f"SELECT * FROM daily_reports WHERE user_id={user_id} ORDER BY created_at DESC", conn)
    conn.close()
    return df