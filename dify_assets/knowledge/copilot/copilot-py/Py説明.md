本郷さん、BS準拠ロジックを組み込んだ .py 更新版を作成しました。
そのまま Dify の Code ノードに貼り付けて動作します（main(**kwargs) -> {"result": "...json..."} 互換）。
ダウンロード

estimate_logic_bs.py（BS係数対応・応援PJ加重・SG&A粗利ベース・逆算式修正 版）
→ estimate_logic_bs.py を取得


変更点（サマリー）


BS_ORG_CONFIG を内蔵

部門 → 間接費単金（円/h） / 本部販管費率 / 全社販管費率（BS=47.8%） を定義。
既定の主所属は 「ビジネスイノベーション事業部共通」。入力が無い・未知部門は自動フォールバック。.py).py) [jp-prod.as...rosoft.com]



直接労務費：PDFのランク人月単価で算定

Rank4=1,098千円 / Rank3=944千円 / Rank2=758千円 / Rank1=541千円（1人月=160h 換算）。
team_ratio（例：Rank3:0.8, Rank2:0.2）で加重平均→人月コスト→人日/20 で人月化。.py).py) [jp-prod.as...rosoft.com]



間接費：固定率ではなく「時間×部門単金」

総人日×8h × 間接費単金（円/h）。
応援PJ配分（dept_allocation）が入力されれば、間接費単金・本部販管費率を加重平均。.py).py) [jp-prod.as...rosoft.com]



販管費（SG&A）：粗利ベース

本部販管費率（部門別）＋全社販管費率（BS=47.8%） を 粗利 に乗算し控除。
営業利益率（Operating Margin） を正しく表示。.py).py).py) [jp-prod.as...rosoft.com]



逆算売価（目標営業利益率 τ）を粗利ベース定義に統一
\text{Sales} = \\frac{\\text{COGS}}{1 - \\frac{\\tau}{1-\\alpha}}\\quad(\\alpha=\\text{HQ+Corp SG&A率})

既存式（SG&Aを売上に直接掛ける前提）から完全置換。.py).py) [jp-prod.as...rosoft.com]



Phase2は直接費に算入、Phase3は外注費扱い

COGS = 直接労務費 + 間接費 + Phase2固定費 + Phase3（外注） として集計。
既存PoCの品目・確度係数（confidence）は踏襲。.py).py) [jp-prod.as...rosoft.com]



出力のエコーバック

bs_input に、適用した部門、加重後の率・単金、ランクミックス を明示。
input_echo は既存の PoC 構成を踏襲し、前提をMECEに表示。.yml).yml) [jp-prod.as...rosoft.com], [nttdatajpp...epoint.com]




Dify への組込みメモ

Code ノードのスクリプトを、この estimate_logic_bs.py の中身で置換。
Start(UI) の質問に以下3つを追加し、Codeノードの variables に接続してください：

department（既定：ビジネスイノベーション事業部共通）
dept_allocation（段落：部門: 割合 形式。自動正規化）
team_ratio（テキスト：Rank3:0.8, Rank2:0.2 形式。自動正規化）
※既存の estimation_profile / target_platform / dev_type / screen_count / tables / table_count / complexity / duration / confidence / phase2_items / phase3_items / target_margin は従来どおり接続でOK。.yml) [nttdatajpp...epoint.com]




中身の確認ポイント（式の整合）

1人月=160h、ランク時給→人月単価、部門別 間接費単金、販管費の粗利控除、応援PJの加重は FY2026 利益管理表の運用思想と一致しています。.py) [jp-prod.as...rosoft.com]
既存PoCの機能一覧/Phase2/3構造・UIフローは保ちつつ、損益ロジックのみBS準拠に差し替えています。.yml)