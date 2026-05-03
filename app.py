import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import textwrap

# 设置网页标题
st.set_page_config(page_title="小红书英语笔记生成器")
st.title("📰 财经英语海报生成器")

# 输入框
text_input = st.text_area("1. 粘贴英文新闻原文：", height=300)
translation_input = st.text_area("2. 粘贴中文翻译：", height=150)

if st.button("生成海报"):
    # 创建 3:4 的海报底图 (1200x1600)
    width, height = 1200, 1600
    img = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # 这里是绘图逻辑（注：Streamlit部署后需配置字体路径，稍后我教你）
    # 模拟一个色块作为标题背景
    draw.rectangle([0, 0, 1200, 300], fill=(40, 44, 52))
    
    st.image(img, caption="预览海报", use_column_width=True)
    st.success("海报生成成功！")
