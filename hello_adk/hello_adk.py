import os
from google import genai
import google.auth
from dotenv import load_dotenv

def main():
    # .envファイルから環境変数を読み込む
    load_dotenv()
    
    # 1. 認証情報の取得（エラー防止のため明示的に取得）
    try:
        credentials, project_id = google.auth.default()
    except Exception as e:
        print(f"認証エラー: {e}")
        return

    print(f"--- Environment Check ---")
    print(f"Project ID: {project_id}")
    
    # 2. クライアントの設定
    # 成功実績のある 'global' を指定し、Vertex AI モードを有効化
    client = genai.Client(
        vertexai=True, 
        project=project_id, 
        location="global"
    )
    
    # 3. Gemini 3.1 Lite Preview を指名打ち
    # 自己紹介で 1.5 と言わせないよう、システムプロンプト的な指示を contents に含めます
    target_model = "gemini-3.1-flash-lite-preview"
    
    print(f"Using Model: {target_model}")
    print(f"--------------------------\n")

    try:
        response = client.models.generate_content(
            model=target_model,
            contents=(
                "あなたは Gemini 3.1 Flash (Lite Preview) です。 "
                "1.5 ではなく、最新世代としてのあなたの特徴や、今動いているモデルの正確な名称を教えてください。"
            )
        )
        
        # thought_signature がある場合の処理（3系の証拠）
        print(f"--- Gemini Response ---")
        print(response.text)
        
        # デバッグ用：もし thought_signature があれば表示
        if hasattr(response.candidates[0], 'thought'):
             print(f"\n(Thinking detected: {target_model} is processing...)")

    except Exception as e:
        print(f"API実行エラー: {e}")
        print("モデル名がプロジェクトで未有効化、または名称変更の可能性があります。")

if __name__ == "__main__":
    main()