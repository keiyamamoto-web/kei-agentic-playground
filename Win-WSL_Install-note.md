# Install-note

1. 基盤環境の初期化とOS設定
- **WSL2の導入**: wsl --install を実行し、Ubuntuディストリビューションを基盤として採用。
- **ユーザー権限の確立**: UNIXユーザー kei の作成と sudo 権限の有効化。
- **システムパッケージの最新化**: apt update および upgrade により、依存関係の競合を予防。

2. Git 認証およびリポジトリの整合性確保
- **資格情報ヘルパーの同期**: Windows側の git-credential-manager.exe を WSL 側の Git 設定に紐付け、認証を透過化。
- **ユーザープロファイルの識別**: user.name および user.email を設定し、コミットの監査性を担保。
- **ファイル属性検知の無効化**: core.filemode false を適用し、NTFSからext4へのコピーに伴う実行権限差分（Mode 755/644）をGitが「変更」と見なすノイズを排除。
- **インデックスの強制同期**: git reset --hard HEAD により、作業領域をリモートの最新状態（Jediに変更した）と完全一致。

3. Python 開発コンポーネントの導入
- **システム要件の補完**: Ubuntu標準で欠落している python3.12-venv および python3-pip を apt 経由で導入。
- **仮想環境の再定義**: Windowsバイナリを含む既存の .venv を破棄し、Linuxネイティブな仮想環境を再生成。
- **依存ライブラリのビルド**: pip install -r requirements.txt を実行し、google-adk 等のパッケージを Linux 実行形式で配置。

4. Antigravity (IDE) との接続確立
- **リモート拡張機能の適用**: 'WSL' 拡張機能を介して、IDEのバックエンドを WSL (Ubuntu) に切り替え。
- **実行コンテキストの統一**: 統合ターミナルのデフォルトプロファイルを bash に固定し、エージェントが Linux コマンドを直接解釈できる環境を確立。

5. gcloud CLI のネイティブ化（パフォーマンス改善）
- **Windows版アクセスの排除**: 遅延の原因となる `/mnt/c/` 経由の Windows 版 `gcloud` の使用を停止。
- **ネイティブ版の導入**: Google Cloud の公式リポジトリを追加し、`apt` 経由で Linux ネイティブ版 `google-cloud-sdk` を導入。
- **認証の再確立**: `gcloud auth login --no-launch-browser` および `gcloud auth application-default login --no-launch-browser` を実行し、WSL 内に独立した認証情報を保持。
- **クォータプロジェクトの設定**: `gcloud auth application-default set-quota-project [PROJECT_ID]` を実行し、ADC 経由の API 呼び出しにおける警告と制限を解消。

6. Node.js / gws 環境の構築（ポータビリティの確保）
- **nvm (Node Version Manager) の導入**: バージョン管理の柔軟性と Mac 等の他環境との互換性を確保するため、`nvm` を導入。
- **ランタイムのネイティブ化**: `nvm install --lts` により Linux 用 Node.js ランタイムを配置。
- **依存関係のクリーンビルド**: `node_modules` を一度破棄し、Linux 側で `npm install` を実行することで、`gws` CLI を含む Node.js コンポーネントを完全にネイティブ化。
