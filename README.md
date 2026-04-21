# Antigravity 開発環境構築ガイド

このリポジトリは、Python 3.12 と Gemini 3.1 Flash (Lite Preview) を使用した Antigravity プロジェクトの実行環境です。
一から環境を構築し、現在の動作確認済み状態を再現するための手順を以下にまとめます。

---

## 1. 前提条件

以下のツールがシステムにインストールされている必要があります。

- **Python 3.12**: `python3.12 --version` で確認
- **Node.js / npm**: `node -v` / `npm -v` で確認
- **gcloud CLI**: `gcloud --version` で確認
- **Homebrew** (macOS の場合): パス設定に使用

---

## 2. Python 仮想環境の構築

依存関係の競合を避け、VS Code で正しく動作させるために仮想環境を構築します。

```bash
# プロジェクトルートで実行
rm -rf .venv
python3.12 -m venv .venv

# 仮想環境を有効化
source .venv/bin/activate

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

## 4. 認証の設定

Google Cloud および Google Workspace API へのアクセス権限を設定します。

### 4.1. Google Cloud 認証 (ADC)

gcloud CLI を使用して、アプリケーションのデフォルト認証情報を作成します。

```bash
gcloud config set project dsk-agentspace-trial
gcloud auth application-default login
```

### 4.2. GWS CLI 認証

`gws` コマンドを使用して、Workspace へのアクセスを認可します。

```bash
./node_modules/.bin/gws auth login
```

---

## 5. 環境変数の設定 (`.env`)

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

## 6. VS Code の設定 (`.vscode/settings.json`)

エディタが正しい Python インタープリタを認識し、エラーを出さないように設定します。

`.vscode/settings.json` に以下の内容を記述します：

```json
{
    "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
    "python.terminal.activateEnvInSelectedTerminal": true,
    "python.analysis.extraPaths": [
        "${workspaceFolder}/.venv/lib/python3.12/site-packages"
    ],
    "python.analysis.typeCheckingMode": "basic",
    "python.languageServer": "Pylance",
    "terminal.integrated.env.osx": {
        "PATH": "/opt/homebrew/bin:/usr/local/bin:${env:PATH}"
    }
}
```

---

## 7. 動作確認 (疎通確認)

以下のスクリプトを実行して、Gemini API との通信が正常に行えるか確認します。

```bash
python hello_adk/hello_adk.py
```

正常に動作すれば、Gemini からのレスポンスがターミナルに表示されます。

---

## 付録: 開発効率化のための自動化設定 (Optional)

ターミナル起動時やフォルダ移動時に、自動的に `.venv` を有効化し `.env` を読み込む設定です。

### `~/.zshrc` への追記例

```bash
# --- プロジェクト自動セットアップ (ロード・アクティベート) ---
function load_project_settings() {
  # 1. .venv の自動有効化/解除
  if [[ -d .venv ]]; then
    if [[ "$VIRTUAL_ENV" != "$PWD/.venv" ]]; then
      source .venv/bin/activate
    fi
  else
    if [[ -n "$VIRTUAL_ENV" ]]; then
      deactivate
    fi
  fi

  # 2. .env の読み込み
  if [[ -f .env ]]; then
    export $(grep -v '^#' .env | xargs)
  fi
}

# フォルダ移動時と起動時に自動実行
autoload -Uz add-zsh-hook
add-zsh-hook chpwd load_project_settings
load_project_settings
```
