# -*- coding: utf-8 -*-
import json
from typing import List, Dict, Any

# =========================================================
# CONFIGURATION & CONSTANTS
# =========================================================
CONFIG = {
    "config_version": "2026-02-CCS-Standard-v2",
    "daily_rates": {
        "sier_internal": 100000,
        "outsource": 80000
    },
    "estimation_profiles": {
        "poc": {
            "label": "PoC/開発重視型",
            "productivity_factor": 0.075,
            "description": "【注意】SI案件の全工程（要件定義〜QA）には非適用。製造/実制作フェーズのみの参考値。"
        },
        "enterprise": {
            "label": "エンタープライズ型",
            "productivity_factor": 1.5,
            "description": "要件定義〜品質保証までの標準プロセスを含む（標準モデル）"
        },
        "mission_critical": {
            "label": "高信頼性型",
            "productivity_factor": 2.0,
            "description": "金融/基幹等の極めて高い品質基準"
        }
    },
    "fp_simplified": {
        "screen_weight": 20,
        "table_weight": 15,
        "default_productivity": 1.5
    },
    "difficulty_multipliers": {"low": 0.8, "medium": 1.0, "high": 1.5, "very_high": 2.0},
    "duration_multipliers": {"long": 0.9, "normal": 1.0, "short": 1.2},
    "dev_type_multipliers": {
        "new": {"design": 1.0, "dev": 1.0},
        "porting": {"design": 0.5, "dev": 0.8}
    },
    "platform_multipliers": {"web_b2e": 1.0, "web_b2c": 1.2, "mobile": 1.5, "all": 1.8},
    "buffer_multiplier": 1.1,
    "profit_config": {
        "rank_costs": {
            "Rank4": 1098000,
            "Rank3": 944000,
            "Rank2": 758000,
            "Rank1": 541000,
        },
        "standard_team_ratio": {"Rank3": 0.8, "Rank2": 0.2}
    }
}

BS_ORG_CONFIG: Dict[str, Dict[str, float]] = {
    "ビジ・企画営業部": {"indirect_per_hour": 2340, "sga_on_propa_labor_rate": 0.751},
    "ビジ・システム開発部": {"indirect_per_hour": 2340, "sga_on_propa_labor_rate": 0.751},
    "ビジネスイノベーション事業部共通": {"indirect_per_hour": 2340, "sga_on_propa_labor_rate": 0.751},
    "ＳＦ＆Ｍ営業部": {"indirect_per_hour": 2030, "sga_on_propa_labor_rate": 0.741},
    "ＳＦ＆Ｍ第１システム開発部": {"indirect_per_hour": 2030, "sga_on_propa_labor_rate": 0.741},
    "ＳＦ＆Ｍ第２システム開発部": {"indirect_per_hour": 2030, "sga_on_propa_labor_rate": 0.741},
    "ＳＦ＆Ｍ事業部（共通）": {"indirect_per_hour": 2030, "sga_on_propa_labor_rate": 0.741},
    "ＣＳ営業部": {"indirect_per_hour": 1940, "sga_on_propa_labor_rate": 0.787},
    "ＣＳ第１システム開発部": {"indirect_per_hour": 1940, "sga_on_propa_labor_rate": 0.787},
    "ＣＳ第２システム開発部": {"indirect_per_hour": 1940, "sga_on_propa_labor_rate": 0.787},
    "ＣＳシステム事業部（共通）": {"indirect_per_hour": 1940, "sga_on_propa_labor_rate": 0.787},
    "ＤＴ営業部": {"indirect_per_hour": 2320, "sga_on_propa_labor_rate": 0.859},
    "ＤＴ第１開発部": {"indirect_per_hour": 2320, "sga_on_propa_labor_rate": 0.859},
    "ＤＴ第２開発部": {"indirect_per_hour": 2320, "sga_on_propa_labor_rate": 0.859},
    "ＤＴ事業部（共通）": {"indirect_per_hour": 2320, "sga_on_propa_labor_rate": 0.859},
    "社会・科学システム営業部": {"indirect_per_hour": 2220, "sga_on_propa_labor_rate": 0.886},
    "データサイエンスシステム部": {"indirect_per_hour": 2220, "sga_on_propa_labor_rate": 0.886},
    "社会・科学システム事業部（共通）": {"indirect_per_hour": 2220, "sga_on_propa_labor_rate": 0.886},
    "ソリューションビジネス推進室": {"indirect_per_hour": 3570, "sga_on_propa_labor_rate": 1.415},
}

