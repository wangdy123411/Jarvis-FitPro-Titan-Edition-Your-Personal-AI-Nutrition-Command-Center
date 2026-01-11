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
                    st.session_state['logged_in'] = True
                    st.session_state['user_info'] = user # user[0] is id, user[1] is username
                    st.success(f"WELCOME BACK, COMMANDER {user[1].upper()}.")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("ACCESS DENIED: Invalid Codename or Key.")

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
    with st.sidebar:
        st.header(f"👤 {current_username.upper()}")
        if st.button("🔒 LOGOUT"):
            st.session_state['logged_in'] = False
            st.session_state['user_info'] = None
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
if st.session_state['logged_in']:
    main_app()
else:

    login_page()
