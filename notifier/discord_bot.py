import os
import requests
import json
from datetime import datetime

def send_to_discord(title: str, content: str, webhook_url: str, color: int = 5814783, url: str = None):
    """
    發送格式化的訊息到 Discord Webhook
    :param title: 訊息標題
    :param content: 訊息主要內容 (支援 Markdown)
    :param webhook_url: Discord Webhook 網址
    :param color: 側邊顏色條 (預設為藍紫色)
    :param url: 點擊標題可前往的網址 (選填)
    """
    if not webhook_url:
        print("❌ 錯誤: 未提供 Discord Webhook URL")
        return False
        
    embed = {
        "title": title,
        "description": content,
        "color": color,
        "footer": {
            "text": f"AI Crypto Tracker • {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        }
    }
    
    if url:
        embed["url"] = url

    payload = {
        "embeds": [embed]
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(webhook_url, data=json.dumps(payload), headers=headers)
        if response.status_code == 204:
            print(f"✅ 成功發送通知至 Discord: {title}")
            return True
        else:
            print(f"❌ 發送失敗，狀態碼: {response.status_code}, 回應: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 發生例外錯誤: {str(e)}")
        return False
