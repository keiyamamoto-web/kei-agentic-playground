import asyncio
import os
from datetime import datetime, timedelta
from typing import Dict, List

from dotenv import load_dotenv
import google.auth

from google.adk.agents.llm_agent import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.genai import types

from tool_test import fetch_release_text_safe as fetch_release_text

# --- 1. カテゴリ定義 ---
CATEGORIES = {
    "GCP_Gemini_Enterprise": [
        "https://docs.cloud.google.com/vertex-ai/docs/release-notes",
        "https://docs.cloud.google.com/gemini/enterprise/docs/release-notes",
    ],
    "Gemini_NotebookLM": [
        "https://workspaceupdates.googleblog.com/search/label/Gemini",
        "https://workspaceupdates.googleblog.com/search/label/Gemini%20App",
        "https://workspaceupdates.googleblog.com/search/label/NotebookLM",
        "https://workspaceupdates.googleblog.com/search/label/Workspace%20Studio",
        "https://gemini.google.com/updates",
    ],
    "Google_Workspace": [
        "https://workspaceupdates.googleblog.com/search/label/Gmail",
        "https://workspaceupdates.googleblog.com/search/label/Google%20Chat",
        "https://workspaceupdates.googleblog.com/search/label/Google%20Calendar",
        "https://workspaceupdates.googleblog.com/search/label/Google%20Tasks",
        "https://workspaceupdates.googleblog.com/search/label/Google%20Meet",
        "https://workspaceupdates.googleblog.com/search/label/Google%20Voice",
        "https://workspaceupdates.googleblog.com/search/label/Google%20Drive",
        "https://workspaceupdates.googleblog.com/search/label/Google%20Docs",
        "https://workspaceupdates.googleblog.com/search/label/Google%20Sheets",
        "https://workspaceupdates.googleblog.com/search/label/Google%20Slides",
        "https://workspaceupdates.googleblog.com/search/label/Google%20Forms",
        "https://workspaceupdates.googleblog.com/search/label/Google%20Keep",
        "https://workspaceupdates.googleblog.com/search/label/Google%20Sites",
        "https://workspaceupdates.googleblog.com/search/label/Admin%20console",
        "https://workspaceupdates.googleblog.com/search/label/Security%20and%20Compliance",
        "https://workspaceupdates.googleblog.com/search/label/Identity",
        "https://support.google.com/a/answer/115037",
    ],
    "Google_Development": [
        "https://antigravity.google/changelog",
        "https://developers.google.com/workspace/release-notes",
        "https://ai.google.dev/gemini-api/docs/changelog",
        "https://workspaceupdates.googleblog.com/search/label/API",
        "https://workspaceupdates.googleblog.com/search/label/Google%20Apps%20Script",
        "https://workspaceupdates.googleblog.com/search/label/AppSheet",
        "https://workspaceupdates.googleblog.com/search/label/Developers",
    ]
}

async def run_specialist(name: str, section_title: str, instruction: str, urls: List[str], target_model: str) -> str:
    print(f"[{section_title}] 分析中... ({len(urls)}件)")
    content = ""
    for url in urls:
        raw_text = await fetch_release_text(url)
        if "Error fetching" in raw_text:
             content += f"\n--- Source: {url} ---\n[Fetch Error] このソースの取得に失敗しました。\n"
        else:
             content += f"\n--- Source URL: {url} ---\n{raw_text}\n"

    agent = LlmAgent(name=name, model=target_model, instruction=instruction)
    runner = Runner(
        app_name=f"Specialist_{name}",
        agent=agent,
        session_service=InMemorySessionService(),
        auto_create_session=True
    )

    result = ""
    async for event in runner.run_async(
        user_id="system",
        session_id=f"session_{name}",
        new_message=types.Content(parts=[types.Part.from_text(text=content)])
    ):
        if event.content and event.content.parts:
            result += "".join(p.text for p in event.content.parts if p.text)
    
    return f"## {section_title}\n\n{result}"

