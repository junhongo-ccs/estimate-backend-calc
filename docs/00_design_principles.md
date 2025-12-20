# 🎯 設計原則宣言（必読）

**このドキュメントは、すべての設計・実装の前に確認する不変条件です。**

---

## 📜 不変条件（Invariant Principles）

### 1. Azure AI Agent が唯一の意思決定コアである

- ✅ **Agent が**「何を計算するか」「どの順番で呼ぶか」「結果をどう統合するか」を決定する
- ❌ UI、Functions、APIが判断・制御してはならない
- ❌ 「ステップ1→ステップ2→ステップ3」のような手続き的フローは**Agent内**で完結させる

### 2. UI / Functions / API はすべて Agent の道具（Tools）である

- ✅ 各コンポーネントは「呼ばれたら応答する」受動的な存在
- ✅ Agent が Tool として登録・管理する
- ❌ 道具同士が直接通信してはならない
- ❌ 道具が他の道具の存在を知っている設計は禁止

### 3. 手続き的フロー（順番にAPIを叩く設計）は最終形では不可

- ✅ Agent のシステムプロンプトで手順を定義する
- ✅ Prompt Flow で依存関係を表現する
- ❌ UI の JavaScript で `fetch(calcAPI).then(() => fetch(agentAPI))` のような順次呼び出しは禁止
- ❌ API-A が API-B を呼ぶ実装は禁止

---

## 🚦 「この設計は Agent 的か？」チェックリスト

**すべての設計レビュー・実装前に以下を確認すること。1つでも ❌ があれば設計やり直し。**

### ✅ Agent 的な設計（Good）

| チェック項目 | 判定基準 |
|------------|---------|
| ✅ Agent がツール選択を決定している | Prompt Flow で Tool Call を定義している |
| ✅ Agent がツール呼び出し順序を決定している | システムプロンプトで「まず calc を呼び、次に... 」と明記 |
| ✅ UI は Agent に1回だけリクエストする | `fetch(agentEndpoint, {... })` が1回のみ |
| ✅ ツールは独立して動作する | calc API は Agent の存在を知らない |
| ✅ ツール同士は通信しない | calc API → UI への直接レスポンスなし |
| ✅ エラー時も Agent が判断する | calc エラー → Agent が「代替手段」または「エラーHTML生成」を決定 |

### ❌ 非 Agent 的な設計（Bad）

| アンチパターン | 問題点 | 正しい設計 |
|---------------|--------|----------|
| ❌ UI が `calcAPI → agentAPI` と順次呼び出し | **UI が意思決定している** | UI は Agent に丸投げ。Agent が calc を呼ぶ |
| ❌ calc API が Agent を呼び出し | **ツールが別のツールを呼ぶ** | Agent が calc 結果を受け取り、次の判断をする |
| ❌ UI に「Step 1, 2, 3」のロジックがある | **UI が手順を制御** | Agent のシステムプロンプトに手順を記載 |
| ❌ Agent が存在しない（UI → calc → UI） | **そもそも Agent がいない** | Agent を中心に据える |
| ❌ 「Agent は最後の装飾だけ」 | **Agent が道具になっている** | Agent がオーケストレーターである |

---

## 📐 設計レビューゲート

**以下のフェーズごとに「Agent 的か？」を必須確認する。**

### Phase 0: アーキテクチャ設計

**チェック項目**: 
- [ ] システム図の中心に "Azure AI Agent" が存在するか？
- [ ] Agent から各コンポーネントへの矢印（Tool Call）が描かれているか？
- [ ] UI → Tool、Tool → Tool の直接矢印は存在しないか？

**NG例**:
```
❌ UI → calc API → enhance API → UI
   (Agent が不在、UIが手順を制御)
```

**OK例**:
```
✅ UI → Agent → [Tool:  calc, Tool: enhance] → Agent → UI
   (Agent がツール選択・順序を決定)
```

---

### Phase 1: データフロー設計

