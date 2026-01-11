import schedule
import time
import threading
import shutil
import os
import datetime
from . import database, ai_engine, config

# === 1. 定义具体任务 ===

def job_auto_backup():
    """任务：自动备份数据库到本地"""
    print("⏳ [System] 开始执行每日备份...")
    
    # 创建备份文件夹
    backup_dir = "backups"
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    # 源文件与目标文件
    src = config.DB_FILE
    date_str, _ = config.get_current_time()
    dst = os.path.join(backup_dir, f"jarvis_data_{date_str}.db")
    
    try:
        if os.path.exists(src):
            shutil.copy2(src, dst)
            print(f"✅ [System] 备份成功: {dst}")
        else:
            print(f"⚠️ [System] 源数据库不存在，跳过备份")
    except Exception as e:
        print(f"❌ [System] 备份失败: {e}")

def job_auto_report():
    """任务：自动生成每日报告"""
    print("⏳ [System] 开始检查每日战报...")
    
    # 1. 检查今天是否已经生成过（避免重复生成）
    date_str, _ = config.get_current_time()
    reports = database.get_report_history() # 假设这个函数返回DataFrame
    
    # 简单的检查：看最新一条的日期是不是今天
    if not reports.empty:
        last_date = reports.iloc[0]['date']
        if last_date == date_str:
            print("✅ [System] 今日战报已存在，跳过生成。")
            return

    # 2. 准备数据
    meals = database.get_today_meals()
    body_df = database.get_body_history()
    
    # 如果没吃东西，可能不需要生成，或者生成一个空数据的报告
    if meals.empty and body_df.empty:
        print("⚠️ [System] 今日无数据，跳过战报生成。")
        return

    # 3. 调用 AI (复用 ai_engine 的逻辑，但我们需要在 ai_engine 里补一个生成报告的函数)
    # 注意：这里我们得去 ai_engine 补一个 generate_report_text 函数
    print("🧠 [System] AI 正在生成战报...")
    try:
        # 这里假设目标默认是 MAINTAIN，或者你可以存一个用户配置
        report_content = ai_engine.generate_report_text(meals, body_df, "MAINTAIN (Auto)")
        database.save_report(report_content)
        print("✅ [System] 自动战报生成完毕！")
    except Exception as e:
        print(f"❌ [System] AI 生成失败: {e}")

# === 2. 守夜人线程 ===

def run_schedule():
    """这是后台线程要跑的死循环"""
    while True:
        schedule.run_pending()
        time.sleep(60) # 每分钟醒来检查一次

def start_background_scheduler():
    """启动后台线程 (单例模式，防止Streamlit刷新导致重复启动)"""
    # 检查当前线程列表，看是否已经有守夜人了
    for t in threading.enumerate():
        if t.name == "Jarvis_Scheduler":
            return # 已经启动了，直接退出

    # 设定定时任务 (每天 23:00 执行)
    schedule.every().day.at("23:00").do(job_auto_backup)
    schedule.every().day.at("23:00").do(job_auto_report)
    
    # 启动线程
    t = threading.Thread(target=run_schedule, name="Jarvis_Scheduler", daemon=True)
    t.start()
    print("🚀 [System] 后台自动化任务已启动 (每天 23:00 执行)")