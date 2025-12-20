# 📋 estimate-backend-calc 実装プラン

**リポジトリ**: `estimate-backend-calc`  
**役割**: 計算API層（AI不使用の確定計算）  
**技術**: Azure Functions (Python 3.11)  
**作成日**: 2025-12-21

---

## 🎯 実装目標

Azure AI Agent から呼ばれる **Tool（計算API）** として、YAML設定に基づく見積金額計算を提供する。

### 設計原則の遵守

- ✅ Agent 以外の存在を知らない（独立したAPI）
- ✅ AI/LLM を一切使用しない
- ✅ HTML生成を行わない
- ✅ YAML設定ベースの確定計算のみ

---

## 📂 ディレクトリ構成

```
estimate-backend-calc/
├── docs/
│   ├── 00_design_principles.md      ← 既存
│   ├── 00_system_specification.md   ← 既存
│   └── implementation_plan.md       ← このファイル
├── function_app.py                  ← メインロジック
├── estimate_config.yaml             ← 係数設定
├── requirements.txt                 ← Python依存関係
├── host.json                        ← Azure Functions設定
├── local.settings.json              ← ローカル開発用（.gitignore）
├── .funcignore                      ← デプロイ除外設定
├── .gitignore                       ← Git除外設定
├── tests/                           ← テストコード
│   ├── __init__.py
│   ├── test_calculate.py
│   └── test_config.py
├── .github/
│   └── workflows/
│       └── deploy.yml               ← CI/CD（OIDC認証）
└── README.md                        ← リポジトリ説明
```

---

## 🔧 実装タスク

### Phase 1: 基本実装

#### ✅ Task 1.1: estimate_config.yaml 作成

**目的**: 計算に使用する係数を定義

**内容**:
```yaml
config_version: "2025-12"

# 基本単価（1画面あたり）
base_cost_per_screen: 120000

# 難易度係数
difficulty_multipliers:
  low: 0.8      # 簡易画面: 80%
  medium: 1.0   # 標準画面: 100%
  high: 1.3     # 高難度画面: 130%

# バッファ係数（リスク・予備費）
buffer_multiplier: 1.1  # 10%上乗せ

# 通貨
currency: "JPY"
```

**検証**:
- [ ] YAML構文が正しい
- [ ] すべての係数が数値型
- [ ] config_version が文字列

---

#### ✅ Task 1.2: function_app.py 実装

**目的**: Azure Functions HTTP トリガー実装

**エンドポイント**: `POST /api/calculate_estimate`

**リクエスト**:
```json
{
  "screen_count": 15,
  "complexity": "medium"
}
```

**レスポンス（成功）**:
```json
{
  "status": "ok",
  "estimated_amount": 1980000,
  "currency": "JPY",
  "screen_count": 15,
  "complexity": "medium",
  "breakdown": {
    "base_cost": 1800000,
    "base_cost_per_screen": 120000,
    "difficulty_multiplier": 1.0,
    "difficulty_applied": 1800000,
    "buffer_multiplier": 1.1,
    "buffer_applied": 1980000,
    "final": 1980000,
    "calculation_details": {
      "formula": "15 screens × ¥120,000 × 1.0 (difficulty) × 1.1 (buffer)",
      "complexity_label": "標準"
    }
  },
  "config_version": "2025-12"
}
```

**レスポンス（エラー）**:
```json
{
  "status": "error",
  "message": "screen_count must be > 0"
}
```

**実装要件**:
- [ ] HTTP POST のみ受付
- [ ] CORS 対応（`Access-Control-Allow-Origin: *`）
- [ ] 入力バリデーション
  - `screen_count` > 0
  - `complexity` in ["low", "medium", "high"]
- [ ] YAML設定読み込み
- [ ] 計算ロジック実装
- [ ] エラーハンドリング
- [ ] ログ出力（Application Insights）

**計算式**:
```
見積金額 = 画面数 × 画面単価 × 難易度係数 × バッファ係数

例: 15 × 120,000 × 1.0 × 1.1 = 1,980,000円
```

---

#### ✅ Task 1.3: requirements.txt 作成

**内容**:
```txt
azure-functions==1.18.0
PyYAML==6.0.2
```

**検証**:
- [ ] バージョン固定
- [ ] 最小限の依存関係（AI/LLM関連なし）

---

#### ✅ Task 1.4: host.json 作成

**目的**: Azure Functions ランタイム設定

**内容**:
```json
{
  "version": "2.0",
  "logging": {
    "applicationInsights": {
      "samplingSettings": {
        "isEnabled": true,
        "maxTelemetryItemsPerSecond": 20
      }
    }
  },
  "extensionBundle": {
    "id": "Microsoft.Azure.Functions.ExtensionBundle",
    "version": "[4.*, 5.0.0)"
  }
}
```

---

#### ✅ Task 1.5: .gitignore 作成

**内容**:
```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/

# Azure Functions
local.settings.json
.python_packages/
.vscode/
.funcignore

# IDE
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db
```

---

### Phase 2: テスト実装

#### ✅ Task 2.1: tests/test_calculate.py 作成

**目的**: 計算ロジックの単体テスト

**テストケース**:
1. 正常系: medium complexity
   - Input: `screen_count=15, complexity="medium"`
   - Expected: `estimated_amount=1,980,000`

