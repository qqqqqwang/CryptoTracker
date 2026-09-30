import os
import sys
from dotenv import load_dotenv

# YouTube 模組
from scrapers.youtube_scraper import get_video_transcript
from scrapers.youtube_vision import get_video_end_frame
from ai_engine.analyzer import analyze_crypto_multimodal

# 推播模組
from notifier.discord_bot import send_to_discord

# Twitter 模組 (Apify)
from scrapers.x_scraper import get_recent_tweets
from ai_engine.tweet_analyzer import filter_and_analyze_tweet

def process_youtube_video(video_url: str):
    """
    綜合分析模式：同時嘗試獲取字幕(CC)與片尾截圖(Vision)。
    只要其中一項成功，就交給 Gemini 進行推理分析。
    """
    print(f"\n🎬 開始處理 YouTube 影片 (綜合分析模式): {video_url}")
    
    api_key = os.environ.get("GEMINI_API_KEY")
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")

    if not api_key or "你的_GEMINI_API_KEY" in api_key:
        print("❌ 找不到 GEMINI_API_KEY")
        return
    if not webhook_url or "你的_DISCORD_WEBHOOK" in webhook_url:
        print("❌ 找不到 DISCORD_WEBHOOK_URL")
        return

    # 1. 嘗試抓取字幕
    print("⏳ 嘗試擷取影片字幕 (CC)...")
    transcript = get_video_transcript(video_url)
    if transcript.startswith("❌"):
        print(f"⚠️ 字幕抓取失敗 (或該影片無字幕): {transcript}")
        transcript = None
    else:
        print("✅ 成功獲取字幕！")

    # 2. 嘗試抓取截圖
    print("⏳ 嘗試下載並截取片尾畫面 (Vision)...")
    image_path = get_video_end_frame(video_url)
    if image_path.startswith("❌"):
        print(f"⚠️ 截圖抓取失敗: {image_path}")
        image_path = None
    else:
        print("✅ 成功獲取片尾截圖！")

    # 3. 判斷是否有任何素材
    if not transcript and not image_path:
        print("❌ 影片所有抓取管道皆失敗，無法進行分析。")
        return

    # 4. 進行綜合 AI 分析
    print("🧠 將取得的素材交給 Gemini 進行綜合分析...")
    analysis_result = analyze_crypto_multimodal(transcript, image_path, api_key)
    
    # 清理暫存圖片
    if image_path and os.path.exists(image_path):
        os.remove(image_path)

    if analysis_result.startswith("❌"):
        print(analysis_result)
        return

    print("✅ AI 綜合分析完成！準備推播至 Discord...")

    # 格式化 Header
    header = f"👤 **分析師**：大漂亮 (GiantCutie-K)\n📺 **發布渠道**：YouTube\n🔗 **影片連結**：{video_url}\n---\n"
    final_content = header + analysis_result

    success = send_to_discord(
        title="📈 AI 交易訊號 (YouTube 綜合解析)",
        content=final_content,
        webhook_url=webhook_url,
        url=video_url
    )

    if success:
        print("🎉 YouTube 綜合分析推播完成！")

def process_twitter_account(username: str):
    print(f"\n🐦 開始追蹤 X 帳號: @{username}")
    apify_token = os.environ.get("APIFY_API_TOKEN")
    if not apify_token:
        print("❌ 找不到 APIFY_API_TOKEN，請確認環境變數或 GitHub Secrets")
        return

    # 抓取最新推文
    tweets = get_recent_tweets(username, pages=1)
    if not tweets:
        print("❌ 抓取推文失敗或無新推文。")
        return

    api_key = os.environ.get("GEMINI_API_KEY")
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")

    print(f"⏳ 成功抓取 {len(tweets)} 則推文，交給 AI 過濾前 3 則最新內容...")
    
    for tweet in tweets[:3]:
        result = filter_and_analyze_tweet(tweet['text'], tweet['url'], api_key)
        
        if "無效訊號" in result:
            print(f"💤 忽略推文 [{tweet['id']}]: 生活廢文/無交易訊號")
        elif result.startswith("❌"):
            print(f"⚠️ 錯誤: {result}")
        else:
            print(f"🚨 發現交易訊號！推文 [{tweet['id']}]")
            send_to_discord(
                title="💡 AI 交易訊號推播 (來自 X 平台)",
                content=result,
                webhook_url=webhook_url,
                url=tweet['url']
            )

if __name__ == "__main__":
    load_dotenv()
    print("🚀 Crypto KOL Tracker 啟動！")
    
    # 1. 執行 X (Twitter) 自動追蹤與過濾
    process_twitter_account("giantcutie666")
    
    # 2. 執行 YouTube 綜合分析
    test_video_url = "https://www.youtube.com/watch?v=BfdLvZRR660"
    process_youtube_video(test_video_url)
