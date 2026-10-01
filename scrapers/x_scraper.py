import os
from apify_client import ApifyClient

def get_recent_tweets(username: str, pages: int = 1):
    """
    使用 Apify (apidojo/tweet-scraper) 抓取使用者的最新推文與回覆
    """
    apify_token = os.environ.get("APIFY_API_TOKEN")
    if not apify_token:
        print("❌ 找不到 APIFY_API_TOKEN")
        return []

    client = ApifyClient(apify_token)

    run_input = {
        "twitterHandles": [username],
        "maxItems": 3,
    }

    try:
        print(f"正在透過 Apify 抓取 @{username} 的最新推文...")
        run = client.actor("apidojo/tweet-scraper").call(run_input=run_input)
        
        extracted_tweets = []
        for item in client.dataset(run["defaultDatasetId"]).iterate_items():
            tweet_text = item.get("text") or item.get("full_text")
            tweet_id = str(item.get("id"))
            tweet_url = item.get("url") or f"https://x.com/i/status/{tweet_id}"
            date = item.get("createdAt") or item.get("created_at")
            
            if tweet_text and tweet_id:
                extracted_tweets.append({
                    "id": tweet_id,
                    "text": tweet_text,
                    "url": tweet_url,
                    "date": date,
                    "is_reply": item.get("isReply", False)
                })
            
        return extracted_tweets
        
    except Exception as e:
        print(f"❌ 抓取 Twitter 失敗: {str(e)}")
        return None
