import streamlit as st
import hashlib
import sqlite3
from .config import DB_FILE, get_current_time

def make_hashes(password):
    """将明文密码加密为 SHA256 哈希值"""
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    """验证密码是否正确"""
    if make_hashes(password) == hashed_text:
        return True
    return False

def create_user(username, password):
    """注册新用户"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # 检查用户名是否存在
    c.execute('SELECT * FROM users WHERE username =?', (username,))
    if c.fetchall():
        conn.close()
        return False, "Username already exists!"
        
    hashed_pw = make_hashes(password)
    date_str, _ = get_current_time()
    
    c.execute('INSERT INTO users(username, password, created_at) VALUES (?,?,?)', 
              (username, hashed_pw, date_str))
    conn.commit()
    conn.close()
    return True, "Account created successfully!"

def login_user(username, password):
    """用户登录校验"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    hashed_pw = make_hashes(password)
    
    # 查找用户
    c.execute('SELECT * FROM users WHERE username =? AND password =?', (username, hashed_pw))
    data = c.fetchall()
    conn.close()
    
    if data:
        # 返回用户信息 (id, username)
        return data[0] 
    return None