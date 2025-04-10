import streamlit as st
import pandas as pd
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import google.generativeai as genai
from dotenv import load_dotenv
import os
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import streamlit as st

try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except:
    from dotenv import load_dotenv
    load_dotenv()
    import os
    API_KEY = os.getenv("GEMINI_API_KEY")


# 載入 FAQ 資料
df = pd.read_csv("twse.csv", encoding='utf-8-sig')
paragraphs = (df["問題"] + " " + df["答案"]).tolist()

# 嵌入模型與 FAISS
@st.cache_resource
def load_model_and_index():
    model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    embeddings = model.encode(paragraphs, convert_to_numpy=True)
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)
    return model, index

embed_model, index = load_model_and_index()

# 檢索函數
def semantic_retrieve(query, k=2):
    query_vec = embed_model.encode([query], convert_to_numpy=True)
    D, I = index.search(query_vec, k)
    return [paragraphs[i] for i in I[0]]

def extract_url(text):
    urls = re.findall(r'https?://[^\s\)]+', text)
    return urls[0] if urls else None

def fetch_dynamic_url_text(url, wait_time=3):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')

    driver = webdriver.Chrome(options=options)
    driver.get(url)
    time.sleep(wait_time)

    text = ""
    try:
        # 優先抓主內容區（可能是主要段落）
        for tag_name in ["main", "article", "div", "section"]:
            try:
                element = driver.find_element("tag name", tag_name)
                if len(element.text.strip()) > 200:
                    text = element.text
                    break
            except:
                continue

        # fallback 抓 body
        if not text.strip():
            text = driver.find_element("tag name", "body").text

    finally:
        driver.quit()

    return text[:2000] + "..." if len(text) > 2000 else text


def summarize_text(text, model=None):
    if not model or not text.strip():
        return text[:300] + "..."  # fallback

    try:
        prompt = (
            f"【網站資料】：\n{text}\n\n【摘要】："
        )
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print("❌ 補充資料摘要失敗：", e)
        return text[:300] + "..."

# prompt 組合
def build_prompt(query, contexts):
    prompt = (
        "你是一位專業的金融投資顧問，請根據下列資料回答使用者的問題。\n\n"
        "請注意：\n"
        "- 僅根據提供資料作答，不要編造或推測。\n"
        "- 若資料不足，請明確說明「目前資料中無法回答此問題」。\n"
        "- 請以條列式說明，每點簡潔扼要，必要時可補充原文中的網址。\n\n"
        "【資料段落】\n"
    )
    supplement_blocks = []

    for i, ctx in enumerate(contexts):
        prompt += f"{i+1}. {ctx.strip()}\n"
        url = extract_url(ctx)
        if url:
            supplement = fetch_dynamic_url_text(url)
            if supplement:
                summary = summarize_text(supplement, model)
                supplement_blocks.append(f"補充資料 {i+1} 來自 {url}：\n{summary}")
                
    if supplement_blocks:
        prompt += "\n【補充資料區】\n" + "\n\n".join(supplement_blocks)

    prompt += f"\n【使用者提問】：{query}\n\n請根據上述資料，以條列式回答：\n"

    return prompt

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

st.title("💬 投資人智慧問答(RAG 強化)")

# 初始化對話記憶
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# 顯示過去的對話
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 使用者輸入區
user_input = st.chat_input("請輸入你的問題...")

try:
    if user_input:
        # 顯示使用者輸入
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # 呼叫 Gemini 回答
        with st.chat_message("assistant"):
            with st.spinner("搜尋知識中..."):
                contexts = semantic_retrieve(user_input)
                prompt = build_prompt(user_input, contexts)
                response = model.generate_content(prompt)
                st.markdown(response.text)

                # 顯示補充資料來源
                for i, ctx in enumerate(contexts):
                    url = extract_url(ctx)
                    if url:
                        supplement = fetch_dynamic_url_text(url)
                        if supplement:
                            st.markdown(f"🔗 補充資料 {i+1}: [{url}]({url})")
                            with st.expander(f"點此展開補充內容 {i+1}"):
                                st.markdown(supplement)

                # 加入 AI 回覆到對話歷史
                st.session_state.chat_history.append({"role": "assistant", "content": response.text})
except Exception as e:
     st.error("目前 Gemini API 已達配額限制，請稍後再試 🙏\n\n + str(e)")