**チェック項目**:
- [ ] シーケンス図で Agent が中央に存在するか？
- [ ] ツールは Agent からのみ呼ばれているか？
- [ ] ツール同士の横矢印（直接通信）は存在しないか？

**NG例**:
```mermaid
❌ 
User → UI → calcAPI → enhanceAPI → UI → User
(Agent が不在)
```

**OK例**:
```mermaid
✅ 
User → UI → Agent → calcAPI
               Agent → enhanceAPI
               Agent → User
(Agent がすべてを制御)
```

---

### Phase 2: API仕様設計

**チェック項目**:
- [ ] 各 API の「呼び出し元」は Agent のみか？
- [ ] API のレスポンスは Agent 向けに設計されているか？
- [ ] API が他の API の URL を知っている実装はないか？

**NG例**:
```python
❌ calc API のコード
def calculate():
    result = do_calc()
    # 他のAPIを呼んでいる
    enhance = requests.post("https://enhance-api.com", json=result)
    return enhance
```

**OK例**:
```python
✅ calc API のコード
def calculate():
    result = do_calc()
    # 自分の仕事だけをする
    return result
```

---

### Phase 3: UI実装

**チェック項目**: 
- [ ] UI の fetch は Agent エンドポイントに1回だけか？
- [ ] UI に「if (calcSuccess) then callEnhance()」のようなロジックはないか？
- [ ] UI は Agent のレスポンスをそのまま表示するだけか？

**NG例**:
```javascript
❌ 
// UIが手順を制御している
const calcResult = await fetch(calcAPI, ... );
if (calcResult.ok) {
  const agentResult = await fetch(agentAPI, { calc: calcResult });
  display(agentResult);
}
```

**OK例**:
```javascript
✅ 
// UIは丸投げするだけ
const agentResult = await fetch(agentEndpoint, { userInput });
display(agentResult);
```

---

### Phase 4:  Prompt Flow 実装

**チェック項目**:
- [ ] System Prompt に「手順」が明記されているか？
- [ ] Tool Call の定義が Prompt Flow に存在するか？
- [ ] ツールの呼び出し順序が Agent 内で管理されているか？

**NG例**:
```yaml
❌ 
# Prompt Flow が単一ツール呼び出しのみ
nodes:
  - call_calc_tool
# その後の処理がUIに委ねられている
```

**OK例**:
```yaml
✅ 
# Prompt Flow が全体を制御
nodes:
  1. call_calc_tool
  2. analyze_calc_result
  3. generate_rationale_with_gemini
  4. aggregate_response
```

---

## 🎓 設計パターン比較

### ❌ アンチパターン:  UI中心設計

```
┌─────────┐
│   UI    │ ← 意思決定者（これがダメ）
└────┬────┘
     │ ① fetch calcAPI
     ▼
┌─────────┐
│ calc API│
└────┬────┘
     │ ② result
     ▼
┌─────────┐
│   UI    │ ← 判断（これがダメ）
└────┬────┘
     │ ③ fetch agentAPI
     ▼
┌─────────┐
│  Agent  │
└────┬────┘
     │ ④ HTML
     ▼
┌─────────┐
│   UI    │
└─────────┘
```

**問題点**:
- UI が「calc → agent」の順序を決定している
- Agent が最後の装飾役になっている
- UI のロジック変更で全体が崩れる

---

### ✅ 正しいパターン: Agent 中心設計

```
┌─────────┐
│   UI    │ ← 入力だけ
└────┬────┘
     │ ① userInput
     ▼
┌─────────────────────┐
│   Azure AI Agent    │ ← 唯一の意思決定者
│  (Prompt Flow)      │
└──┬──────────────┬───┘
   │ ② Tool Call  │ ③ Tool Call
   ▼              ▼
┌────────┐    ┌─────────┐
│calc API│    │enhance  │
└────┬───┘    └────┬────┘
     │ ④ result    │ ⑤ result
     ▼              ▼
┌─────────────────────┐
│   Agent             │ ← 統合判断
└──────────┬──────────┘
           │ ⑥ finalResponse
           ▼
      ┌─────────┐
      │   UI    │ ← 表示だけ
      └─────────┘
```

