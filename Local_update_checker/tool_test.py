import httpx
from bs4 import BeautifulSoup

def fetch_release_text(url: str) -> str:
    """
    指定されたURLからHTMLを取得し、日付情報が含まれる可能性が高いテキストを抽出します。
    """
    try:
        # User-Agentを設定してブロックを回避
        headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}
        response = httpx.get(url, headers=headers, follow_redirects=True, timeout=15.0)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 不要なタグ（script, style, nav, footer等）を排除
        for element in soup(['script', 'style', 'nav', 'footer', 'header']):
            element.decompose()
            
        # 最初の2000文字程度を抽出（リリースノートは冒頭に日付が固まる傾向があるため）
        text = soup.get_text(separator=' ', strip=True)
        return text[:2000]
    except Exception as e:
        return f"Error fetching {url}: {str(e)}"

# 検証：Vertex AIのリリースノートでテスト
if __name__ == "__main__":
    test_url = "https://docs.cloud.google.com/vertex-ai/docs/release-notes"
    print(f"Testing URL: {test_url}")
    print(fetch_release_text(test_url))