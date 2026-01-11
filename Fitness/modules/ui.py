import streamlit as st

def inject_css():
    """注入艺术家级全局 CSS 样式"""
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Oswald:wght@400;500;700&family=Montserrat:wght@300;400;600&display=swap');

        /* === 全局画布 === */
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
        
        header {visibility: hidden;}
        
        h1, h2, h3 {
            font-family: 'Oswald', sans-serif !important;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            color: #ffffff !important;
        }
        
        /* === 玻璃态卡片 === */
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

        .stFileUploader {
            background: rgba(255, 87, 34, 0.03);
            border: 2px dashed rgba(255, 87, 34, 0.3);
            border-radius: 16px;
            padding: 30px;
        }

        button[kind="primary"] {
            background: linear-gradient(90deg, #FF5722 0%, #F44336 100%) !important;
            color: white !important;
            font-family: 'Oswald', sans-serif !important;
            font-size: 16px !important;
            padding: 0.8rem 2.5rem !important;
            border-radius: 50px !important;
            border: none;
            box-shadow: 0 4px 15px rgba(255, 87, 34, 0.4);
        }
        
        .stTabs [aria-selected="true"] {
            background-color: transparent !important;
            border-bottom: 3px solid #FF5722 !important;
            color: #FF5722 !important;
        }
    </style>
    """, unsafe_allow_html=True)

def render_meal_card(row):
    """
    渲染卡片。使用 Python 字符串拼接，彻底杜绝缩进问题。
    """
    # 顶部：菜名和热量
    header_html = (
        f'<div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:15px; border-bottom:1px solid rgba(255,255,255,0.05); padding-bottom:15px;">'
        f'<div><h3 class="food-title">{row["food_name"]}</h3><div style="font-family:\'Montserrat\'; font-size:11px; color:#666; letter-spacing:1px; margin-top:4px;">SCAN TIME: {row["time"]}</div></div>'
        f'<div style="text-align:right;"><div class="cal-val">{int(row["calories"])}</div><div style="font-size:10px; color:#888; font-weight:700; letter-spacing:2px; margin-top:-5px;">KCAL</div></div>'
        f'</div>'
    )

    # 中部：营养素
    macros_html = (
        f'<div style="display:flex; justify-content:space-around; align-items:center; padding: 5px 0;">'
        f'<div style="text-align:center;"><div style="font-family:\'Oswald\'; font-size:22px; color:#FF5722; font-weight:600;">{row["protein"]}</div><div style="font-size:9px; color:#555; font-weight:700; letter-spacing:1px;">PROTEIN</div></div>'
        f'<div style="width:1px; height:20px; background:rgba(255,255,255,0.1);"></div>'
        f'<div style="text-align:center;"><div style="font-family:\'Oswald\'; font-size:22px; color:#e0e0e0; font-weight:600;">{row["carbs"]}</div><div style="font-size:9px; color:#555; font-weight:700; letter-spacing:1px;">CARBS</div></div>'
        f'<div style="width:1px; height:20px; background:rgba(255,255,255,0.1);"></div>'
        f'<div style="text-align:center;"><div style="font-family:\'Oswald\'; font-size:22px; color:#e0e0e0; font-weight:600;">{row["fat"]}</div><div style="font-size:9px; color:#555; font-weight:700; letter-spacing:1px;">FAT</div></div>'
        f'</div>'
    )

    # 底部：建议
    advice_html = (
        f'<div style="margin-top:20px; font-size:13px; color:#aaa; font-style:italic; line-height:1.6;">'
        f'"{row["advice"]}"'
        f'</div>'
    )

    # 组合
    full_html = f'<div class="titan-card">{header_html}{macros_html}{advice_html}</div>'
    
    st.markdown(full_html, unsafe_allow_html=True)