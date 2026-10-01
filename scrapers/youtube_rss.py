import requests
import xml.etree.ElementTree as ET

def get_latest_youtube_video(channel_id: str) -> str:
    """
    透過 YouTube 官方 RSS 獲取頻道的最新影片網址。
    完全合法，不需要 Cookie，不會被擋。
    """
    url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # 解析 XML
        root = ET.fromstring(response.content)
        
        # XML Namespace 處理
        namespaces = {'default': 'http://www.w3.org/2005/Atom', 'yt': 'http://www.youtube.com/xml/schemas/2015'}
        
        # 找第一筆 entry
        entry = root.find('default:entry', namespaces)
        if entry is not None:
            video_id_elem = entry.find('yt:videoId', namespaces)
            if video_id_elem is not None:
                video_id = video_id_elem.text
                return f"https://www.youtube.com/watch?v={video_id}"
                
        return None
    except Exception as e:
        print(f"❌ 獲取 YouTube RSS 失敗: {str(e)}")
        return None
