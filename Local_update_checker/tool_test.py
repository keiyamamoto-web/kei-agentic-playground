from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

def fetch_release_text(url: str) -> str:
    """
    Playwrightを使用して、JavaScript実行後のHTMLからテキストを抽出します。
    """
    try:
        with sync_playwright() as p:
            # ブラウザを起動 (chromium)
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36")
            
            # URLに遷移
            # wait_until="networkidle" を使用して、通信が落ち着くまで待機
            page.goto(url, wait_until="networkidle", timeout=30000)
            
            # 追加の待機が必要な場合（SPA等のため、少し余裕を持つ）
            page.wait_for_timeout(2000) 
            
            content = page.content()
            browser.close()
            
        soup = BeautifulSoup(content, 'html.parser')
        
        # 不要なタグを排除
        for element in soup(['script', 'style', 'nav', 'footer', 'header', 'iframe']):
            element.decompose()
            
        # テキスト抽出（冒頭3000文字程度を返す）
        text = soup.get_text(separator=' ', strip=True)
        return text[:3000]
        
    except Exception as e:
        return f"Error fetching {url} with Playwright: {str(e)}"

# 検証：JS必須の Antigravity Changelog でテスト
if __name__ == "__main__":
    # test_url = "https://docs.cloud.google.com/vertex-ai/docs/release-notes"
    test_url = "https://antigravity.google/changelog"
    print(f"Testing URL (Browser Mode): {test_url}")
    print(fetch_release_text(test_url))