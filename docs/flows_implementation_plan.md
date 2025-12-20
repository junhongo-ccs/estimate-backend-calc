# 📋 flows リポジトリ実装プラン

**リポジトリ**: `flows`  
**役割**: Agent層（オーケストレーション）  
**技術**: Azure AI Foundry / Prompt Flow / Azure OpenAI / Azure AI Search (RAG)  
**作成日**: 2025-12-21

---

## 🎯 実装目標

Azure AI Agent として、UI と calc API を繋ぐ**唯一の意思決定コア**を実装する。

### 設計原則の遵守

- ✅ Agent が唯一の意思決定者
- ✅ ツール（calc API）の呼び出し順序を制御
- ✅ Azure OpenAI による根拠HTML生成
- ✅ エラー時の判断も Agent が実施
- ❌ 見積金額の計算は行わない（calc API に委譲）

---

## 📂 ディレクトリ構成

```
flows/
├── estimation_agent/
│   ├── flow.dag.yaml                ← Prompt Flow 定義
│   ├── system_prompt.txt            ← システムプロンプト
│   ├── call_calc_tool.py            ← calc API 呼び出しツール
│   ├── generate_rationale.jinja2    ← Azure OpenAI プロンプト
│   ├── requirements.txt             ← Python依存関係
│   └── .env.example                 ← 環境変数サンプル
├── docs/
│   ├── 00_design_principles.md      ← 設計原則（コピー）
│   ├── 00_system_specification.md   ← システム仕様（コピー）
│   └── implementation_plan.md       ← このファイル
├── tests/
│   ├── __init__.py
│   ├── test_flow.py                 ← Flow統合テスト
│   └── test_calc_tool.py            ← calc tool単体テスト
├── .github/
│   └── workflows/
│       └── deploy.yml               ← Azure AI Foundry デプロイ
├── .gitignore
└── README.md
```

---

## 🔧 実装タスク

### Phase 1: Prompt Flow 基本実装

#### ✅ Task 1.1: flow.dag.yaml 作成

**目的**: Prompt Flow の全体構造を定義

**構成**:
```yaml
$schema: https://azuremlschemas.azureedge.net/promptflow/latest/Flow.schema.json
inputs:
  project_name:
    type: string
  summary:
    type: string
  scope:
    type: string
  screen_count:
    type: int
  complexity:
    type: string
    enum: ["low", "medium", "high"]

outputs:
  response:
    type: object
    reference: ${aggregate_response.output}

nodes:
  # ノード1: calc API 呼び出し
  - name: call_calc_api
    type: python
    source:
      type: code
      path: call_calc_tool.py
    inputs:
      screen_count: ${inputs.screen_count}
      complexity: ${inputs.complexity}
    
  # ノード2: Azure AI Search (RAG) 検索
  - name: query_rag
    type: python
    source:
      type: code
      path: query_rag_tool.py
    inputs:
      query: ${inputs.summary}
      project_name: ${inputs.project_name}

  # ノード3: Azure OpenAI で根拠HTML生成
  - name: generate_rationale
    type: llm
    source:
      type: code
      path: generate_rationale.jinja2
    inputs:
      deployment_name: gpt-4o
      temperature: 0.3
      max_tokens: 2000
      project_name: ${inputs.project_name}
      summary: ${inputs.summary}
      scope: ${inputs.scope}
      calc_result: ${call_calc_api.output}
      rag_result: ${query_rag.output}
    connection: azure_openai_connection
    
  # ノード4: レスポンス統合
  - name: aggregate_response
    type: python
    source:
      type: code
      path: aggregate_response.py
    inputs:
      calc_result: ${call_calc_api.output}
      rationale_result: ${generate_rationale.output}
```

**検証**:
- [ ] YAML構文が正しい
- [ ] ノード依存関係が正しい
- [ ] 入出力型が正しい

---

#### ✅ Task 1.2: system_prompt.txt 作成

