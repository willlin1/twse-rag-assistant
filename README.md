# twse-rag-assistant

# 💬 TWSE 投資人智慧問答系統（RAG 強化版）

本專案是一個基於 Retrieval-Augmented Generation（RAG） 的問答系統，針對「台灣證券交易所投資人FAQ」進行語意檢索與智慧回答。系統結合語意向量檢索、網站補充資料爬蟲、自動摘要與 Gemini LLM 回答生成，並部署於雲端平台供即時互動。

👉 [點我體驗線上系統](https://your-streamlit-app-url.streamlit.app)

---

## 💡 功能亮點

- ✅ 語意搜尋：使用 Sentence-Transformer + FAISS 建立語意檢索向量庫
- ✅ 補充資料：自動擷取 FAQ 回答中的網址並動態爬取原始網站內容
- ✅ 自動摘要：透過 Gemini 將網頁資訊摘要為關鍵知識補充，提升 LLM 理解力
- ✅ RAG 組合：將 FAQ + 補充資料整合為 prompt，由 LLM 條列式回答問題
- ✅ 雲端部署：完整部署於 Streamlit Cloud，支援即時互動與快速 Demo 展示

---

## 🖼️ 介面預覽

![image](https://github.com/user-attachments/assets/d74fbf2d-ff13-4286-aedb-6fff5064fd2a)

---

## ⚙️ 技術架構

| 類別 | 技術 |
|------|------|
| 前端介面 | Streamlit |
| 向量檢索 | FAISS + Sentence-Transformers |
| LLM | Gemini 1.5 Flash (via Google Generative AI API) |
| 爬蟲 | requests / Selenium + BeautifulSoup |
| 自動摘要 | Gemini API 總結補充資料 |
| 快取處理 | JSON 快取 + 預抓邏輯 |
| 部署 | Streamlit Cloud |

---

## 📦 安裝與使用

```bash
git clone https://github.com/你的帳號/twse-rag-assistant.git
cd twse-rag-assistant

# 建立虛擬環境（建議）
python -m venv venv
source venv/bin/activate  # 或 Windows: venv\Scripts\activate

# 安裝依賴
pip install -r requirements.txt

# 設定環境變數
echo "GEMINI_API_KEY=你的KEY" > .env

# 執行
streamlit run app.py
