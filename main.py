import os
import sys
from dotenv import load_dotenv
from scrapers.youtube_vision import get_video_end_frame, analyze_crypto_image
from notifier.discord_bot import send_to_discord

from scrapers.x_scraper import get_recent_tweets
from ai_engine.tweet_analyzer import filter_and_analyze_tweet

def process_youtube_video(video_url: str):
    print(f"\n🎬 開始處理 YouTube 影片: {video_url}")

    print("⏳ 正在下載並截取片尾畫面...")
    image_path = get_video_end_frame(video_url)
    if image_path.startswith("❌"):
        print(image_path)
        return

    print("✅ 截圖成功，準備進行 AI 視覺分析...")
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key or "你的_GEMINI_API_KEY" in api_key:
        print("❌ 找不到 GEMINI_API_KEY")
        return

    analysis_result = analyze_crypto_image(image_path, api_key)
    if analysis_result.startswith("❌"):
        print(analysis_result)
        return

    print("✅ AI 視覺分析完成！準備推播至 Discord...")
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    if not webhook_url or "你的_DISCORD_WEBHOOK" in webhook_url:
        print("❌ 找不到 DISCORD_WEBHOOK_URL")
        return

    # 在訊息中補上 URL
    final_content = analysis_result.replace("發布渠道**：YouTube", f"發布渠道**：YouTube\n   🔗 **影片連結**：{video_url}")

    success = send_to_discord(
        title="📊 AI 交易訊號 (視覺讀圖)",
        content=final_content,
        webhook_url=webhook_url,
        url=video_url
    )

    if success:
        print("🎉 YouTube 流程完成！")
        # 清理暫存圖片
        if os.path.exists(image_path):
            os.remove(image_path)

def process_twitter_account(username: str):
    print(f"\n🐦 開始追蹤 X 帳號: @{username}")
    auth_token = os.environ.get("X_AUTH_TOKEN")
    if not auth_token:
        print("❌ 找不到 X_AUTH_TOKEN，請確認環境變數或 GitHub Secrets")
        return

    # 抓取最新推文
    tweets = get_recent_tweets(username, auth_token=auth_token, pages=1)
    if not tweets:
        print("❌ 抓取推文失敗或無新推文。")
        return

    api_key = os.environ.get("GEMINI_API_KEY")
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")

    # 為了避免初次啟動發送太多，我們先取前 3 則最新推文 (含回覆) 進行分析
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
    
    # 2. 執行 YouTube 視覺擷圖分析
    print("\nℹ️ 執行 YouTube 預設測試流程...")
    test_video_url = "https://www.youtube.com/watch?v=BfdLvZRR660"
    process_youtube_video(test_video_url)
