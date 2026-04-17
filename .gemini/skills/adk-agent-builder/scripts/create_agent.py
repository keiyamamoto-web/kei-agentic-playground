import os
import argparse

TEMPLATE_AGENT_PY = """
import os
from google.adk.agents.llm_agent import Agent
from google.adk.tools.openapi_tool.openapi_spec_parser.openapi_toolset import OpenAPIToolset
from google.adk.auth.auth_schemes import OpenIdConnectWithConfig
from google.adk.auth.auth_credential import AuthCredential, AuthCredentialTypes, OAuth2Auth

# ツールの定義 (オプション)
tools = []
spec_path = os.path.join(os.path.dirname(__file__), 'spec.yaml')
if os.path.exists(spec_path):
    with open(spec_path, 'r', encoding='utf-8') as f:
        spec_content = f.read()
    
    # 認証設定の例 (必要に応じてカスタマイズしてください)
    # auth_scheme = OpenIdConnectWithConfig(...)
    # auth_credential = AuthCredential(...)
    
    # OpenAPI仕様からツールを生成
    toolset = OpenAPIToolset(
        spec_str=spec_content,
        spec_str_type='yaml',
        # auth_scheme=auth_scheme,
        # auth_credential=auth_credential,
    )
    tools.extend(toolset.get_tools())

# メインのエージェントを定義
root_agent = Agent(
    model='{model}',
    name='{name}',
    description='{description}',
    instruction='{instruction}',
    tools=tools,
)
"""

TEMPLATE_SPEC_YAML = """
openapi: 3.0.0
info:
  title: Example API
  version: "1.0.0"
  description: API仕様の例です。
paths:
  /example:
    get:
      summary: サンプルのエンドポイント
      operationId: getExample
      responses:
        '200':
          description: OK
"""

def main():
    parser = argparse.ArgumentParser(description="Create a new ADK agent.")
    parser.add_argument("name", help="Name of the agent (and directory)")
    parser.add_argument("--description", help="Description of the agent", default="")
    parser.add_argument("--instruction", help="Instruction for the agent", default="You are a helpful assistant.")
    parser.add_argument("--model", help="Model to use", default="gemini-2.0-flash-exp")
    
    args = parser.parse_args()
    
    base_dir = args.name
    os.makedirs(base_dir, exist_ok=True)
    
    # Create agent.py
    with open(os.path.join(base_dir, "agent.py"), "w", encoding="utf-8") as f:
        f.write(TEMPLATE_AGENT_PY.format(
            name=args.name,
            description=args.description,
            instruction=args.instruction,
            model=args.model
        ))

    # Create spec.yaml
    with open(os.path.join(base_dir, "spec.yaml"), "w", encoding="utf-8") as f:
        f.write(TEMPLATE_SPEC_YAML)

    # Create .env
    with open(os.path.join(base_dir, ".env"), "w", encoding="utf-8") as f:
        f.write("# ここに環境変数を追加してください\n")

    # Create __init__.py
    with open(os.path.join(base_dir, "__init__.py"), "w", encoding="utf-8") as f:
        f.write("")

    print(f"Agent '{args.name}' created successfully in {os.path.abspath(base_dir)}")

if __name__ == "__main__":
    main()
