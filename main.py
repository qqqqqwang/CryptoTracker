import os
import sys
from dotenv import load_dotenv
from scrapers.youtube_scraper import get_video_transcript
from ai_engine.analyzer import analyze_crypto_text
from notifier.discord_bot import send_to_discord

def process_youtube_video(video_url: str):
    print(f"\n🎬 開始處理影片: {video_url}")

    # 1. 抓取字幕
    print("⏳ 正在擷取影片字幕...")
    transcript = get_video_transcript(video_url)
    if transcript.startswith("❌"):
        print(transcript)
        return

    print("✅ 字幕擷取成功，準備進行 AI 分析...")

    # 2. AI 分析
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key or "你的_GEMINI_API_KEY" in api_key:
        print("❌ 找不到 GEMINI_API_KEY，請確認 .env 檔案設定")
        return

    print("⏳ AI 正在閱讀並總結影片內容...")
    analysis_result = analyze_crypto_text(transcript, api_key)
    if analysis_result.startswith("❌"):
        print(analysis_result)
        return

    print("✅ AI 分析完成！準備推播至 Discord...")

    # 3. Discord 推播
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    if not webhook_url or "你的_DISCORD_WEBHOOK" in webhook_url:
        print("❌ 找不到 DISCORD_WEBHOOK_URL，請確認 .env 檔案設定")
        return

    success = send_to_discord(
        title="📈 AI 加密貨幣交易訊號 (來自 YouTube)",
        content=analysis_result,
        webhook_url=webhook_url,
        url=video_url
    )

    if success:
        print("🎉 處理流程全部完成！你可以去 Discord 看看有沒有收到訊息了。")

if __name__ == "__main__":
    # 載入 .env 環境變數
    load_dotenv()
    
    if len(sys.argv) > 1:
        test_video_url = sys.argv[1]
    else:
        # 在 GitHub Actions 等無頭環境中，如果沒有傳入參數，避免使用 input() 導致程式崩潰 (EOFError)
        print("\nℹ️ 未提供影片網址。這是一次自動排程執行 (Cron-job)。")
        print("🔧 未來這裡將會加入自動獲取最新影片的邏輯，目前先以測試網址執行，確保流程暢通。")
        test_video_url = "https://www.youtube.com/watch?v=BfdLvZRR660" # 預設測試網址
        
    if test_video_url:
        process_youtube_video(test_video_url)
