# Antigravity 実行環境構築手順

## 構築の前提条件を定義する

本手順は、Python 3.12.7環境下でGemini 3.1 Flash (Lite Preview) を利用するAntigravityプロジェクトを対象とします。gcloud CLIがシステムにインストールされていることを前提とし、プロジェクトルートディレクトリでの実行を想定しています。前提条件を揃えることで、実行時の依存関係エラーを低減します。次は、仮想環境の構築とライブラリの導入手順を示します。

## 仮想環境の構築および依存関係の導入を実行する

プロジェクトディレクトリ内で以下のコマンドを実行し、独立した仮想環境 `.venv` を構築します。`google-genai`、`google-adk`、`python-dotenv`、および `google-cloud-bigquery` をインストールします。仮想環境の利用により、システム全体のPython環境への干渉を防ぎます。次は、Google Cloud リソースへの認証手順を示します。

```bash
rm -rf .venv
python3.12 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install google-genai google-adk python-dotenv google-cloud-bigquery
```

## Google Cloud の認証を確立する

gcloud CLIを用いて対象プロジェクトへの接続と、アプリケーションのデフォルト認証情報（ADC）の生成を行います。これにより、ソースコード内に認証情報をハードコードするセキュリティリスクを排除します。ただし、ADCの有効期限が切れた場合は再実行が必要となります。次は、環境変数の設定手順を示します。

```bash
gcloud config set project dsk-agentspace-trial
gcloud auth application-default login
```

## 環境変数を設定する

プロジェクトルートに `.env` ファイルを作成し、以下の内容を記述します。`GOOGLE_CLOUD_LOCATION` を `global` に指定することは、プレビュー版モデルのルーティングに関するエラーを回避するための措置です。この設定により、コード側での環境依存値の動的ロードが可能となります。次は、VS Codeの拡張機能エラーを回避する手順を示します。

```text
GOOGLE_CLOUD_PROJECT=dsk-agentspace-trial
GOOGLE_CLOUD_LOCATION=global
GOOGLE_GENAI_USE_VERTEXAI=True
AGENT_MODEL=gemini-3.1-flash-lite-preview
```

## VS Code の環境スキャンエラーを回避する

`.vscode` ディレクトリを作成し、その配下に `settings.json` を配置して以下の設定を記述します。これにより、VS CodeのPET（Python Environment Tool）によるpyenv環境の不適切な自動スキャンを停止させ、明示的に `.venv` を参照させます。結果として、エディタ上のインポート警告やクラッシュのポップアップを排除します。次は、構築環境の疎通確認手順を示します。

```json
{
    "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
    "python.terminal.activateEnvInSelectedTerminal": true,
    "python.analysis.extraPaths": ["${workspaceFolder}/.venv/lib/python3.12/site-packages"]
}
```

## 疎通確認スクリプトを実行する

プロジェクトルート直下に `hello_adk.py` （または任意のテストファイル）を作成し、以下のコードを配置します。実行には仮想環境を有効化したターミナルで `python hello_adk.py` を使用します。このスクリプトは、ADCを経由したGemini APIへのリクエストを検証し、正常な応答が得られるかを確認するためのものです。

```python
import os
from google import genai
from dotenv import load_dotenv

def main():
    load_dotenv()
    client = genai.Client()
    target_model = os.getenv("AGENT_MODEL")
    
    print(f"Target Model: {target_model}")

    try:
        response = client.models.generate_content(
            model=target_model,
            contents="現在の接続状況を報告してください。"
        )
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()

---

## Google Workspace CLI (gws) 導入・運用ガイド

本プロジェクトでは、Google Workspace 操作を自動化し、AI エージェントが自律的にデータを扱えるようにするために `gws` CLI を活用しています。

### 1. インストール
プロジェクトの `node_modules` に含まれているバイナリを使用するか、以下のコマンドで導入してください。

```bash
# プロジェクトローカルにインストール
npm install @googleworkspace/cli

# パスの確認
./node_modules/.bin/gws version
```

### 2. 初期セットアップと認証

初回使用時には、Google Cloud プロジェクトとの連携と認証が必要です。

```bash
# 認証セットアップ（ブラウザが起動します）
./node_modules/.bin/gws auth login
```

> [!TIP]
> 認証がうまくいかない場合は、`gws auth setup` を実行して、必要な API の有効化状態を確認してください。

### 3. AI エージェント（Antigravity）との連携

gws は AI エージェントが効率的に動作するように設計されています。

* **構造化出力**: デフォルトで JSON 形式のレスポンスを返します。
* **文字コードへの対応**: Shift-JIS (CP932) 形式のファイルを取得した際は、エージェント側で Python (`encoding='cp932'`) や `iconv` コマンドを用いて UTF-8 に変換して処理してください。
* **スキル・ワークフローの活用**: `.gemini/skills` および `.agents/workflows` 内の指示書を読み込ませることで、エージェントは自動的に最適な操作を選択し、出力の品質（Markdown形式など）を維持します。

### 4. 高度なコマンド（ヘルパーコマンド）

API を直接叩く以外に、人間や AI が直感的に使える `+` プレフィックス付きのヘルパーコマンドが利用可能です。

* `gws drive +upload <file>` : メタデータを自動構成してアップロード
* `gws sheets +append <id> <row_data>` : スプレッドシートへ行を追加
* `gws gmail +send` : メールの送信

詳細なリファレンスはプロジェクトルートの `./gws_cli_reference.md` を参照してください。
