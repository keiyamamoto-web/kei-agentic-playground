# Antigravity 開発環境構築ガイド

このリポジトリは、Python 3.12 と Gemini 3.1 Flash (Lite Preview) を使用した Antigravity プロジェクトの実行環境です。
一から環境を構築し、現在の動作確認済み状態を再現するための手順を以下にまとめます。

> [!NOTE]
> **環境移行の経緯について**:
> 当初WSL環境への移行を試みましたが、ブラウザエージェント用のChrome拡張機能（Browser Subagent機能）がWSL環境下で正常に利用できないという制約が判明したため、移行を断念し**Windowsローカル環境（Native環境）へロールバック**して作業を継続しています。過去のWSL環境構築手順や固有の設定は、`Win-WSL_Install-note.md` に退避しています。

---

## 1. 前提条件

以下のツールがシステムにインストールされている必要があります。

* **Python 3.12**: `python3.12 --version` で確認
* **Node.js / npm**: `node -v` / `npm -v` で確認
* **gcloud CLI**: `gcloud --version` で確認
* **GitHub CLI (gh)**: `gh --version` で確認
* **Homebrew** (macOS の場合): パス設定に使用

---

## 2. Python 仮想環境の構築

依存関係の競合を避け、VS Code で正しく動作させるために仮想環境を構築します。

```powershell
# プロジェクトルートで実行 (PowerShellの場合)
Remove-Item -Recurse -Force .venv
python -m venv .venv

# 仮想環境を有効化
.\.venv\Scripts\Activate.ps1

# 依存関係のインストール
pip install --upgrade pip
pip install -r requirements.txt
```

> [!NOTE]
> `requirements.txt` には `google-genai`, `google-adk`, `python-dotenv`, `google-cloud-bigquery` 等が含まれています。

---

## 3. Node.js 環境 (gws CLI) の構築

Google Workspace 操作用のコマンドラインツール `gws` をローカルに導入します。

```bash
# package.json に基づく依存関係のインストール
npm install

# パスの確認（正常にインストールされていればバージョンが表示されます）
./node_modules/.bin/gws version
```

---

## 4. Gemini CLI の構築

AI エージェントとしての機能を拡張し、IDE 連携や MCP サーバー管理を行うための `gemini` CLI を導入します。

```bash
# Homebrew を使用したインストール
brew install googleworkspace-cli

# バージョンの確認
gemini --version
```

---

## 5. 認証の設定

Google Cloud および Google Workspace API へのアクセス権限を設定します。

### 5.1. Google Cloud 認証 (ADC)

gcloud CLI を使用して、アプリケーションのデフォルト認証情報を作成します。

```bash
gcloud config set project dsk-agentspace-trial
gcloud auth application-default login
```

### 5.2. GWS CLI 認証

`gws` CLI を使用して、Workspace へのアクセスを認可します。

```bash
./node_modules/.bin/gws auth login
```

### 5.3. Gemini CLI 認証

Gemini CLI は独自のアカウント管理を行っています。コーポレートアカウント（`densan-s.co.jp`）での認証を確実に行う必要があります。

```bash
# 初回ログイン
gemini login

# 認証がループする場合やアカウントを切り替える場合のリセット
rm ~/.gemini/oauth_creds.json ~/.gemini/google_accounts.json
gemini login
```

### 5.4. GitHub 認証 (gh CLI)

リポジトリの操作や GitHub CLI を使用するために認証を行います。

```bash
gh auth login
```

プロンプトに従って `GitHub.com` > `HTTPS` > `Yes` > `Login with a web browser` を選択し、表示されたコードをブラウザで入力して認証します。

## 6. 環境変数の設定 (`.env`)

プロジェクトルートに `.env` ファイルを作成し、以下の内容を設定します。

```text
# ADK用の環境変数
GOOGLE_GENAI_USE_VERTEXAI=True
GOOGLE_CLOUD_PROJECT=dsk-agentspace-trial
GOOGLE_CLOUD_LOCATION=global
AGENT_MODEL=gemini-3.1-flash-lite-preview
TOOL_MODEL=gemini-3.1-flash-lite-preview

# GWS CLI用の環境変数
GOOGLE_WORKSPACE_PROJECT_ID=dsk-agentspace-trial
```

---

## 7. VS Code の設定 (`.vscode/settings.json`)

エディタが正しい Python インタープリタを認識し、エラーを出さないように設定します。

`.vscode/settings.json` に以下の内容を記述します：

```json
{
    "python.defaultInterpreterPath": "${workspaceFolder}/.venv/Scripts/python.exe",
    "python.terminal.activateEnvInSelectedTerminal": true,
    "python.analysis.extraPaths": [
        "${workspaceFolder}/.venv/Lib/site-packages"
    ],
    "python.analysis.typeCheckingMode": "basic",
    "python.languageServer": "Pylance",
    "terminal.integrated.env.osx": {
        "PATH": "/opt/homebrew/bin:/usr/local/bin:${env:PATH}"
    },
    "ty.enable": true,
    "[markdown]": {
        "editor.formatOnSave": true,
        "editor.defaultFormatter": "vscode.markdown-language-features"
    },
    "files.insertFinalNewline": true,
    "files.trimTrailingWhitespace": true,
    "python.analysis.exclude": [
        "**/__pyrefly_virtual__/**",
        "**/inmemory/**"
    ]
}
```

---

## 8. 動作確認 (疎通確認)

以下のスクリプトを実行して、Gemini API との通信が正常に行えるか確認します。

```bash
python hello_adk/hello_adk.py
```

正常に動作すれば、Gemini からのレスポンスがターミナルに表示されます。

---

## 9. カテゴリ別設定記録 (Configuration Records)

過去のトラブルシューティングや特定ツール向けの詳細な運用ノウハウを、カテゴリ別に記録しています。

### GWS CLI 連携 (Google Workspace)

`gws` CLI を使用した Google Chat 等の連携に関する設定です（詳細は [.agents/gws_cli_reference.md](.agents/gws_cli_reference.md) 参照）。

* **認証トラブルの解決**:
  * 権限（Scope）追加後に発生する 403 エラーは、`~/.config/gws/token_cache.json` を削除し、キャッシュを強制リフレッシュすることで解決します。
* **スレッド返信の「正解の型」**:
  * Google Chat のサイドパネルスレッドへ返信する際、APIが意図せず新しいスレッドを作成してしまう問題は、`messageReplyOption: REPLY_MESSAGE_OR_FAIL` パラメータを指定することで解決できます。

### Gemini CLI 連携 (AI Agents)

エージェント開発および IDE 連携に用いる `gemini` CLI の設定です（詳細は [.agents/gemini_cli_reference.md](.agents/gemini_cli_reference.md) 参照）。

* **認証リセット手順**:
  * 個人アカウントとコーポレートアカウントの混在による認証エラー（403 Permission Denied）が発生した場合は、`~/.gemini/` 配下の `oauth_creds.json` および `google_accounts.json` を削除し、再度 `gemini login` を行うことでコーポレートアカウントを強制的に再認識させます。
* **IDE モード設定**:
  * CLI とエディタ（VS Code）を連携させるには、CLI 内で `/ide enable` を実行します。これによりネイティブの Diff ビュアー等が利用可能になります。
