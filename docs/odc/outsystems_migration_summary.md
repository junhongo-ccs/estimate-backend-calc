# AI Estimation System: Dify -> OutSystems Migration Summary

This document consolidates the API usage and JSON schema references for Antigravity.
This document is updated to the latest verified state as of **2026-03-10 (JST)**.

## Environment
- Python: `/usr/bin/python3` (3.8.2)
- Repo (logic): `/Users/hongoujun/Documents/GitHub/estimate-backend-calc`
- Logic source of truth: `/Users/hongoujun/Documents/GitHub/estimate-backend-calc/dify_estimate_logic_full_for_workflow_ui_mapped.py`

## API Wrapper
- Entry: `/Users/hongoujun/Documents/GitHub/estimate-backend-calc/outsystems_api_wrapper.py`
- Framework: FastAPI
- Endpoint: `POST /calculate`
- Report: `POST /report` (Gemini)
- Simple Calc: `POST /calculate_simple` (Minimal params for ODC)
- Health: `GET /health`

Run:

```bash
python3 /Users/hongoujun/Documents/GitHub/estimate-backend-calc/outsystems_api_wrapper.py
```

Env:
- `GEMINI_API_KEY` for `/report`
- `GEMINI_MODEL` (default: `gemini-2.5-flash`)
- Model fallback is implemented in wrapper (`gemini-2.5-flash` -> `gemini-2.0-flash` -> `gemini-1.5-flash` on 404)

## Current Progress (Verified)

- Railway deployment is active and reachable.
- Public base URL is fixed:
  - `https://estimate-backend-calc-production.up.railway.app`
- Health check is verified:
  - `GET /health` returns `{"status":"ok"}`.
- `/report` is verified with Gemini key:
  - Returns `report_markdown`
  - Returns `report_html` when `output_format=html`
- `Procfile` start command is in place:
  - `web: uvicorn outsystems_api_wrapper:app --host 0.0.0.0 --port $PORT`
- Runtime dependencies for wrapper are added in `requirements.txt`:
  - `fastapi`, `uvicorn`, `pydantic`, `markdown`

## Production Endpoints (Current)

- Base URL: `https://estimate-backend-calc-production.up.railway.app`
- Calculate: `POST https://estimate-backend-calc-production.up.railway.app/calculate`
- Calculate Simple: `POST https://estimate-backend-calc-production.up.railway.app/calculate_simple`
- Report: `POST https://estimate-backend-calc-production.up.railway.app/report`
- Health: `GET https://estimate-backend-calc-production.up.railway.app/health`

## Implementation Plan (Personal Environment, Minimum Parity with Dify)

- Day 0.5: Environment setup (OutSystems Personal + API running)
- Day 1: REST integration + Request/Response Structures
- Day 2: Input form and execution flow
- Day 3: Result rendering + error handling + defaults

## Required Form Inputs (Parity with Dify Flow)

Core inputs:
- screen_count (Number)
- table_count (Number)
- estimation_profile (Choice: poc / enterprise / mission_critical)
- department (Choice: BS部門一覧)
- complexity (Choice: low / medium / high / very_high)
- duration (Choice: long / normal / short)
- dev_type (Choice: new / porting)
- target_platform (Choice: web_b2e / web_b2c / mobile / all)
- confidence (Choice: low / high)
- target_margin (Number, % or 0-1)

Optional lists:
- features (Multi-select)
- phase2_items (Multi-select)
- phase3_items (Multi-select)
- tables (List of strings)

Advanced (optional):
- dept_allocation (Repeater: dept + share)
- team_ratio (Rank1-4 ratios)

## Full Input Variable Coverage (User-Provided)

Scalar fields:
- screen_count (int, default 10)
- table_count (int, default 0)
- estimation_profile (string: poc | enterprise | mission_critical)
- complexity (string: low | medium | high | very_high)
- duration (string: long | normal | short)
- dev_type (string: new | porting)
- target_platform (string: web_b2e | web_b2c | mobile | all)
- confidence (string: low | high)
- target_margin (float, 0-1 or percent)
- department (string: BS部門名)

List fields:
- features (string[])
- phase2_items (string[])
- phase3_items (string[])
- tables (string[])

Structured fields:
- dept_allocation (list of `{ dept: string, share: float }`)
- team_ratio (object: `{ Rank4: float, Rank3: float, Rank2: float, Rank1: float }`)

## Choice Lists (for UI Pickers)

Estimation profile:
- poc
- enterprise
- mission_critical

Complexity:
- low
- medium
- high
- very_high

Duration:
- long
- normal
- short

Dev type:
- new
- porting

Target platform:
- web_b2e
- web_b2c
- mobile
- all

Confidence:
- low
- high

Features (labels users can pick):
- 認証・認可 (Auth/SSO)
- 決済基盤連携 (Payment)
- 検索・フィルタリング (Basic)
- 高度な検索 (AI/ベクトル)
- プッシュ通知
- SNS連携・シェア
- 管理画面 (Admin)
- 外部API連携
- オフライン対応
- 多言語対応 (i18n)

