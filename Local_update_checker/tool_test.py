import asyncio
import random
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
async def fetch_release_text(url: str) -> str:
    """
    Playwright (Async) を使用して、JavaScript実行後のHTMLからテキストを抽出します。
    """
    # 同時起動を分散させるために少し待機 (1-3秒)
    await asyncio.sleep(random.uniform(1.0, 3.0))
    
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                viewport={'width': 1280, 'height': 800}
            )
            page = await context.new_page()
            
            # タイムアウトを60秒に延長し、'load' イベントを待つ
            await page.goto(url, wait_until="load", timeout=60000)
            
            # JSのレンダリング完了を待つために長めに待機 (5秒)
            await page.wait_for_timeout(5000) 
            
            content = await page.content()
            await browser.close()
            
        soup = BeautifulSoup(content, 'html.parser')
        
        # 不要なタグを排除
        for element in soup(['script', 'style', 'nav', 'footer', 'header', 'iframe']):
            element.decompose()
            
        # テキスト抽出（内容をしっかり読み取れるよう、文字数を拡大）
        text = soup.get_text(separator=' ', strip=True)
        
        if len(text) < 200:
             # あまりに短い場合は、クッキー同意画面などで止まっている可能性がある
             raise ValueError(f"Fetched text is too short ({len(text)} chars). Content might not have loaded correctly.")
             
        return text[:8000]
        
    except Exception as e:
        # Tenacityがリトライを行うために例外を再送出
        raise e

async def fetch_release_text_safe(url: str) -> str:
    try:
        return await fetch_release_text(url)
    except Exception as e:
        # 最終的な失敗理由を明示
        error_type = type(e).__name__
        return f"Error fetching {url} [Fetch Error: {error_type}] Detail: {str(e)[:100]}"

# 検証用
if __name__ == "__main__":
    test_url = "https://developers.google.com/workspace/release-notes"
    print(f"Testing URL (Robust Mode): {test_url}")
    result = asyncio.run(fetch_release_text_safe(test_url))
    print(result)