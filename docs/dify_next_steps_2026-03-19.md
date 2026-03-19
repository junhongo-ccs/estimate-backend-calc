# Dify 再始動メモ

## 方針

- 主軸は OutSystems 再現ではなく Dify に戻す
- 理由は、発表までに価値を見せるうえで、Dify の方が実装と改善の速度が高いから
- 今後は、Dify の入力UIと Python 計算ロジックを一致させることを優先する

## 現状認識

- Dify の入力画面には、`department`、`estimation_profile`、`target_margin`、`target_platform`、`dev_type`、`screen_count`、`complexity`、`tables`、`table_count`、`features`、`duration`、`confidence`、`phase2_items`、`phase3_items`、`dept_allocation`、`team_ratio` が並んでいる
- ただし、Dify 上で実際に使っていたコードは軽量版で、入力UIの全項目をまだ活かし切れていなかった
- そのため、見えている入力と効いている計算ロジックを一致させる必要がある

## 追加したファイル

- Dify のコードノード差し替え用に、フル版ロジックをワークフロー互換の返却形式で保存した
- 保存先:
  - [/Users/hongoujun/Documents/GitHub/estimate-backend-calc/dify_estimate_logic_full_for_workflow.py](/Users/hongoujun/Documents/GitHub/estimate-backend-calc/dify_estimate_logic_full_for_workflow.py)

## このファイルの意図

- ベースは本命版の見積ロジック
- Dify ワークフローの後段を壊しにくいよう、返り値は `calc_json` にそろえてある
- これにより、今の Dify ワークフロー上で:
  - `duration`
  - `dev_type`
  - `target_platform`
  - `phase2_items`
  - `phase3_items`
  - `confidence`
  - `dept_allocation`
  - `team_ratio`
 まで計算に反映できる状態を目指す

## 差し替え後の確認順

1. `department` を変えて結果が変わる
2. `duration` を変えて結果が変わる
3. `dev_type` を変えて結果が変わる
4. `target_platform` を変えて結果が変わる
5. `phase2_items` を追加して結果が変わる
6. `target_margin` を入れて逆算売価が出る
7. `team_ratio` を変えて直接労務費が変わる
8. `dept_allocation` を変えて部門係数が変わる

## 次回の作業方針

- 次回は機能追加より先に、今日換装した計算式が本当に生きているかを検証する
- 主目的は、Dify の入力UIに見えている各項目が、結果へ正しく反映されることを確認すること

## 次回の検証観点

各入力について、次を確認する:

1. 入力を変えたら結果が変わるか
2. 変わるべき方向に変わるか
3. LLM の説明文がその変更を正しく説明しているか

## 次回の検証対象

優先順:

1. `department`
2. `duration`
3. `dev_type`
4. `target_platform`
5. `features`
6. `phase2_items`
7. `phase3_items`
8. `target_margin`
9. `team_ratio`
10. `dept_allocation`

## 次回の位置づけ

- 次回は「計算ロジックの疎通確認日」とする
- ここが通れば、その後は発表用デモ設計と見せ方の調整に入る

## 発表に向けた重点

- 追加実装を増やすより、Dify 上の見えている入力が本当に効いている状態を作る
- 特に見せ場は:
  - 部署差
  - 人材レイヤー差
  - 他部署応援差
  - 営業利益率からの逆算売価

## 補足

- OutSystems 側の検証は無駄ではなく、部門差やマスタ設計の確認には役立った
- ただし、発表までの主戦場は Dify とする