DEFAULT_BS_DEPT = "ビジネスイノベーション事業部共通"

FEATURE_MAN_DAYS = {
    "auth": 3.0,
    "payment": 5.0,
    "search_basic": 2.0,
    "search_advanced": 4.0,
    "push_notification": 2.0,
    "sns_integration": 3.0,
    "admin_dashboard": 5.0,
    "api_external": 4.0,
    "offline_mode": 6.0,
    "multi_language": 3.0,
    "search": 2.0,
    "admin": 5.0,
}

FEATURE_LABEL_MAP = {
    "認証・認可 (Auth/SSO)": "auth",
    "決済基盤連携 (Payment)": "payment",
    "検索・フィルタリング (Basic)": "search_basic",
    "高度な検索 (AI/ベクトル)": "search_advanced",
    "プッシュ通知": "push_notification",
    "SNS連携・シェア": "sns_integration",
    "管理画面 (Admin)": "admin_dashboard",
    "外部API連携": "api_external",
    "オフライン対応": "offline_mode",
    "多言語対応 (i18n)": "multi_language",
    # Dify UI aliases
    "ユーザー認証": "auth",
    "認証": "auth",
    "決済機能": "payment",
    "決済": "payment",
    "CRUD操作": "admin_dashboard",
    "管理ダッシュボード": "admin_dashboard",
}

PHASE2_ITEMS = {
    "basic_design": 1000000,
    "detail_design": 1500000,
    "infra_design": 800000,
    "security_review": 500000,
    "standardization": 1200000,
}

PHASE2_LABEL_MAP = {
    "基本設計書作成": "basic_design",
    "詳細設計書作成": "detail_design",
    "インフラ・クラウド設計": "infra_design",
    "セキュリティ審査・対策案": "security_review",
    "開発標準化・共通部設計": "standardization",
    # Dify UI aliases
    "基本設計": "basic_design",
    "詳細設計": "detail_design",
    "IA設計": "basic_design",
    "WF作成": "detail_design",
    "Figma化": "detail_design",
}

PHASE3_ITEMS = {
    # Values are based on 33_design_cost_standards.md.
    # unit = "per_screen" uses screen_count, otherwise fixed by mandays * outsource daily rate.
    "ui_design": {"unit": "per_screen", "mandays": 0.375},
    "design_system": {"unit": "fixed", "mandays": 1.875},
    "prototype": {"unit": "fixed", "mandays": 2.0},
    "logo_branding": {"unit": "fixed", "mandays": 8.125},
}

PHASE3_LABEL_MAP = {
    "企業/プロダクトロゴ制作": "logo_branding",
    "ロゴ・ブランディング": "logo_branding",
    "ブランドガイドライン策定": "design_system",
    "高精度UIプロトタイプ": "prototype",
    "プロトタイプ作成": "prototype",
    "UIデザイン": "ui_design",
    "デザインガイドライン": "design_system",
    "デザインシステム": "design_system",
    "ブランドガイドライン": "design_system",
    # Dify UI aliases
    "UIプロトタイプ": "prototype",
}


def resolve_keys(input_list, label_map, item_dict):
    if not isinstance(input_list, list):
        return []
    resolved = []
    for x in input_list:
        if not x:
            continue
        if x in label_map:
            resolved.append(label_map[x])
        elif x in item_dict:
            resolved.append(x)
    return list(dict.fromkeys(resolved))


def parse_list_from_text(val):
    items = []
    if isinstance(val, str):
        for line in val.replace("\r", "").split("\n"):
            items.extend([x.strip() for x in line.split(",") if x.strip()])
    elif isinstance(val, list):
        items = val

    noise_prefixes = ["説明:例）", "説明:", "例）", "例:"]
    cleaned = []
    for x in items:
        if x in ["なし", "未定", "不明", "N/A", "-"]:
            continue
        if any(x.startswith(prefix) for prefix in noise_prefixes):
            continue
        cleaned.append(x)
    return cleaned


def parse_int(val, default=None):
    if isinstance(val, (int, float)):
        return int(val)
    if isinstance(val, str) and val.strip():
        try:
            return int(val)
        except Exception:
            return default
    return default


def parse_target_margin(val):
    if isinstance(val, (int, float)):
        return float(val)
    if isinstance(val, str) and val.strip():
        try:
            v = val.replace("%", "").strip()
            num = float(v)
            return num / 100.0 if num > 1.0 else num
        except Exception:
            return None
    return None