**目的**: Agent の役割・手順を定義

**内容**:
```text
# システム開発見積もりエージェント

## 役割
あなたはシステム開発の見積もりを算出し、経営層に説明する専門エージェントです。

## 重要な原則
- 見積金額は calculate_estimate ツールの結果を**必ず使用**（改変禁止）
- HTML出力は必ず <div class="doc--8px"> でラップ
- 日本語で出力
- 経営層が理解できる平易な表現を使用

## 手順
1. ユーザーから案件情報を受け取る
   - 案件名 (project_name)
   - 概要 (summary)
   - 範囲 (scope)
   - 画面数 (screen_count)
   - 複雑度 (complexity: low/medium/high)

2. calculate_estimate ツールを呼び出して基本金額を算出

3. 計算結果を分析し、以下を含む見積もり根拠をHTML形式で生成:
   a. 見積もりサマリー（金額と案件概要）
   b. 計算根拠（画面数×単価×係数の詳細説明）
   c. 前提条件（assumptions: 3-5個）
   d. リスク要因と注意事項（warnings: 2-4個）

## 出力形式
JSON:
{
  "status": "ok",
  "estimated_amount": 整数（円）,
  "currency": "JPY",
  "rationale_html": "<div class=\"doc--8px\">...</div>",
  "assumptions": ["前提条件1", "前提条件2", ...],
  "warnings": ["注意事項1", "注意事項2", ...],
  "config_version": "2025-12"
}

## エラー時の対応
- calculate_estimate がエラーを返した場合:
  - status: "error"
  - rationale_html: エラー内容を説明するHTML
  - ユーザーに入力内容の確認を促す
```

**検証**:
- [ ] 役割が明確
- [ ] 手順が具体的
- [ ] 出力形式が明示

---

#### ✅ Task 1.3: call_calc_tool.py 作成

**目的**: calc API を呼び出すツール

**実装**:
```python
from promptflow import tool
import requests
import os
from typing import Dict, Any

@tool
def call_calc_api(screen_count: int, complexity: str) -> Dict[str, Any]:
    """
    calc API を呼び出して見積金額を計算する
    
    Args:
        screen_count: 画面数
        complexity: 複雑度 (low/medium/high)
    
    Returns:
        calc API のレスポンス
    """
    # 環境変数から calc API エンドポイントを取得
    calc_api_url = os.getenv(
        "CALC_API_URL",
        "https://estimate-backend-calc.azurewebsites.net/api/calculate_estimate"
    )
    
    try:
        # calc API 呼び出し
        response = requests.post(
            calc_api_url,
            json={
                "screen_count": screen_count,
                "complexity": complexity
            },
            timeout=10
        )
        
        response.raise_for_status()
        return response.json()
        
    except requests.exceptions.RequestException as e:
        # エラー時のフォールバック
        return {
            "status": "error",
            "message": f"calc API エラー: {str(e)}"
        }
```

**検証**:
- [ ] @tool デコレータ使用
- [ ] エラーハンドリング実装
- [ ] タイムアウト設定
- [ ] 環境変数対応

---

#### ✅ Task 1.4: generate_rationale.jinja2 作成

**目的**: Azure OpenAI プロンプトテンプレート