Phase2 items:
- 基本設計書作成
- 詳細設計書作成
- インフラ・クラウド設計
- セキュリティ審査・対策案
- 開発標準化・共通部設計

Phase3 items:
- 企業/プロダクトロゴ制作
- ブランドガイドライン策定
- 高精度UIプロトタイプ
- マーケティング素材/LP

Departments (BS):
- ビジ・企画営業部
- ビジ・システム開発部
- ビジネスイノベーション事業部共通
- ＳＦ＆Ｍ営業部
- ＳＦ＆Ｍ第１システム開発部
- ＳＦ＆Ｍ第２システム開発部
- ＳＦ＆Ｍ事業部（共通）
- ＣＳ営業部
- ＣＳ第１システム開発部
- ＣＳ第２システム開発部
- ＣＳシステム事業部（共通）
- ＤＴ営業部
- ＤＴ第１開発部
- ＤＴ第２開発部
- ＤＴ事業部（共通）
- 社会・科学システム営業部
- データサイエンスシステム部
- 社会・科学システム事業部（共通）
- ソリューションビジネス推進室

## Request/Response Overview
Key request fields:
- `screen_count`, `table_count`
- `estimation_profile` (preferred) or `profile` (legacy)
- `department`, `complexity`, `duration`, `dev_type`, `target_platform`
- `features`, `phase2_items`, `phase3_items`, `tables`
- `dept_allocation` (array of `{ "dept": "...", "share": 0.6 }`)
- `team_ratio` (object like `{ "Rank3": 0.8, "Rank2": 0.2 }`)
- `target_margin` (float)

Key response fields:
- `estimated_amount`, `estimated_range`
- `man_days`, `profit_analysis`, `input_echo`

Current production behavior note:
- `/calculate` currently returns `calc_json` (JSON string wrapper) in the deployed environment.
- OutSystems side should parse `calc_json` string to object before binding fields, or backend should be aligned to direct object response.

Report endpoint:
- Request: `estimation_result` (object), `rag_context` (string, optional), `user_notes` (string, optional), `language` (string), `output_format` (markdown|html)
- Response: `report_markdown` (string), `report_html` (string, when html)

## JSON Schemas (for OutSystems Structures)
Use the schemas here:
- `/Users/hongoujun/Documents/GitHub/estimate-backend-calc/outsystems_json_schemas.md`
Includes `/report` request/response schemas.

## OutSystems Structure Mapping (Quick Table)

Request Structure -> JSON field (type)

- ScreenCount -> `screen_count` (Integer)
- TableCount -> `table_count` (Integer)
- EstimationProfile -> `estimation_profile` (Text)
- Profile -> `profile` (Text, legacy)
- Department -> `department` (Text)
- Complexity -> `complexity` (Text)
- Duration -> `duration` (Text)
- DevType -> `dev_type` (Text)
- TargetPlatform -> `target_platform` (Text)
- Confidence -> `confidence` (Text)
- Features -> `features` (List<Text>)
- Phase2Items -> `phase2_items` (List<Text>)
- Phase3Items -> `phase3_items` (List<Text>)
- Tables -> `tables` (List<Text>)
- DeptAllocation -> `dept_allocation` (List<DeptAllocation>)
- TeamRatio -> `team_ratio` (TeamRatio)
- TargetMargin -> `target_margin` (Decimal)

DeptAllocation Structure:
- Dept -> `dept` (Text)
- Share -> `share` (Decimal)

TeamRatio Structure (dynamic):
- Use a Structure with optional attributes `Rank4`, `Rank3`, `Rank2`, `Rank1` (Decimal)

Response Structure -> JSON field (type)

- Status -> `status` (Text)
- EstimatedAmount -> `estimated_amount` (Text)
- EstimatedRange -> `estimated_range` (Text)
- ManDays -> `man_days` (ManDays)
- BsInput -> `bs_input` (BsInput)
- InputEcho -> `input_echo` (InputEcho)
- ProfitAnalysis -> `profit_analysis` (ProfitAnalysis)
- Productivity -> `productivity` (Text)

ManDays Structure:
- DevelopmentTotal -> `development_total` (Decimal)
- FpBased -> `fp_based` (Decimal)
- FeatureBased -> `feature_based` (Decimal)

BsInput Structure:
- Department -> `department` (Text)
- DeptAllocation -> `dept_allocation` (List<DeptAllocation>)
- SgaRateApplied -> `sga_rate_applied` (Text)
- IndirectYenPerHour -> `indirect_yen_per_hour` (Decimal)
- TeamRatio -> `team_ratio` (TeamRatio)

