import streamlit as st
import pandas as pd
import base64
from openai import OpenAI
import datetime
import json
import sqlite3
from PIL import Image
import io
import time
import random
import os
db_path = "jarvis_pro_v2.db"
# ================= ⚡ 配置区域 =================
API_KEY = "sk-cedf4c8f0d1042138740dbce8fbd0a30" # 替换你的 Key
BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
MODEL_NAME = "qwen-vl-max"
TEXT_MODEL = "qwen-plus"
DB_FILE = "jarvis_pro_v2.db"

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
# === 📥 紧急数据导出工具 ===

if os.path.exists(db_path):
    with open(db_path, "rb") as f:
        st.download_button(
            label="📥 点击下载我的数据库备份 (Save Data)",
            data=f,
            file_name="jarvis_backup.db",
            mime="application/octet-stream"
        )
else:
    st.warning("⚠️ 暂无数据库文件 (No Database Found)")

# ================= 🖼️ 激励素材 =================
HERO_IMAGES = [
    {"url": "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?q=80&w=1200&auto=format&fit=crop", "text": "DISCIPLINE EQUALS FREEDOM"},
    {"url": "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?q=80&w=1200&auto=format&fit=crop", "text": "YOUR ONLY LIMIT IS YOU"},
    {"url": "https://images.unsplash.com/photo-1599058917212-d750089bc07e?q=80&w=1200&auto=format&fit=crop", "text": "EARN YOUR BODY"},
]