**内容**:
```jinja2
system:
{{system_prompt}}

user:
## 案件情報
- 案件名: {{project_name}}
- 概要: {{summary}}
- 範囲: {{scope}}

## 計算ツールの結果
{% if calc_result.status == "ok" %}
- 見積金額: ¥{{calc_result.estimated_amount | format_number}}
- 画面数: {{calc_result.screen_count}}画面
- 複雑度: {{calc_result.complexity}}
- 内訳:
  - 画面単価: ¥{{calc_result.breakdown.base_cost_per_screen | format_number}}/画面
  - 基本コスト: ¥{{calc_result.breakdown.base_cost | format_number}}
  - 複雑度係数: {{calc_result.breakdown.difficulty_multiplier}} ({{calc_result.breakdown.calculation_details.complexity_label}})
  - 複雑度適用後: ¥{{calc_result.breakdown.difficulty_applied | format_number}}
  - バッファ係数: {{calc_result.breakdown.buffer_multiplier}}
  - 最終金額: ¥{{calc_result.breakdown.final | format_number}}
  - 計算式: {{calc_result.breakdown.calculation_details.formula}}
  - 設定バージョン: {{calc_result.config_version}}
{% else %}
【エラー】
計算ツールがエラーを返しました: {{calc_result.message}}
見積もりを生成できません。ユーザーに入力内容の確認を促してください。
{% endif %}

## 参考ナレッジ (RAG)
{% for knowledge in rag_result %}
- {{knowledge}}
{% endfor %}

## タスク
上記の情報から、経営層が意思決定できる見積もり根拠を生成してください。

### 出力要件
1. **見積もりサマリー** (<h2>)
   - 案件名と概要
   - 見積金額（強調表示）
   - 画面数と複雑度

2. **計算根拠** (<h2>)
   - 計算式の説明
   - 各係数の意味
   - なぜこの金額になったか

3. **前提条件** (<h2> + <ul>)
   - 3-5個の前提条件をリスト形式で
   - 例: 「要件定義が完了済み」「標準的なUI/UX」

4. **リスク要因と注意事項** (<h2> + <ul>)
   - 2-4個の注意事項をリスト形式で
   - 例: 「外部連携がある場合は追加費用」

### HTML制約
- 必ず <div class="doc--8px"> でラップ
- セマンティックHTML使用（<h2>, <ul>, <p>, <strong>）
- インラインスタイル禁止
- 8pxグリッドに準拠
```

**検証**:
- [ ] Jinja2構文が正しい
- [ ] エラー時の分岐あり
- [ ] HTML制約が明示

---

#### ✅ Task 1.5: aggregate_response.py 作成

**目的**: 最終レスポンスを統合

**実装**:
```python
from promptflow import tool
from typing import Dict, Any
import json

@tool
def aggregate_response(calc_result: Dict[str, Any], rationale_result: str) -> Dict[str, Any]:
    """
    calc API と Azure OpenAI の結果を統合
    
    Args:
        calc_result: calc API のレスポンス
        rationale_result: Azure OpenAI の生成結果
    
    Returns:
        統合されたレスポンス
    """
    # Azure OpenAI の結果をパース
    try:
        rationale_data = json.loads(rationale_result)
    except json.JSONDecodeError:
        # パースエラー時のフォールバック
        rationale_data = {
            "rationale_html": f"<div class='doc--8px'><p>{rationale_result}</p></div>",
            "assumptions": [],
            "warnings": []
        }
    
    # 最終レスポンス構築
    if calc_result.get("status") == "ok":
        return {
            "status": "ok",
            "estimated_amount": calc_result["estimated_amount"],
            "currency": calc_result["currency"],
            "rationale_html": rationale_data.get("rationale_html", ""),
            "assumptions": rationale_data.get("assumptions", []),
            "warnings": rationale_data.get("warnings", []),
            "config_version": calc_result.get("config_version", "")
        }
    else:
        # エラー時
        return {
            "status": "error",
            "message": calc_result.get("message", "Unknown error"),
            "estimated_amount": 0,
            "currency": "JPY",
            "rationale_html": rationale_data.get("rationale_html", ""),
            "assumptions": [],
            "warnings": [],
            "config_version": ""
        }
```

**検証**:
- [ ] calc エラー時の処理
- [ ] Azure OpenAI パースエラー時の処理
- [ ] 必須フィールドすべて含む

---

#### ✅ Task 1.6: requirements.txt 作成

**内容**:
```txt
promptflow==1.10.0
promptflow-tools==1.4.0
requests==2.31.0
python-dotenv==1.0.0
```