async def run_discovery():
    load_dotenv()
    try:
        credentials, project_id = google.auth.default()
        project_id = project_id or os.environ.get("GOOGLE_CLOUD_PROJECT")
        if not project_id:
            raise ValueError("Project ID could not be determined.")
        os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
    except Exception as e:
        print(f"認証エラー: {e}")
        return

    today = datetime.now()
    limit_7days = today - timedelta(days=7)
    target_model = f"projects/{project_id}/locations/us-central1/publishers/google/models/gemini-3.1-flash-lite-preview"

    # --- 2. Specialist 実行 ---
    specialists_tasks = [
        run_specialist(
            "Enterprise_Specialist", "GCP & Gemini Enterprise",
            f"あなたはプロダクトアナリストです。{limit_7days.strftime('%Y-%m-%d')} 以降の更新をプロダクト単位で報告してください。見出しや内容はすべて日本語で記述し、見出しは [202X-XX-XX：日本語タイトル](ソースURL) の形式にしてください。各更新について、何が変更されたのか（新機能、メリット、修正点など）を技術的な詳細を含めて日本語で詳しく解説してください。テキスト内に '[Fetch Error]' と記載されているソースのみを「取得失敗」として最後にリストアップしてください。",
            CATEGORIES["GCP_Gemini_Enterprise"], target_model
        ),
        run_specialist(
            "AI_Tool_Specialist", "Gemini & NotebookLM",
            f"あなたはプロダクトアナリストです。{limit_7days.strftime('%Y-%m-%d')} 以降の更新を抽出してください。見出しや要約はすべて日本語で記述し、タイトルを [日本語タイトル](ソースURL) の形式にしてください。各更新について、どのような機能追加や変更があったのかを一般ユーザーにも分かりやすく日本語で具体的に説明してください。'[Fetch Error]' と明記されたソースのみ「取得失敗」として最後に記載してください。",
            CATEGORIES["Gemini_NotebookLM"], target_model
        ),
        run_specialist(
            "Workspace_Specialist", "Google Workspace",
            f"あなたはプロダクトアナリストです。{limit_7days.strftime('%Y-%m-%d')} 以降の更新を抽出してください。見出しや内容はすべて日本語で記述し、タイトルを [日本語タイトル](ソースURL) の形式にしてください。各更新について、ユーザーにどのようなメリットがあるのか、操作がどう変わるのかを日本語で具体的に要約してください。'[Fetch Error]' と明記されたソースのみ「取得失敗」として最後に記載してください。",
            CATEGORIES["Google_Workspace"], target_model
        ),
        run_specialist(
            "Dev_Specialist", "Google Development (Antigravity & SDKs)",
            f"あなたはデベロッパーアドボケイトです。{limit_7days.strftime('%Y-%m-%d')} 以降の更新を抽出してください。見出しや技術解説はすべて日本語で記述し、見出しを [日本語タイトル](ソースURL) の形式にしてください。開発者にとって重要な変更点（APIの仕様変更、新機能の使い方、SDKのアップデート内容など）を日本語で技術的に詳しく説明してください。'[Fetch Error]' と明記されたソースのみ「取得失敗」として最後に記載してください。",
            CATEGORIES["Google_Development"], target_model
        )
    ]

    intermediate_results = await asyncio.gather(*specialists_tasks)

    # --- 3. Final Aggregator ---
    print("\n[Final] 最終リポート構成中...")
    aggregated_intermediate = "\n\n".join(intermediate_results)

    final_agent = LlmAgent(
        name="FinalAggregator",
        model=target_model,
        instruction=(
            f"本日の日付は {today.strftime('%Y-%m-%d %H:%M')} (JST) です。サマリーは不要です。以下の構成でリポートを構成してください：\n\n"
            f"リポート生成時刻：{today.strftime('%Y-%m-%d %H:%M')} (JST)\n\n"
            f"1. 【最優先】「最新の主要アップデート」セクション：全セクションの中から、特に Gemini Enterprise の最新の更新（{limit_7days.strftime('%Y-%m-%d')}以降で最も新しいもの）を必ず最上部に要約して記載してください。その他、直近48時間以内の重要な動きも併せてここにまとめてください。\n"
            "2. 「プロダクトカテゴリごとの詳細」：各専門エージェントから提供されたセクションを順番に並べてください。各リンク形式は維持し、内容は詳細な日本語で記述してください。\n"
            "3. 「技術的なステータス」：リポートの最後に記載してください。各エージェントから「[Fetch Error]」による最終的な失敗報告が**一つでも**ある場合は、「技術的な問題で取得できなかったソース」としてそれらをリストアップしてください。もし「[Fetch Error]」の報告が**一つもない**場合は、「すべての情報ソースから正常に通信し、技術的な問題なく取得を完了しました」とだけ明記してください。リトライの有無など、取得過程に関する説明は一切不要です。\n\n"
            "更新がなかっただけのソースについては、エラーとして扱わず、特に言及する必要はありません。"
        )
    )

    runner = Runner(
        app_name="FinalReportApp",
        agent=final_agent,
        session_service=InMemorySessionService(),
        auto_create_session=True
    )

    print("\n" + "="*30)
    print("### 更新リポート (Self-Contained Mode) ###")
    print("="*30 + "\n")

    async for event in runner.run_async(
        user_id="user_1", session_id="final",
        new_message=types.Content(parts=[types.Part.from_text(text=aggregated_intermediate)])
    ):
        if event.content and event.content.parts:
            print("".join(p.text for p in event.content.parts if p.text), end="", flush=True)

if __name__ == "__main__":
    asyncio.run(run_discovery())
