import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import google.generativeai as genai
import textwrap

# 1. AI 配置
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"API配置失败，请检查Secrets: {e}")

st.title("🎨 财经英语·小红书海报生成器")

# 2. 输入区域
english_text = st.text_area("1. 粘贴英文新闻原文：", height=250, placeholder="在此处粘贴英文内容...")

if st.button("🚀 一键全自动生成海报"):
    if not english_text:
        st.warning("请输入英文原文后再点击生成。")
    else:
        with st.spinner('AI 正在翻译并排版中...'):
            # 3. 让 AI 按照固定格式输出，方便程序解析
            prompt = f"""
            你是一个专业的财经翻译。请处理以下内容：
            1. 翻译成地道、优雅的中文（适合小红书财经博主风格）。
            2. 提取3个核心关键词，给出中文解释。
            格式要求：
            [TRANSLATION]
            (此处只写翻译内容)
            [VOCAB]
            (此处只写词汇解析)
            
            原文：{english_text}
            """
            
            try:
                response = model.generate_content(prompt)
                full_result = response.text
                
                # 简单的格式解析
                trans_part = full_result.split("[TRANSLATION]")[1].split("[VOCAB]")[0].strip()
                vocab_part = full_result.split("[VOCAB]")[1].strip()
                
                # 4. 绘图逻辑开始
                width, height = 1200, 1600
                img = Image.new('RGB', (width, height), color=(255, 255, 255))
                draw = ImageDraw.Draw(img)
                
                # --- 加载字体 (请确保 GitHub 仓库里有这个文件) ---
                # 建议上传 SourceHanSans-Bold.ttf 或 SimHei.ttf
                font_path = "SimHei.ttf" 
                try:
                    font_title = ImageFont.truetype(font_path, 65)
                    font_main = ImageFont.truetype(font_path, 42)
                except:
                    st.error(f"找不到字体文件 '{font_path}'，请确保已上传到GitHub仓库根目录。")
                    st.stop()

                # 绘制顶部黑色深色块 (高级感)
                draw.rectangle([0, 0, 1200, 250], fill=(30, 30, 30))
                draw.text((80, 80), "DAILY FINANCE ENGLISH", font=font_title, fill=(255, 255, 255))
                
                # 绘制翻译标题
                draw.text((80, 320), "【 深度翻译 】", font=font_title, fill=(230, 70, 70))
                
                # 自动换行处理翻译内容
                y_cursor = 420
                lines = textwrap.wrap(trans_part, width=24) # 这里的24是中文字数
                for line in lines:
                    draw.text((80, y_cursor), line, font=font_main, fill=(40, 40, 40))
                    y_cursor += 70
                
                # 绘制词汇标题
                y_cursor += 60
                draw.text((80, y_cursor), "【 核心词汇 】", font=font_title, fill=(230, 70, 70))
                
                # 自动换行处理词汇解析
                y_cursor += 100
                vocab_lines = textwrap.wrap(vocab_part, width=24)
                for v_line in vocab_lines:
                    draw.text((80, y_cursor), v_line, font=font_main, fill=(60, 60, 60))
                    y_cursor += 70

                # 5. 在网页上显示
                st.image(img, caption="长按图片保存到手机", use_container_width=True)
                st.balloons()
                
            except Exception as e:
                st.error(f"生成过程中出错: {e}")