InputEcho Structure:
- Profile -> `profile` (Text)
- ProfileDescription -> `profile_description` (Text)
- ScreenCount -> `screen_count` (Integer)
- TableCount -> `table_count` (Integer)
- Tables -> `tables` (List<Text>)
- Complexity -> `complexity` (Text)
- Duration -> `duration` (Text)
- DevType -> `dev_type` (Text)
- TargetPlatform -> `target_platform` (Text)
- Confidence -> `confidence` (Text)
- TargetMargin -> `target_margin` (Decimal)
- Features -> `features` (List<Text>)
- Phase2Items -> `phase2_items` (List<Text>)
- Phase3Items -> `phase3_items` (List<Text>)

ProfitAnalysis Structure:
- Sales -> `sales` (Decimal)
- Cogs -> `cogs` (Decimal)
- GrossProfit -> `gross_profit` (Decimal)
- SgaCost -> `sga_cost` (Decimal)
- OperatingProfit -> `operating_profit` (Decimal)
- OperatingMargin -> `operating_margin` (Text)
- TargetMarginSpecified -> `target_margin_specified` (Text)
- SuggestedPriceToAttainTarget -> `suggested_price_to_attain_target` (Decimal)
- Breakdown -> `breakdown` (ProfitBreakdown)

ProfitBreakdown Structure:
- SgaCalculationBase -> `sga_calculation_base` (Text)
- SgaRateOnPropaLabor -> `sga_rate_on_propa_labor` (Text)

## OutSystems Integration Steps (Summary)
1) Service Studio -> Integrations -> REST -> Consume REST API
2) Method: `POST` to `https://estimate-backend-calc-production.up.railway.app/calculate`
3) Use schemas above to build Request/Response Structures
4) Test via built-in REST test tab

## OutSystems Integration (Report Endpoint)
1) Add another REST method for `POST /report`
2) Use `ReportRequest` / `ReportResponse` schemas
3) Endpoint: `https://estimate-backend-calc-production.up.railway.app/report`
4) Call `/calculate` first, then pass its output as `estimation_result`

## OutSystems Screen Flow (Calculate -> Report -> Display)

Screen: `EstimateForm`
1) User inputs (all parity fields)
2) OnClick "Calculate" button:
   - Call `Calculate` REST method
   - Store response in `EstimateResult` (Structure)
3) OnClick "Generate Report" button:
   - Build `ReportRequest`:
     - `estimation_result` = `EstimateResult`
     - `rag_context` = optional text
     - `user_notes` = optional text
     - `language` = "ja"
   - Call `Report` REST method
   - Store `report_markdown` in `ReportText`
4) Display area:
   - Summary cards: `estimated_amount`, `estimated_range`
   - Detail: `man_days`, `profit_analysis`
   - Report preview: `report_markdown` (Markdown viewer or multiline text)

Data elements on the screen:
- Input variables (screen_count, table_count, etc.)
- `EstimateResult` (Structure)
- `ReportText` (Text)
- `IsCalculating` / `IsReporting` (Boolean) for loading states

## Screen Layout (Form Design Proposal)

Layout: single screen with 2-column layout (left: inputs, right: results)

Left column (Inputs):
- Section: "Core"
  - screen_count (Number)
  - table_count (Number)
  - estimation_profile (Dropdown)
  - department (Dropdown)
  - complexity (Dropdown)
  - duration (Dropdown)
  - dev_type (Dropdown)
  - target_platform (Dropdown)
  - confidence (Dropdown)
  - target_margin (Number, with % hint)
- Section: "Features"
  - features (Multi-select)
- Section: "Phase 2"
  - phase2_items (Multi-select)
- Section: "Phase 3"
  - phase3_items (Multi-select)
- Section: "Tables (optional)"
  - tables (Text Area, one per line)
- Section: "Advanced (optional)"
  - dept_allocation (Editable Table: dept + share)
  - team_ratio (Inputs: Rank4/Rank3/Rank2/Rank1)
- Buttons:
  - Calculate
  - Generate Report

Right column (Results):
- Summary cards:
  - estimated_amount
  - estimated_range
- Man-days:
  - development_total, fp_based, feature_based
- Profit analysis:
  - sales, cogs, gross_profit, sga_cost, operating_profit, operating_margin
  - suggested_price_to_attain_target
- Report:
  - report_markdown (Markdown viewer or multi-line text)

UX notes:
- Disable "Generate Report" until Calculate succeeds.
- Show loading indicators using `IsCalculating` / `IsReporting`.
- Preserve input state to allow iterative tweaks.

## Screen Components (OutSystems Widgets)

Inputs (left column):
- `screen_count`, `table_count` -> `Input` (type: Integer)
- `estimation_profile` -> `Dropdown` (Static List: poc/enterprise/mission_critical)
- `department` -> `Dropdown` (Static List: BS departments)
- `complexity` -> `Dropdown` (Static List)
- `duration` -> `Dropdown` (Static List)
- `dev_type` -> `Dropdown` (Static List)
- `target_platform` -> `Dropdown` (Static List)
- `confidence` -> `Dropdown` (Static List)
- `target_margin` -> `Input` (type: Decimal) + `Hint` (%)
- `features` -> `ListBox` (Multi-select) or `Checkbox` list
- `phase2_items` -> `ListBox` (Multi-select) or `Checkbox` list
- `phase3_items` -> `ListBox` (Multi-select) or `Checkbox` list
- `tables` -> `Text Area` (one item per line, split in logic)
- `dept_allocation` -> `Editable Table` (Columns: Department dropdown + Share decimal)
- `team_ratio` -> `Input` fields (Rank4/Rank3/Rank2/Rank1 decimal)
- `Calculate` -> `Button` (OnClick: call REST `Calculate`)
- `Generate Report` -> `Button` (OnClick: call REST `Report`)

