# MacでのDocker環境構築メモ

Mac環境でDockerを使用し、VS CodeのDev Containersで開発環境を構築するまでの手順です。

## 1. 事前準備

### Docker Desktopのインストール
1. [Docker Desktop for Mac](https://www.docker.com/products/docker-desktop/) をダウンロードしてインストールします。
2. インストール後、Docker Desktopを起動し、正常に動作していることを確認します。

### VS Code 拡張機能のインストール
VS Codeに以下の拡張機能をインストールします。
- **Dev Containers** (Microsoft製)

## 2. 環境構築手順

### プロジェクトをコンテナで開く
1. プロジェクトのルートディレクトリに `.devcontainer/` フォルダを作成し、以下のファイルを配置します。
   - `devcontainer.json`: コンテナの設定（拡張機能、設定など）
   - `Dockerfile`: コンテナの構成（OS、ライブラリのインストール）
2. VS Codeの左下にある緑色のアイコン（またはコマンドパレットから `Dev Containers: Reopen in Container`）を選択して、コンテナを起動します。

### .env ファイルの設定
プロジェクトルートに `.env` ファイルを作成し、必要な環境変数を設定します。
```text
GOOGLE_GENAI_USE_VERTEXAI=True
GOOGLE_CLOUD_PROJECT=your-project-id
...
```

## 3. 仮想環境（.venv）の再構築（重要）

Mac上のローカルで作成した `.venv` は、内部のパスがMacのファイルシステム（`/Users/...`）を参照しているため、LinuxベースのDockerコンテナ内では動作しません。コンテナ内で作り直す必要があります。

### 手順
ターミナル（コンテナ内）で以下のコマンドを実行します：

```bash
# 1. 既存の壊れた仮想環境を削除
rm -rf .venv

# 2. コンテナ内のPythonで仮想環境を作成
python3 -m venv .venv

# 3. 仮想環境を有効化
source .venv/bin/activate

# 4. ライブラリのインストール
pip install --upgrade pip
pip install -r requirements.txt
```

## 4. 動作確認
以下のコマンドで、ライブラリが正しく読み込めるか確認します。
```bash
python -c "import google.cloud.aiplatform; print(google.cloud.aiplatform.__version__)"
```

## 5. Tips
- **整合性の維持**: WSL環境など他の仮想環境と構成を合わせる場合も、この `.venv` を再構築する手法で環境を統一できます。
- **拡張機能**: `devcontainer.json` の `customizations.vscode.extensions` に拡張機能IDを記述しておくと、コンテナ起動時に自動でインストールされます。

## 6. GitHub連携 (gh CLI)

コンテナ内からGitHubを操作するために、GitHub CLIでの認証を行います。

### 認証手順
1. ターミナルで以下のコマンドを実行します。
   ```bash
   gh auth login
   ```
2. インタラクティブなプロンプトに従って選択します：
   - Where do you use GitHub? **GitHub.com**
   - Preferred protocol? **HTTPS**
   - Authenticate Git with your GitHub credentials? **Yes**
   - How would you like to authenticate? **Login with a web browser**
3. 表示された **one-time code** をコピーし、Enterキーを押してブラウザを開きます。
4. ブラウザでコードを入力し、認証を完了させます。

### 状態確認
```bash
gh auth status
```
正常にログインできていれば、ユーザー名が表示されます。