# ================= 🎨 终极 CSS (修复侧边栏白底问题) =================
def inject_final_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Oswald:wght@400;700&family=Roboto+Condensed:wght@400;700&display=swap');

        /* --- 1. 暴力强制黑魂主题 --- */
        /* 主界面 */
        .stApp {
            background-color: #050505 !important;
            color: #e0e0e0 !important;
            font-family: 'Roboto Condensed', sans-serif;
        }
        
        /* 修复：侧边栏强制变黑 */
        section[data-testid="stSidebar"] {
            background-color: #000000 !important;
            border-right: 1px solid #333;
        }
        
        /* 修复：侧边栏里的文字颜色 */
        section[data-testid="stSidebar"] p, 
        section[data-testid="stSidebar"] span,
        section[data-testid="stSidebar"] label {
            color: #b0b0b0 !important;
        }
        
        /* 隐藏顶部红条和菜单 */
        header {visibility: hidden;}
        
        /* --- 2. 字体与标题 --- */
        h1, h2, h3 {
            font-family: 'Oswald', sans-serif !important;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: #ffffff !important;
        }

        /* --- 3. 扫描区优化 --- */
        .stFileUploader {
            border: 2px dashed #FF5722;
            border-radius: 12px;
            padding: 20px;
            background: rgba(255, 87, 34, 0.08);
        }
        .stFileUploader:hover {
            border-color: #FF8A65;
            background: rgba(255, 87, 34, 0.15);
        }
        div[data-testid="stFileUploader"] section > div { padding-top: 0; }

        /* --- 4. 泰坦卡片 (Titan Card) --- */
        .titan-card {
            background: #121212;
            border: 1px solid #333;
            border-left: 6px solid #FF5722;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 10px 20px rgba(0,0,0,0.6);
            position: relative;
        }
        
        /* 关键：防止 HTML 渲染错位 */
        .titan-card * {
            box-sizing: border-box;
        }

        .food-title {
            font-family: 'Oswald', sans-serif;
            font-size: 24px;
            color: #fff;
            margin: 0 0 5px 0;
        }
        
        .scan-time {
            font-family: monospace;
            font-size: 12px;
            color: #666;
            margin-bottom: 15px;
        }

        /* 数据网格布局 */
        .data-grid {
            display: flex;
            align-items: flex-end;
            justify-content: space-between;
            background: rgba(255,255,255,0.03);
            padding: 15px;
            border-radius: 8px;
        }

        .cal-val {
            font-family: 'Oswald', sans-serif;
            font-size: 48px;
            font-weight: 700;
            color: #FF5722;
            line-height: 1;
        }
        .cal-label {
            font-size: 12px;
            color: #888;
            font-weight: bold;
            letter-spacing: 2px;
        }

        .macro-row {
            display: flex;
            gap: 20px;
        }
        .macro-item {
            text-align: center;
        }
        .macro-val {
            font-family: 'Oswald', sans-serif;
            font-size: 20px;
            color: #fff;
            font-weight: bold;
        }
        .macro-label {
            font-size: 10px;
            color: #aaa;
            font-weight: bold;
        }
        .highlight { color: #FF5722; }

        .advice-box {
            margin-top: 15px;
            font-size: 14px;
            color: #ccc;
            font-style: italic;
            border-top: 1px dashed #333;
            padding-top: 10px;
        }

        /* --- 5. 按钮 --- */
        button[kind="primary"] {
            background: linear-gradient(135deg, #FF5722, #D84315) !important;
            color: white !important;
            font-family: 'Oswald', sans-serif !important;
            font-size: 18px !important;
            padding: 0.6rem 2rem !important;
            border-radius: 8px !important;
            text-transform: uppercase;
            border: none;
            width: 100%;
        }
        button[kind="primary"]:hover {
            transform: scale(1.02);
            box-shadow: 0 0 20px rgba(255, 87, 34, 0.5);
        }

        /* --- 6. Tabs --- */
        .stTabs [data-baseweb="tab-list"] { gap: 8px; }
        .stTabs [data-baseweb="tab"] {
            height: 45px;
            background-color: #1a1a1a;
            border-radius: 6px;
            color: #888;
            font-family: 'Oswald', sans-serif;
            font-size: 16px;
            border: 1px solid #333;
        }
        .stTabs [aria-selected="true"] {
            background-color: #FF5722 !important;
            color: #fff !important;
            border-color: #FF5722;
        }
    </style>
    """, unsafe_allow_html=True)

# ================= 💾 数据库 =================
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS meals (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, time TEXT, food_name TEXT, calories REAL, protein REAL, carbs REAL, fat REAL, advice TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS body_stats (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, weight REAL, body_fat REAL, muscle REAL, water_rate REAL, bmr INTEGER, visceral_fat INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS daily_reports (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, content TEXT, created_at TEXT)''')
    conn.commit()
    conn.close()

def save_meal(data):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    now = datetime.datetime.now()
    c.execute("INSERT INTO meals (date, time, food_name, calories, protein, carbs, fat, advice) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
              (now.strftime("%Y-%m-%d"), now.strftime("%H:%M"), data['food_name'], data['calories'], data['protein'], data['carbs'], data['fat'], data['advice']))
    conn.commit()
    conn.close()

def save_body_stats(w, f, m):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    c.execute("DELETE FROM body_stats WHERE date=?", (today,))
    c.execute("INSERT INTO body_stats (date, weight, body_fat, muscle, water_rate, bmr, visceral_fat) VALUES (?, ?, ?, ?, ?, ?, ?)", (today, w, f, m, 0, 0, 0))
    conn.commit()
    conn.close()

def save_report(content):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO daily_reports (date, content, created_at) VALUES (?, ?, ?)", (today, content, now_str))
    conn.commit()
    conn.close()

def get_today_meals():
    conn = sqlite3.connect(DB_FILE)
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    df = pd.read_sql_query(f"SELECT * FROM meals WHERE date = '{today}' ORDER BY id DESC", conn)
    conn.close()
    return df

def get_body_history(days=14):
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query(f"SELECT * FROM body_stats ORDER BY date ASC LIMIT {days}", conn)
    conn.close()
    return df

def get_report_history():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM daily_reports ORDER BY created_at DESC", conn)
    conn.close()
    return df

def delete_meal(meal_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM meals WHERE id=?", (meal_id,))
    conn.commit()
    conn.close()

# ================= 🧠 AI 核心 =================
def process_image(image_file):
    image = Image.open(image_file)
    if image.mode in ("RGBA", "P"): image = image.convert("RGB")
    image.thumbnail((512, 512))
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG", quality=60)
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

def analyze_food(image_file, desc):
    b64 = process_image(image_file)
    prompt = f"""
    User Desc: {desc}.
    Estimate calories and macros accurately based on image.
    Output JSON: {{"food_name": "Dish Name", "calories": 0, "protein": 0, "carbs": 0, "fat": 0, "advice": "Short advice"}}
    """
    res = client.chat.completions.create(
        model=MODEL_NAME, messages=[{"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}]}], temperature=0.01
    )
    return json.loads(res.choices[0].message.content.replace("```json","").replace("```",""))

def generate_smart_report(meals_df, body_df, goal):
    today_sum = "No Records"
    if not meals_df.empty:
        today_sum = f"Total: {int(meals_df['calories'].sum())}kcal (Protein: {int(meals_df['protein'].sum())}g)"
    
    body_trend = "No Trend"
    if len(body_df) >= 2:
        last, prev = body_df.iloc[-1], body_df.iloc[-2]
        diff = round(last['weight'] - prev['weight'], 2)
        body_trend = f"Weight change: {diff}kg"
    elif not body_df.empty:
        body_trend = f"Current Weight: {body_df.iloc[-1]['weight']}kg"

    prompt = f"""
    Role: Jarvis Fitness Coach. Goal: {goal}.
    Today: {today_sum}. Trend: {body_trend}.
    Generate: 1. Review of today. 2. 3 Actionable tips for tomorrow.
    Style: Hardcore, professional, concise. Markdown.
    """
    res = client.chat.completions.create(model=TEXT_MODEL, messages=[{"role": "user", "content": prompt}])
    return res.choices[0].message.content

# ================= 📱 主界面 =================
st.set_page_config(page_title="Jarvis Titan", page_icon="⚡", layout="centered")
inject_final_css()
init_db()

# 1. Hero Banner
hero = random.choice(HERO_IMAGES)
st.markdown(f"""
<div style="position:relative; height:240px; border-radius:15px; overflow:hidden; margin-bottom:20px; border-bottom: 4px solid #FF5722; box-shadow: 0 10px 30px rgba(0,0,0,0.5);">
    <img src="{hero['url']}" style="width:100%; height:100%; object-fit:cover; filter:brightness(0.5);">
    <div style="position:absolute; bottom:20px; left:25px; color:#fff; font-family:'Oswald'; font-size:36px; font-weight:bold; letter-spacing: 1px;">
        {hero['text']}
    </div>
</div>
""", unsafe_allow_html=True)

# 2. Sidebar (侧边栏) - 修复 ValueError
with st.sidebar:
    st.header("⚙️ CONTROL PANEL")
    goal = st.selectbox("Current Mode", ["BULK", "CUT", "MAINTAIN"])
    st.divider()
    
    # Get Data
    body_df = get_body_history()
    
    # 🔥 修复逻辑：先定义默认值，再判断 DataFrame 是否为空
    # 绝对不要直接在 widget 里写 if last else ...
    d_w = 70.0
    if not body_df.empty:
        last_row = body_df.iloc[-1]
        d_w = float(last_row['weight'])
        
    st.markdown(f"### Current Weight: `{d_w} KG`")
    
    if not body_df.empty:
        st.line_chart(body_df.set_index('date')['weight'], color="#FF5722", height=150)

# 3. Core Tabs
tab1, tab2, tab3 = st.tabs(["🔥 DIET SCAN", "📊 BODY STATS", "📑 DAILY REPORT"])

# --- Tab 1: Diet (修复 HTML 乱码) ---
with tab1:
    st.markdown("### 📡 CAPTURE INTAKE")
    
    with st.container():
        img = st.file_uploader("Click to upload food", type=["jpg","png"], label_visibility="collapsed")
        desc = st.text_input("Extra Info", placeholder="e.g. 200g Steak...", label_visibility="collapsed")
        
        if img:
            st.markdown(f"<div style='text-align:center; color:#FF5722; margin-bottom:10px;'>📸 IMAGE LOADED</div>", unsafe_allow_html=True)
            if st.button("🚀 INITIATE SCAN", type="primary"):
                with st.spinner("JARVIS IS ANALYZING..."):
                    try:
                        data = analyze_food(img, desc)
                        save_meal(data)
                        st.toast("Data Logged", icon="✅")
                        time.sleep(0.5)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")

    st.divider()
    
    meals = get_today_meals()
    if not meals.empty:
        # Summary Bar
        t_cal = int(meals['calories'].sum())
        t_pro = int(meals['protein'].sum())
        
        # 扁平化 HTML (避免缩进问题)
        summary_html = f"""<div style="display:flex; justify-content:space-between; align-items:flex-end; margin-bottom:20px;">
<span style="font-family:'Oswald'; font-size:20px; color:#fff;">TODAY'S TOTAL</span>
<div><span style="font-family:'Oswald'; font-size:32px; color:#FF5722;">{t_cal}</span> <span style="font-size:12px; color:#888;">KCAL</span>
<span style="margin:0 10px; color:#333;">|</span>
<span style="font-family:'Oswald'; font-size:32px; color:#fff;">{t_pro}g</span> <span style="font-size:12px; color:#888;">PRO</span></div></div>"""
        
        st.markdown(summary_html, unsafe_allow_html=True)

        for _, row in meals.iterrows():
            # 🔥 终极修复：将 HTML 拼接成一行，或者完全不要前面的缩进
            # 这样 Markdown 就绝对不会把它当成代码块显示了
            card_html = f"""<div class="titan-card">
<div style="margin-bottom:15px; border-bottom:1px solid #333; padding-bottom:10px;">
<h3 class="food-title">{row['food_name']}</h3>
<div class="scan-time">SCAN TIME: {row['time']}</div>
</div>
<div class="data-grid">
<div><div class="cal-val">{int(row['calories'])}</div><div class="cal-label">CALORIES</div></div>
<div class="macro-row">
<div class="macro-item"><div class="macro-val highlight">{row['protein']}</div><div class="macro-label">PRO</div></div>
<div class="macro-item"><div class="macro-val">{row['carbs']}</div><div class="macro-label">CARB</div></div>
<div class="macro-item"><div class="macro-val">{row['fat']}</div><div class="macro-label">FAT</div></div>
</div></div>
<div class="advice-box">💡 {row['advice']}</div></div>"""
            
            st.markdown(card_html, unsafe_allow_html=True)
            
            if st.button("DELETE", key=f"del_{row['id']}"):
                delete_meal(row['id'])
                st.rerun()
    else:
        st.info("No records today. Start scanning.")

# --- Tab 2: Body Stats (修复 Ambiguous) ---
with tab2:
    st.markdown("### 📝 SYNC BODY DATA")
    with st.form("body_form"):
        c1, c2, c3 = st.columns(3)
        
        # 🔥 逻辑修复：数据解包
        val_w, val_f, val_m = 70.0, 20.0, 30.0
        if not body_df.empty:
            last = body_df.iloc[-1]
            val_w = float(last['weight'])
            val_f = float(last['body_fat'])
            val_m = float(last['muscle'])

        w = c1.number_input("Weight (KG)", value=val_w, step=0.1)
        f = c2.number_input("Body Fat (%)", value=val_f, step=0.1)
        m = c3.number_input("Muscle (KG)", value=val_m, step=0.1)
        
        if st.form_submit_button("💾 SAVE DATA", type="primary"):
            save_body_stats(w, f, m)
            st.success("Updated Successfully!")
            time.sleep(0.5)
            st.rerun()

# --- Tab 3: Report ---
with tab3:
    st.markdown("### 📑 DAILY BRIEFING")
    if st.button("⚡ GENERATE REPORT", type="primary"):
        if meals.empty:
            st.warning("No diet data available.")
        else:
            with st.spinner("ANALYZING..."):
                rep = generate_smart_report(meals, body_df, goal)
                save_report(rep)
                st.rerun()
    
    st.divider()
    reports = get_report_history()
    if not reports.empty:
        for _, row in reports.iterrows():
            with st.expander(f"📅 {row['date']} REPORT"):
                st.markdown(row['content'])
    else:
        st.info("No reports yet.")
