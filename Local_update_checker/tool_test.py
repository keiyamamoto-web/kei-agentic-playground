import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

async def fetch_release_text(url: str) -> str:
    """
    Playwright (Async) を使用して、JavaScript実行後のHTMLからテキストを抽出します。
    """
    try:
        async with async_playwright() as p:
            # ブラウザを起動 (chromium)
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page(user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36")
            
            # URLに遷移
            # wait_until="networkidle" を使用して、通信が落ち着くまで待機
            await page.goto(url, wait_until="networkidle", timeout=30000)
            
            # 追加の待機が必要な場合（SPA等のため、少し余裕を持つ）
            await page.wait_for_timeout(2000) 
            
            content = await page.content()
            await browser.close()
            
        soup = BeautifulSoup(content, 'html.parser')
        
        # 不要なタグを排除
        for element in soup(['script', 'style', 'nav', 'footer', 'header', 'iframe']):
            element.decompose()
            
        # テキスト抽出（冒頭3000文字程度を返す）
        text = soup.get_text(separator=' ', strip=True)
        return text[:3000]
        
    except Exception as e:
        return f"Error fetching {url} with Playwright (Async): {str(e)}"

# 検証用
if __name__ == "__main__":
    test_url = "https://antigravity.google/changelog"
    print(f"Testing URL (Async Browser Mode): {test_url}")
    result = asyncio.run(fetch_release_text(test_url))
    print(result)