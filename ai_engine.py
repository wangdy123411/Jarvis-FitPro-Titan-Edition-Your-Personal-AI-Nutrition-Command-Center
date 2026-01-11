import base64
import json
import io
from openai import OpenAI
from PIL import Image
from .config import API_KEY, BASE_URL, VISION_MODEL, TEXT_MODEL

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

def process_image(image_file):
    """图片转 Base64"""
    image = Image.open(image_file)
    if image.mode in ("RGBA", "P"): image = image.convert("RGB")
    image.thumbnail((512, 512))
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG", quality=60)
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

def analyze_food(image_file, desc):
    b64 = process_image(image_file)
    prompt = f"User Desc: {desc}. Estimate calories and macros. Output JSON: {{'food_name': 'String', 'calories': 0, 'protein': 0, 'carbs': 0, 'fat': 0, 'advice': 'String'}}"
    res = client.chat.completions.create(
        model=VISION_MODEL, 
        messages=[{"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}]}], 
        temperature=0.01
    )
    return json.loads(res.choices[0].message.content.replace("```json","").replace("```",""))
# ... (保留前面的代码) ...

def generate_report_text(meals_df, body_df, goal):
    """
    纯逻辑函数：接收数据，返回 AI 写的战报文本。
    不涉及任何 UI 操作。
    """
    # 1. 整理数据字符串
    today_sum = "No Diet Records"
    if not meals_df.empty:
        today_sum = f"Total: {int(meals_df['calories'].sum())}kcal (Protein: {int(meals_df['protein'].sum())}g)"
    
    body_trend = "No Body Data"
    if len(body_df) >= 2:
        last = body_df.iloc[-1]
        prev = body_df.iloc[-2]
        diff = round(float(last['weight']) - float(prev['weight']), 2)
        body_trend = f"Weight Change: {diff}kg"
    elif not body_df.empty:
        body_trend = f"Current Weight: {body_df.iloc[-1]['weight']}kg"

    # 2. 组装 Prompt
    prompt = f"""
    Role: Jarvis Fitness Coach. Goal: {goal}.
    Data: 
    - Today's Diet: {today_sum}
    - Recent Body Trend: {body_trend}
    
    Task: Generate a daily summary report.
    Format: Markdown.
    Content:
    1. 💥 BRUTAL TRUTH (Review of today's compliance)
    2. ⚔️ BATTLE PLAN (3 specific actions for tomorrow)
    Style: Hardcore, short, punchy. No generic fluff.
    """
    
    # 3. 调用大模型
    res = client.chat.completions.create(
        model=TEXT_MODEL, # 确保 config.py 里定义了 TEXT_MODEL = "qwen-plus"
        messages=[{"role": "user", "content": prompt}]
    )
    
    return res.choices[0].message.content