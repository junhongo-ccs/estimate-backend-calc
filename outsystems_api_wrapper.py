# -*- coding: utf-8 -*-
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
import os
import sys
import urllib.request
import urllib.error
import html
from pricing_simulator_input import (
    DEFAULT_CURRENCY,
    DEFAULT_PROJECT_NAME,
    attach_pricing_simulator_input,
    build_pricing_simulator_input,
)

# dify_assets/code/estimate_logic.py があるディレクトリをパスに追加
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "dify_assets", "code"))
from estimate_logic import main as dify_main

app = FastAPI(title="AI Estimation API for OutSystems")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
DEFAULT_TEST_REQUEST = {
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
    "target_margin": 0.2,
}


def _utf8_json_response(payload: Any) -> JSONResponse:
    return JSONResponse(
        content=payload,
        media_type="application/json; charset=utf-8",
    )


def _normalize_model_name(model: str) -> str:
    value = (model or "").strip()
    if value.startswith("models/"):
        value = value[len("models/") :]
    return value


def _build_gemini_endpoint(model: str) -> str:
    normalized = _normalize_model_name(model)
    return f"https://generativelanguage.googleapis.com/v1beta/models/{normalized}:generateContent"


def _parse_api_error_detail(detail: str) -> str:
    try:
        data = json.loads(detail)
        return data.get("error", {}).get("message", detail)
    except Exception:
        return detail

class EstimationRequest(BaseModel):
    screen_count: int = 0
    table_count: int = 0
    estimation_profile: Optional[str] = None
    profile: Optional[str] = None
    department: Optional[str] = None
    complexity: Optional[str] = None
    duration: Optional[str] = None
    dev_type: Optional[str] = None
    target_platform: Optional[str] = None
    confidence: Optional[str] = None
    features: Optional[List[str]] = None
    phase2_items: Optional[List[str]] = None
    phase3_items: Optional[List[str]] = None
    tables: Optional[List[str]] = None
    dept_allocation: Optional[List[Dict[str, Any]]] = None
    team_ratio: Optional[Dict[str, float]] = None
    target_margin: Optional[float] = None


class SimpleEstimationRequest(BaseModel):
    screen_count: int = DEFAULT_TEST_REQUEST["screen_count"]
    table_count: int = DEFAULT_TEST_REQUEST["table_count"]
    department: str = DEFAULT_TEST_REQUEST["department"]


class ReportRequest(BaseModel):
    estimation_result: Dict[str, Any]
    rag_context: Optional[str] = None
    user_notes: Optional[str] = None
    language: Optional[str] = "ja"
    output_format: Optional[str] = "markdown"


class PricingSimulatorRequest(EstimationRequest):
    project_name: Optional[str] = None
    currency: Optional[str] = DEFAULT_CURRENCY


def _unwrap_dify_result(result: Any) -> Any:
    while isinstance(result, dict) and len(result) == 1:
        key = list(result.keys())[0]
        if key in ["result", "calc_json"]:
            val = result[key]
            if isinstance(val, str):
                try:
                    result = json.loads(val)
                except json.JSONDecodeError:
                    break
            else:
                result = val
        else:
            break
    return result


