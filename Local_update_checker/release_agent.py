import asyncio
import os
from datetime import datetime, timedelta

from dotenv import load_dotenv
import google.auth

from google.adk.agents.llm_agent import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.genai import types

from tool_test import fetch_release_text

# クロール対象のURLリスト
URLS = [
    "https://docs.cloud.google.com/vertex-ai/docs/release-notes",
    "https://docs.cloud.google.com/gemini/enterprise/docs/release-notes",
    "https://support.google.com/a/answer/115037",
    "https://gemini.google.com/updates",
    "https://ai.google.dev/gemini-api/docs/changelog",
    "https://antigravity.google/changelog"
]

async def run_discovery():
    # 1. 認証と環境変数のセットアップ
    load_dotenv()
    try:
        _, project_id = google.auth.default()
        # プロジェクトIDが自動取得できない場合は.envの値を使用
        project_id = project_id or os.environ.get("GOOGLE_CLOUD_PROJECT")
        if not project_id:
            raise ValueError("Project ID could not be determined.")
        os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
    except Exception as e:
        print(f"認証エラー: {e}")
        return

    # 本日の日付（2026-04-22）とフィルタリングの閾値を設定
    today = datetime(2026, 4, 22)
    limit_date = today - timedelta(days=7)

    # 2. 各URLから情報を収集
    aggregated_content = ""
    for url in URLS:
        print(f"Fetching updates from: {url}")
        raw_text = fetch_release_text(url)
        aggregated_content += f"\n--- Source: {url} ---\n{raw_text}\n"

    # 3. ADK エージェントの定義
    # Vertex AIのエンドポイントを明示的に使用
    # 実績のある 'us-central1' と 'gemini-3.1-flash-lite-preview' を使用します
    target_model = f"projects/{project_id}/locations/us-central1/publishers/google/models/gemini-3.1-flash-lite-preview"
    
    agent = LlmAgent(
        name="ReleaseDiscoveryAgent",
        model=target_model,
        instruction=(
            f"あなたは技術調査エージェントです。本日の日付は {today.strftime('%Y-%m-%d')} です。"
            "提供された各ソースのテキストから、新機能やアップデートの日付を特定してください。"
            f"{limit_date.strftime('%Y-%m-%d')} 以降に公開された更新情報のみを抽出し、"
            "日付の新しい順に並べた Markdown 形式のリポートを作成してください。"
            "各項目には必ずソースURLへのリンクを含めてください。"
        )
    )

    # 4. Runner を介した実行
    print("Analyzing release metadata with ADK Runner...")
    runner = Runner(
        app_name="ReleaseCheckApp",
        agent=agent,
        session_service=InMemorySessionService(),
        auto_create_session=True
    )
    
    try:
        print("\n" + "="*30)
        print("### 過去7日間の更新リポート ###")
        print("="*30 + "\n")
        
        # 非同期ジェネレータ run_async を使用してイベントを取得
        async for event in runner.run_async(
            user_id="user_1",
            session_id="session_1",
            new_message=types.Content(parts=[types.Part.from_text(text=aggregated_content)])
        ):
            if event.content and event.content.parts:
                text = "".join(p.text for p in event.content.parts if p.text)
                print(text, end="", flush=True)
        print("\n")
        
    except Exception as e:
        print(f"\nError during agent execution: {str(e)}")

if __name__ == "__main__":
    asyncio.run(run_discovery())