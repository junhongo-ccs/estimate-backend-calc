from typing import Any, Dict, Optional


DEFAULT_PROJECT_NAME = "案件A"
DEFAULT_CURRENCY = "JPY"


def parse_target_margin_value(value: Any) -> Optional[float]:
    if isinstance(value, str) and value.strip():
        try:
            num = float(value.replace("%", "").strip())
            return num / 100.0 if num > 1.0 else num
        except Exception:
            return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


def build_pricing_simulator_input(
    estimation_result: Dict[str, Any],
    project_name: Optional[str] = None,
    target_margin: Any = None,
    currency: Optional[str] = None,
) -> Dict[str, Any]:
    profit = estimation_result.get("profit_analysis") or {}
    sales = profit.get("sales")
    cogs = profit.get("cogs")
    total_sga_cost = profit.get("total_sga_cost")

    if sales is None or cogs is None or total_sga_cost is None:
        raise ValueError("profit_analysis.sales, cogs, total_sga_cost are required")

    normalized_target_margin = parse_target_margin_value(target_margin)
    if normalized_target_margin is None:
        input_echo = estimation_result.get("input_echo") or {}
        normalized_target_margin = parse_target_margin_value(input_echo.get("target_margin"))

    payload = {
        "project_name": (project_name or DEFAULT_PROJECT_NAME).strip() or DEFAULT_PROJECT_NAME,
        "cost": int(cogs) + int(total_sga_cost),
        "current_sales": int(sales),
        "currency": (currency or DEFAULT_CURRENCY).strip() or DEFAULT_CURRENCY,
    }
    if normalized_target_margin is not None:
        payload["target_margin"] = normalized_target_margin
    return payload


def attach_pricing_simulator_input(
    estimation_result: Any,
    project_name: Optional[str] = None,
    target_margin: Any = None,
    currency: Optional[str] = None,
) -> Any:
    if not isinstance(estimation_result, dict):
        return estimation_result
    if estimation_result.get("status") != "success":
        return estimation_result
    if "pricing_simulator_input" in estimation_result:
        return estimation_result

    enriched = dict(estimation_result)
    enriched["pricing_simulator_input"] = build_pricing_simulator_input(
        enriched,
        project_name=project_name,
        target_margin=target_margin,
        currency=currency,
    )
    return enriched
