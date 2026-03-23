# Master Status

## Objective

Deliver a credible 2026-03-31 demo using Dify as the primary implementation track.

This is not just a generic AI estimate demo. The core business objective is:

- enable UIUX-phase work to be included earlier in development proposals
- make UIUX estimation visible to development-side stakeholders
- show that a non-engineer-led team can still build a business-facing PoC to this level

## Current State

As of 2026-03-23:

- Dify is the primary delivery path.
- Presentation preparation has shifted from live broad-URL demo to:
  - recorded demo first
  - individual follow-up sharing only when necessary
- The Dify workflow path is:
  - `ユーザー入力`
  - `コード実行`
  - `知識検索`
  - `LLM`
- The code execution node returns:
  - `calc_json`
  - `query_for_rag`
  - `pricing_simulator_input`
- The knowledge search node uses:
  - `コード実行 / query_for_rag`
- The LLM node uses:
  - knowledge-search `context` as background-only input
  - `コード実行 / calc_json` in the USER message as the factual input

- A downstream pricing simulator app is now operating as a separate Dify app.
- The estimate app now emits copy/paste JSON for that downstream app.
- The downstream app now includes an opening guide so first-time users know what to paste and what they can ask.

## What Is Now Materially Achieved

### 1. UIUX estimation is no longer just "explained"

It is now reflected in the deterministic Python calculation layer.

Specifically, the Phase 3 / UIUX side has been wired into the estimate engine based on:

- [33_design_cost_standards.md](C:/Users/hongouj/OneDrive%20-%20NTT%20DATA/%E3%83%89%E3%82%AD%E3%83%A5%E3%83%A1%E3%83%B3%E3%83%88/GitHub/estimate-backend-calc/dify_assets/knowledge/33_design_cost_standards.md)

This includes:

- UI design per-screen costing
- design system / guideline costing
- prototype costing
- logo / branding costing
- outsource basis
- 15% management fee
- confidence-based Phase 3 variance

### 2. Latest verified Phase 3 calculation behavior

For a validation input of:

- `screen_count = 22`
- `phase3_items = UIデザイン, デザインシステム`
- `confidence = medium`

the code node returned:

- `phase3_items = [ui_design, design_system]`
- `outsource_cost = 810000`
- `management_fee = 121500`
- `confidence_multiplier = 1.2`
- `total_phase3_cost = 1117800`

This confirms that the UIUX team's design-cost logic is now in the actual computation path.

### 3. Dify UI labels are mapped into Python logic

The repo-side updated code now absorbs Dify UI labels for:

- `features`
- `phase2_items`
- `phase3_items`

This prevents the earlier failure mode where the UI looked rich but the Python result returned empty arrays.

### 4. The latest workflow supports result Q&A

The working flow can now answer follow-up questions such as:

- breakdown of total man-days
- main red-margin causes
- required price to attain target margin
- how Phase 3 / UIUX items are reflected

while avoiding invented detail when `calc_json` does not contain it.

### 5. Estimate-to-pricing handoff is now explicit

The front-side Dify app now emits:

- a narrative estimate answer
- a downstream simulator URL
- `価格シミュレーターコピペ用JSON`

The downstream app can accept that JSON directly and answer:

- current sales/profit/margin
- required sales for target margin
- candidate-price comparisons

## Why This Matters

This project began as a UIUX-team mission, not as a generic engineering exercise.

The original intent was:

- to create a hook that helps development-side proposal work include UIUX phases
- to reduce the weakness of UIUX estimation in development-led sales discussions

The meaningful result is therefore not "an AI chatbot exists."

The meaningful result is:

- UIUX-phase work is now visible in the estimate logic
- that logic is tied to a deterministic Python engine
- it is explainable through RAG and LLM
- and it was brought to this point from a non-engineer-led context using Vibe Coding

## Workflow Architecture

Use strict separation of responsibilities:

1. Dify UI
   - collects user inputs

2. Python code node
   - computes the estimate deterministically
   - emits:
     - `calc_json`
     - `query_for_rag`

3. Knowledge search
   - uses `query_for_rag`
   - retrieves basis/background material only

4. LLM
   - uses `calc_json` as the only case-fact source
   - uses RAG only for explanation background

This separation remains essential to avoid hallucinated case details.

### 5. Downstream pricing app
   - accepts minimal JSON only
   - focuses on pricing simulation only
   - now has opening guidance for first-time users

## Security / Demo Operating Mode

- The Dify URL should not be broadly shared.
- The logic and knowledge contain company-sensitive content.
- SharePoint embedding does not solve the root issue under the current environment.
- iframe/embed approaches are only entry masking, not true access control.

Therefore the recommended operating mode is:

- recorded demo in the main presentation
- no public URL on slides
- individual follow-up sharing only for interested people

## Source of Truth for Copy/Paste

The current recommended Dify code-node source file is:

- [dify_estimate_logic_full_for_workflow_ui_mapped.py](C:/Users/hongouj/OneDrive%20-%20NTT%20DATA/%E3%83%89%E3%82%AD%E3%83%A5%E3%83%A1%E3%83%B3%E3%83%88/GitHub/estimate-backend-calc/dify_estimate_logic_full_for_workflow_ui_mapped.py)

This file includes:

- Dify UI label aliases
- `project_name` input support with fallback to `ユーザー案件`
- `tables` noise filtering
- `query_for_rag`
- `pricing_simulator_input`
- Phase 3 logic aligned to `33_design_cost_standards.md`
- `phase3_breakdown`

## Exact Resume Point

If work resumes in a new session, start from:

1. Treat Dify as the only active implementation track.
2. Use:
   - [dify_estimate_logic_full_for_workflow_ui_mapped.py](C:/Users/hongouj/OneDrive%20-%20NTT%20DATA/%E3%83%89%E3%82%AD%E3%83%A5%E3%83%A1%E3%83%B3%E3%83%88/GitHub/estimate-backend-calc/dify_estimate_logic_full_for_workflow_ui_mapped.py)
   as the copy/paste source for the Dify code execution node.
3. Keep the knowledge-search node query bound to:
   - `コード実行 / query_for_rag`
4. Keep the LLM node structured as:
   - system: rules only
   - context: knowledge-search result
   - user: `userinput.query` plus `コード実行 / calc_json`
5. Use recorded demo as the presentation baseline.
6. Use the verified Phase 3 sample if you need to prove UIUX logic reflection.

## Success Condition

The current track is considered successful when:

- the recorded demo clearly shows estimate generation
- UIUX / Phase 3 logic is visibly reflected
- the report remains aligned with `calc_json`
- follow-up Q&A stays grounded in the deterministic result
- the presentation communicates that this is a UIUX-team business enabler, not just a technical toy
