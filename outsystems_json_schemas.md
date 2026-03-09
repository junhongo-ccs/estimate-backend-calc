# OutSystems JSON Schemas (Draft-07)

Use these schemas to define the Request/Response Structures in OutSystems.

## Request Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "EstimationRequest",
  "type": "object",
  "properties": {
    "screen_count": { "type": "integer", "minimum": 0 },
    "table_count": { "type": "integer", "minimum": 0 },
    "estimation_profile": { "type": ["string", "null"] },
    "profile": { "type": ["string", "null"] },
    "department": { "type": ["string", "null"] },
    "complexity": { "type": ["string", "null"] },
    "duration": { "type": ["string", "null"] },
    "dev_type": { "type": ["string", "null"] },
    "target_platform": { "type": ["string", "null"] },
    "confidence": { "type": ["string", "null"] },
    "features": {
      "type": ["array", "null"],
      "items": { "type": "string" }
    },
    "phase2_items": {
      "type": ["array", "null"],
      "items": { "type": "string" }
    },
    "phase3_items": {
      "type": ["array", "null"],
      "items": { "type": "string" }
    },
    "tables": {
      "type": ["array", "null"],
      "items": { "type": "string" }
    },
    "dept_allocation": {
      "type": ["array", "null"],
      "items": {
        "type": "object",
        "properties": {
          "dept": { "type": "string" },
          "share": { "type": "number" }
        },
        "required": ["dept", "share"]
      }
    },
    "team_ratio": {
      "type": ["object", "null"],
      "additionalProperties": { "type": "number" }
    },
    "target_margin": { "type": ["number", "null"] }
  },
  "additionalProperties": false
}
```

## Response Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "EstimationResponse",
  "type": "object",
  "properties": {
    "status": { "type": "string" },
    "estimated_amount": { "type": "string" },
    "estimated_range": { "type": "string" },
    "man_days": {
      "type": "object",
      "properties": {
        "development_total": { "type": "number" },
        "fp_based": { "type": "number" },
        "feature_based": { "type": "number" }
      },
      "required": ["development_total", "fp_based", "feature_based"]
    },
    "bs_input": {
      "type": "object",
      "properties": {
        "department": { "type": "string" },
        "dept_allocation": {
          "type": ["array", "null"],
          "items": {
            "type": "object",
            "properties": {
              "dept": { "type": "string" },
              "share": { "type": "number" }
            },
            "required": ["dept", "share"]
          }
        },
        "sga_rate_applied": { "type": "string" },
        "indirect_yen_per_hour": { "type": "number" },
        "team_ratio": {
          "type": "object",
          "additionalProperties": { "type": "number" }
        }
      },
      "required": ["department", "sga_rate_applied", "indirect_yen_per_hour", "team_ratio"]
    },
    "input_echo": {
      "type": "object",
      "properties": {
        "profile": { "type": "string" },
        "profile_description": { "type": "string" },
        "screen_count": { "type": "integer" },
        "table_count": { "type": "integer" },
        "tables": {
          "type": "array",
          "items": { "type": "string" }
        },
        "complexity": { "type": "string" },
        "duration": { "type": "string" },
        "dev_type": { "type": "string" },
        "target_platform": { "type": "string" },
        "confidence": { "type": ["string", "null"] },
        "target_margin": { "type": ["number", "null"] },
        "features": {
          "type": "array",
          "items": { "type": "string" }
        },
        "phase2_items": {
          "type": "array",
          "items": { "type": "string" }
        },
        "phase3_items": {
          "type": "array",
          "items": { "type": "string" }
        }
      }
    },
    "profit_analysis": {
      "type": "object",
      "properties": {
        "sales": { "type": "number" },
        "cogs": { "type": "number" },
        "gross_profit": { "type": "number" },
        "sga_cost": { "type": "number" },
        "operating_profit": { "type": "number" },
        "operating_margin": { "type": "string" },
        "target_margin_specified": { "type": ["string", "null"] },
        "suggested_price_to_attain_target": { "type": "number" },
        "breakdown": {
          "type": "object",
          "properties": {
            "sga_calculation_base": { "type": "string" },
            "sga_rate_on_propa_labor": { "type": "string" }
          }
        }
      },
      "required": ["sales", "cogs", "gross_profit", "sga_cost", "operating_profit", "operating_margin"]
    },
    "productivity": { "type": "string" }
  },
  "required": ["status", "estimated_amount", "man_days", "profit_analysis"]
}
```

## Report Request Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "ReportRequest",
  "type": "object",
  "properties": {
    "estimation_result": { "type": "object" },
    "rag_context": { "type": ["string", "null"] },
    "user_notes": { "type": ["string", "null"] },
    "language": { "type": ["string", "null"] },
    "output_format": { "type": ["string", "null"] }
  },
  "required": ["estimation_result"],
  "additionalProperties": false
}
```

## Report Response Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "ReportResponse",
  "type": "object",
  "properties": {
    "status": { "type": "string" },
    "report_markdown": { "type": "string" },
    "report_html": { "type": ["string", "null"] }
  },
  "required": ["status", "report_markdown"]
}
```
