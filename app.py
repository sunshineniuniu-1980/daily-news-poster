import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import google.generativeai as genai
import textwrap

# ==========================================
# 1. 基础配置 (无需修改)
# ==========================================
st.set_page_config(page_title="财经英语海报生成器", layout="centered")
st.title("📰 财经英语海报一键生成")

# ==========================================
# 2. AI 配置 (重要：请确保Secrets里已设置 GOOGLE_API_KEY)
# ==========================================
try:
    # 自动从 Streamlit Secrets 读取你的 Key
    api_key_val = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key_val)
    
    # 使用兼容性最强的模型
    model = genai.GenerativeModel('gemini-3-flash-preview')
    st.sidebar.success("✅ AI 引擎已就绪")
except Exception as e:
    st.error(f"❌ API配置失败，请检查Secrets设置: {e}")
    st.stop()

# ==========================================
# 3. 这里的参数你可以根据喜好修改 (个性化部分)
# ==========================================
# 字体文件名：必须与你上传到 GitHub 的文件名完全一致！
FONT_FILE = "simhei.ttf"  # 如果你上传的是其他字体，请改名

# 海报颜色设置 (RGB格式)
COLOR_BG = (255, 255, 255)      # 背景色：白色
COLOR_HEADER = (30, 30, 30)     # 顶部色块：深灰色
COLOR_TITLE = (230, 70, 70)     # 标题颜色：小红书红
COLOR_TEXT = (40, 40, 40)       # 正文字体颜色：深灰/黑

# ==========================================
# 4. 网页输入区域
# ==========================================
english_text = st.text_area("在此粘贴英文新闻原文：", height=250, placeholder="Enter English news here...")

if st.button("🚀 开始全自动生成海报"):
    if not english_text:
        st.warning("请先输入内容再生成。")
    else:
        with st.spinner('AI 正在翻译并排版海报，请稍候...'):
            try:
                # 让 AI 按照固定标签返回内容，方便程序切割
                prompt = f"""
                你是一个专业的财经翻译。请处理以下内容：
                1. 翻译成地道、优雅的中文（适合小红书财经博主风格）。
                2. 提取3-5个核心关键词或短语，给出中文解析。
                格式要求：
                [TRANS]
                (只写翻译内容)
                [VOCAB]
                (只写单词解析，每行一个)
                
                原文：{english_text}
                """
                
                response = model.generate_content(prompt)
                full_text = response.text
                
                # 提取翻译和词汇
                trans_content = full_text.split("[TRANS]")[1].split("[VOCAB]")[0].strip()
                vocab_content = full_text.split("[VOCAB]")[1].strip()

                # --- 绘图逻辑开始 ---
                width, height = 1200, 1600
                img = Image.new('RGB', (width, height), color=COLOR_BG)
                draw = ImageDraw.Draw(img)
                
                # 加载字体
                try:
                    font_title = ImageFont.truetype(FONT_FILE, 60) # 标题字号
                    font_main = ImageFont.truetype(FONT_FILE, 42)  # 正文字号
                    font_logo = ImageFont.truetype(FONT_FILE, 70)  # 顶部Logo字号
                except:
                    st.error(f"❌ 找不到字体文件 '{FONT_FILE}'，请确认已上传至GitHub。")
                    st.stop()

                # A. 绘制顶部色块
                draw.rectangle([0, 0, 1200, 250], fill=COLOR_HEADER)
                draw.text((80, 85), "FINANCE DAILY NEWS", font=font_logo, fill=(255, 255, 255))
                
                # B. 绘制翻译部分
                draw.text((80, 320), "【 深度翻译 】", font=font_title, fill=COLOR_TITLE)
                y_cursor = 420
                # textwrap.wrap 自动处理换行，width=22指每行大约22个汉字
                for line in textwrap.wrap(trans_content, width=22):
                    draw.text((80, y_cursor), line, font=font_main, fill=COLOR_TEXT)
                    y_cursor += 70
                
                # C. 绘制词汇部分
                y_cursor += 80
                draw.text((80, y_cursor), "【 核心词汇 】", font=font_title, fill=COLOR_TITLE)
                y_cursor += 100
                for v_line in textwrap.wrap(vocab_content, width=24):
                    draw.text((80, y_cursor), v_line, font=font_main, fill=(80, 80, 80))
                    y_cursor += 70

                # 5. 输出展示
                st.image(img, caption="长按图片保存到手机", use_container_width=True)
                st.balloons() # 成功特效
                
                # 可选：在网页上也显示文本，方便复制文案
                with st.expander("点击展开查看文本版翻译"):
                    st.write(trans_content)
                    st.write(vocab_content)

            except Exception as e:
                st.error(f"❌ 生成失败: {e}")
