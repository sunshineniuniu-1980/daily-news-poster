import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import google.generativeai as genai
import textwrap

# 1. 配置 AI 大脑 (API Key 从 Streamlit 后台读取，稍后教你设置)
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
except:
    st.warning("请先在后台设置 API Key")

st.title("📰 财经英语海报一键生成")

# 输入框
english_text = st.text_area("1. 粘贴英文新闻原文：", height=250)

if st.button("全自动生成海报"):
    if not english_text:
        st.error("请输入内容")
    else:
        with st.spinner('AI 正在翻译并解析单词...'):
            # 2. 向 AI 发送指令
            prompt = f"""
            你是一个专业的财经翻译和英语老师。请根据以下英文新闻：
            1. 翻译成地道的中文（适合小红书阅读）。
            2. 提取3-5个核心词汇或短语，给出中文释义。
            
            原文内容：{english_text}
            
            请按以下格式输出：
            ---翻译开始---
            (中文翻译内容)
            ---翻译结束---
            ---解析开始---
            (单词1: 释义; 单词2: 释义)
            ---解析结束---
            """
            
            response = model.generate_content(prompt)
            result = response.text
            
            # 解析 AI 返回的内容 (简单的字符串切分)
            try:
                translation = result.split("---翻译开始---")[1].split("---翻译结束---")[0].strip()
                vocab = result.split("---解析开始---")[1].split("---解析结束---")[0].strip()
            except:
                translation = result
                vocab = "解析失败，请检查 AI 输出"

            # 3. 显示结果供预览
            st.subheader("AI 翻译预览")
            st.write(translation)
            st.subheader("核心词汇")
            st.write(vocab)

            # 4. 生成海报 (绘图逻辑)
            width, height = 1200, 1600
            img = Image.new('RGB', (width, height), color=(255, 255, 255))
            draw = ImageDraw.Draw(img)
            
            # --- 在这里添加加载字体的命令 ---
            # 定义字体路径和大小（40是字号，你可以根据需要调整）
            font_path = "SimHei.ttf" 
            font_main = ImageFont.truetype(font_path, 40)
            font_title = ImageFont.truetype(font_path, 60)
            # ------------------------------

            # 绘制背景色块
            draw.rectangle([0, 0, 1200, 300], fill=(40, 44, 52))

            # --- 在这里使用字体画出文字 ---
            # 这里的 (100, 400) 是文字在图片上的坐标
            draw.text((100, 350), "AI 翻译结果：", font=font_title, fill=(230, 70, 70))
            
            # 使用 textwrap 处理长文字换行
            lines = textwrap.wrap(translation, width=25) # 25是指每行大约多少个中文字
            y_text = 450
            for line in lines:
                draw.text((100, y_text), line, font=font_main, fill=(0, 0, 0))
                y_text += 60 # 每行行间距
            # ------------------------------
            
            st.image(img, caption="海报预览", use_column_width=True)