Results (right column):
- `estimated_amount`, `estimated_range` -> `Expression` inside `Card`
- `man_days` -> `Expression` or `List` in `Card`
- `profit_analysis` -> `Table` or `List` (key/value)
- `report_markdown` -> `Text Area` or `Rich Text` (Markdown)

Logic nodes:
- `OnClick Calculate` -> REST `Calculate` -> Assign `EstimateResult`
- `OnClick Generate Report` -> Build `ReportRequest` -> REST `Report` -> Assign `ReportText`

## Widget Placement (Concrete Layout)

Screen: `EstimateForm`

Top bar:
- `Container` (Full width)
  - `Text` (Title: "AI見積システム")
  - `Text` (Subtitle: "Dify PoC互換")

Body:
- `Container` (Full width)
  - `Columns` (2 columns, 5/7 split)

Left column (Inputs):
- `Section` (Title: "Core")
  - `Input` screen_count (Integer)
  - `Input` table_count (Integer)
  - `Dropdown` estimation_profile
  - `Dropdown` department
  - `Dropdown` complexity
  - `Dropdown` duration
  - `Dropdown` dev_type
  - `Dropdown` target_platform
  - `Dropdown` confidence
  - `Input` target_margin (Decimal) + `Hint` (%)
- `Section` (Title: "Features")
  - `ListBox` features (Multi-select)
- `Section` (Title: "Phase 2")
  - `ListBox` phase2_items (Multi-select)
- `Section` (Title: "Phase 3")
  - `ListBox` phase3_items (Multi-select)
- `Section` (Title: "Tables")
  - `Text Area` tables (one per line)
- `Section` (Title: "Advanced")
  - `Editable Table` dept_allocation
    - Column: Dept (`Dropdown`)
    - Column: Share (`Input` Decimal)
  - `Inputs` team_ratio (Rank4/Rank3/Rank2/Rank1)
- `Container` (Buttons)
  - `Button` Calculate (Primary)
  - `Button` Generate Report (Secondary)

Right column (Results):
- `Section` (Title: "Summary")
  - `Card` estimated_amount
  - `Card` estimated_range
- `Section` (Title: "Man-days")
  - `Table` (development_total, fp_based, feature_based)
- `Section` (Title: "Profit Analysis")
  - `Table` (sales, cogs, gross_profit, sga_cost, operating_profit, operating_margin, suggested_price_to_attain_target)
- `Section` (Title: "Report")
  - `Rich Text` or `Text Area` report_markdown

Gate screen: `Gate`
- `Container` (Centered)
  - `Text` Title
  - `Text` Description
  - `Input` Password (Password mode)
  - `Button` Enter
  - `Message` Error

## Dropdown / List Source Setup (Static Lists)

Create Static Entities (or Local Variables as lists) for dropdowns:

EstimationProfile:
- Key: `poc` Label: `PoC/開発重視型`
- Key: `enterprise` Label: `エンタープライズ型`
- Key: `mission_critical` Label: `高信頼性型`

Complexity:
- `low` / `medium` / `high` / `very_high`

Duration:
- `long` / `normal` / `short`

DevType:
- `new` / `porting`

TargetPlatform:
- `web_b2e` / `web_b2c` / `mobile` / `all`

Confidence:
- `low` / `high`

Department (Static list):
- ビジ・企画営業部
- ビジ・システム開発部
- ビジネスイノベーション事業部共通
- ＳＦ＆Ｍ営業部
- ＳＦ＆Ｍ第１システム開発部
- ＳＦ＆Ｍ第２システム開発部
- ＳＦ＆Ｍ事業部（共通）
- ＣＳ営業部
- ＣＳ第１システム開発部
- ＣＳ第２システム開発部
- ＣＳシステム事業部（共通）
- ＤＴ営業部
- ＤＴ第１開発部
- ＤＴ第２開発部
- ＤＴ事業部（共通）
- 社会・科学システム営業部
- データサイエンスシステム部
- 社会・科学システム事業部（共通）
- ソリューションビジネス推進室

Features (Multi-select list):
- 認証・認可 (Auth/SSO)
- 決済基盤連携 (Payment)
- 検索・フィルタリング (Basic)
- 高度な検索 (AI/ベクトル)
- プッシュ通知
- SNS連携・シェア
- 管理画面 (Admin)
- 外部API連携
- オフライン対応
- 多言語対応 (i18n)