def parse_team_ratio(text):
    default = {"Rank3": 0.8, "Rank2": 0.2}
    if isinstance(text, dict):
        res = {}
        for k, v in text.items():
            try:
                if k in CONFIG["profit_config"]["rank_costs"]:
                    res[k] = float(v)
            except Exception:
                pass
        total = sum(res.values())
        if total > 0:
            return {k: v / total for k, v in res.items()}
        return default

    if not isinstance(text, str) or not text.strip():
        return default

    res = {}
    for part in text.split(","):
        if ":" in part:
            k, v = part.split(":", 1)
            k = k.strip()
            try:
                s = float(v.strip())
                if s >= 0 and k in CONFIG["profit_config"]["rank_costs"]:
                    res[k] = s
            except Exception:
                pass
    total = sum(res.values())
    if total > 0:
        return {k: v / total for k, v in res.items()}
    return default


def parse_dept_allocation(text):
    if isinstance(text, list):
        items = []
        for x in text:
            if isinstance(x, dict):
                dept = x.get("dept")
                try:
                    share = float(x.get("share", 0))
                except Exception:
                    share = 0
                if dept in BS_ORG_CONFIG and share > 0:
                    items.append({"dept": dept, "share": share})
        total = sum(i["share"] for i in items)
        if total > 0:
            for i in items:
                i["share"] = i["share"] / total
        return items

    items = []
    if isinstance(text, str) and text.strip():
        for line in text.splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                k = k.strip()
                try:
                    s = float(v.strip())
                    if k in BS_ORG_CONFIG and s > 0:
                        items.append({"dept": k, "share": s})
                except Exception:
                    pass
    total = sum(i["share"] for i in items)
    if total > 0:
        for i in items:
            i["share"] = i["share"] / total
    return items


def resolve_bs_org_rates(primary_dept: str, allocations: List[Dict[str, Any]] | None):
    if not primary_dept or primary_dept not in BS_ORG_CONFIG:
        primary_dept = DEFAULT_BS_DEPT
    if not allocations:
        cfg = BS_ORG_CONFIG[primary_dept]
        return (cfg["indirect_per_hour"], cfg["sga_on_propa_labor_rate"])

    total = sum(max(0.0, float(a.get("share", 0.0))) for a in allocations)
    if total <= 0:
        cfg = BS_ORG_CONFIG[primary_dept]
        return (cfg["indirect_per_hour"], cfg["sga_on_propa_labor_rate"])

    ipt = 0.0
    sga_rate = 0.0
    for a in allocations:
        dept = a.get("dept")
        share = max(0.0, float(a.get("share", 0.0))) / total
        if dept in BS_ORG_CONFIG and share > 0:
            cfg = BS_ORG_CONFIG[dept]
            ipt += cfg["indirect_per_hour"] * share
            sga_rate += cfg["sga_on_propa_labor_rate"] * share
    return (int(round(ipt)), sga_rate)


def compute_direct_labor_cost(total_man_days: float, team_ratio: Dict[str, float], rank_costs: Dict[str, int]) -> int:
    man_months = total_man_days / 20.0
    avg_monthly_cost = sum(rank_costs.get(r, 0) * w for r, w in team_ratio.items())
    return int(man_months * avg_monthly_cost)


def compute_indirect_cost(total_man_days: float, indirect_yen_per_hour: float) -> int:
    hours = total_man_days * 8.0
    return int(hours * indirect_yen_per_hour)


def compute_phase3_outsource_cost(selected_phase3, screen_count: int) -> int:
    outsource_daily_rate = CONFIG["daily_rates"]["outsource"]
    total = 0
    for item_key in selected_phase3:
        item = PHASE3_ITEMS.get(item_key)
        if not item:
            continue
        if item["unit"] == "per_screen":
            total += int(round(screen_count * item["mandays"] * outsource_daily_rate))
        else:
            total += int(round(item["mandays"] * outsource_daily_rate))
    return total


