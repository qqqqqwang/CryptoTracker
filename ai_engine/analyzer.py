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

from PIL import Image

def analyze_crypto_multimodal(transcript: str, image_path: str, api_key: str):
    """
    綜合分析字幕與截圖 (若其中一個缺失則自動適應)
    """
    if not api_key:
        return "❌ 錯誤: 未提供 Gemini API Key"
        
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-3.8-flash')
        
        prompt = """
        你是一個專業的加密貨幣交易訊號過濾器。
        我將提供一位分析師最新 YouTube 影片的資訊給你。
        
        【排版與內容嚴格規則】：
        1. ⚠️ **絕對不要使用 Markdown 表格 (Table)**：請一律使用「條列式 (Bullet points)」搭配粗體與 Emoji。
        2. **標題動態化**：根據提及的「所有幣種」下標，例如 `# 🔔 [BTC, SOL] 最新交易策略`。
        3. **大盤觀點**：精簡總結短線與長線觀點。
        4. **操作策略與點位**：明確列出阻力、支撐、目標價。過濾掉免責聲明。
        """
        
        contents = [prompt]
        
        if transcript and not transcript.startswith("❌"):
            contents.append(f"\n以下是影片字幕內容：\n{transcript}\n")
            
        if image_path and not image_path.startswith("❌") and os.path.exists(image_path):
            contents.append("\n以下是影片片尾的總結圖表截圖：\n")
            contents.append(Image.open(image_path))
            
        if len(contents) == 1:
            return "❌ 無法取得任何分析材料 (無字幕且無圖表)"
            
        response = model.generate_content(contents)
        return response.text.strip()
        
    except Exception as e:
        return f"❌ 綜合 AI 分析失敗: {str(e)}"
