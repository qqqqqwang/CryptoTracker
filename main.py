import os
import sys
from dotenv import load_dotenv
from scrapers.youtube_scraper import get_video_transcript
from ai_engine.analyzer import analyze_crypto_text
from notifier.discord_bot import send_to_discord

from scrapers.x_scraper import get_recent_tweets
from ai_engine.tweet_analyzer import filter_and_analyze_tweet

def process_youtube_video(video_url: str):
    print(f"\n🎬 開始處理 YouTube 影片: {video_url}")

    print("⏳ 正在擷取影片字幕...")
    transcript = get_video_transcript(video_url)
    if transcript.startswith("❌"):
        print(transcript)
        return

    print("✅ 字幕擷取成功，準備進行 AI 分析...")
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key or "你的_GEMINI_API_KEY" in api_key:
        print("❌ 找不到 GEMINI_API_KEY")
        return

    analysis_result = analyze_crypto_text(transcript, api_key)
    if analysis_result.startswith("❌"):
        print(analysis_result)
        return

    print("✅ AI 分析完成！準備推播至 Discord...")
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    if not webhook_url or "你的_DISCORD_WEBHOOK" in webhook_url:
        print("❌ 找不到 DISCORD_WEBHOOK_URL")
        return

    success = send_to_discord(
        title="📈 AI 加密貨幣交易訊號 (來自 YouTube)",
        content=analysis_result,
        webhook_url=webhook_url,
        url=video_url
    )

    if success:
        print("🎉 YouTube 流程完成！")

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
    
    # 2. 執行 YouTube (目前仍先跑測試網址確保流程暢通，待下次加入視覺擷圖模組)
    print("\nℹ️ 執行 YouTube 預設測試流程...")
    test_video_url = "https://www.youtube.com/watch?v=BfdLvZRR660"
    process_youtube_video(test_video_url)