**良い点**:
- Agent がすべてのツール呼び出しを制御
- UI は入力と表示のみ
- ツール追加時も Agent の設定だけで対応

---

## 📋 設計レビューチェックシート

**すべての Pull Request / 設計書レビュー時にこのチェックシートを使用する。**

### 必須項目（1つでも No なら差し戻し）

| # | チェック項目 | Yes/No | 備考 |
|---|------------|--------|------|
| 1 | Azure AI Agent がシステムの中心に存在するか？ | □ | アーキテクチャ図確認 |
| 2 | UI は Agent に1回だけリクエストするか？ | □ | コードレビュー |
| 3 | ツール（API）同士が直接通信していないか？ | □ | シーケンス図確認 |
| 4 | Agent が「どのツールを使うか」を決定しているか？ | □ | Prompt Flow 確認 |
| 5 | システムプロンプトに手順が明記されているか？ | □ | system_prompt. txt 確認 |
| 6 | ツールは Agent の存在を知らない（独立している）か？ | □ | API コード確認 |
| 7 | エラー時も Agent が判断しているか？ | □ | エラーハンドリング確認 |

### 推奨項目（No の場合は改善提案）

| # | チェック項目 | Yes/No | 備考 |
|---|------------|--------|------|
| 8 | Prompt Flow で依存関係が可視化されているか？ | □ | flow. dag. yaml 確認 |
| 9 | ツールのレスポンスは Agent 向けに最適化されているか？ | □ | breakdown 詳細度など |
| 10 | ドキュメントに「Agent 中心」と明記されているか？ | □ | README 確認 |

---

## 🚨 NG ケーススタディ

### ケース1: UI が手順を制御

**コード例**:
```javascript
// ❌ これはダメ
async function estimate() {
  const calc = await fetch('/calc', ... );
  const enhance = await fetch('/enhance', { calc });
  display(enhance);
}
```

**問題**:  UI が「calc → enhance」の順序を決定している

**修正**:
```javascript
// ✅ これが正しい
async function estimate() {
  const agent = await fetch('/agent', { userInput });
  display(agent);
}
```

---

### ケース2: API が別の API を呼ぶ

**コード例**: 
```python
# ❌ これはダメ
@app.route("/calc")
def calc():
    result = calculate()
    # 別のAPIを呼んでいる
    enhance = requests.post("https://enhance. com", json=result)
    return enhance
```

**問題**: ツールが他のツールを呼んでいる

**修正**:
```python
# ✅ これが正しい
@app.route("/calc")
def calc():
    result = calculate()
    return result  # 自分の仕事だけ
```

---

### ケース3: Agent が装飾役

**設計例**:
```
UI → calc API → UI（判断） → Agent（HTML装飾）→ UI
```

**問題**: Agent が最後の見た目調整だけ。意思決定していない

**修正**: 
```
UI → Agent → [Tool: calc] → Agent（判断・統合）→ UI
```

---

## 📚 参考:  Agent 的設計の利点

| 観点 | Agent 中心設計 | 従来の手続き的設計 |
|------|---------------|------------------|
| **拡張性** | ツール追加は Agent 設定のみ | UI/API すべてに影響 |
| **保守性** | 手順変更は Prompt のみ | コード全体を修正 |
| **テスタビリティ** | ツール単体テスト可能 | 統合テスト必須 |
| **再利用性** | ツールは他の Agent でも使用可 | UI と密結合 |
| **AI 進化対応** | LLM 更新で自動改善 | コード書き直し |

---

## ✅ まとめ

**設計・実装の前に必ず確認すること**: 

1. ✅ **Azure AI Agent が中心か？**
2. ✅ **UI は Agent に丸投げしているか？**
3. ✅ **ツール同士は独立しているか？**

**1つでも No なら設計やり直し。**

**この原則を守ることで**:  
- AI の進化に追従できる
- 仕様変更に強い
- コードがシンプルになる