# Google Workspace Updates - Product URLs

Google Workspace Updates ブログにおけるプロダクト別のアップデート情報への直リンク集です。`release_agent.py` の `URLS` リストを構成する際の参照用として利用します。

* **Source**: [Google Workspace Updates](https://workspaceupdates.googleblog.com/)

---

## 🚀 Product Update Categories

### 💬 Comms & Meetings (コミュニケーションと会議)

* **Gmail**: <https://workspaceupdates.googleblog.com/search/label/Gmail>
* **Google Chat**: <https://workspaceupdates.googleblog.com/search/label/Google%20Chat>
* **Google Calendar**: <https://workspaceupdates.googleblog.com/search/label/Google%20Calendar>
* **Google Tasks**: <https://workspaceupdates.googleblog.com/search/label/Google%20Tasks>
* **Google Meet**: <https://workspaceupdates.googleblog.com/search/label/Google%20Meet>
* **Google Voice**: <https://workspaceupdates.googleblog.com/search/label/Google%20Voice>

### 📄 Content & Collaboration (コンテンツとコラボレーション)

* **Google Drive**: <https://workspaceupdates.googleblog.com/search/label/Google%20Drive>
* **Google Docs**: <https://workspaceupdates.googleblog.com/search/label/Google%20Docs>
* **Google Sheets**: <https://workspaceupdates.googleblog.com/search/label/Google%20Sheets>
* **Google Slides**: <https://workspaceupdates.googleblog.com/search/label/Google%20Slides>
* **Google Forms**: <https://workspaceupdates.googleblog.com/search/label/Google%20Forms>
* **Google Keep**: <https://workspaceupdates.googleblog.com/search/label/Google%20Keep>
* **Google Sites**: <https://workspaceupdates.googleblog.com/search/label/Google%20Sites>

### ✨ Gemini

* **Gemini**: <https://workspaceupdates.googleblog.com/search/label/Gemini>
* **Gemini App**: <https://workspaceupdates.googleblog.com/search/label/Gemini%20App>
* **NotebookLM**: <https://workspaceupdates.googleblog.com/search/label/NotebookLM>

### 🛡️ Admin & Security (管理とセキュリティ)

* **Admin console**: <https://workspaceupdates.googleblog.com/search/label/Admin%20console>
* **Security and Compliance**: <https://workspaceupdates.googleblog.com/search/label/Security%20and%20Compliance>
* **Identity**: <https://workspaceupdates.googleblog.com/search/label/Identity>

### 🛠️ Developer & Platform (開発者とプラットフォーム)

* **API**: <https://workspaceupdates.googleblog.com/search/label/API>
* **Google Apps Script**: <https://workspaceupdates.googleblog.com/search/label/Google%20Apps%20Script>
* **AppSheet**: <https://workspaceupdates.googleblog.com/search/label/AppSheet>
* **Developers**: <https://workspaceupdates.googleblog.com/search/label/Developers>

---

## 📝 Usage for `release_agent.py`

上記の中から、定期的にチェックしたいプロダクトの URL を `URLS` リストにコピーして使用してください。
例：

```python
URLS = [
    "https://workspaceupdates.googleblog.com/search/label/Google%20Chat",
    "https://workspaceupdates.googleblog.com/search/label/Gemini",
    # ...
]
```