Phase2 (Multi-select list):
- 基本設計書作成
- 詳細設計書作成
- インフラ・クラウド設計
- セキュリティ審査・対策案
- 開発標準化・共通部設計

Phase3 (Multi-select list):
- 企業/プロダクトロゴ制作
- ブランドガイドライン策定
- 高精度UIプロトタイプ
- マーケティング素材/LP

Mapping note:
- The labels above must map to the keys in `dify_estimate_logic_full_for_workflow_ui_mapped.py`.
- If you store labels only, convert them via the label map before sending to `/calculate`.

## Label -> Key Mapping (OutSystems Logic)

If the UI stores labels (Japanese), convert to keys before calling `/calculate`.

Example (Features):
- 認証・認可 (Auth/SSO) -> `auth`
- 決済基盤連携 (Payment) -> `payment`
- 検索・フィルタリング (Basic) -> `search_basic`
- 高度な検索 (AI/ベクトル) -> `search_advanced`
- プッシュ通知 -> `push_notification`
- SNS連携・シェア -> `sns_integration`
- 管理画面 (Admin) -> `admin_dashboard`
- 外部API連携 -> `api_external`
- オフライン対応 -> `offline_mode`
- 多言語対応 (i18n) -> `multi_language`

Example (Phase2):
- 基本設計書作成 -> `basic_design`
- 詳細設計書作成 -> `detail_design`
- インフラ・クラウド設計 -> `infra_design`
- セキュリティ審査・対策案 -> `security_review`
- 開発標準化・共通部設計 -> `standardization`

Example (Phase3):
- 企業/プロダクトロゴ制作 -> `logo_creation`
- ブランドガイドライン策定 -> `brand_guideline`
- 高精度UIプロトタイプ -> `ui_prototype`
- マーケティング素材/LP -> `marketing_asset`

Implementation hint:
- Create a local list with two columns: `Label`, `Key`.
- Map selected labels to keys before building the request payload.

## Click-Through Steps (Service Studio)

Create app:
1) Launch Service Studio
2) `New Application` -> `Reactive Web App`
3) Name: `AI_Estimation_PoC`

Add REST (Calculate):
1) `Logic` -> `Integrations` -> `REST`
2) Right-click -> `Consume REST API` -> `Add Single Method`
3) Method: `POST`, URL: `https://estimate-backend-calc-production.up.railway.app/calculate`
4) Click `Test`, paste sample request, verify response
5) Save; confirm Request/Response Structures created

Add REST (Report):
1) `Logic` -> `Integrations` -> `REST`
2) Right-click -> `Consume REST API` -> `Add Single Method`
3) Method: `POST`, URL: `https://estimate-backend-calc-production.up.railway.app/report`
4) Click `Test`, pass `estimation_result` from calculate response
5) Save; confirm Request/Response Structures created

Create Gate screen:
1) `Interface` tab -> `Screens` -> `Add Screen`
2) Name: `Gate`
3) Place `Input` (Password), `Button`, `Text` blocks
4) Create `AppGatePassword` Site Property
5) Create Session var `GatePassed`
6) Add OnClick logic to validate and redirect

Create EstimateForm screen:
1) `Interface` tab -> `Screens` -> `Add Screen`
2) Name: `EstimateForm`
3) Add `Columns` (2 column layout)
4) Place inputs on left, results on right
5) Add `Calculate` and `Generate Report` buttons
6) Create actions `CalculateEstimate` and `GenerateReport`
7) Wire buttons to actions

Guard all screens:
1) For each screen, open `OnInitialize`
2) If `GatePassed` is False -> Redirect to `Gate`

## Naming Conventions (OutSystems)

Screens:
- `Gate`
- `EstimateForm`

Actions:
- `CalculateEstimate`
- `GenerateReport`

REST Integrations:
- `Estimate_Calculate`
- `Estimate_Report`

Structures:
- `EstimateRequest`
- `EstimateResponse`
- `ReportRequest`
- `ReportResponse`
- `ManDays`
- `ProfitAnalysis`
- `ProfitBreakdown`
- `BsInput`
- `InputEcho`
- `DeptAllocation`
- `TeamRatio`

Variables:
- `EstimateResult` (EstimateResponse)
- `ReportText` (Text)
- `IsCalculating` (Boolean)
- `IsReporting` (Boolean)
- `GatePassed` (Session Boolean)
- `RagContext` (Text)
- `UserNotes` (Text)

Site Properties:
- `AppGatePassword` (Text)

## Data Type Mapping (OutSystems)

Request:
- `screen_count` -> Integer
- `table_count` -> Integer
- `estimation_profile` -> Text
- `department` -> Text
- `complexity` -> Text
- `duration` -> Text
- `dev_type` -> Text
- `target_platform` -> Text
- `confidence` -> Text
- `features` -> List<Text>
- `phase2_items` -> List<Text>
- `phase3_items` -> List<Text>
- `tables` -> List<Text>
- `dept_allocation` -> List<DeptAllocation>
- `team_ratio` -> TeamRatio
- `target_margin` -> Decimal