def calculate_profitability_ccs(
    total_price: int,
    cogs: int,
    direct_labor_cost: int,
    sga_rate_on_labor: float,
    target_margin_input: float | None,
):
    total_sga = int(direct_labor_cost * sga_rate_on_labor)
    gross_profit = total_price - cogs
    operating_profit = total_price - cogs - total_sga
    operating_margin = (operating_profit / total_price) if total_price > 0 else 0.0

    suggested_price = 0
    if target_margin_input is not None and target_margin_input < 1.0:
        denom = 1.0 - target_margin_input
        numerator = cogs + total_sga
        suggested_price = int(numerator / denom)

    return {
        "sales": total_price,
        "cogs": cogs,
        "gross_profit": gross_profit,
        "sga_cost": total_sga,
        "operating_profit": operating_profit,
        "operating_margin": f"{operating_margin:.1%}",
        "target_margin_specified": f"{target_margin_input:.1%}" if target_margin_input is not None else None,
        "suggested_price_to_attain_target": suggested_price,
        "breakdown": {
            "sga_calculation_base": "direct_labor_cost",
            "sga_rate_on_propa_labor": f"{sga_rate_on_labor:.1%}",
        },
    }


def main_logic(req_body, tables=None):
    if tables is None:
        tables = []

    complexity = req_body.get("complexity") or "medium"
    duration = req_body.get("duration") or "normal"
    dev_type = req_body.get("dev_type") or "new"
    target_platform = req_body.get("target_platform") or req_body.get("target_platform".replace("target_", "")) or "web_b2e"
    profile_key = req_body.get("estimation_profile") or req_body.get("profile") or "enterprise"
    target_margin = req_body.get("target_margin")

    screen_count = req_body.get("screen_count")
    screen_count = 10 if screen_count is None else screen_count
    table_count = req_body.get("table_count")
    table_count = 0 if table_count is None else table_count

    primary_dept = req_body.get("department")
    dept_allocation = req_body.get("dept_allocation")
    team_ratio = req_body.get("team_ratio")

    selected_features = resolve_keys(req_body.get("features", []), FEATURE_LABEL_MAP, FEATURE_MAN_DAYS)
    selected_phase2 = resolve_keys(req_body.get("phase2_items", []), PHASE2_LABEL_MAP, PHASE2_ITEMS)
    selected_phase3 = resolve_keys(req_body.get("phase3_items", []), PHASE3_LABEL_MAP, PHASE3_ITEMS)

    diff_multiplier = CONFIG["difficulty_multipliers"].get(complexity, 1.0)
    dur_multiplier = CONFIG["duration_multipliers"].get(duration, 1.0)
    current_dev_type_mults = CONFIG["dev_type_multipliers"].get(dev_type, {"design": 1.0, "dev": 1.0})
    dev_type_design_mult = current_dev_type_mults.get("design", 1.0)
    dev_type_dev_mult = current_dev_type_mults.get("dev", 1.0)
    platform_multiplier = CONFIG["platform_multipliers"].get(target_platform, 1.0)
    buffer_multiplier = CONFIG["buffer_multiplier"]

    profiles = CONFIG["estimation_profiles"]
    selected_profile = profiles.get(profile_key, profiles["enterprise"])
    prod_factor = selected_profile.get("productivity_factor", CONFIG["fp_simplified"]["default_productivity"])

    dev_feature_days = sum(FEATURE_MAN_DAYS.get(f, 0) for f in selected_features)
    screen_weight = CONFIG["fp_simplified"]["screen_weight"]
    table_weight = CONFIG["fp_simplified"]["table_weight"]
    screen_fp = screen_count * screen_weight
    table_fp = table_count * table_weight
    total_ufp = screen_fp + table_fp
    dev_fp_based_days = total_ufp * prod_factor
    dev_base_days = dev_feature_days + dev_fp_based_days
    dev_total_days = dev_base_days * diff_multiplier * dev_type_dev_mult

    rank_costs = CONFIG["profit_config"]["rank_costs"]
    team_ratio_dict = team_ratio if isinstance(team_ratio, dict) else CONFIG["profit_config"]["standard_team_ratio"]
    direct_labor_cost = compute_direct_labor_cost(dev_total_days, team_ratio_dict, rank_costs)

    resolved_alloc = dept_allocation if isinstance(dept_allocation, list) else None
    indirect_per_hour, sga_rate = resolve_bs_org_rates(primary_dept, resolved_alloc)
    indirect_cost = compute_indirect_cost(dev_total_days, indirect_per_hour)

    p2_base_cost = sum(PHASE2_ITEMS.get(p, 0) for p in selected_phase2)
    p2_total_cost = int(p2_base_cost * diff_multiplier * dev_type_design_mult)

    confidence = req_body.get("confidence")
    p3_outsource_cost = compute_phase3_outsource_cost(selected_phase3, screen_count)
    p3_management_fee = int(round(p3_outsource_cost * 0.15))

    conf_multiplier = 1.2
    if confidence == "low":
        conf_multiplier = 1.4
    elif confidence == "high":
        conf_multiplier = 1.1
    p3_before_variance = p3_outsource_cost + p3_management_fee
    p3_final_cost = int(round(p3_before_variance * conf_multiplier))

    cogs = direct_labor_cost + indirect_cost + p3_final_cost + p2_total_cost
    final_amount = int(cogs * platform_multiplier * dur_multiplier * buffer_multiplier)

    profit_data = calculate_profitability_ccs(
        total_price=final_amount,
        cogs=cogs,
        direct_labor_cost=direct_labor_cost,
        sga_rate_on_labor=sga_rate,
        target_margin_input=target_margin,
    )

    return {
        "status": "success",
        "estimated_amount": f"¥{final_amount:,}",
        "estimated_range": f"¥{int(final_amount * 0.9):,} - ¥{int(final_amount * 1.2):,}",
        "man_days": {
            "development_total": round(dev_total_days, 1),
            "fp_based": round(dev_fp_based_days, 1),
            "feature_based": round(dev_feature_days, 1),
        },
        "bs_input": {
            "department": primary_dept or DEFAULT_BS_DEPT,
            "dept_allocation": resolved_alloc,
            "sga_rate_applied": f"{sga_rate:.1%}",
            "indirect_yen_per_hour": indirect_per_hour,
            "team_ratio": team_ratio_dict,
        },
        "input_echo": {
            "profile": selected_profile.get("label"),
            "profile_description": selected_profile.get("description"),
            "screen_count": screen_count,
            "table_count": table_count,
            "tables": tables,
            "complexity": complexity,
            "duration": duration,
            "dev_type": dev_type,
            "target_platform": target_platform,
            "confidence": confidence,
            "target_margin": target_margin,
            "features": selected_features,
            "phase2_items": selected_phase2,
            "phase3_items": selected_phase3,
        },
        "phase3_breakdown": {
            "outsource_cost": p3_outsource_cost,
            "management_fee": p3_management_fee,
            "confidence_multiplier": conf_multiplier,
            "total_phase3_cost": p3_final_cost,
        },
        "profit_analysis": profit_data,
        "productivity": f"{prod_factor} MD/FP",
    }


