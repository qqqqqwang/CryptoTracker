import os
import google.generativeai as genai

def analyze_crypto_text(text: str, api_key: str) -> str:
    """
    使用 Gemini 分析文本，提取加密貨幣大盤觀點與交易訊號。
    """
    if not api_key:
        return "❌ 錯誤: 未提供 Gemini API Key"
        
    try:
        genai.configure(api_key=api_key)
        
        # 使用 Gemini 3.8 Flash 速度快且便宜
        model = genai.GenerativeModel('gemini-3.8-flash')
        
        prompt = f"""
        你是一位專業的加密貨幣交易助理。請閱讀以下來自社群/影片的文本，並提取關鍵資訊：
        
        1. **大盤觀點**：請用 1~2 句話總結作者對總體市場的看法（看多、看空、震盪等）。
        2. **提及幣種與點位**：如果文本中有明確提到特定幣種（如 BTC, ETH, SOL）的看好/看壞原因，或是具體的進出場點位（例如 60k 以下買入），請以條列式清楚列出：
           - 【幣種】動作 (買入/賣出/換倉) : 點位與原因
        3. 如果通篇只是閒聊，沒有任何與市場分析或交易相關的內容，請直接回覆：「無有效交易訊號」。

        請用繁體中文，並以清晰的 Markdown 格式輸出。
        
        以下是原始文本：
        ---
        {text}
        """
        
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        return f"❌ AI 分析失敗: {str(e)}"