Response:
- `estimated_amount` -> Text
- `estimated_range` -> Text
- `man_days.development_total` -> Decimal
- `man_days.fp_based` -> Decimal
- `man_days.feature_based` -> Decimal
- `profit_analysis.sales` -> Decimal
- `profit_analysis.cogs` -> Decimal
- `profit_analysis.gross_profit` -> Decimal
- `profit_analysis.sga_cost` -> Decimal
- `profit_analysis.operating_profit` -> Decimal
- `profit_analysis.operating_margin` -> Text
- `profit_analysis.target_margin_specified` -> Text
- `profit_analysis.suggested_price_to_attain_target` -> Decimal
- `profit_analysis.breakdown.sga_rate_on_propa_labor` -> Text
- `profit_analysis.breakdown.sga_calculation_base` -> Text

Report:
- `report_markdown` -> Text

## UI Validation Rules (OutSystems)

Numeric inputs:
- `screen_count`, `table_count`: min 0, max 9999
- `target_margin`: min 0, max 1 (or allow 0-100 and convert)
- `dept_allocation.share`: min 0, max 1
- `team_ratio` values: min 0, max 1

Required fields:
- `screen_count`
- `estimation_profile`
- `department`
- `complexity`
- `duration`
- `dev_type`
- `target_platform`

Cross-field:
- If `tables` is filled and `table_count` is 0, set `table_count = number of lines`.
- If `dept_allocation` is provided, normalize shares to sum 1.0.
- If `team_ratio` sums to 0, use default `Rank3=0.8, Rank2=0.2`.

UX:
- Show inline error messages under fields.
- Block `Calculate` until required fields are valid.

## 8px Grid Design (Clean UI)

Goal: consistent spacing and alignment across all screens.

Spacing rules:
- Base unit = 8px
- Small gap = 8px
- Medium gap = 16px
- Large gap = 24px
- Section padding = 24px
- Card padding = 16px
- Field vertical spacing = 16px

Layout rules:
- Two-column layout: 5/7 split
- Top bar height = 56px (7 * 8)
- Section title margin-bottom = 8px
- Button group gap = 8px

Typography (simple and clean):
- Title: 24px, semi-bold
- Section title: 16px, semi-bold
- Body text: 14px

Implementation in OutSystems:
- Use `Container` padding set to 24px
- Use `Gap` / `Margin` values in multiples of 8
- Apply a shared `Theme` or `Style Class` for cards and sections

## Theme / Style Class (OutSystems)

Define reusable classes in Theme > CSS:

Example classes:
- `.section-card`:
  - padding: 16px
  - margin-bottom: 24px
  - border: 1px solid #e6e6e6
  - border-radius: 8px
  - background: #ffffff
- `.section-title`:
  - font-size: 16px
  - font-weight: 600
  - margin-bottom: 8px
- `.page-title`:
  - font-size: 24px
  - font-weight: 600
  - margin-bottom: 8px
- `.page-subtitle`:
  - font-size: 14px
  - color: #666666
  - margin-bottom: 16px
- `.button-row`:
  - display: flex
  - gap: 8px
- `.result-card`:
  - padding: 16px
  - border-radius: 8px
  - background: #FAFAFA

How to apply:
- Wrap each section in a `Container` with `section-card`
- Use `Text` with `section-title` or `page-title`
- Place buttons in a `Container` with `button-row`

## Color Palette (Clean + Intelligent)

Base:
- Background: `#FAFAFA`
- Surface (cards): `#FFFFFF`
- Border: `#E6E6E6`

Accent (navy):
- Primary: `#1E2A4A`
- Primary hover: `#16203A`
- Link/Focus: `#2C3E66`

Text:
- Primary text: `#111111`
- Secondary text: `#666666`

Usage:
- Apply `#FAFAFA` to page background
- Use navy for primary buttons and key highlights
- Keep body text black/gray for contrast

## Apply Theme to Gate + EstimateForm

Gate screen:
- Set screen background to `#FAFAFA` (use a full-width `Container` with background color).
- Wrap the card in `.section-card`.
- Use `.page-title` for title, `.page-subtitle` for description.
- Primary button color to `#1E2A4A`.

EstimateForm:
- Set page background to `#FAFAFA`.
- Use `.section-card` for each section (Core/Features/Phase/Results).
- Apply `.result-card` to summary cards.
- Use `.button-row` for Calculate/Report buttons.
- Ensure all margins/paddings use multiples of 8.

OutSystems steps:
1) Theme -> CSS -> paste class definitions (section-card, page-title, etc.)
2) In each screen, select containers and set `Style Classes`
3) For buttons, set `Style` to Primary and override color in Theme if needed

## CSS Override (Primary Button Color)

Add to Theme CSS:

```css
.btn-primary {
  background-color: #1E2A4A;
  border-color: #1E2A4A;
}

.btn-primary:hover,
.btn-primary:focus {
  background-color: #16203A;
  border-color: #16203A;
}
```

