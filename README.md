# estimate-backend-calc

AI見積もりシステムの **計算API層** です。  
Azure AI Agent からツールとして呼び出され、YAML設定に基づく確定計算を提供します。

## 🚀 特徴

- **AI不使用**: 統計やLLMを使わない確定ロジックにより、信頼性の高い概算を出力します。
- **YAML設定ベース**: 係数や単価を `estimate_config.yaml` で一括管理。
- **Agentファースト**: エージェントが説明しやすいよう、計算の「内訳（Breakdown）」をレスポンスに含みます。

## 🛠 技術スタック

- **Runtime**: Azure Functions (Python 3.11)
- **Logic**: Pure Python + PyYAML

## 📖 API 仕様

### `POST /api/calculate_estimate`

見積金額を計算します。

#### リクエストボディ
```json
{
  "screen_count": 15,
  "complexity": "medium"
}
```
- `screen_count`: 画面数 (正の数値)
- `complexity`: 複雑度 (`low`, `medium`, `high`)

#### レスポンス (成功)
```json
{
  "status": "ok",
  "estimated_amount": 1980000,
  "currency": "JPY",
  "breakdown": {
    "base_cost": 1800000,
    "difficulty_multiplier": 1.0,
    "buffer_multiplier": 1.1,
    "calculation_details": {
      "formula": "15 screens × ¥120,000 × 1.0 (difficulty) × 1.1 (buffer)"
    }
  },
  "config_version": "2025-12"
}
```

## 💻 ローカル開発

### 1. 依存関係のインストール
```bash
pip install -r requirements.txt
```

### 2. ローカル起動
[Azure Functions Core Tools](https://github.com/Azure/azure-functions-core-tools) が必要です。

```bash
func start
```

### 3. テストの実行
```bash
python -m unittest discover tests
```

## 🏗 デプロイ

GitHub Actions を通じて自動デプロイされます。  
Azure 側で GitHub OIDC 認証と、以下のシークレットの設定が必要です。

- `AZURE_CLIENT_ID`
- `AZURE_TENANT_ID`
- `AZURE_SUBSCRIPTION_ID`

---
Copyright (c) 2025 AI Estimation System Project