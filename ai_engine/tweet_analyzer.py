import os
import google.generativeai as genai

def filter_and_analyze_tweet(tweet_text: str, tweet_url: str, api_key: str):
    """
    分析推文是否包含交易信號，並格式化輸出。
    如果只是生活閒聊，則回傳 "無效訊號"
    """
    if not api_key:
        return "❌ 錯誤: 未提供 Gemini API Key"
        
    try:
        genai.configure(api_key=api_key)
        # 使用 Gemini 3.8 Flash
        model = genai.GenerativeModel('gemini-3.8-flash')
        
        prompt = f"""
        你是一個專業的加密貨幣交易訊號過濾器。
        請閱讀以下這則來自分析師（大漂亮 GiantCutie-K）的推文。

        任務：
        1. 判斷這則推文是否包含「明確的交易訊號、幣種觀點、點位預測或換倉動作」。
        2. 如果是「生活廢文、純閒聊、沒有具體市場分析」，請只輸出四個字：「無效訊號」。絕對不要輸出其他內容。
        3. 如果「包含交易訊號」，請幫我整理成一份簡潔的「交易策略通知」。

        【有效訊號的排版與內容嚴格規則】：
        1. ⚠️ **絕對不要使用 Markdown 表格 (Table)**，請用「條列式 (Bullet points)」搭配粗體。
        2. **標題動態化**：根據提及的幣種下標，如 `# 🔔 [ETH, SOL] 交易策略通知`。
        3. **資訊來源 Header**（直接照抄填入）：
           👤 **分析師**：大漂亮 (GiantCutie-K)
           📺 **發布渠道**：X (Twitter)
           🔗 **原文連結**：{tweet_url}
           ---
        4. 條列式整理大盤觀點、操作策略與點位（使用 Emoji 標註）。

        以下是推文內容：
        ---
        {tweet_text}
        """
        
        response = model.generate_content(prompt)
        return response.text.strip()
        
    except Exception as e:
        return f"❌ AI 推文分析失敗: {str(e)}"
