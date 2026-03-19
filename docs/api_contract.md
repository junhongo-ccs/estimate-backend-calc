# API Contract

## Host

Production host currently used by ODC:

- `https://estimate-backend-calc-production.up.railway.app`

## Endpoints

### 1. `GET /calculate_test`

Purpose:
- fixed test endpoint for initial ODC connectivity

Request:
- no input

Response shape:

```json
{
  "status": "success",
  "estimated_amount": 31921098,
  "total_man_days": 453.0,
  "estimated_range": "¥27,132,933 〜 ¥36,709,262",
  "profile": "SIer標準（全工程網羅）",
  "profile_description": "要件定義〜品質保証までの標準SIプロセス（約13.3 FP/人月）を包含。",
  "profit_analysis": {
    "sales": 31921098,
    "cogs": 29019180,
    "operating_profit": -12522886,
    "operating_margin": "-39.2%",
    "total_sga_cost": 15424804,
    "sga_rate_applied": "75.1%",
    "suggested_price_to_attain_target": 55554980
  },
  "input_echo": {
    "profile": "SIer標準（全工程網羅）",
    "department": "ビジネスイノベーション事業部共通",
    "screen_count": 12,
    "table_count": 4,
    "features": [
      "auth",
      "admin_dashboard"
    ],
    "complexity": "medium",
    "target_margin": "20.0%"
  },
  "details": {
    "direct_labor": 20539020,
    "indirect_cost": 8480160,
    "total_fp": 300,
    "fp_days": 450.0,
    "feature_days": 3.0
  }
}
```

### 2. `GET /calculate_simple_get`

Purpose:
- current preferred endpoint for ODC dynamic input PoC
- avoids ODC POST request-object binding issues

Request query params:

- `department` (string, formal department name)
- `screen_count` (integer)
- `table_count` (integer)

Example:

```text
/calculate_simple_get?screen_count=12&table_count=4&department=ビジネスイノベーション事業部共通
```

Response shape:
- same as `GET /calculate_test`

Known verification:

- `screen_count=12`, `table_count=4`
  - `estimated_amount=31921098`
  - `total_man_days=453.0`
  - current ODC screen is already using this case

- `screen_count=18`, `table_count=6`
  - `estimated_amount=47775948`
  - `total_man_days=678.0`

### 3. `POST /calculate_simple`

Purpose:
- minimal POST variant
- currently not preferred for ODC because GET query binding is easier

Request body:

```json
{
  "department": "ビジネスイノベーション事業部共通",
  "screen_count": 12,
  "table_count": 4
}
```

Response shape:
- same as `GET /calculate_test`

Current ODC status:
- consumed successfully as a REST method
- not used in the active screen flow
- kept only as a fallback/reference route

### 4. `POST /calculate`

Purpose:
- richer route closer to production direction

Current reality:
- not the preferred ODC route yet
- POST request typing in ODC caused repeated friction
- defer until the UI flow is stable

### 5. `POST /report`

Purpose:
- LLM-generated natural-language reporting

Status:
- implemented in backend
- not the current ODC focus

## Backend Notes

Implementation file:

- `/Users/hongoujun/Documents/GitHub/estimate-backend-calc/outsystems_api_wrapper.py`

Important helper:

- UTF-8 explicit response handling is already implemented
- this fixed previous mojibake on ODC display

## Active ODC Route

The active route for the current ODC screen is:

- `GET /calculate_simple_get`

The ODC action currently passes ODC client variables:

- `Client.Department`
- `Client.ScreenCount`
- `Client.TableCount`

Current ODC screen state:

- `EstimateForm` contains a working department selector plus two numeric inputs
- `Department` is a working dropdown backed by `DepartmentMaster`
- `Department` is bound to `Client.Department`
- `Screen Count` is bound to `Client.ScreenCount`
- `Table Count` is bound to `Client.TableCount`
- `DoTestCalculate` passes those values into `GetCalculateSimpleGet`
- `Client.Department` is `Text`
- `Dropdown1.List = GetDepartmentMasters.List`
- `Dropdown1.Options Text = DepartmentMaster.DisplayName`
- `Dropdown1.Options Value = DepartmentMaster.DisplayName`

Verified live browser case:

- `department=ＣＳ第１システム開発部`
- `screen_count=4`
- `table_count=7`
- result changes from the previous default-department case

This should remain the first route resumed in any follow-up session.
