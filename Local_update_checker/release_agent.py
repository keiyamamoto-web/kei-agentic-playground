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

from tool_test import fetch_release_text

# --- 1. カテゴリ定義 (完全にコード内に埋め込み) ---
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
        raw_text = fetch_release_text(url)
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
    limit_24h = today - timedelta(days=1)
    target_model = f"projects/{project_id}/locations/us-central1/publishers/google/models/gemini-3.1-flash-lite-preview"

    # --- 2. Specialist 実行 (見出しリンク形式を指示) ---
    specialists_tasks = [
        run_specialist(
            "Enterprise_Specialist", "GCP & Gemini Enterprise",
            f"あなたはプロダクトアナリストです。{limit_7days.strftime('%Y-%m-%d')} 以降の更新をプロダクト単位で見出しを付けて報告してください。見出しは必ず [202X-XX-XX：タイトル](ソースURL) の形式にしてリンクを埋め込んでください。取得失敗したURLはリポートの最後に記載してください。",
            CATEGORIES["GCP_Gemini_Enterprise"], target_model
        ),
        run_specialist(
            "AI_Tool_Specialist", "Gemini & NotebookLM",
            f"あなたはプロダクトアナリストです。{limit_7days.strftime('%Y-%m-%d')} 以降の更新を抽出してください。タイトルを [タイトル](ソースURL) の形式にしてリンクを埋め込んでください。取得失敗したURLは最後に記載してください。",
            CATEGORIES["Gemini_NotebookLM"], target_model
        ),
        run_specialist(
            "Workspace_Specialist", "Google Workspace",
            f"あなたはプロダクトアナリストです。{limit_7days.strftime('%Y-%m-%d')} 以降の更新を抽出してください。タイトルを [タイトル](ソースURL) の形式にしてリンクを埋め込んでください。取得失敗したURLは最後に記載してください。",
            CATEGORIES["Google_Workspace"], target_model
        ),
        run_specialist(
            "Dev_Specialist", "Google Development (Antigravity & SDKs)",
            f"あなたはデベロッパーアドボケイトです。{limit_7days.strftime('%Y-%m-%d')} 以降の更新を抽出してください。見出しを [タイトル](ソースURL) の形式にしてリンクを埋め込んでください。取得失敗したURLは最後に記載してください。",
            CATEGORIES["Google_Development"], target_model
        )
    ]

    intermediate_results = await asyncio.gather(*specialists_tasks)
    
    # --- 3. Final Aggregator (サマリーなし、24時間優先、リンク形式維持) ---
    print("\n[Final] 最終リポート構成中...")
    aggregated_intermediate = "\n\n".join(intermediate_results)

    final_agent = LlmAgent(
        name="FinalAggregator",
        model=target_model,
        instruction=(
            f"本日の日付は {today.strftime('%Y-%m-%d')} です。サマリーは不要です。提供されたセクションをそのまま並べてください。"
            "各エージェントが作成した [タイトル](URL) 形式のリンクを必ず維持してください。"
            f"最後に「直近24時間の主要更新」セクションを設け、{limit_24h.strftime('%Y-%m-%d')} 以降の更新（特に Gemini Enterprise）を優先して抽出してください。ここでも見出しにリンクを含めてください。"
            "取得失敗の報告がある場合は、さらにその後に「情報取得エラーが発生したソース」としてまとめてください。"
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
            print("".join(p.text for p in event.content.parts if p.text) , end="", flush=True)
    print("\n")

if __name__ == "__main__":
    asyncio.run(run_discovery())
