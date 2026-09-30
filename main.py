import os
import sys
from dotenv import load_dotenv

from scrapers.youtube_scraper import get_video_transcript
from scrapers.youtube_vision import get_video_end_frame
from ai_engine.analyzer import analyze_crypto_multimodal
from notifier.discord_bot import send_to_discord
from scrapers.x_scraper import get_recent_tweets
from ai_engine.tweet_analyzer import filter_and_analyze_tweet
from state_manager import load_state, save_state

def process_youtube_video(video_url: str):
    print(f"\n🎬 開始處理 YouTube 影片 (綜合分析模式): {video_url}")
    
    state = load_state()
    if state.get("last_youtube_url") == video_url:
        print("💤 影片無更新，跳過分析。")
        return

    api_key = os.environ.get("GEMINI_API_KEY")
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")

    if not api_key or "你的_GEMINI_API_KEY" in api_key:
        print("❌ 找不到 GEMINI_API_KEY")
        return
    if not webhook_url or "你的_DISCORD_WEBHOOK" in webhook_url:
        print("❌ 找不到 DISCORD_WEBHOOK_URL")
        return

    print("⏳ 嘗試擷取影片字幕 (CC)...")
    transcript = get_video_transcript(video_url)
    if transcript.startswith("❌"):
        print(f"⚠️ 字幕抓取失敗: {transcript}")
        transcript = None
    else:
        print("✅ 成功獲取字幕！")

    print("⏳ 嘗試下載並截取片尾畫面 (Vision)...")
    image_path = get_video_end_frame(video_url)
    if image_path.startswith("❌"):
        print(f"⚠️ 截圖抓取失敗: {image_path}")
        image_path = None
    else:
        print("✅ 成功獲取片尾截圖！")

    if not transcript and not image_path:
        print("❌ 影片所有抓取管道皆失敗，無法進行分析。")
        return

    print("🧠 將取得的素材交給 Gemini 進行綜合分析...")
    analysis_result = analyze_crypto_multimodal(transcript, image_path, api_key)
    
    if image_path and os.path.exists(image_path):
        os.remove(image_path)

    if analysis_result.startswith("❌"):
        print(analysis_result)
        return

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
        state["last_youtube_url"] = video_url
        save_state(state)

def process_twitter_account(username: str):
    print(f"\n🐦 開始追蹤 X 帳號: @{username}")
    apify_token = os.environ.get("APIFY_API_TOKEN")
    if not apify_token:
        print("❌ 找不到 APIFY_API_TOKEN")
        return

    state = load_state()
    last_tweet_id = state.get("last_tweet_id")

    # 為了確保抓到更新，稍微多抓幾則，再用程式過濾
    tweets = get_recent_tweets(username, pages=1)
    
    if tweets is None:
        print("❌ 抓取推文失敗 (API 錯誤或資料格式解析失敗)。")
        return
    elif not tweets:
        print("💤 該帳號目前沒有任何推文。")
        return

    api_key = os.environ.get("GEMINI_API_KEY")
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    
    new_tweets = []
    for tweet in tweets:
        # Twitter ID 越大代表越新，我們比較 ID 大小來判斷是否為新推文
        if last_tweet_id is None or int(tweet['id']) > int(last_tweet_id):
            new_tweets.append(tweet)

    if not new_tweets:
        print("💤 自上次排程以來沒有新推文。")
        return

    print(f"⏳ 發現 {len(new_tweets)} 則新推文，交給 AI 過濾...")
    
    max_processed_id = last_tweet_id
    
    # 從舊到新處理，這樣如果中斷，狀態紀錄比較準確
    for tweet in reversed(new_tweets):
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
        
        # 更新目前處理過的最大推文 ID
        if max_processed_id is None or int(tweet['id']) > int(max_processed_id):
            max_processed_id = tweet['id']

    # 處理完所有新推文後，儲存狀態
    if max_processed_id:
        state["last_tweet_id"] = str(max_processed_id)
        save_state(state)

if __name__ == "__main__":
    load_dotenv()
    print("🚀 Crypto KOL Tracker 啟動！")
    
    process_twitter_account("giantcutie666")
    
    test_video_url = "https://www.youtube.com/watch?v=BfdLvZRR660"
    process_youtube_video(test_video_url)
