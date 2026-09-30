import os
from tweety import Twitter
from tweety.filters import SearchFilters

def get_recent_tweets(username: str, auth_token: str = None, pages: int = 1):
    """
    使用 tweety-ns 抓取使用者的最新推文與回覆
    """
    app = Twitter("session")
    
    try:
        if auth_token:
            # 登入以繞過 Twitter 限制
            app.load_auth_token(auth_token)
        
        print(f"正在抓取 @{username} 的最新推文...")
        # 取得使用者推文 (包含回覆)
        tweets = app.get_tweets(username, pages=pages)
        
        extracted_tweets = []
        for tweet in tweets:
            extracted_tweets.append({
                "id": tweet.id,
                "text": tweet.text,
                "url": tweet.url,
                "date": tweet.date,
                "is_reply": tweet.is_reply
            })
            
        return extracted_tweets
        
    except Exception as e:
        print(f"❌ 抓取 Twitter 失敗: {str(e)}")
        return []