## Report Rendering (Markdown)

Option A (Simple): Use `Text Area` to show raw Markdown.

Option B (Preferred): Use `Rich Text` widget to render HTML.

Flow:
1) Convert Markdown to HTML (client-side or server-side).
2) Bind HTML to `Rich Text`.

Notes:
- If you do not want to add conversion, show raw Markdown for MVP.
- For HTML conversion, set `/report` `output_format=html` and bind `report_html`.

## Bind report_html to Rich Text (OutSystems)

Steps:
1) Add a `Rich Text` widget in the Report section.
2) Create a screen variable `ReportHtml` (Text).
3) In `GenerateReport`, set:
   - `ReportHtml = Report.Response.report_html`
4) Bind the Rich Text `Content` property to `ReportHtml`.

Fallback:
- If `ReportHtml` is empty, display `report_markdown` in a `Text Area`.

## Common Pitfalls (OutSystems)

REST test errors:
- If REST test fails, check that the endpoint is reachable from OutSystems (use Railway if needed).
- Ensure request JSON matches schema (null vs empty list).

Structure mismatches:
- If fields are missing, re-import schema or add attributes manually.
- For `team_ratio`, ensure it's an object, not a list.

Null handling:
- If `features` / `phase2_items` / `phase3_items` are empty, send empty lists `[]` (not null) to avoid mapping issues.
- If `dept_allocation` is empty, send null or omit the field.

Type issues:
- `target_margin` should be Decimal; if user enters percent, convert before send.
- `estimated_amount` is text with currency; do not parse as number.

Report endpoint:
- If `/report` returns error, verify `GEMINI_API_KEY`.
- If `/report` returns model 404, set `GEMINI_MODEL=gemini-2.5-flash` (fallback exists but explicit setting is recommended).
- Large `estimation_result` may need to truncate or omit `input_echo` when sending to `/report`.

## Report Prompt Template (Gemini)

Use this prompt structure when calling `/report`:

System instruction (fixed):
- "You are an expert estimation consultant. Write a clear, concise Markdown report in the requested language."

User payload (suggested):
1) Language: `ja`
2) Estimation Result (JSON)
3) RAG context (optional)
4) User notes (optional)

Recommended report outline (Markdown):
- タイトル
- 概要（1-2段落）
- 主要前提（入力値の要約）
- 見積内訳（工数/費用/利益）
- リスクと注意事項
- 次のアクション

Output rules:
- Keep it under ~500-800 words.
- Use bullet points for assumptions and risks.
- Do not invent numbers; use only the provided JSON.

## Report Payload Minimization

To avoid long response times, send a trimmed object to `/report`.

Recommended payload:
```json
{
  "estimation_result": {
    "estimated_amount": "...",
    "estimated_range": "...",
    "man_days": { "development_total": 0, "fp_based": 0, "feature_based": 0 },
    "profit_analysis": {
      "sales": 0,
      "cogs": 0,
      "gross_profit": 0,
      "sga_cost": 0,
      "operating_profit": 0,
      "operating_margin": "0.0%",
      "target_margin_specified": "0.0%",
      "suggested_price_to_attain_target": 0
    },
    "input_echo": {
      "profile": "...",
      "screen_count": 0,
      "table_count": 0,
      "complexity": "...",
      "duration": "...",
      "dev_type": "...",
      "target_platform": "...",
      "features": []
    }
  },
  "rag_context": "...",
  "user_notes": "..."
}
```

Trim rules:
- Omit `input_echo.tables` and other verbose lists if not needed.
- Do not include full `bs_input` unless the report needs it.
- Keep `features` concise (labels or keys only).

## Build Trimmed Report Payload (OutSystems)

Action: `BuildReportPayload`
1) Create a new Structure `ReportEstimateLite` (local)
   - estimated_amount (Text)
   - estimated_range (Text)
   - man_days (ManDays)
   - profit_analysis (ProfitAnalysis)
   - input_echo (InputEchoLite)
2) Create `InputEchoLite` with:
   - profile (Text)
   - screen_count (Integer)
   - table_count (Integer)
   - complexity (Text)
   - duration (Text)
   - dev_type (Text)
   - target_platform (Text)
   - features (List<Text>)
3) Assign from `EstimateResult`:
   - `ReportEstimateLite.estimated_amount = EstimateResult.estimated_amount`
   - `ReportEstimateLite.estimated_range = EstimateResult.estimated_range`
   - `ReportEstimateLite.man_days = EstimateResult.man_days`
   - `ReportEstimateLite.profit_analysis = EstimateResult.profit_analysis`
   - `ReportEstimateLite.input_echo = (mapped lite fields)`
4) Build `ReportRequest`:
   - `estimation_result = ReportEstimateLite`
   - `rag_context = RagContext`
   - `user_notes = UserNotes`
   - `language = "ja"`
5) Call REST `Report` with this payload

