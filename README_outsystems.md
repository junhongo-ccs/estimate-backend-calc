# OutSystems Integration Guide

This guide explains how to run the Estimation API and connect it to OutSystems.

## 1. Environment Setup

Ensure you have Python 3.8+ installed. You will need to install the following dependencies for the API wrapper:

```bash
pip install fastapi uvicorn pydantic pyyaml
```

## 2. Running the API

Run the wrapper script from the root of the `estimate-backend-calc` repository:

```bash
python3 outsystems_api_wrapper.py
```

- **Env**: set `GEMINI_API_KEY` for the `/report` endpoint (optional).
- **Host**: `0.0.0.0` (Accepts connections from other machines)
- **Port**: `8000`
- **Endpoint**: `http://<your-server-ip>:8000/calculate`
- **Report Endpoint**: `http://<your-server-ip>:8000/report`

---

## 3. Request/Response Overview

### Request (POST /calculate)
Key fields used by the calculation engine:

- `screen_count` (int)
- `table_count` (int)
- `estimation_profile` (string, preferred) or `profile` (string, legacy)
- `department` (string, BS部門名)
- `complexity` (low|medium|high|very_high)
- `duration` (long|normal|short)
- `dev_type` (new|porting)
- `target_platform` (web_b2e|web_b2c|mobile|all)
- `confidence` (low|high)
- `features` (string[])
- `phase2_items` (string[])
- `phase3_items` (string[])
- `tables` (string[])
- `dept_allocation` (object[]: `{ "dept": "...", "share": 0.6 }`)
- `team_ratio` (object: `{ "Rank3": 0.8, "Rank2": 0.2 }`)
- `target_margin` (float, 0-1 or percent)

Example:

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

### Response
The API returns a JSON object with `estimated_amount`, `man_days`, `profit_analysis`, and a full `input_echo` block.

### Report Generation (Optional)
To generate a natural language report, call `POST /report` with:

- `estimation_result` (object): the output of `/calculate`
- `rag_context` (string, optional)
- `user_notes` (string, optional)
- `language` (string, default `ja`)
- `output_format` (string, `markdown` or `html`, default `markdown`)

The response includes `report_markdown` and optional `report_html` when `output_format=html`.

If you want HTML rendering, install:
```bash
pip install markdown
```

### JSON Schemas
See `outsystems_json_schemas.md` for the Request/Response schemas (including `/report`).

---

## 4. OutSystems Integration Steps

1.  **Open Service Studio**: Open your OutSystems application.
2.  **Add REST Integration**:
    *   Navigate to the **Logic** tab -> **Integrations** -> **REST**.
    *   Right-click and select **Consume REST API** -> **Add Single Method**.
3.  **Configure API**:
    *   **Method**: `POST`
    *   **URL**: `http://<your-server-ip>:8000/calculate`
4.  **Define Data Structures**:
    *   Use the example request and response fields in this guide to create the Request and Response Structures.
5.  **Test the Connection**:
    *   Use the **Test** tab in the REST Method configuration to verify the connection to your local Python server.

---

## 5. Maintenance

The logic used by this API is located in:
`dify_assets/code/estimate_logic.py`

Any changes to the business rules (rates, profiles, etc.) should be made in that file, and the API will reflect them immediately upon restart.

## 6. OutSystems Integration (Report Endpoint)

Repeat the REST integration steps for `/report`.

1.  **Add REST Integration**:
    *   **Logic** -> **Integrations** -> **REST** -> **Consume REST API** -> **Add Single Method**
2.  **Configure API**:
    *   **Method**: `POST`
    *   **URL**: `http://<your-server-ip>:8000/report`
3.  **Define Structures**:
    *   Use `ReportRequest` and `ReportResponse` schemas in `outsystems_json_schemas.md`.
4.  **Test**:
    *   Send the `/calculate` response as `estimation_result`.
