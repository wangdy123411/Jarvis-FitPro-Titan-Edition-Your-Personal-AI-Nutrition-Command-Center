import streamlit as st
import time
import random
import os
import base64
import textwrap

# 引入新模块 auth
from modules import config, database, ai_engine, ui, automation, auth

# === 初始化 ===
st.set_page_config(page_title="Jarvis Titan", page_icon="🦍", layout="centered")
ui.inject_css()
database.init_db()
automation.start_background_scheduler()

# === Session 状态管理 ===
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_info' not in st.session_state:
    st.session_state['user_info'] = None

# === 🚪 登录/注册界面 (The Gateway) ===
def login_page():
    st.markdown("""
    <div style="text-align: center; margin-top: 50px; margin-bottom: 30px;">
        <h1 style="font-size: 60px; color: #FF5722; text-shadow: 0 0 20px rgba(255,87,34,0.5);">JARVIS ACCESS</h1>
        <p style="color: #666; letter-spacing: 2px;">SECURE FITNESS PROTOCOL // LOGIN REQUIRED</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 使用 Tabs 分离登录和注册
    tab_login, tab_signup = st.tabs(["🔓 LOGIN", "📝 JOIN PROTOCOL"])
    
    with tab_login:
        with st.form("login_form"):
            username = st.text_input("CODENAME (Username)")
            password = st.text_input("ACCESS KEY (Password)", type="password")
            
            if st.form_submit_button("🚀 AUTHENTICATE", type="primary"):
                user = auth.login_user(username, password)
                if user:
                    # 🟢 新增：登录成功后，设置 Session 和 URL 参数
                    st.session_state['logged_in'] = True
                    st.session_state['user_info'] = user
                    
                    # 这是一个 Streamlit 的原生功能，可以在 URL 里存参数
                    # 这样刷新页面后，我们可以读回来
                    st.query_params["user"] = user[1]  # 存用户名
                    st.query_params["token"] = "valid" # 简单验证（可做更复杂的加密）
                    
                    st.success(f"WELCOME BACK, COMMANDER {user[1].upper()}.")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("ACCESS DENIED.")

    with tab_signup:
        with st.form("signup_form"):
            new_user = st.text_input("CHOOSE CODENAME")
            new_pass = st.text_input("SET ACCESS KEY", type="password")
            confirm_pass = st.text_input("CONFIRM KEY", type="password")
            if st.form_submit_button("🔥 INITIATE SEQUENCE"):
                if new_pass != confirm_pass:
                    st.error("KEYS DO NOT MATCH.")
                elif len(new_pass) < 4:
                    st.error("KEY TOO WEAK.")
                else:
                    success, msg = auth.create_user(new_user, new_pass)
                    if success:
                        st.success("IDENTITY ESTABLISHED. PLEASE LOGIN.")
                    else:
                        st.error(f"FAILURE: {msg}")

# === 🏠 主程序 (The Core) ===
def main_app():
    # 获取当前用户ID
    current_user_id = st.session_state['user_info'][0]
    current_username = st.session_state['user_info'][1]

    # --- 侧边栏 ---
  # 在 main_app 函数的侧边栏 (with st.sidebar:)
    with st.sidebar:
        st.divider()
    st.markdown("### 🧹 数据库清洁工 (Cleaner)")
    
    if st.button("♻️ 执行去重 (Remove Duplicates)"):
        import sqlite3
        conn = sqlite3.connect(config.DB_FILE)
        c = conn.cursor()
        
        # 1. 清理饮食记录 (Meals)
        # 逻辑：如果 用户、日期、时间、食物名、卡路里 都一样，只保留 ID 最小的那条
        c.execute("""
            DELETE FROM meals 
            WHERE id NOT IN (
                SELECT MIN(id) 
                FROM meals 
                GROUP BY user_id, date, time, food_name, calories
            )
        """)
        deleted_meals = c.rowcount
        
        # 2. 清理身体数据 (Body Stats)
        # 逻辑：同一天如果有多条记录，只保留最早录入的那条
        c.execute("""
            DELETE FROM body_stats 
            WHERE id NOT IN (
                SELECT MIN(id) 
                FROM body_stats 
                GROUP BY user_id, date
            )
        """)
        deleted_stats = c.rowcount
        
        conn.commit()
        conn.close()
        
        st.success(f"🧹 清理完成！删除了 {deleted_meals} 条重复饮食记录，{deleted_stats} 条重复身体数据。")
        time.sleep(2)
        st.rerun()
        
        st.header(f"👤 {current_username.upper()}")
        
        # 🔴 修改后的 Logout 逻辑
        if st.button("🔒 LOGOUT"):
            # 1. 清空 URL 参数（这一步最关键！撕掉免死金牌）
            st.query_params.clear()
            
            # 2. 清空登录状态
            st.session_state['logged_in'] = False
            st.session_state['user_info'] = None
            
            # 3. 强制刷新页面
            st.rerun()
            
        st.divider()
        st.header("⚙️ CONTROL PANEL")
        goal = st.selectbox("Current Mode", ["BULK", "CUT", "MAINTAIN"])
        st.divider()
        
        # ⚠️ 注意：这里传入了 current_user_id
        body_df = database.get_body_history(current_user_id)
        
        d_w = 70.0
        if not body_df.empty:
            d_w = float(body_df.iloc[-1]['weight'])
            
        st.markdown(f"### Current Weight: `{d_w} KG`")
        if not body_df.empty:
            st.line_chart(body_df.set_index('date')['weight'], color="#FF5722", height=150)
            
        # 安全备份按钮
        st.divider()
        st.markdown("### 🛡️ DATA SAFETY")
        try:
            with open(config.DB_FILE, "rb") as f:
                st.download_button(
                    label="📥 BACKUP DATABASE",
                    data=f,
                    file_name=f"jarvis_backup_{config.get_current_time()[0]}.db",
                    mime="application/octet-stream"
                )
        except:
            pass

    # --- Banner 图片逻辑 (本地加载) ---
    def get_local_banner_images():
        img_folder = "Fitness/Picture"
        if not os.path.exists(img_folder):
            os.makedirs(img_folder)
            return [{"url": "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?q=80&w=1200", "text": "NO PAIN NO GAIN"}]
        files = [f for f in os.listdir(img_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        if not files:
             return [{"url": "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?q=80&w=1200", "text": "ADD PHOTOS TO ASSETS"}]
        hero_images = []
        quotes = ["DISCIPLINE IS FREEDOM", "BUILD YOUR LEGACY", "UNLEASH THE BEAST", "SWEAT IS LUXURY"]
        for f in files:
            with open(os.path.join(img_folder, f), "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode()
                hero_images.append({"url": f"data:image/jpeg;base64,{encoded_string}", "text": random.choice(quotes)})
        return hero_images

    hero_pool = get_local_banner_images()
    hero = random.choice(hero_pool)
    
    st.markdown(textwrap.dedent(f"""
    <div style="position: relative; height: 260px; border-radius: 20px; overflow: hidden; margin-bottom: 30px; box-shadow: 0 15px 50px rgba(0,0,0,0.7);">
        <img src="{hero['url']}" style="width: 100%; height: 100%; object-fit: cover; filter: brightness(0.6) contrast(1.1);">
        <div style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: linear-gradient(to top, rgba(0,0,0,0.9) 0%, rgba(0,0,0,0) 60%);"></div>
        <div style="position: absolute; bottom: 25px; left: 30px; color: #fff; font-family: 'Oswald', sans-serif; font-size: 42px; font-weight: 700; letter-spacing: 2px; text-shadow: 0 5px 15px rgba(0,0,0,0.8); text-transform: uppercase;">{hero['text']}</div>
    </div>
    """), unsafe_allow_html=True)

    # --- Main Tabs ---
    tab1, tab2, tab3 = st.tabs(["🔥 DIET SCAN", "📊 BODY STATS", "📑 DAILY REPORT"])

    # === Tab 1: Diet ===
    with tab1:
        with st.container():
            img = st.file_uploader("Click to upload food", type=["jpg","png"], label_visibility="collapsed")
            desc = st.text_input("Extra Info", placeholder="e.g. 200g Steak...", label_visibility="collapsed")
            
            if img:
                st.markdown(f"<div style='text-align:center; color:#FF5722; margin-bottom:10px;'>📸 IMAGE LOADED</div>", unsafe_allow_html=True)
                if st.button("🚀 INITIATE SCAN", type="primary"):
                    with st.spinner("JARVIS IS ANALYZING..."):
                        try:
                            data = ai_engine.analyze_food(img, desc)
                            # ⚠️ 传入 current_user_id
                            database.save_meal(current_user_id, data)
                            st.toast("Data Logged", icon="✅")
                            time.sleep(0.5)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")

        st.divider()
        st.divider()
    st.markdown("### 🧬 万能数据注入 (Universal Restore)")
    
    # 允许上传任意 .db 文件
    uploaded_file = st.file_uploader("拖入你的数据库文件 (v2pro.db 或 old.db)", type=["db"])
    
    if uploaded_file and st.button("🚀 强制注入给 John"):
        import sqlite3
        import hashlib
        
        # 1. 保存上传的文件到临时区
        temp_path = "temp_restore.db"
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
            
        st.caption("正在分析文件结构...")
        
        try:
            # === A. 准备目标环境 (云端现有的库) ===
            conn_dest = sqlite3.connect(config.DB_FILE)
            c_dest = conn_dest.cursor()
            
            # 确保 John 存在
            c_dest.execute("SELECT id FROM users WHERE username='John'")
            john = c_dest.fetchone()
            if not john:
                # 如果没有 John，创建一个，密码 200487
                pw_hash = hashlib.sha256(str.encode("200487")).hexdigest()
                date_now = config.get_current_time()[0]
                c_dest.execute("INSERT INTO users (username, password, created_at) VALUES (?, ?, ?)", 
                              ("John", pw_hash, date_now))
                target_user_id = c_dest.lastrowid
                st.success(f"已自动创建账户 John (ID: {target_user_id})")
            else:
                target_user_id = john[0]
                st.info(f"数据将注入到账户 John (ID: {target_user_id})")

            # === B. 分析上传的文件 (来源库) ===
            conn_src = sqlite3.connect(temp_path)
            c_src = conn_src.cursor()
            
            # 🕵️‍♂️ 侦探逻辑：看看上传的文件里，meals 表到底长什么样？
            # 获取 meals 表的所有列名
            cursor = c_src.execute("SELECT * FROM meals LIMIT 1")
            columns = [description[0] for description in cursor.description]
            st.write(f"🔍 检测到上传文件的列: {columns}")
            
            # 判断是不是新版数据 (有没有 user_id)
            is_v3_format = 'user_id' in columns
            
            # === C. 开始搬运饮食数据 (Meals) ===
            if is_v3_format:
                # 这种情况：你上传的是 v2pro.db (已经带 user_id 了)
                st.info("识别为新版格式 (V3)，正在合并...")
                # 我们只取数据列，忽略它原来的 user_id，强制改成当前的 John
                data = c_src.execute("SELECT date, time, food_name, calories, protein, carbs, fat, advice FROM meals").fetchall()
            else:
                # 这种情况：你上传的是 old.db (旧版)
                st.info("识别为旧版格式 (V2)，正在升级...")
                data = c_src.execute("SELECT date, time, food_name, calories, protein, carbs, fat, advice FROM meals").fetchall()
            
            count_m = 0
            for row in data:
                # 写入云端库，强制 user_id = John
                c_dest.execute("INSERT INTO meals (user_id, date, time, food_name, calories, protein, carbs, fat, advice) VALUES (?,?,?,?,?,?,?,?,?)",
                              (target_user_id, row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]))
                count_m += 1
            
            # === D. 开始搬运身体数据 (Body Stats) ===
            # 同样的侦探逻辑检测 body_stats
            cursor_b = c_src.execute("SELECT * FROM body_stats LIMIT 1")
            cols_b = [desc[0] for desc in cursor_b.description]
            
            if 'user_id' in cols_b:
                data_b = c_src.execute("SELECT date, weight, body_fat, muscle, water_rate, bmr, visceral_fat FROM body_stats").fetchall()
            else:
                data_b = c_src.execute("SELECT date, weight, body_fat, muscle, water_rate, bmr, visceral_fat FROM body_stats").fetchall()
                
            count_s = 0
            for row in data_b:
                # 查重，避免重复插入同一天的体重
                exists = c_dest.execute("SELECT id FROM body_stats WHERE user_id=? AND date=?", (target_user_id, row[0])).fetchone()
                if not exists:
                    c_dest.execute("INSERT INTO body_stats (user_id, date, weight, body_fat, muscle, water_rate, bmr, visceral_fat) VALUES (?,?,?,?,?,?,?,?)",
                                  (target_user_id, row[0], row[1], row[2], row[3], row[4], row[5], row[6]))
                    count_s += 1
            
            conn_dest.commit()
            conn_src.close()
            conn_dest.close()
            
            st.balloons()
            st.success(f"🎉 成功！注入了 {count_m} 条饮食记录，{count_s} 条身体数据！")
            st.markdown("### 👉 请立即刷新网页并查看！")
            
        except Exception as e:
            st.error(f"❌ 注入失败 (详情): {e}")
        # ⚠️ 传入 current_user_id
        meals = database.get_today_meals(current_user_id)
        if not meals.empty:
            t_cal = int(meals['calories'].sum())
            t_pro = int(meals['protein'].sum())
            st.markdown(f"""
            <div style="display:flex; justify-content:space-between; align-items:flex-end; margin-bottom:20px;">
                <span style="font-family:'Oswald'; font-size:20px; color:#fff;">TODAY'S TOTAL</span>
                <div>
                    <span style="font-family:'Oswald'; font-size:32px; color:#FF5722;">{t_cal}</span> <span style="font-size:12px; color:#888;">KCAL</span>
                    <span style="margin:0 10px; color:#333;">|</span>
                    <span style="font-family:'Oswald'; font-size:32px; color:#fff;">{t_pro}g</span> <span style="font-size:12px; color:#888;">PRO</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            for _, row in meals.iterrows():
                ui.render_meal_card(row)
                if st.button("DELETE", key=f"del_{row['id']}"):
                    database.delete_meal(row['id'])
                    st.rerun()
        else:
            st.info("No records today. Start scanning.")

    # === Tab 2: Body Stats ===
    with tab2:
        with st.form("body_form"):
            c1, c2, c3 = st.columns(3)
            d_w, d_f, d_m = 70.0, 20.0, 30.0
            if not body_df.empty:
                last = body_df.iloc[-1]
                d_w = float(last['weight'])
                d_f = float(last['body_fat'])
                d_m = float(last['muscle'])

            w = c1.number_input("Weight (KG)", value=d_w, step=0.1)
            f = c2.number_input("Body Fat (%)", value=d_f, step=0.1)
            m = c3.number_input("Muscle (KG)", value=d_m, step=0.1)
            
            if st.form_submit_button("💾 SAVE DATA", type="primary"):
                # ⚠️ 传入 current_user_id
                database.save_body_stats(current_user_id, w, f, m)
                st.success("Updated Successfully!")
                time.sleep(0.5)
                st.rerun()

    # === Tab 3: Reports ===
    with tab3:
        st.markdown("### 📑 BATTLE ARCHIVE")
        if st.button("⚡ FORCE GENERATE REPORT (MANUAL)", type="primary"):
            meals = database.get_today_meals(current_user_id)
            body_h = database.get_body_history(current_user_id)
            if meals.empty:
                st.warning("No diet records today.")
            else:
                with st.spinner("ANALYZING..."):
                    report = ai_engine.generate_report_text(meals, body_h, goal)
                    # ⚠️ 传入 current_user_id
                    database.save_report(current_user_id, report)
                    st.rerun()

        st.divider()
        # ⚠️ 传入 current_user_id
        reports = database.get_report_history(current_user_id)
        if not reports.empty:
            for _, row in reports.iterrows():
                with st.expander(f"📅 WAR REPORT: {row['date']}"):
                    st.markdown(row['content'])
                    st.caption(f"Generated at: {row['created_at']}")
        else:
            st.info("No reports yet.")

# === 🚀 程序入口逻辑 ===
# 在 app.py 的最底部 (原来的 if st.session_state['logged_in']: ... 那里)
# 替换为以下代码：

# === 🚀 程序入口与自动登录逻辑 ===

# 1. 如果没登录，先检查 URL 里有没有“免死金牌”
if not st.session_state['logged_in']:
    params = st.query_params
    # 检查是否有 user 和 token 参数
    if "user" in params and "token" in params:
        auto_user = params["user"]
        # 这里为了演示简单，直接信任 URL。
        # (严格来说应该验证 token 的哈希值，但对于个人应用这样足够了)
        
        # 去数据库查一下这个用户，获取 ID
        import sqlite3
        conn = sqlite3.connect(config.DB_FILE)
        # 注意：这里需要根据你的 users 表结构调整，假设 username 是唯一的
        u_data = conn.execute("SELECT * FROM users WHERE username=?", (auto_user,)).fetchone()
        conn.close()
        
        if u_data:
            st.session_state['logged_in'] = True
            st.session_state['user_info'] = u_data
            st.toast(f"⚡ AUTO-LOGIN: {auto_user}", icon="🔓")

# 2. 正常的路由逻辑
if st.session_state['logged_in']:
    main_app()
else:
    login_page()




