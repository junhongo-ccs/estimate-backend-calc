# Dify 再始動メモ

## 現在の到達点

- Dify を主戦場とする方針で固定
- ワークフローは以下で整理済み
  - `ユーザー入力`
  - `コード実行`
  - `知識検索`
  - `LLM`
- `コード実行` ノードは最新形では
  - `calc_json`
  - `query_for_rag`
  を返す
- `知識検索` ノードは
  - `コード実行 / query_for_rag`
  をクエリとして使う
- `LLM` ノードは
  - `context` に知識検索結果
  - `USER` に `userinput.query` + `コード実行 / calc_json`
  を入れる構成に整理済み

## 直近で確定した重要事項

### 1. UIUX 見積はもう素通りではない

`33_design_cost_standards.md` を基準に、Phase 3 ロジックを Python 側へ反映済み。

反映内容:

- UIデザイン
- デザインシステム / ガイドライン
- プロトタイプ
- ロゴ・ブランディング
- 外注費単価
- 管理費 15%
- confidence 係数

### 2. 確認済みの検証結果

以下のサンプル入力で:

- `screen_count = 22`
- `features = ユーザー認証`
- `phase3_items = UIデザイン,デザインシステム`
- `confidence = medium`

コード実行出力は次を返した:

- `features = [auth]`
- `phase3_items = [ui_design, design_system]`
- `outsource_cost = 810000`
- `management_fee = 121500`
- `confidence_multiplier = 1.2`
- `total_phase3_cost = 1117800`

これは期待値どおりであり、UIUX チーム基準が実計算に入っていることを確認済み。

## 現在の推奨コード元

- [dify_estimate_logic_full_for_workflow_ui_mapped.py](/Users/hongoujun/Documents/GitHub/estimate-backend-calc/dify_estimate_logic_full_for_workflow_ui_mapped.py)

このファイルに含まれるもの:

- Dify UI ラベル吸収
- `tables` のノイズ除去
- `query_for_rag`
- `phase3_breakdown`
- `33_design_cost_standards.md` ベースの Phase 3 計算

## 現在の推奨デモ運用

- 発表本編は録画
- URL の全体公開はしない
- 希望者に個別案内

## 録画で見せるべき内容

### シーン A

- 条件入力
- UIUX フェーズ込みの見積結果
- 目標利益率から必要売価が出る様子

### シーン B

- 結果に対する追加質問
- 例:
  - 工数内訳
  - 赤字要因
  - 目標利益率達成売価
  - UIUX フェーズがどう反映されているか

## 発表で使いやすいメッセージ

- 出発点は UIUX チームの提案余地を増やすことだった
- チームに開発者がいない中で Vibe Coding で実装した
- AI は最初それっぽく振る舞ったが、UIUX 見積を実計算には入れていなかった
- そこを Codex と一緒に検証し、UIUX 見積も計算に乗るところまで持っていった

## 次にやること

1. 発表録画を完成させる
2. 使う入力パターンを固定する
3. 想定質問を 5〜10 本に絞る
4. 発表資料にこのストーリーを反映する
