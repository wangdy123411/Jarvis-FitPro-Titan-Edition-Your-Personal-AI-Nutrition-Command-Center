# 🦍 Jarvis FitPro: Titan Edition

![Python](https://img.shields.io/badge/Python-3.8%2B-blue) ![Streamlit](https://img.shields.io/badge/Streamlit-1.30%2B-FF4B4B) ![AI Model](https://img.shields.io/badge/AI-Qwen--VL--Max-orange) ![License](https://img.shields.io/badge/License-MIT-green)

> **Your Personal AI Nutrition Command Center.**
>
> 你的私人 AI 营养指挥中心 —— 拒绝繁琐记录，拍照即算，数据驱动，硬核进化。

---

## 📖 Introduction (项目介绍)

**Jarvis FitPro** 是一款基于 **Streamlit** 构建的轻量化、移动端友好的健身追踪应用，由阿里云 **Qwen-VL-Max (通义千问视觉大模型)** 提供核心驱动力。

不同于传统的卡路里计算器，Jarvis 允许用户通过 **简单的拍照** 即可完成饮食记录。AI 会瞬间识别食材、估算重量，并精准计算热量与宏量营养素（蛋白质、碳水、脂肪）。结合多维度的身体数据追踪与 AI 每日战报，它就是你口袋里的虚拟私教。

**核心理念**：极简录入，极致视觉，科学反馈。

---

## ✨ Key Features (核心功能)

### 1. 📡 AI Diet Scanner (AI 饮食扫描)
* **Snap & Analyze**: 上传食物照片，AI 自动拆解营养成分。
* **Titan UI Design**: 采用 "Titan" 泰坦级 UI 设计风格，强制深色模式 (`#050505`)，配合 **Oswald** 硬核字体，数据展示清晰震撼。
* **Macro Focus**: 针对增肌/减脂人群，特别高亮 **蛋白质 (Protein)** 数据（熔岩橙配色）。

### 2. 📊 Body Stats Tracking (全维体测录入)
* 追踪 **体重 (Weight)**、**体脂率 (Body Fat)** 和 **骨骼肌 (Muscle Mass)**。
* 自动生成趋势折线图，直观监测身体变化。
* 智能填充逻辑：自动读取上一次记录的数据，减少重复输入。

### 3. 📑 Daily Battle Report (每日智能战报)
* **Context-Aware AI**: 系统会自动读取你 **最近几天的身体变化趋势** + **今日饮食总摄入**。
* **Actionable Advice**: 生成一份 Markdown 格式的科学日报，包含数据复盘和 **3条具体的明日执行建议**（如：“碳水后置”、“增加训练强度”）。
* **Archive System**: 所有战报自动存入 SQLite 数据库，形成你的个人训练日记。

### 4. 📱 Mobile-First Experience (移动端适配)
* **Dark Mode**: 强制深邃黑魂主题，省电且高级。
* **Responsive**: 隐藏式侧边栏，优化的上传触控区，在手机浏览器上体验如原生 App。
* **LAN Access**: 支持局域网访问，无需公网服务器，手机连 WiFi 即可使用。

---

## 🛠️ Tech Stack (技术栈)

* **Frontend**: [Streamlit](https://streamlit.io/) (Python-based UI framework)
* **AI Engine**:
    * Vision: `qwen-vl-max` (Image Recognition & Estimation)
    * Logic: `qwen-plus` (Reasoning & Report Generation)
* **Database**: SQLite (Zero-config, local storage)
* **Data Processing**: Pandas
* **Styling**: Custom CSS injection (Google Fonts: Oswald & Roboto Condensed)

---

## 🚀 Quick Start (快速开始)

### Prerequisites (前置要求)
* Python 3.8+
* 阿里云 DashScope (灵积) API Key ([获取地址](https://dashscope.aliyun.com/))

### 1. Clone the Repo
```bash
git clone [https://github.com/your-username/jarvis-fitpro.git](https://github.com/your-username/jarvis-fitpro.git)
cd jarvis-fitpro
