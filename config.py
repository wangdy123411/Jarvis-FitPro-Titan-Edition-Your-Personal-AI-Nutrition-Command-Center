import os
import pytz
from datetime import datetime

# === 基础配置 ===
API_KEY = "sk-cedf4c8f0d1042138740dbce8fbd0a30"  # 建议后续改为 st.secrets
BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"

# === 核心模型 ===
VISION_MODEL = "qwen-vl-max"
TEXT_MODEL = "qwen-plus"

# === 数据库文件 ===
DB_FILE = "jarvis_pro_v2.db"

# === 🌍 时区设置 (Timezone Fix) ===
# 无论服务器在美国还是火星，这里强制转为中国时间
TZ_CN = pytz.timezone('Asia/Shanghai')

def get_current_time():
    """获取当前时区的日期和时间字符串"""
    now = datetime.now(TZ_CN)
    return now.strftime("%Y-%m-%d"), now.strftime("%H:%M")

def get_current_datetime_obj():
    """获取当前时区的 datetime 对象"""
    return datetime.now(TZ_CN)