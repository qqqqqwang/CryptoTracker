from youtube_transcript_api import YouTubeTranscriptApi
import re

def extract_video_id(url: str) -> str:
    """從 YouTube 網址中提取 Video ID"""
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
    return match.group(1) if match else None

def get_video_transcript(video_url: str, language: str = 'zh-Hant') -> str:
    """
    抓取 YouTube 影片的 CC 字幕 (支援繁體中文/簡體中文/英文自動翻譯)
    """
    video_id = extract_video_id(video_url)
    if not video_id:
        return "❌ 無效的 YouTube 網址"
        
    try:
        # 嘗試抓取繁體中文，若無則抓取其他可用語言並翻譯
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        try:
            # 優先找中文
            transcript = transcript_list.find_transcript(['zh-TW', 'zh-Hant', 'zh-Hans', 'zh-CN'])
        except:
            # 如果沒有中文，抓預設語言然後翻譯成中文
            transcript = transcript_list.find_transcript(['en']).translate('zh-Hant')
            
        result = transcript.fetch()
        
        # 將零碎的字幕拼接成一段完整的純文本
        full_text = " ".join([item['text'] for item in result])
        
        # 如果字幕太長，做簡單的截斷限制前 15000 字元
        return full_text[:15000]
        
    except Exception as e:
        return f"❌ 無法獲取字幕: {str(e)}"