def main(**kwargs):
    args = dict(kwargs)

    for key in ["features", "phase2_items", "phase3_items", "tables"]:
        args[key] = parse_list_from_text(args.get(key))

    for key in ["screen_count", "table_count"]:
        args[key] = parse_int(args.get(key))

    if args.get("tables") and (args.get("table_count") is None or args.get("table_count") == 0):
        args["table_count"] = len(args["tables"])

    args["target_margin"] = parse_target_margin(args.get("target_margin"))

    dept = args.get("department")
    if not dept or dept not in BS_ORG_CONFIG:
        args["department"] = DEFAULT_BS_DEPT

    if isinstance(args.get("dept_allocation"), str) or isinstance(args.get("dept_allocation"), list):
        args["dept_allocation"] = parse_dept_allocation(args.get("dept_allocation"))

    if isinstance(args.get("team_ratio"), str) or isinstance(args.get("team_ratio"), dict):
        args["team_ratio"] = parse_team_ratio(args.get("team_ratio"))

    rag_query = "BS事業部 見積基準 利益管理基準 間接費 販管費 生産性 Function Point 外注費 デザイン積算"

    try:
        data = main_logic(args, args.get("tables", []))
        pricing_simulator_input = {
            "project_name": "案件A",
            "cost": data["profit_analysis"]["cogs"] + data["profit_analysis"]["sga_cost"],
            "current_sales": data["profit_analysis"]["sales"],
            "target_margin": float(args.get("target_margin") or 0),
            "currency": "JPY",
        }
        return {
            "calc_json": json.dumps(data, ensure_ascii=False, indent=2),
            "query_for_rag": rag_query,
            "pricing_simulator_input": json.dumps(
                pricing_simulator_input, ensure_ascii=False, indent=2
            ),
        }
    except Exception as e:
        import traceback

        err_data = {
            "status": "error",
            "message": str(e),
            "trace": traceback.format_exc(),
            "input_echo": args,
        }
        return {
            "calc_json": json.dumps(err_data, ensure_ascii=False, indent=2),
            "query_for_rag": rag_query,
            "pricing_simulator_input": "",
        }
