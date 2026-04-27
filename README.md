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

# 仮想環境を有効化 (PowerShell)
.\.venv\Scripts\Activate.ps1

# 依存関係のインストール
pip install --upgrade pip
pip install -r requirements.txt
```

### Git Bash を使用する場合

```bash
# プロジェクトルートで実行 (Git Bashの場合)
rm -rf .venv
python -m venv .venv

# 仮想環境を有効化 (Git Bash)
source .venv/Scripts/activate

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

### Python インタープリター解決の技術録 (Python Interpreter Issues)

Google Antigravity（Windsurfベース）環境において、WSLからWindowsローカルへの移行や、`${workspaceFolder}` 変数の展開失敗に起因する「インタープリター認識エラー」および「スキャン無限ループ」の解決プロセスを以下にまとめます。

---

#### 1. 根本原因の特定

* **変数展開のバグ**: IDEが `${workspaceFolder}` を実際のパスに変換する前にスキャンを開始し、存在しない文字列パスを探してスタックする。
* **拡張機能の競合**: `Python Environments` 拡張機能が、IDE本体の設定を無視してシステム全体を再帰的にスキャンし、UI（くるくる）をフリーズさせる。
* **パス形式の不一致**: Windows環境において、相対パス（`./`）やスラッシュ（`/`）の混在が原因でバイナリ（`python.exe`）の特定に失敗する。

#### 2. 確定的な解決プロトコル

##### ステップ1：競合拡張機能の無効化（最重要）

バックグラウンドのスキャンループを止めるため、以下の拡張機能を「無効（Disable）」にする。

* **Python Environments** (`ms-python.vscode-python-envs`)

##### ステップ2：`settings.json` への絶対パス強制適用

変数 `${workspaceFolder}` を使わず、ドライブレターから始まる **二重バックスラッシュ (`\\`)** 形式の絶対パスを記述する。

###### パスの書き換え例

```json
{
    "python.defaultInterpreterPath": "C:\\Users\\[ユーザー名]\\...\\.venv\\Scripts\\python.exe",
    "python.languageServer": "None",
    "python.locator": "jsons",
    "python.experiments.enabled": false
}
```

* **`python.locator: "jsons"`**: 設定ファイルに書かれたパス以外を探さないよう強制し、スキャンを停止させる。

##### ステップ3：キャッシュのクリーンアップ

設定反映がされない場合は、以下のディレクトリ内のキャッシュを削除して再起動する。

* `%APPDATA%\Code\User\globalStorage\ms-python.python`

---

#### 3. 再発時のチェックリスト

1. **右下のステータスバーを確認**: `3.12.x ('.venv': venv)` と表示されているか。
2. **エラーログを確認**: `Could not resolve interpreter path` に `${workspaceFolder}` という文字列が残っていないか（残っていれば絶対パス化が不完全）。
3. **信頼設定を確認**: ワークスペースを開いた際に「このフォルダーを信頼しますか？」に「はい」と答えているか。

#### 根拠

* **解決の決定打**: `Python Environments` 拡張の無効化と絶対パス指定により、IDEの不安定な変数展開プロセスを完全にバイパスできたこと。
* **技術的整合性**: Pylanceの代わりに `ty` を使用し、`languageServer: "None"` に設定することで、IDEの負荷を下げつつ補完機能を維持できる。

---

## 付録: Git Bash 向け 開発効率化設定 (Optional)

ターミナル（Git Bash）起動時やフォルダ移動時に、自動的に `.venv` を有効化し `.env` を読み込む設定です。
Git Bash の設定ファイル（`~/.bashrc`）に以下を追記してください。

```bash
# --- プロジェクト自動セットアップ (ロード・アクティベート) ---
function cd() {
  builtin cd "$@"
  
  # 1. .venv の自動有効化/解除
  if [[ -d .venv ]]; then
    # Git Bash上での VIRTUAL_ENV は "C:\..." 形式になるため変換して比較
    local expected_venv
    expected_venv=$(cygpath -w "$PWD/.venv")
    if [[ "$VIRTUAL_ENV" != "$expected_venv" ]]; then
      # 既存のプロンプトから古い仮想環境表示の「跡」を削除（2重括弧を防止）
      export PS1="${PS1//\((.venv)\) /}"
      export PS1="${PS1//(.venv) /}"

      # venv側の自動追記をオフにして、手動で1重のカッコを付与
      export VIRTUAL_ENV_DISABLE_PROMPT=1
      source .venv/Scripts/activate
      export PS1="(.venv) $PS1"
    fi
  else
    if [[ -n "$VIRTUAL_ENV" ]]; then
      deactivate
      # プロンプトから (.venv) を削除
      export PS1="${PS1/(.venv) /}"
    fi
  fi

  # 2. .env の読み込み
  if [[ -f .env ]]; then
    export $(grep -v '^#' .env | xargs)
  fi
}

# 初回起動時にも実行
cd .
```