---

#### ✅ Task 1.7: .env.example 作成

**内容**:
```bash
# calc API エンドポイント
CALC_API_URL=https://estimate-backend-calc.azurewebsites.net/api/calculate_estimate

# Azure OpenAI 接続名（Azure AI Foundry で設定）
AZURE_OPENAI_CONNECTION=azure_openai_connection
```

---

#### ✅ Task 1.8: query_rag_tool.py 作成

**目的**: Azure AI Search からナレッジを検索

**実装**:
```python
from promptflow import tool
import os
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient

@tool
def query_rag(query: str, project_name: str):
    search_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
    search_key = os.getenv("AZURE_SEARCH_KEY")
    index_name = os.getenv("AZURE_SEARCH_INDEX")
    
    client = SearchClient(search_endpoint, index_name, AzureKeyCredential(search_key))
    results = client.search(search_text=query, top=3)
    
    return [r['content'] for r in results]
```

#### ✅ Task 2.1: tests/test_calc_tool.py 作成

**目的**: calc tool の単体テスト

**テストケース**:
1. 正常系: calc API が成功レスポンス
2. エラー系: calc API がエラーレスポンス
3. エラー系: calc API タイムアウト
4. エラー系: calc API 接続エラー

---

#### ✅ Task 2.2: tests/test_flow.py 作成

**目的**: Flow 全体の統合テスト

**テストケース**:
1. E2E正常系: 入力 → 計算 → HTML生成 → 出力
2. E2E エラー系: 不正な入力値
3. E2E エラー系: calc API エラー

---

### Phase 3: Azure AI Foundry 設定

#### ✅ Task 3.1: Azure AI Foundry プロジェクト作成

**手順**:
1. Azure Portal で Azure AI Foundry リソース作成
2. リージョン: **East US**（Azure OpenAI 利用可能）
3. プロジェクト名: `estimation-agent`

---

#### ✅ Task 3.2: Azure OpenAI 接続設定

**手順**:
1. Azure AI Foundry で Azure OpenAI 接続を作成
2. 接続名: `azure_openai_connection`
3. デプロイメント:
   - モデル: `gpt-4o` または `gpt-4o-mini`
   - デプロイメント名: `gpt-4o`

---

#### ✅ Task 3.3: Prompt Flow デプロイ

**手順**:
1. Azure AI Foundry で Prompt Flow をインポート
2. `flow.dag.yaml` をアップロード
3. 接続設定を確認
4. テスト実行
5. Managed Online Endpoint 作成
6. エンドポイント URL を取得

---

### Phase 4: CI/CD 設定

#### ✅ Task 4.1: .github/workflows/deploy.yml 作成

**目的**: Azure AI Foundry への自動デプロイ

**トリガー**:
- `main` ブランチへの push

**ステップ**:
1. Python セットアップ
2. promptflow CLI インストール
3. Azure ログイン（OIDC）
4. Prompt Flow デプロイ

**実装例**:
```yaml
name: Deploy to Azure AI Foundry

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install promptflow promptflow-tools
      
      - name: Azure Login (OIDC)
        uses: azure/login@v1
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
      
      - name: Deploy Prompt Flow
        run: |
          pf flow deploy \
            --source ./estimation_agent \
            --name estimation-agent-endpoint \
            --resource-group rg-estimation-agent \
            --workspace estimation-ai-hub
```

---

### Phase 5: ドキュメント整備

#### ✅ Task 5.1: README.md 作成

**内容**:
- リポジトリ概要
- ローカル開発手順
- Azure AI Foundry セットアップ手順
- デプロイ手順
- API仕様
- トラブルシューティング

---

#### ✅ Task 5.2: docs/ にドキュメントコピー

**内容**:
- `00_design_principles.md`（estimate-backend-calc からコピー）
- `00_system_specification.md`（estimate-backend-calc からコピー）