## Logic Flow (OutSystems Actions)

Action: `CalculateEstimate`
1) `IsCalculating = True`
2) `Call REST: Calculate` with mapped inputs
3) If `Calculate` returns error -> `ShowMessage` + `IsCalculating = False` + `Return`
4) If response has `calc_json`, deserialize it to `EstimateResult` (JSON Deserialize)
5) Else assign `EstimateResult = Calculate.Response`
6) `IsCalculating = False`

Action: `GenerateReport`
1) If `EstimateResult` is empty -> `ShowMessage` and `Return`
2) `IsReporting = True`
3) Build `ReportRequest`
   - `estimation_result = EstimateResult`
   - `rag_context = RagContext` (optional)
   - `user_notes = UserNotes` (optional)
   - `language = "ja"`
4) `Call REST: Report`
5) If `Report` returns error -> `ShowMessage` + `IsReporting = False` + `Return`
6) Assign `ReportText = Report.Response.report_markdown`
7) `IsReporting = False`

UI rules:
- Disable `Generate Report` until `EstimateResult` is available.
- Show spinner when `IsCalculating` or `IsReporting` is True.

## Error Handling Rules

Validation (before REST call):
- Require `screen_count` >= 0 and `table_count` >= 0.
- Require `estimation_profile` and `department` selected.
- If `target_margin` > 1, convert to percent in backend; warn user if > 100%.

REST errors:
- Timeout: show "API timeout, please retry."
- 4xx: show "Input error, please review fields."
- 5xx: show "Server error, please retry later."

Report errors:
- If `GEMINI_API_KEY` missing, show "Report generation not configured."
- If response empty, show "Report generation failed."

Logging (minimum):
- Log request payload (without secrets) and response status.
- Capture error messages for retry support.

## Access Gate (Common Password)

Goal: Require a shared password before any screen is accessible (including direct URL access).

Implementation:
- Site Property: `AppGatePassword` (Text)
- Session variable: `GatePassed` (Boolean, default False)
- Screen: `Gate`
  - Input: Password
  - Button: Enter
  - OnClick:
    - If input == `AppGatePassword` -> `GatePassed = True` -> redirect to `EstimateForm`
    - Else -> show error message
- Guard:
  - In every screen `OnInitialize`:
    - If `GatePassed` is False -> redirect to `Gate`

UI copy (Gate screen):
- Title: `AI見積システム`
- Description: `閲覧にはパスワードが必要です`
- Label: `パスワード`
- Button: `入室する`
- Error: `パスワードが違います。`

## Sample Request/Response (for REST Test)

Request:

```json
{
  "screen_count": 12,
  "table_count": 4,
  "estimation_profile": "enterprise",
  "department": "ビジネスイノベーション事業部共通",
  "complexity": "medium",
  "duration": "normal",
  "dev_type": "new",
  "target_platform": "web_b2e",
  "features": ["auth", "admin_dashboard"],
  "phase2_items": ["basic_design"],
  "phase3_items": [],
  "target_margin": 0.2
}
```

Response (example values, current production shape):

```json
{
  "calc_json": "{ \"status\": \"success\", \"estimated_amount\": 42490998, \"estimated_range\": \"¥36,117,348 〜 ¥48,864,647\", \"profit_analysis\": { \"sales\": 42490998 } }"
}
```

`calc_json` decoded object example:

```json
{
  "status": "success",
  "estimated_amount": "¥5,432,100",
  "estimated_range": "¥4,888,890 - ¥6,518,520",
  "man_days": {
    "development_total": 34.6,
    "fp_based": 28.8,
    "feature_based": 5.8
  },
  "bs_input": {
    "department": "ビジネスイノベーション事業部共通",
    "dept_allocation": null,
    "sga_rate_applied": "75.1%",
    "indirect_yen_per_hour": 2340,
    "team_ratio": {
      "Rank3": 0.8,
      "Rank2": 0.2
    }
  },
  "input_echo": {
    "profile": "エンタープライズ型",
    "profile_description": "要件定義〜品質保証までの標準プロセスを含む（標準モデル）",
    "screen_count": 12,
    "table_count": 4,
    "tables": [],
    "complexity": "medium",
    "duration": "normal",
    "dev_type": "new",
    "target_platform": "web_b2e",
    "confidence": null,
    "target_margin": 0.2,
    "features": ["auth", "admin_dashboard"],
    "phase2_items": ["basic_design"],
    "phase3_items": []
  },
  "profit_analysis": {
    "sales": 5432100,
    "cogs": 3652000,
    "gross_profit": 1780100,
    "sga_cost": 742000,
    "operating_profit": 1038100,
    "operating_margin": "19.1%",
    "target_margin_specified": "20.0%",
    "suggested_price_to_attain_target": 5512000,
    "breakdown": {
      "sga_calculation_base": "direct_labor_cost",
      "sga_rate_on_propa_labor": "75.1%"
    }
  },
  "productivity": "1.5 MD/FP"
}
```
