import os
import cv2
import yt_dlp
import google.generativeai as genai
from PIL import Image

def get_video_end_frame(video_url: str, output_image_path: str = "end_frame.jpg"):
    """
    下載影片並截取片尾畫面 (倒數 5 秒處)
    """
    print(f"🎥 正在解析 YouTube 影片: {video_url}")
    
    # yt-dlp 設定：抓取最低畫質即可，並下載為暫存檔案
    temp_video_file = "temp_video.mp4"
    ydl_opts = {
        'format': 'worstvideo[ext=mp4]+worstaudio[ext=m4a]/worst[ext=mp4]/worst',
        'outtmpl': temp_video_file,
        'quiet': True,
        'noplaylist': True,
        'cookiesfrombrowser': ('chrome', ) # 自動讀取 Chrome 瀏覽器的 YouTube 登入狀態來繞過阻擋
    }

    try:
        # 如果存在舊檔案則先刪除
        if os.path.exists(temp_video_file):
            os.remove(temp_video_file)

        print("⏱️ 正在下載影片暫存檔...")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            duration = info.get('duration', 0)

        if not os.path.exists(temp_video_file):
            return "❌ 影片下載失敗"

        print(f"⏱️ 影片總長度: {duration} 秒，正在讀取畫面...")
        
        # 使用 OpenCV 讀取本地檔案
        cap = cv2.VideoCapture(temp_video_file)
        if not cap.isOpened():
            return "❌ OpenCV 無法開啟本地影片"

        # 跳轉到倒數 5 秒的位置
        target_time = max(0, duration - 5)
        cap.set(cv2.CAP_PROP_POS_MSEC, target_time * 1000)

        ret, frame = cap.read()
        cap.release()
        
        # 刪除暫存影片
        if os.path.exists(temp_video_file):
            os.remove(temp_video_file)

        if ret:
            cv2.imwrite(output_image_path, frame)
            print(f"✅ 成功截取片尾畫面: {output_image_path}")
            return output_image_path
        else:
            return "❌ 無法截取影片畫面"

    except Exception as e:
        return f"❌ 影片解析失敗: {str(e)}"

def analyze_crypto_image(image_path: str, api_key: str):
    """
    使用 Gemini Vision 分析截圖中的交易策略
    """
    if not api_key:
        return "❌ 錯誤: 未提供 Gemini API Key"
        
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-3.8-flash')
        
        img = Image.open(image_path)
        
        prompt = """
        這是一張加密貨幣分析師影片片尾的策略截圖。
        請精準讀取圖片文字，整理成一份簡潔、有條理的「交易訊號通知」。

        【排版與內容嚴格規則】：
        1. ⚠️ **絕對不要使用 Markdown 表格 (Table)**：Discord 無法正常渲染表格，請一律使用「條列式 (Bullet points)」搭配粗體。
        2. **標題動態化**：請根據圖中實際提到的「所有幣種」來下標題。例如 `# 🔔 [BTC, SOL] 最新交易策略`。
        3. **資訊來源 Header**：請在最開頭加上（佔位符，影片連結由外部補上）：
           👤 **分析師**：大漂亮 (GiantCutie-K)
           📺 **發布渠道**：YouTube
           ---
        4. **大盤觀點**：精簡總結短線與長線觀點。
        5. **操作策略與點位**：明確列出阻力、支撐、目標價。請用 Emoji 輔助閱讀。
        6. 過濾掉底部的免責聲明。
        """
        
        response = model.generate_content([prompt, img])
        return response.text.strip()
        
    except Exception as e:
        return f"❌ 視覺 AI 分析失敗: {str(e)}"
