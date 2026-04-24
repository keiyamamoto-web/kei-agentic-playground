import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
async def fetch_release_text(url: str) -> str:
    """
    Playwright (Async) を使用して、JavaScript実行後のHTMLからテキストを抽出します。
    tenacityによるリトライ処理付き。
    """
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            # タイムアウトを少し長めに設定 (45秒)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                viewport={'width': 1280, 'height': 800}
            )
            page = await context.new_page()
            
            # wait_until="domcontentloaded" に変更し、その後の追加待機で制御
            await page.goto(url, wait_until="domcontentloaded", timeout=45000)
            
            # ページが安定するまで少し待つ
            await page.wait_for_timeout(3000) 
            
            content = await page.content()
            await browser.close()
            
        soup = BeautifulSoup(content, 'html.parser')
        
        # 不要なタグを排除
        for element in soup(['script', 'style', 'nav', 'footer', 'header', 'iframe']):
            element.decompose()
            
        text = soup.get_text(separator=' ', strip=True)
        # 取得できたテキストが極端に短い場合はエラーとしてリトライ対象にする（オプション）
        if len(text) < 100:
             raise ValueError("Fetched text is too short, might have failed to render.")
             
        return text[:3000]
        
    except Exception as e:
        # リトライ後に最終的に失敗した場合はこのメッセージが返る
        raise e

# 呼び出し側のインターフェースを維持するためのラッパー
async def fetch_release_text_safe(url: str) -> str:
    try:
        return await fetch_release_text(url)
    except Exception as e:
        return f"Error fetching {url} with Playwright (Async) after retries: {str(e)}"

# 検証用
if __name__ == "__main__":
    test_url = "https://ai.google.dev/gemini-api/docs/changelog"
    print(f"Testing URL (Async + Retry): {test_url}")
    result = asyncio.run(fetch_release_text_safe(test_url))
    print(result)