---

## 🚀 デプロイ手順

### ローカル開発

```bash
# 1. リポジトリクローン
git clone https://github.com/junhongo-ccs/flows.git
cd flows/estimation_agent

# 2. 依存関係インストール
pip install -r requirements.txt

# 3. 環境変数設定
cp .env.example .env
# .env を編集

# 4. ローカルテスト
pf flow test --flow . --inputs input.json

# 5. ローカルサーバー起動
pf flow serve --source . --port 8080
```

### Azure AI Foundry デプロイ

```bash
# 1. Azure CLI ログイン
az login

# 2. Prompt Flow デプロイ
pf flow deploy \
  --source ./estimation_agent \
  --name estimation-agent-endpoint \
  --resource-group rg-estimation-agent \
  --workspace estimation-ai-hub

# 3. エンドポイント確認
pf deployment show --name estimation-agent-endpoint
```

---

## ✅ 受け入れ条件

### 機能要件

- [ ] UI からのリクエストを受付
- [ ] calc API を正しく呼び出し
- [ ] Azure OpenAI で根拠HTML生成
- [ ] assumptions 3-5個生成
- [ ] warnings 2-4個生成
- [ ] エラー時に適切なレスポンス

### 非機能要件

- [ ] レスポンス時間 < 5秒 (P99)
- [ ] Azure OpenAI エラー時のフォールバック
- [ ] calc API エラー時のフォールバック
- [ ] ログが適切に出力

### 設計原則遵守

- [ ] Agent が唯一の意思決定者
- [ ] calc API の結果を改変していない
- [ ] Tool として calc API を呼んでいる
- [ ] HTML は `<div class="doc--8px">` でラップ

---

## 📊 進捗管理

| Phase | タスク | ステータス | 担当 | 期限 |
|-------|--------|-----------|------|------|
| 1 | flow.dag.yaml | 未着手 | - | - |
| 1 | system_prompt.txt | 未着手 | - | - |
| 1 | call_calc_tool.py | 未着手 | - | - |
| 1 | generate_rationale.jinja2 | 未着手 | - | - |
| 1 | aggregate_response.py | 未着手 | - | - |
| 1 | requirements.txt | 未着手 | - | - |
| 1 | .env.example | 未着手 | - | - |
| 2 | test_calc_tool.py | 未着手 | - | - |
| 2 | test_flow.py | 未着手 | - | - |
| 3 | Azure AI Foundry 作成 | 未着手 | - | - |
| 3 | Azure OpenAI 接続 | 未着手 | - | - |
| 3 | Prompt Flow デプロイ | 未着手 | - | - |
| 4 | deploy.yml | 未着手 | - | - |
| 5 | README.md | 未着手 | - | - |

---

## 🔄 次のステップ

1. **flowsリポジトリ作成**
   ```bash
   mkdir flows
   cd flows
   git init
   ```

2. **Phase 1 を実装**
   - estimation_agent/ ディレクトリ作成
   - 各ファイル実装

3. **ローカルテスト**
   - `pf flow test` で動作確認

4. **Azure AI Foundry セットアップ**
   - East US リージョンで作成
   - Azure OpenAI 接続設定

5. **デプロイ**
   - Managed Online Endpoint 作成
   - エンドポイント URL を UI に設定

---

## 📝 重要な注意事項

### Azure OpenAI リージョン

- **East US** を使用（gpt-4o 利用可能）
- Japan East は gpt-4o 未対応の可能性あり

### 見積金額の扱い

- **calc API の結果を絶対に改変しない**
- Agent は説明・根拠生成のみ

### エラーハンドリング

- calc API エラー時も HTML 生成
- Azure OpenAI エラー時はフォールバック HTML

---

## 🔗 関連リポジトリ

- **estimation-ui-app**: UI層
- **estimate-backend-calc**: 計算API層
- **flows**: Agent層（このリポジトリ）
