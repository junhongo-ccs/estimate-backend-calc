# 開発一時中断と再開の手順書

**作成日**: 2026-01-20
**目的**: 開発一時中断に伴い、日々の従量課金を最小化しつつ、環境設定を保持する（月額固定費ごとの「スリープ」状態）。

## 1. 原状回復・コスト削減のために実施したこと（2026-01-20実施）

以下のリソースに対し、**設定やデータを削除することなく「停止」処理**を行いました。

### 停止したリソース（従量課金の停止）
1.  **Azure Container Apps** (`rg-estimation-agent`)
    *   対象: `estimation-agent-app`
    *   処置: 停止 (Stop)
    *   効果: 日々の稼働コスト（約 ¥1,000/日規模）の停止。
2.  **Azure Web Apps** (`rg-jhongo0067-1948`)
    *   対象: `estimate-api-cli`, `estimation-agent-core`
    *   処置: 停止 (Stop)
    *   効果: アプリ自体の稼働停止。

### 維持したリソース（設定保持のため課金継続）
1.  **App Service Plan** (`rg-jhongo0067-1948`)
    *   対象: `estimation-core-plan`
    *   状態: **Basic Tier (有料) を維持**
    *   理由: 無料プランへの変更による設定消失やIPアドレス変更のリスクを避けるため。
    *   コスト: 月額 約 ¥2,000 程度（開発していなくても発生します）。

### 確認事項
*   **仮想マシン (VM)**: すべてのリソースグループ (`rg-estimation-agent`, `rg-est-v2` 等) で稼働中のVMが存在しないことを確認済み。
    *   画像にあった高額コスト要因（¥4,000/日）は解消済み。

---

## 2. 開発再開時の手順

開発を再開する際は、以下の手順でリソースを叩き起こしてください。

### 手順 1: リソースの起動 (CLI推奨)
以下のコマンドをターミナルで実行して、一括で起動します。

```bash
# Container App (Prompt Flow Agent) の起動
az containerapp start --name estimation-agent-app --resource-group rg-estimation-agent

# Web Apps (Backend API) の起動
az webapp start --name estimate-api-cli --resource-group rg-jhongo0067-1948
az webapp start --name estimation-agent-core --resource-group rg-jhongo0067-1948
```

※ Azure Portal から行う場合は、各リソース画面の「概要」ページにある **[開始] (Start)** ボタンを押してください。

### 手順 2: 動作確認
起動後、数分待ってから以下を確認してください。
1.  バックエンドAPIのエンドポイントが応答するか。
2.  チャットUIからエージェントが応答するか（Container Appの起動には少し時間がかかります）。

### 注意事項
*   **Prompt Flowの再デプロイが必要な場合**: もし Container App を起動してもエージェントが正常に動かない場合（内部エラー等）、Azure AI Studio から再度「Deploy」ボタンを押してデプロイし直すのが確実です（Flowの定義自体は消えていません）。
*   **課金の再開**: 上記のリソースを起動した瞬間から、再び日々の従量課金が発生し始めます。開発が終わったら再度「停止」することを忘れないでください。
