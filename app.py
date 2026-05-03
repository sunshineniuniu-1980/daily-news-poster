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
        with st.spinner('AI 正在处理长文并计算排版空间...'):
            try:
                # 1. 获取 AI 翻译内容
                # 提示：这里使用了你之前调通的 gemini-3-flash-preview
                prompt = f"""
                你是一个专业的财经翻译。请处理以下内容：
                1. 翻译成地道、中文（适合小红书财经博主风格）。
                2. 提取3-5个核心关键词或短语，给出中文解析。
                格式要求：
                - 翻译内容请【务必保留原有的分段】，段落之间加一个空行。
                - 使用 [TRANS] 和 [VOCAB] 标签包裹。
                
                原文：{english_text}
                """
                
                response = model.generate_content(prompt)
                full_text = response.text
                
                # 提取翻译和词汇
                trans_content = full_text.split("[TRANS]")[1].split("[VOCAB]")[0].strip()
                vocab_content = full_text.split("[VOCAB]")[1].strip()

                # 2. 【核心逻辑】预计算文字行数以确定图片高度
                font_main_size = 42
                line_height = 70
                padding = 450 # 顶部和底部的留白总和
                
                # 模拟换行处理，计算总行数
                all_lines_count = 0
                # 合并所有段落进行高度预估
                paragraphs = trans_content.split('\n') + ["", "【 核心词汇 】", ""] + vocab_content.split('\n')
                for para in paragraphs:
                    if not para.strip():
                        all_lines_count += 1 # 空行占位
                    else:
                        wrapped = textwrap.wrap(para, width=24)
                        all_lines_count += len(wrapped)
                
                # 动态计算高度：行数 * 行高 + 额外预留空间
                dynamic_height = all_lines_count * line_height + padding
                img_height = max(1600, dynamic_height) # 保底 1600 像素

                # 3. 创建动态高度的图片
                width = 1200
                img = Image.new('RGB', (width, img_height), color=COLOR_BG)
                draw = ImageDraw.Draw(img)
                
                # 加载字体
                try:
                    font_title = ImageFont.truetype(FONT_FILE, 60)
                    font_main = ImageFont.truetype(FONT_FILE, font_main_size)
                    font_logo = ImageFont.truetype(FONT_FILE, 70)
                except:
                    st.error(f"❌ 找不到字体文件 '{FONT_FILE}'，请确认已上传至GitHub。")
                    st.stop()

                # 4. 开始绘制内容
                # A. 顶部色块
                draw.rectangle([0, 0, 1200, 250], fill=COLOR_HEADER)
                draw.text((80, 85), "FINANCE DAILY NEWS", font=font_logo, fill=(255, 255, 255))
                
                # B. 绘制翻译部分
                draw.text((80, 320), "【 深度翻译 】", font=font_title, fill=COLOR_TITLE)
                y_cursor = 420
                
                def draw_section(text_block, current_y, fill_color):
                    paras = text_block.split('\n')
                    for para in paras:
                        if not para.strip():
                            current_y += 40 # 段落间的空行间距
                            continue
                        lines = textwrap.wrap(para, width=24)
                        for line in lines:
                            draw.text((80, current_y), line, font=font_main, fill=fill_color)
                            current_y += line_height
                        current_y += 20 # 段落后的微调间距
                    return current_y

                # 绘制正文
                y_cursor = draw_section(trans_content, y_cursor, COLOR_TEXT)
                
                # C. 绘制词汇部分
                y_cursor += 60
                draw.text((80, y_cursor), "【 核心词汇 】", font=font_title, fill=COLOR_TITLE)
                y_cursor += 100
                draw_section(vocab_content, y_cursor, (80, 80, 80))

                # 5. 输出展示
                st.image(img, caption="图片已根据内容长度自动延伸", use_container_width=True)
                st.balloons() 
                
                with st.expander("点击展开查看文本版"):
                    st.write(trans_content)
                    st.write(vocab_content)

            except Exception as e:
                st.error(f"❌ 生成失败: {e}")