2. 正常系: low complexity
   - Input: `screen_count=10, complexity="low"`
   - Expected: `estimated_amount=1,056,000` (10 × 120,000 × 0.8 × 1.1)

3. 正常系: high complexity
   - Input: `screen_count=20, complexity="high"`
   - Expected: `estimated_amount=3,432,000` (20 × 120,000 × 1.3 × 1.1)

4. エラー系: screen_count = 0
   - Expected: `status="error"`

5. エラー系: invalid complexity
   - Input: `complexity="invalid"`
   - Expected: `status="error"`

6. エラー系: 負の値
   - Input: `screen_count=-5`
   - Expected: `status="error"`

**実装**:
```python
import pytest
import json
from function_app import main

def test_calculate_medium_complexity():
    # テスト実装
    pass
```

---

#### ✅ Task 2.2: tests/test_config.py 作成

**目的**: YAML設定の読み込みテスト

**テストケース**:
1. YAML読み込み成功
2. 必須フィールド存在確認
3. 数値型バリデーション

---

### Phase 3: CI/CD 設定

#### ✅ Task 3.1: .github/workflows/deploy.yml 作成

**目的**: Azure Functions への自動デプロイ

**トリガー**:
- `main` ブランチへの push
- Pull Request

**ステップ**:
1. Python 3.11 セットアップ
2. 依存関係インストール
3. テスト実行
4. Azure Functions へデプロイ（OIDC認証）

**OIDC認証**:
- Managed Identity 使用
- シークレット不要

**環境変数**:
- `AZURE_FUNCTIONAPP_NAME`: 関数アプリ名
- `AZURE_RESOURCE_GROUP`: リソースグループ名

---

### Phase 4: ドキュメント整備

#### ✅ Task 4.1: README.md 作成

**内容**:
- リポジトリ概要
- ローカル開発手順
- デプロイ手順
- API仕様（リクエスト/レスポンス例）
- テスト実行方法

---

#### ✅ Task 4.2: API仕様書（OpenAPI）作成（オプション）

**ファイル**: `docs/api_spec.yaml`

**内容**: OpenAPI 3.0 形式でAPI仕様を定義

---

## 🚀 デプロイ手順

### ローカル開発

```bash
# 1. 依存関係インストール
pip install -r requirements.txt

# 2. Azure Functions Core Tools インストール
brew install azure-functions-core-tools@4

# 3. ローカル実行
func start

# 4. テスト
curl -X POST http://localhost:7071/api/calculate_estimate \
  -H "Content-Type: application/json" \
  -d '{"screen_count": 15, "complexity": "medium"}'
```

### Azure デプロイ

```bash
# 1. Azure CLI ログイン
az login

# 2. リソースグループ作成
az group create --name rg-estimate-calc --location japaneast

# 3. ストレージアカウント作成
az storage account create \
  --name stestcalc \
  --resource-group rg-estimate-calc \
  --location japaneast

# 4. 関数アプリ作成
az functionapp create \
  --name estimate-backend-calc \
  --resource-group rg-estimate-calc \
  --storage-account stestcalc \
  --runtime python \
  --runtime-version 3.11 \
  --functions-version 4 \
  --os-type Linux

# 5. デプロイ
func azure functionapp publish estimate-backend-calc
```

---

## ✅ 受け入れ条件

### 機能要件

- [ ] `POST /api/calculate_estimate` が正常動作
- [ ] YAML設定に基づく計算が正確
- [ ] 入力バリデーションが機能
- [ ] エラー時に適切なメッセージ返却
- [ ] CORS が有効

### 非機能要件

- [ ] レスポンス時間 < 500ms (P99)
- [ ] テストカバレッジ > 80%
- [ ] CI/CD が正常動作
- [ ] ログが Application Insights に出力

### 設計原則遵守

- [ ] AI/LLM を使用していない
- [ ] HTML生成を行っていない
- [ ] Agent以外の存在を知らない（独立したAPI）
- [ ] Tool として呼ばれる受動的な実装

---

## 📊 進捗管理

| Phase | タスク | ステータス | 担当 | 期限 |
|-------|--------|-----------|------|------|
| 1 | estimate_config.yaml | 未着手 | - | - |
| 1 | function_app.py | 未着手 | - | - |
| 1 | requirements.txt | 未着手 | - | - |
| 1 | host.json | 未着手 | - | - |
| 1 | .gitignore | 未着手 | - | - |
| 2 | test_calculate.py | 未着手 | - | - |
| 2 | test_config.py | 未着手 | - | - |
| 3 | deploy.yml | 未着手 | - | - |
| 4 | README.md | 未着手 | - | - |

---

## 🔄 次のステップ

1. **Phase 1 を実装**
   - estimate_config.yaml
   - function_app.py
   - requirements.txt
   - host.json
   - .gitignore

2. **ローカルテスト**
   - `func start` で起動確認
   - curl でAPI動作確認

3. **Phase 2 を実装**
   - 単体テスト作成
   - テスト実行

4. **Phase 3 を実装**
   - CI/CD設定
   - Azure デプロイ

5. **Phase 4 を実装**
   - ドキュメント整備

---

## 📝 備考

- このリポジトリは **計算API専用**
- Agent層は別リポジトリ（`flows`）
- UI層も別リポジトリ（`estimation-ui-app`）
- 設計原則を厳守すること
