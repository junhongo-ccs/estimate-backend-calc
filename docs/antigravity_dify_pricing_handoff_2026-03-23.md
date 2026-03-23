# Antigravity Dify Pricing Handoff Update (2026-03-23)

## What Was Achieved Today

Today we completed a working two-app Dify flow:

1. A front-side estimate app generates a deterministic estimate and explanatory report.
2. That app now also emits a copy/paste JSON payload for downstream price simulation.
3. A separate downstream price-simulator app accepts that JSON and answers pricing questions immediately.

This is no longer just an estimate explanation flow.
It is now a usable handoff flow from "estimate generation" to "price negotiation simulation".

## Why This Matters

The problem was not only calculation accuracy.
The problem was workflow continuity.

Before today:

- the estimate app could calculate and explain
- the price simulator app could simulate
- but the bridge between them was implicit and fragile
- and the price simulator UX was poor for first-time users

After today:

- the bridge is explicit
- the handoff JSON is generated automatically by the estimate app
- the downstream app tells users what to paste and what they can ask
- repository source code and Dify runtime behavior are now aligned

This materially improves demo credibility.

## Final Operating Model

We intentionally kept a **two-app structure**.

### Front-side app

Responsibility:

- collect estimate inputs
- run deterministic estimate calculation
- explain the estimate result
- output a copy/paste JSON payload for the pricing simulator

Current workflow shape:

- `ユーザー入力`
- `コード実行`
- `知識検索`
- `LLM`
- `回答`

### Downstream pricing app

Responsibility:

- accept minimal estimate-result JSON
- calculate profit amount
- calculate operating margin
- calculate required sales for target margin
- compare multiple price candidates

Current workflow shape:

- `ユーザー入力`
- `LLM`
- `回答`

This separation is deliberate.
The first app is allowed to think and explain.
The second app is intentionally narrow and optimized for pricing interaction.

## Handoff JSON Contract

The front-side app now emits a minimal JSON payload at the end of its answer.

Current shape:

```json
{
  "project_name": "ユーザー案件",
  "cost": 42717253,
  "current_sales": 31668483,
  "target_margin": 0.1,
  "currency": "JPY"
}
```

Meaning of fields:

- `project_name`
  - optional user input on the estimate side
  - fallback is `"ユーザー案件"`
- `cost`
  - `profit_analysis.cogs + profit_analysis.sga_cost`
- `current_sales`
  - `profit_analysis.sales`
- `target_margin`
  - parsed from estimate-side user input
- `currency`
  - currently fixed to `JPY`

## Front-side Dify Code Change

The Dify code execution node now returns:

- `calc_json`
- `query_for_rag`
- `pricing_simulator_input`

The recommended copy/paste source file is:

- [dify_estimate_logic_full_for_workflow_ui_mapped.py](/Users/hongoujun/Documents/GitHub/estimate-backend-calc/dify_estimate_logic_full_for_workflow_ui_mapped.py)

Important runtime behavior now included in that file:

- `project_name` input support
- default `project_name = "ユーザー案件"` when blank
- `pricing_simulator_input` generation
- stable `query_for_rag`
- deterministic estimate calculation path unchanged

Relevant code behavior:

```python
pricing_simulator_input = {
    "project_name": args["project_name"],
    "cost": data["profit_analysis"]["cogs"] + data["profit_analysis"]["sga_cost"],
    "current_sales": data["profit_analysis"]["sales"],
    "target_margin": float(args.get("target_margin") or 0),
    "currency": "JPY",
}
```

## Dify UI Changes on the Front-side App

### 1. New input variable

Added user input field:

- `project_name`

Rules:

- not required
- if blank, Python fills `"ユーザー案件"`

### 2. LLM output behavior

The estimate-side answer now ends with:

- a short sentence telling users they can continue price simulation
- the downstream simulator URL
- `価格シミュレーターコピペ用JSON`

This makes the handoff visible and usable without hidden operator knowledge.

## Downstream App UX Upgrade

The downstream app originally had poor first-contact UX.
It behaved like a silent blank tool.

That is now fixed by configuring `会話の開始`.

The opening text now explains:

- this is a pricing simulator
- users should paste the estimate-result JSON
- where to go if they need to regenerate that JSON
- example payload
- example questions

This was a major UX improvement.
The downstream app now behaves like a guided tool rather than an empty chat box.

## Verified Runtime Behavior

### Front-side output

A test run now produces report text plus:

```text
価格シミュレーターコピペ用JSON:
{
  "project_name": "テスト",
  "cost": 42717253,
  "current_sales": 31668483,
  "target_margin": 0.1,
  "currency": "JPY"
}
```

When `project_name` is blank, output becomes:

```json
{
  "project_name": "ユーザー案件",
  "cost": 42717253,
  "current_sales": 31668483,
  "target_margin": 0.1,
  "currency": "JPY"
}
```

### Downstream output

The downstream pricing simulator correctly answered:

- current sales / profit / margin
- required sales to meet target margin
- comparison of candidate prices

Example verified result for target margin question:

- current sales: `31,668,483 JPY`
- required sales: `47,463,614 JPY`
- operating profit at target: `4,746,361 JPY`
- margin: `10.0%`

## Repository State

The repository was updated to match actual Dify runtime behavior.

Important commits made today on `estimate-backend-calc`:

- `ec70e1d`
  - sync Dify workflow copy/paste source with pricing handoff output
- `9478b9b`
  - add `project_name` support to Dify workflow handoff

Main branch now includes these changes.

## What Antigravity Should Understand

The meaningful achievement is not "we have two chat apps."

The meaningful achievement is:

- deterministic estimate calculation now hands off cleanly into pricing simulation
- the user does not need internal team vocabulary to continue the workflow
- the runtime Dify configuration and the repository source are aligned
- the demo now shows an end-to-end operator path instead of isolated features

This is demo-grade and explainable.

## Recommended Resume Point

If work resumes later, use these files first:

1. [master_status.md](/Users/hongoujun/Documents/GitHub/estimate-backend-calc/docs/master_status.md)
2. [antigravity_dify_pricing_handoff_2026-03-23.md](/Users/hongoujun/Documents/GitHub/estimate-backend-calc/docs/antigravity_dify_pricing_handoff_2026-03-23.md)
3. [dify_estimate_logic_full_for_workflow_ui_mapped.py](/Users/hongoujun/Documents/GitHub/estimate-backend-calc/dify_estimate_logic_full_for_workflow_ui_mapped.py)

## Next Practical Step

No urgent architecture rewrite is required.

The next practical work should be one of:

- document the front-side Dify LLM prompt used for the report app
- document the downstream pricing-app prompt and opening text in repo form
- optionally add `suggested_price_to_attain_target` to the handoff JSON if business users want a stronger hint