def generate_report_with_gemini(request: ReportRequest) -> str:
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is not set")

    system_instruction = (
        "You are an expert estimation consultant. "
        "Write a clear, concise Markdown report in the requested language."
    )
    parts = [
        {"text": system_instruction},
        {"text": f"Language: {request.language or 'ja'}"},
        {"text": "Estimation Result (JSON):"},
        {"text": json.dumps(request.estimation_result, ensure_ascii=False, indent=2)},
    ]
    if request.rag_context:
        parts.append({"text": "Reference Knowledge (RAG):"})
        parts.append({"text": request.rag_context})
    if request.user_notes:
        parts.append({"text": "User Notes:"})
        parts.append({"text": request.user_notes})

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": parts,
            }
        ]
    }

    data = json.dumps(payload).encode("utf-8")

    primary_model = _normalize_model_name(GEMINI_MODEL)
    fallback_models = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]
    model_candidates = [primary_model] + [m for m in fallback_models if m != primary_model]
    last_error = None

    for model in model_candidates:
        req = urllib.request.Request(
            _build_gemini_endpoint(model) + f"?key={GEMINI_API_KEY}",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                body = json.loads(resp.read().decode("utf-8"))
                break
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8")
            message = _parse_api_error_detail(detail)
            # モデル未対応時のみ次候補へフォールバック
            if e.code == 404:
                last_error = f"{model}: {message}"
                continue
            raise RuntimeError(f"Gemini API error: {message}") from e
        except Exception as e:
            raise RuntimeError(f"Gemini API request failed: {str(e)}") from e
    else:
        raise RuntimeError(
            "No available Gemini model for generateContent. "
            f"Tried: {', '.join(model_candidates)}. Last error: {last_error or 'unknown'}"
        )

    candidates = body.get("candidates", [])
    if not candidates:
        raise RuntimeError("Gemini API returned no candidates")
    content = candidates[0].get("content", {})
    parts = content.get("parts", [])
    if not parts:
        raise RuntimeError("Gemini API returned empty content")
    return parts[0].get("text", "").strip()

@app.post("/calculate")
async def calculate(request: EstimationRequest):
    try:
        # Pydanticモデルを辞書に変換してDify互換ロジックに渡す
        req_data = request.dict()
        if not req_data.get("estimation_profile") and req_data.get("profile"):
            req_data["estimation_profile"] = req_data["profile"]
        
        result = dify_main(**req_data)
        result = attach_pricing_simulator_input(
            _unwrap_dify_result(result),
            target_margin=req_data.get("target_margin"),
        )
        return _utf8_json_response(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return _utf8_json_response({"status": "ok"})


@app.get("/calculate_test")
async def calculate_test():
    try:
        result = dify_main(**DEFAULT_TEST_REQUEST)
        result = attach_pricing_simulator_input(
            _unwrap_dify_result(result),
            target_margin=DEFAULT_TEST_REQUEST.get("target_margin"),
        )
        return _utf8_json_response(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/calculate_simple")
async def calculate_simple(request: SimpleEstimationRequest):
    try:
        req_data = dict(DEFAULT_TEST_REQUEST)
        req_data["screen_count"] = request.screen_count
        req_data["table_count"] = request.table_count
        req_data["department"] = request.department

        result = dify_main(**req_data)
        result = attach_pricing_simulator_input(
            _unwrap_dify_result(result),
            target_margin=req_data.get("target_margin"),
        )
        return _utf8_json_response(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/calculate_simple_get")
async def calculate_simple_get(
    screen_count: int = Query(DEFAULT_TEST_REQUEST["screen_count"]),
    table_count: int = Query(DEFAULT_TEST_REQUEST["table_count"]),
    department: str = Query(DEFAULT_TEST_REQUEST["department"]),
):
    try:
        req_data = dict(DEFAULT_TEST_REQUEST)
        req_data["screen_count"] = screen_count
        req_data["table_count"] = table_count
        req_data["department"] = department

        result = dify_main(**req_data)
        result = attach_pricing_simulator_input(
            _unwrap_dify_result(result),
            target_margin=req_data.get("target_margin"),
        )
        return _utf8_json_response(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/pricing_simulator_input")
async def pricing_simulator_input(request: PricingSimulatorRequest):
    try:
        req_data = request.dict()
        project_name = req_data.pop("project_name", None)
        currency = req_data.pop("currency", DEFAULT_CURRENCY)
        if not req_data.get("estimation_profile") and req_data.get("profile"):
            req_data["estimation_profile"] = req_data["profile"]

        result = attach_pricing_simulator_input(
            _unwrap_dify_result(dify_main(**req_data)),
            project_name=project_name,
            target_margin=req_data.get("target_margin"),
            currency=currency,
        )
        return _utf8_json_response({
            "status": "success",
            "pricing_simulator_input": result["pricing_simulator_input"],
            "estimation_result": result,
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/pricing_simulator_input_simple_get")
async def pricing_simulator_input_simple_get(
    screen_count: int = Query(DEFAULT_TEST_REQUEST["screen_count"]),
    table_count: int = Query(DEFAULT_TEST_REQUEST["table_count"]),
    department: str = Query(DEFAULT_TEST_REQUEST["department"]),
    project_name: str = Query(DEFAULT_PROJECT_NAME),
    target_margin: float = Query(DEFAULT_TEST_REQUEST["target_margin"]),
    currency: str = Query(DEFAULT_CURRENCY),
):
    try:
        req_data = dict(DEFAULT_TEST_REQUEST)
        req_data["screen_count"] = screen_count
        req_data["table_count"] = table_count
        req_data["department"] = department
        req_data["target_margin"] = target_margin

        result = attach_pricing_simulator_input(
            _unwrap_dify_result(dify_main(**req_data)),
            project_name=project_name,
            target_margin=target_margin,
            currency=currency,
        )
        return _utf8_json_response({
            "status": "success",
            "pricing_simulator_input": result["pricing_simulator_input"],
            "estimation_result": result,
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/report")
async def report(request: ReportRequest):
    try:
        report_text = generate_report_with_gemini(request)
        response = {"status": "success", "report_markdown": report_text}
        if (request.output_format or "").lower() == "html":
            try:
                import markdown  # type: ignore
                response["report_html"] = markdown.markdown(report_text)
            except Exception:
                response["report_html"] = f"<pre>{html.escape(report_text)}</pre>"
        return _utf8_json_response(response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # OutSystemsサーバーからアクセス可能なホスト・ポートで起動
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
