# ADK (Agent Development Kit) リファレンス

ライブラリのソースコードとドキュメントに基づいています。
参照元: https://google.github.io/adk-docs/api-reference/python/index.html

## Agent (`google.adk.agents.llm_agent.Agent`)

LLMベースのエージェントを定義するコアクラスです。

### コンストラクタ引数

- `model` (Union[str, BaseLlm]): 使用するモデル (例: `'gemini-2.0-flash-exp'`). デフォルト設定がない場合は親エージェントから継承されます。
- `name` (str): エージェントの一意な名前。
- `description` (str): エージェントの目的の短い説明。
- `instruction` (Union[str, InstructionProvider]): エージェントの振る舞いをガイドするシステム指示。プレースホルダーを含めることが可能です。
- `tools` (list[ToolUnion]): エージェントが利用可能なツールのリスト。
- `static_instruction` (Optional[types.ContentUnion]): 静的なシステム指示（コンテキストキャッシュの最適化に使用）。
- `input_schema` (Optional[type[BaseModel]]): ツールとして使用される際の入力検証用Pydanticモデル。
- `output_schema` (Optional[type[BaseModel]]): 出力検証用のPydanticモデル。設定された場合、エージェントは応答のみを行いツール使用等は行いません。
- `output_key` (Optional[str]): エージェントの出力を保存するセッション状態のキー。

### コールバック
- `before_model_callback`: LLM呼び出し前のコールバック。
- `after_model_callback`: LLM呼び出し後のコールバック。
- `on_model_error_callback`: モデルエラー時のコールバック。

## OpenAPIToolset (`google.adk.tools.openapi_tool.openapi_spec_parser.openapi_toolset.OpenAPIToolset`)

OpenAPI仕様書を解析し、実行可能な `RestApiTool` のリストに変換するクラスです。

### コンストラクタ引数

- `spec_str` (Optional[str]): OpenAPI仕様の文字列。
- `spec_dict` (Optional[Dict[str, Any]]): OpenAPI仕様の辞書。
- `spec_str_type` (Literal["json", "yaml"]): 仕様文字列のタイプ (`'json'` または `'yaml'`)。
- `auth_scheme` (Optional[AuthScheme]): ツールセット全体で使用する認証スキーム。
- `auth_credential` (Optional[AuthCredential]): ツールセット全体で使用する認証情報。
- `tool_filter` (Optional[Union[ToolPredicate, List[str]]]): 特定のツールのみを有効にするためのフィルター。

### メソッド

- `get_tools()`: `Agent` に渡すためのツールリストを取得します。
- `get_tool(tool_name: str)`: 特定のツールを取得します。

## AuthCredential (`google.adk.auth.auth_credential.AuthCredential`)

認証情報を表すクラスです。`CredentialExchanger` で実際の認証情報と交換されます。

### 属性

- `auth_type` (AuthCredentialTypes): 認証タイプ。
- `api_key` (Optional[str]): APIキー。
- `http` (Optional[HttpAuth]): HTTP認証情報 (Basic, Bearer)。
- `oauth2` (Optional[OAuth2Auth]): OAuth2認証情報。
- `service_account` (Optional[ServiceAccount]): サービスアカウント設定。

### AuthCredentialTypes (Enum)
- `API_KEY` ("apiKey")
- `HTTP` ("http")
- `OAUTH2` ("oauth2")
- `OPEN_ID_CONNECT` ("openIdConnect")
- `SERVICE_ACCOUNT` ("serviceAccount")

### 使用例

**API Key:**
```python
from google.adk.auth.auth_credential import AuthCredential, AuthCredentialTypes

cred = AuthCredential(
    auth_type=AuthCredentialTypes.API_KEY,
    api_key="your-api-key",
)
```

**OAuth2 (Authorization Code):**
```python
from google.adk.auth.auth_credential import AuthCredential, AuthCredentialTypes, OAuth2Auth

cred = AuthCredential(
    auth_type=AuthCredentialTypes.OAUTH2,
    oauth2=OAuth2Auth(
        client_id="your-client-id",
        client_secret="your-client-secret",
    ),
)
```

**OpenID Connect:**
```python
from google.adk.auth.auth_schemes import OpenIdConnectWithConfig
from google.adk.auth.auth_credential import AuthCredential, AuthCredentialTypes, OAuth2Auth

# 認証スキームの設定（エンドポイントなど）
auth_scheme = OpenIdConnectWithConfig(
   authorization_endpoint="https://example.com/oauth/authorize",
   token_endpoint="https://example.com/oauth/token",
   scopes=['scope1', 'scope2']
)

# 認証情報の設定（クライアントIDなど）
auth_credential = AuthCredential(
    auth_type=AuthCredentialTypes.OPEN_ID_CONNECT,
    oauth2=OAuth2Auth(
        client_id="your-client-id",
        client_secret="your-client-secret"
    )
)
```

## ToolContext (`google.adk.tools.tool_context.ToolContext`)

ツールが実行されるコンテキストを提供するクラスです。ツールはこのコンテキストを使用して、アーティファクトの保存、セッション状態へのアクセス、認証情報の取得などを行います。

### 属性
- `session_state` (dict[str, Any]): セッション間で状態を共有するための辞書。
- `invocation_context` (InvocationContext): 呼び出しに関する情報。

### メソッド
- `save_artifact(name: str, data: Any, mime_type: Optional[str] = None)`: アーティファクト（ファイル、画像など）を保存します。
- `list_artifacts()`: 保存されたアーティファクトの一覧を取得します。
- `load_artifact(name: str)`: 指定されたアーティファクトの内容を取得します。

### 使用例

**画像の保存:**
```python
from google.genai import types

async def generate_image(prompt: str, tool_context: ToolContext):
    # 画像生成ロジック...
    image_bytes = ... # 画像データ

    # アーティファクトとして保存
    await tool_context.save_artifact(
        "image.png",
        types.Part.from_bytes(data=image_bytes, mime_type="image/png")
    )
```

## ベストプラクティス

### 1. ツールの実装方法
`BaseTool` クラスを継承するよりも、シンプルな非同期関数 (`async def`) としてツールを定義することを推奨します。これにより、ツール登録の問題を回避しやすくなります。

```python
async def my_tool(arg1: str, tool_context: ToolContext) -> str:
    """ツールの説明ドキュメント"""
    # 処理内容
    return "結果"
```

### 2. API呼び出しのリトライ設定
Gemini APIなどを呼び出す際は、`GenerateContentConfig` 内の `http_options` を使用して、429エラーなどのリトライを自動化します。

```python
from google.genai import types

config = types.GenerateContentConfig(
    http_options=types.HttpOptions(
        retry_options=types.HttpRetryOptions(initial_delay=2, attempts=5)
    )
)
```

### 3. MCPサーバーへの接続
リモートMCPサーバーへの接続には、`StreamableHTTPConnectionParams` を使用します。

```python
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset, StreamableHTTPConnectionParams

connection_params = StreamableHTTPConnectionParams(
    url="https://example.com/mcp",
    headers={"X-Api-Key": "your-key"},
    terminate_on_close=True
)

mcp_toolset = McpToolset(connection_params=connection_params)
```
