import streamlit as st
import textwrap

def inject_css():
    """注入 CSS (保持不变)"""
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Oswald:wght@400;500;700&family=Montserrat:wght@300;400;600&display=swap');
        
        .stApp {
            background-color: #000000 !important;
            background-image: radial-gradient(circle at 50% 0%, #1a0500 0%, #000000 70%);
            color: #e0e0e0 !important;
            font-family: 'Montserrat', sans-serif;
        }
        
        section[data-testid="stSidebar"] {
            background-color: #050505 !important;
            border-right: 1px solid #1a1a1a;
        }
        
        .titan-card {
            background: rgba(20, 20, 20, 0.6);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-left: 4px solid #FF5722;
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 24px;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5);
            transition: all 0.3s ease;
        }
        .titan-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 12px 40px 0 rgba(255, 87, 34, 0.15);
            border-left-color: #FF8A65;
        }
        
        .cal-val {
            font-family: 'Oswald', sans-serif;
            font-size: 56px;
            font-weight: 700;
            background: -webkit-linear-gradient(45deg, #FF5722, #FF8A65);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            line-height: 1;
        }
        
        .food-title {
            font-family: 'Oswald', sans-serif;
            font-size: 26px;
            color: #fff;
            margin: 0;
            letter-spacing: 1px;
        }
        
        /* 其他样式保持默认... */
        .stFileUploader {
            background: rgba(255, 87, 34, 0.03);
            border: 2px dashed rgba(255, 87, 34, 0.3);
            border-radius: 16px;
            padding: 30px;
        }
        .stTabs [aria-selected="true"] {
            background-color: transparent !important;
            border-bottom: 3px solid #FF5722 !important;
            color: #FF5722 !important;
        }
    </style>
    """, unsafe_allow_html=True)

def render_meal_card(row):
    # 将所有变量先取出来，防止在 f-string 里写逻辑出错
    food = row['food_name']
    time = row['time']
    cal = int(row['calories'])
    pro = row['protein']
    carbs = row['carbs']
    fat = row['fat']
    advice = row['advice']

    # 🟢 核心修改：使用一行流写法，或者确保没有任何换行缩进
    # 这里我们用最稳妥的方式：直接写成一行长的 HTML，虽然代码不好看，但绝对不会渲染错
    html = f"""
    <div class="titan-card">
        <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:15px; border-bottom:1px solid rgba(255,255,255,0.05); padding-bottom:15px;">
            <div>
                <h3 class="food-title">{food}</h3>
                <div style="font-family:'Montserrat'; font-size:11px; color:#666; letter-spacing:1px; margin-top:4px;">SCAN TIME: {time}</div>
            </div>
            <div style="text-align:right;">
                <div class="cal-val">{cal}</div>
                <div style="font-size:10px; color:#888; font-weight:700; letter-spacing:2px; margin-top:-5px;">KCAL</div>
            </div>
        </div>
        <div style="display:flex; justify-content:space-around; align-items:center; padding: 5px 0;">
            <div style="text-align:center;">
                <div style="font-family:'Oswald'; font-size:22px; color:#FF5722; font-weight:600;">{pro}</div>
                <div style="font-size:9px; color:#555; font-weight:700; letter-spacing:1px;">PROTEIN</div>
            </div>
            <div style="width:1px; height:20px; background:rgba(255,255,255,0.1);"></div>
            <div style="text-align:center;">
                <div style="font-family:'Oswald'; font-size:22px; color:#e0e0e0; font-weight:600;">{carbs}</div>
                <div style="font-size:9px; color:#555; font-weight:700; letter-spacing:1px;">CARBS</div>
            </div>
            <div style="width:1px; height:20px; background:rgba(255,255,255,0.1);"></div>
            <div style="text-align:center;">
                <div style="font-family:'Oswald'; font-size:22px; color:#e0e0e0; font-weight:600;">{fat}</div>
                <div style="font-size:9px; color:#555; font-weight:700; letter-spacing:1px;">FAT</div>
            </div>
        </div>
        <div style="margin-top:20px; font-size:13px; color:#aaa; font-style:italic; line-height:1.6;">"{advice}"</div>
    </div>
    """
    
    st.markdown(html, unsafe_allow_html=True)

