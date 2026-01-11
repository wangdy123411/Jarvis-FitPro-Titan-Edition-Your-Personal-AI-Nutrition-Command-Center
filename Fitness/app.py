import streamlit as st
import time
import random
import os
import base64
import textwrap

# 🟢 安全导入：避免 KeyError 循环引用
import modules.config as config
import modules.database as database
import modules.ai_engine as ai_engine
import modules.ui as ui
import modules.automation as automation
import modules.auth as auth

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

# === 🚪 登录/注册界面 ===
def login_page():
    st.markdown("""
    <div style="text-align: center; margin-top: 50px; margin-bottom: 30px;">
        <h1 style="font-size: 60px; color: #FF5722; text-shadow: 0 0 20px rgba(255,87,34,0.5);">JARVIS ACCESS</h1>
        <p style="color: #666; letter-spacing: 2px;">SECURE FITNESS PROTOCOL // LOGIN REQUIRED</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab_login, tab_signup = st.tabs(["🔓 LOGIN", "📝 JOIN PROTOCOL"])
    
    with tab_login:
        with st.form("login_form"):
            username = st.text_input("CODENAME (Username)")
            password = st.text_input("ACCESS KEY (Password)", type="password")
            
            if st.form_submit_button("🚀 AUTHENTICATE", type="primary"):
                user = auth.login_user(username, password)
                if user:
                    # 🟢 登录成功：设置 Session 和 URL 参数 (免死金牌)
                    st.session_state['logged_in'] = True
                    st.session_state['user_info'] = user
                    st.query_params["user"] = user[1]
                    st.query_params["token"] = "valid"
                    
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

# === 🏠 主程序 ===
def main_app():
    current_user_id = st.session_state['user_info'][0]
    current_username = st.session_state['user_info'][1]

    # --- 侧边栏 ---
    with st.sidebar:
        st.header(f"👤 {current_username.upper()}")
        
        # 🔴 登出逻辑：必须清空 URL 参数
        if st.button("🔒 LOGOUT"):
            st.query_params.clear()
            st.session_state['logged_in'] = False
            st.session_state['user_info'] = None
            st.rerun()
            
        st.divider()
        st.header("⚙️ CONTROL PANEL")
        goal = st.selectbox("Current Mode", ["BULK", "CUT", "MAINTAIN"])
        
        # 显示体重
        body_df = database.get_body_history(current_user_id)
        d_w = 70.0
        if not body_df.empty:
            d_w = float(body_df.iloc[-1]['weight'])
        st.markdown(f"### Current Weight: `{d_w} KG`")
        if not body_df.empty:
            st.line_chart(body_df.set_index('date')['weight'], color="#FF5722", height=150)
            
        # 🟢 数据维护区 (Admin Zone)
        st.divider()
        st.markdown("### 🛠️ ADMIN TOOLS")
        
        # 1. 数据库去重 (Cleaner)
        if st.button("♻️ 去除重复数据"):
            import sqlite3
            conn = sqlite3.connect(config.DB_FILE)
            c = conn.cursor()
            # 清理饮食
            c.execute("DELETE FROM meals WHERE id NOT IN (SELECT MIN(id) FROM meals GROUP BY user_id, date, time, food_name, calories)")
            d_m = c.rowcount
            # 清理身体数据
            c.execute("DELETE FROM body_stats WHERE id NOT IN (SELECT MIN(id) FROM body_stats GROUP BY user_id, date)")
            d_s = c.rowcount
            conn.commit()
            conn.close()
            st.success(f"Cleaned: {d_m} meals, {d_s} stats.")
            time.sleep(1)
            st.rerun()

        # 2. 数据库备份下载
        try:
            with open(config.DB_FILE, "rb") as f:
                st.download_button("📥 备份数据库 (Backup)", data=f, file_name=f"jarvis_backup_{config.get_current_time()[0]}.db")
        except:
            pass
            
        # 3. 万能注入 (Restore)
        st.markdown("---")
        uploaded_file = st.file_uploader("导入旧数据库 (.db)", type=["db"])
        if uploaded_file and st.button("🚀 注入给当前用户"):
            import sqlite3
            import hashlib
            
            # 保存临时文件
            with open("temp.db", "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            try:
                # 连接目标库
                conn_dest = sqlite3.connect(config.DB_FILE)
                c_dest = conn_dest.cursor()
                
                # 连接源库
                conn_src = sqlite3.connect("temp.db")
                c_src = conn_src.cursor()
                
                # 检查源文件格式
                cols = [d[0] for d in c_src.execute("SELECT * FROM meals LIMIT 1").description]
                is_v3 = 'user_id' in cols
                
                # 搬运饮食
                if is_v3:
                    data = c_src.execute("SELECT date, time, food_name, calories, protein, carbs, fat, advice FROM meals").fetchall()
                else:
                    data = c_src.execute("SELECT date, time, food_name, calories, protein, carbs, fat, advice FROM meals").fetchall()
                
                for r in data:
                    c_dest.execute("INSERT INTO meals (user_id, date, time, food_name, calories, protein, carbs, fat, advice) VALUES (?,?,?,?,?,?,?,?,?)",
                                  (current_user_id, r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7]))
                                  
                # 搬运身体数据
                cols_b = [d[0] for d in c_src.execute("SELECT * FROM body_stats LIMIT 1").description]
                if 'user_id' in cols_b:
                    data_b = c_src.execute("SELECT date, weight, body_fat, muscle, water_rate, bmr, visceral_fat FROM body_stats").fetchall()
                else:
                    data_b = c_src.execute("SELECT date, weight, body_fat, muscle, water_rate, bmr, visceral_fat FROM body_stats").fetchall()
                
                for r in data_b:
                    # 简单查重
                    exists = c_dest.execute("SELECT id FROM body_stats WHERE user_id=? AND date=?", (current_user_id, r[0])).fetchone()
                    if not exists:
                        c_dest.execute("INSERT INTO body_stats (user_id, date, weight, body_fat, muscle, water_rate, bmr, visceral_fat) VALUES (?,?,?,?,?,?,?,?)",
                                      (current_user_id, r[0], r[1], r[2], r[3], r[4], r[5], r[6]))

                conn_dest.commit()
                conn_src.close()
                conn_dest.close()
                st.balloons()
                st.success("导入成功！请点击上方'去除重复数据'清理。")
            except Exception as e:
                st.error(f"Error: {e}")

    # --- Banner ---
    st.markdown("""
    <div style="position: relative; height: 260px; border-radius: 20px; overflow: hidden; margin-bottom: 30px; box-shadow: 0 15px 50px rgba(0,0,0,0.7);">
        <img src="https://images.unsplash.com/photo-1517836357463-d25dfeac3438?q=80&w=1200" style="width: 100%; height: 100%; object-fit: cover; filter: brightness(0.6) contrast(1.1);">
        <div style="position: absolute; bottom: 25px; left: 30px; color: #fff; font-family: 'Oswald', sans-serif; font-size: 42px; font-weight: 700; letter-spacing: 2px;">UNLEASH THE BEAST</div>
    </div>
    """, unsafe_allow_html=True)

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
                            database.save_meal(current_user_id, data)
                            st.toast("Data Logged", icon="✅")
                            time.sleep(0.5)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")

        st.divider()
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
            # 默认值
            w_val, f_val, m_val = 70.0, 20.0, 30.0
            if not body_df.empty:
                last = body_df.iloc[-1]
                w_val = float(last['weight'])
                f_val = float(last['body_fat'])
                m_val = float(last['muscle'])

            w = c1.number_input("Weight (KG)", value=w_val, step=0.1)
            f = c2.number_input("Body Fat (%)", value=f_val, step=0.1)
            m = c3.number_input("Muscle (KG)", value=m_val, step=0.1)
            
            if st.form_submit_button("💾 SAVE DATA", type="primary"):
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
                    database.save_report(current_user_id, report)
                    st.rerun()

        st.divider()
        reports = database.get_report_history(current_user_id)
        if not reports.empty:
            for _, row in reports.iterrows():
                with st.expander(f"📅 WAR REPORT: {row['date']}"):
                    st.markdown(row['content'])
                    st.caption(f"Generated at: {row['created_at']}")
        else:
            st.info("No reports yet.")

# === 🚀 程序入口与自动登录逻辑 ===
if __name__ == "__main__":
    # 1. 如果没登录，先检查 URL 里有没有“免死金牌”
    if not st.session_state['logged_in']:
        params = st.query_params
        # 检查是否有 user 和 token 参数
        if "user" in params and "token" in params:
            auto_user = params["user"]
            
            import sqlite3
            try:
                conn = sqlite3.connect(config.DB_FILE)
                u_data = conn.execute("SELECT * FROM users WHERE username=?", (auto_user,)).fetchone()
                conn.close()
                
                if u_data:
                    st.session_state['logged_in'] = True
                    st.session_state['user_info'] = u_data
                    st.toast(f"⚡ AUTO-LOGIN: {auto_user}", icon="🔓")
            except:
                pass

    # 2. 正常的路由逻辑
    if st.session_state['logged_in']:
        main_app()
    else:
        login_page()
