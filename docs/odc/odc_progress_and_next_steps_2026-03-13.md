# ODC 連携進捗と次のステップ (2026-03-13)

## 今日やったこと

1.  **Backend: `/calculate_simple` エンドポイントの実装完了**
    - OutSystems (ODC) からの呼び出しを極限まで簡略化するため、`screen_count` と `table_count` だけを送信すれば計算ができるエンドポイントを作成しました。
    - 他のパラメータ（複雑度、プロファイルなど）は、バックエンド側で定義された「標準的なデフォルト値」が自動的に使用されます。
    - レスポンス形式は `calculate_test` と完全に同一であり、既存の UI ロジックをそのまま流用可能です。

2.  **API 仕様の確認**
    - **Method**: `POST`
    - **URL**: `https://estimate-backend-calc-production.up.railway.app/calculate_simple`
    - **Request Body**:
      ```json
      {
        "screen_count": 12,
        "table_count": 4
      }
      ```

## 次に ODC でやること (手順)

1.  **REST API の追加 (Consume REST API)**
    - ODC Studio の **Logic** -> **Integrations** -> **REST** から `Consume REST API` を選択。
    - `Add Single Method` で `POST` を選択し、上記 URL を入力します。
    - **Test** タブで上記 Request Body を貼り付け、`Test` を実行してレスポンスが返ってくることを確認します。
    - `Copy to Response Body` を押して、Structure を自動生成させます。

2.  **画面 (UI) の作成**
    - 画面に以下の 2 つの入力欄 (Input) を配置します。
      - `screen_count` (Integer)
      - `table_count` (Integer)
    - 「計算実行 (Calculate Simple)」ボタンを配置します。

3.  **ロジックの配線**
    - ボタンの `OnClick` イベントで、新しく追加した `PostCalculate_Simple` REST API を呼び出します。
    - 入力欄の値をリクエストパラメータに詰め込みます。
    - 返ってきたレスポンスを、画面上の結果表示エリア（`estimated_amount` など）に bind します。

## メモ
- この構成により、ネストされた複雑な JSON 構造を ODC 側で意識することなく、最短距離で動くものを作ることができます。
