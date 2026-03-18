# Day 1 ODC Setup Checklist

Date: 2026-03-10

Goal:
- ODC Studio から Railway の `/calculate` を呼び出し、`calc_json` を OutSystems Structure に変換できる状態にする。

## Target Endpoint
- `POST https://estimate-backend-calc-production.up.railway.app/calculate`

## Steps
1. Create a new Reactive Web App in ODC Studio.
2. Add REST integration for `/calculate`.
3. Use the sample request below in the REST Test tab.
4. Create raw response Structure:
   - `CalculateRawResponse`
   - `calc_json` (Text)
5. Create final response Structure:
   - `EstimateResponse`
   - Use `/Users/hongoujun/Documents/GitHub/estimate-backend-calc/outsystems_json_schemas.md`
6. Create a Client Action:
   - Input: `RawResponse` (`CalculateRawResponse`)
   - Output: `EstimateResult` (`EstimateResponse`)
   - Logic: deserialize `RawResponse.calc_json` into `EstimateResult`
7. Bind `EstimateResult.estimated_amount` to a temporary text widget and confirm it displays.

## Sample Request
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

## Expected Current Production Response
```json
{
  "calc_json": "{ ... }"
}
```

## Done When
- REST Test returns 200 OK.
- `calc_json` can be parsed.
- `estimated_amount` is visible in the app.
