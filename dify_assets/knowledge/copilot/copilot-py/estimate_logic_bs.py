# -*- coding: utf-8 -*-
"""
BS版 見積ロジック（Dify Code Node用）
- FY2026 利益管理表の係数に準拠（1人月=160h、部門別 間接費単金、本部/全社販管費率=BSは47.8%）
- SG&Aは粗利ベースで控除（= 本部販管費率 + 全社販管費率）
- 目標営業利益率からの逆算売価式も粗利ベースの定義に合わせて修正

入出力：
  def main(**kwargs) -> dict:
    return {"result": json.dumps(data, ensure_ascii=False, indent=2)}
"""

import json
import math
from typing import List, Dict, Any

# =========================================================
# CONFIGURATION & CONSTANTS
# =========================================================
CONFIG = {
    "config_version": "2026-02-BS",
    "daily_rates": {
        "sier_internal": 100000,  # 参考値（直接は使わず、ランク人月で計算）
        "outsource": 80000
    },
    # 生産性プロファイル（MD/FP相当係数）
    "estimation_profiles": {
        "poc": {
            "label": "PoC/開発重視型",
            "productivity_factor": 0.075,
            "description": "スピード重視（管理工数を抑制）"
        },
        "enterprise": {
            "label": "エンタープライズ型",
            "productivity_factor": 1.4,
            "description": "要件定義〜品質保証までの標準プロセスを含む"
        },
        "mission_critical": {
            "label": "高信頼性型",
            "productivity_factor": 2.2,
            "description": "金融/基幹等の極めて高い品質基準"
        }
    },
    # 簡易FP基準
    "fp_simplified": {
        "screen_weight": 20,  # FP/画面
        "table_weight": 15,   # FP/テーブル
        "default_productivity": 0.075
    },
    # 難易度・納期・開発タイプ係数（工数側）
    "difficulty_multipliers": {"low": 0.8, "medium": 1.0, "high": 1.5, "very_high": 2.0},
    "duration_multipliers": {"long": 0.9, "normal": 1.0, "short": 1.2},
    "dev_type_multipliers": {
        "new": {"design": 1.0, "dev": 1.0},
        "porting": {"design": 0.5, "dev": 0.8}
    },
    # プラットフォームの売価プレミアム
    "platform_multipliers": {"web_b2e": 1.0, "web_b2c": 1.2, "mobile": 1.5, "all": 1.8},
    "buffer_multiplier": 1.1,
    # 損益計算（ランク人月コスト/標準チーム構成）
    "profit_config": {
        # PDFのランク別（時給→人月=160h）に合わせて上書き
        "rank_costs": {
            "Rank4": 1098000,  # L4: 6,860×160h
            "Rank3":  944000,  # L3: 5,900×160h
            "Rank2":  758000,  # L2: 4,740×160h
            "Rank1":  541000,  # L1: 3,380×160h
        },
        "standard_team_ratio": {"Rank3": 0.8, "Rank2": 0.2}
    }
}

# =========================================================
# BS事業部：部門→(間接費単金[円/h], 本部販管費率, 全社販管費率)
# =========================================================
BS_ORG_CONFIG: Dict[str, Dict[str, float]] = {
    # --- ビジネスイノベーション ---
    "ビジ・企画営業部":              {"indirect_per_hour": 2340, "hq_sga": 0.273, "corp_sga": 0.478},
    "ビジ・システム開発部":            {"indirect_per_hour": 2340, "hq_sga": 0.273, "corp_sga": 0.478},
    "ビジネスイノベーション事業部共通": {"indirect_per_hour": 2340, "hq_sga": 0.273, "corp_sga": 0.478},
    # --- SF&M ---
    "ＳＦ＆Ｍ営業部":                {"indirect_per_hour": 2030, "hq_sga": 0.263, "corp_sga": 0.478},
    "ＳＦ＆Ｍ第１システム開発部":        {"indirect_per_hour": 2030, "hq_sga": 0.263, "corp_sga": 0.478},
    "ＳＦ＆Ｍ第２システム開発部":        {"indirect_per_hour": 2030, "hq_sga": 0.263, "corp_sga": 0.478},
    "ＳＦ＆Ｍ事業部（共通）":           {"indirect_per_hour": 2030, "hq_sga": 0.263, "corp_sga": 0.478},
    # --- CS ---
    "ＣＳ営業部":                   {"indirect_per_hour": 1940, "hq_sga": 0.309, "corp_sga": 0.478},
    "ＣＳ第１システム開発部":           {"indirect_per_hour": 1940, "hq_sga": 0.309, "corp_sga": 0.478},
    "ＣＳ第２システム開発部":           {"indirect_per_hour": 1940, "hq_sga": 0.309, "corp_sga": 0.478},
    "ＣＳシステム事業部（共通）":         {"indirect_per_hour": 1940, "hq_sga": 0.309, "corp_sga": 0.478},
    # --- DT ---
    "ＤＴ営業部":                   {"indirect_per_hour": 2320, "hq_sga": 0.381, "corp_sga": 0.478},
    "ＤＴ第１開発部":                 {"indirect_per_hour": 2320, "hq_sga": 0.381, "corp_sga": 0.478},
    "ＤＴ第２開発部":                 {"indirect_per_hour": 2320, "hq_sga": 0.381, "corp_sga": 0.478},
    "ＤＴ事業部（共通）":              {"indirect_per_hour": 2320, "hq_sga": 0.381, "corp_sga": 0.478},
    # --- 社会・科学システム ---
    "社会・科学システム営業部":           {"indirect_per_hour": 2220, "hq_sga": 0.408, "corp_sga": 0.478},
    "データサイエンスシステム部":         {"indirect_per_hour": 2220, "hq_sga": 0.408, "corp_sga": 0.478},
    "社会・科学システム事業部（共通）":     {"indirect_per_hour": 2220, "hq_sga": 0.408, "corp_sga": 0.478},
    # --- ソリューションビジネス推進室 ---
    "ソリューションビジネス推進室":         {"indirect_per_hour": 3570, "hq_sga": 0.937, "corp_sga": 0.478},
}

DEFAULT_BS_DEPT = "ビジネスイノベーション事業部共通"

# =========================================================
# Feature & Phase Item Maps（元PoCの構造を踏襲）
# =========================================================
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
}

PHASE3_ITEMS = {
    "logo_creation": {"fixed": 650000, "range": [500000, 800000]},
    "brand_guideline": {"fixed": 1200000, "range": [1000000, 1500000]},
    "ui_prototype": {"fixed": 800000, "range": [600000, 1200000]},
    "marketing_asset": {"fixed": 450000, "range": [300000, 600000]},
}

PHASE3_LABEL_MAP = {
    "企業/プロダクトロゴ制作": "logo_creation",
    "ブランドガイドライン策定": "brand_guideline",
    "高精度UIプロトタイプ": "ui_prototype",
    "マーケティング素材/LP": "marketing_asset",
}

# =========================================================
# HELPERS
# =========================================================

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
    # 重複排除
    return list(dict.fromkeys(resolved))


def parse_list_from_text(val):
    # 改行/カンマ区切り → list
    items = []
    if isinstance(val, str):
        for line in val.replace('\r', '').split('\n'):
            items.extend([x.strip() for x in line.split(',') if x.strip()])
    elif isinstance(val, list):
        items = val
    return [x for x in items if x not in ['なし', '未定', '不明', 'N/A', '-']]


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
            v = val.replace('%', '').strip()
            num = float(v)
            return num/100.0 if num > 1.0 else num
        except Exception:
            return None
    return None


def parse_team_ratio(text):
    # 例: "Rank3:0.8, Rank2:0.2"
    default = {"Rank3": 0.8, "Rank2": 0.2}
    if not isinstance(text, str) or not text.strip():
        return default
    res = {}
    for part in text.split(','):
        if ':' in part:
            k, v = part.split(':', 1)
            k = k.strip()
            try:
                s = float(v.strip())
                if s >= 0 and k in CONFIG["profit_config"]["rank_costs"]:
                    res[k] = s
            except Exception:
                pass
    s = sum(res.values())
    if s > 0:
        for k in list(res.keys()):
            res[k] = res[k] / s
        return res
    return default


def parse_dept_allocation(text):
    # 段落: 「部門: 0.6\nＣＳ第１システム開発部: 0.4」→ 正規化list
    items = []
    if isinstance(text, str) and text.strip():
        for line in text.splitlines():
            if ':' in line:
                k, v = line.split(':', 1)
                k = k.strip()
                try:
                    s = float(v.strip())
                    if k in BS_ORG_CONFIG and s > 0:
                        items.append({"dept": k, "share": s})
                except Exception:
                    pass
    total = sum(i['share'] for i in items)
    if total > 0:
        for i in items:
            i['share'] = i['share'] / total
    return items


def resolve_bs_org_rates(primary_dept: str, allocations: List[Dict[str, Any]] | None):
    # デフォルト=主所属100%
    if not primary_dept or primary_dept not in BS_ORG_CONFIG:
        primary_dept = DEFAULT_BS_DEPT
    if not allocations:
        cfg = BS_ORG_CONFIG[primary_dept]
        return (cfg["indirect_per_hour"], cfg["hq_sga"], cfg["corp_sga"])

    # 加重平均
    total = sum(max(0.0, float(a.get("share", 0.0))) for a in allocations)
    if total <= 0:
        cfg = BS_ORG_CONFIG[primary_dept]
        return (cfg["indirect_per_hour"], cfg["hq_sga"], cfg["corp_sga"])

    ipt = 0.0
    hq = 0.0
    corp = 0.478  # BS固定
    for a in allocations:
        dept = a.get("dept")
        share = max(0.0, float(a.get("share", 0.0))) / total
        if dept in BS_ORG_CONFIG and share > 0:
            cfg = BS_ORG_CONFIG[dept]
            ipt += cfg["indirect_per_hour"] * share
            hq  += cfg["hq_sga"] * share
    return (int(round(ipt)), hq, corp)


def compute_direct_labor_cost(total_man_days: float, team_ratio: Dict[str, float], rank_costs: Dict[str, int]) -> int:
    # 人月換算：20日/月（= 160h/8h）
    man_months = total_man_days / 20.0
    avg_monthly_cost = sum(rank_costs.get(r, 0) * w for r, w in team_ratio.items())
    return int(man_months * avg_monthly_cost)


def compute_indirect_cost(total_man_days: float, indirect_yen_per_hour: float) -> int:
    hours = total_man_days * 8.0
    return int(hours * indirect_yen_per_hour)


def calculate_profitability_bs(total_price: int, cogs: int, hq_rate: float, corp_rate: float, target_margin_input: float | None):
    gross_profit = total_price - cogs
    sga_total_rate = hq_rate + corp_rate   # 粗利に対する率
    total_sga = int(gross_profit * sga_total_rate)
    operating_profit = gross_profit - total_sga
    operating_margin = (operating_profit / total_price) if total_price > 0 else 0.0

    suggested_price = 0
    if target_margin_input is not None:
        # 営業利益率 τ を達成する必要売価： Sales = COGS / (1 - τ/(1-α))
        denom_base = (1.0 - sga_total_rate)
        if denom_base > 0:
            denom = 1.0 - (target_margin_input / denom_base)
            if denom > 0:
                suggested_price = int(cogs / denom)

    return {
        "sales": total_price,
        "cogs": cogs,
        "gross_profit": gross_profit,
        "operating_profit": operating_profit,
        "operating_margin": f"{operating_margin:.1%}",
        "target_margin_specified": f"{target_margin_input:.1%}" if target_margin_input is not None else None,
        "suggested_price_to_attain_target": suggested_price,
        "breakdown": {
            "total_sga_cost": total_sga,
            "hq_sga_rate": f"{hq_rate:.1%}",
            "corp_sga_rate": f"{corp_rate:.1%}",
        }
    }

# =========================================================
# MAIN LOGIC
# =========================================================

def main_logic(req_body, tables=[]):
    config = CONFIG

    # 入力取得
    method = req_body.get('method', 'screen')
    complexity = req_body.get('complexity') or 'medium'
    duration = req_body.get('duration') or 'normal'
    dev_type = req_body.get('dev_type') or 'new'
    target_platform = req_body.get('target_platform') or 'web_b2e'
    profile_key = req_body.get('estimation_profile') or 'poc'
    target_margin = req_body.get('target_margin')  # None可（float）

    # 規模
    screen_count = req_body.get('screen_count'); screen_count = 10 if screen_count is None else screen_count
    table_count = req_body.get('table_count'); table_count = 0 if table_count is None else table_count

    # 部門・応援配分・ランクミックス
    primary_dept = req_body.get('department')
    dept_allocation = req_body.get('dept_allocation')  # list(dict)想定
    team_ratio = req_body.get('team_ratio')  # dict想定

    # 選択項目の解決
    selected_features = resolve_keys(req_body.get('features', []), FEATURE_LABEL_MAP, FEATURE_MAN_DAYS)
    selected_phase2 = resolve_keys(req_body.get('phase2_items', []), PHASE2_LABEL_MAP, PHASE2_ITEMS)
    selected_phase3 = resolve_keys(req_body.get('phase3_items', []), PHASE3_LABEL_MAP, PHASE3_ITEMS)

    # 係数
    diff_multiplier = config.get('difficulty_multipliers', {}).get(complexity, 1.0)
    dur_multiplier  = config.get('duration_multipliers', {}).get(duration, 1.0)
    dev_type_mults  = config.get('dev_type_multipliers', {}).get(dev_type, {"design":1.0, "dev":1.0})
    dev_type_design_mult = dev_type_mults.get("design", 1.0)
    dev_type_dev_mult    = dev_type_mults.get("dev", 1.0)
    platform_multiplier  = config.get('platform_multipliers', {}).get(target_platform, 1.0)
    buffer_multiplier    = config.get('buffer_multiplier', 1.1)

    # プロファイル
    profiles = config.get('estimation_profiles', {})
    selected_profile = profiles.get(profile_key, profiles['poc'])
    prod_factor = selected_profile.get('productivity_factor', 0.075)

    # ===== 工数 =====
    dev_feature_days = sum(FEATURE_MAN_DAYS.get(f, 0) for f in selected_features)
    fp_conf = config.get('fp_simplified', {})
    screen_weight = fp_conf.get('screen_weight', 20)
    table_weight  = fp_conf.get('table_weight', 15)
    screen_fp = screen_count * screen_weight
    table_fp  = table_count  * table_weight
    total_ufp = screen_fp + table_fp
    dev_fp_based_days = total_ufp * prod_factor
    dev_base_days = dev_feature_days + dev_fp_based_days
    dev_total_days = dev_base_days * diff_multiplier * dev_type_dev_mult

    # ===== 費用 =====
    # 直接労務費：ランク人月×人月
    pf = config.get("profit_config", {})
    rank_costs = pf.get("rank_costs", {})
    team_ratio_dict = team_ratio if isinstance(team_ratio, dict) else CONFIG["profit_config"].get("standard_team_ratio", {"Rank3":0.8, "Rank2":0.2})
    direct_labor_cost = compute_direct_labor_cost(dev_total_days, team_ratio_dict, rank_costs)

    # 間接費：部門間接費単金×時間、応援PJ加重
    resolved_alloc = dept_allocation if isinstance(dept_allocation, list) else None
    indirect_per_hour, hq_rate, corp_rate = resolve_bs_org_rates(primary_dept, resolved_alloc)
    indirect_cost = compute_indirect_cost(dev_total_days, indirect_per_hour)

    # Phase2：固定費（直接費に含める）
    p2_base_cost = sum(PHASE2_ITEMS.get(p, 0) for p in selected_phase2)
    p2_total_cost = int(p2_base_cost * diff_multiplier * dev_type_design_mult)

    # Phase3：外注費（確度係数）
    confidence = req_body.get('confidence')
    p3_total_fixed = 0
    for p in selected_phase3:
        item = PHASE3_ITEMS.get(p, {})
        p3_total_fixed += item.get('fixed', 0)
    conf_multiplier = 1.0
    if confidence == 'low':
        conf_multiplier = 1.3
    elif confidence == 'high':
        conf_multiplier = 1.0
    p3_final_cost = int(p3_total_fixed * conf_multiplier)

    # COGS：直接労務費 + 間接費 + 外注費 + Phase2
    cogs = direct_labor_cost + indirect_cost + p3_final_cost + p2_total_cost

    # ===== 売価（プラットフォーム/納期/バッファは売価側に寄与） =====
    base_estimated_amount = cogs
    final_amount = int(base_estimated_amount * platform_multiplier * dur_multiplier * buffer_multiplier)

    # ===== 損益（粗利ベースSG&A） =====
    profit_data = calculate_profitability_bs(final_amount, cogs, hq_rate, corp_rate, target_margin)

    return {
        "status": "success",
        "estimated_amount": f"¥{final_amount:,}",
        "estimated_range": f"¥{int(final_amount*0.9):,} - ¥{int(final_amount*1.2):,}",
        "man_days": {
            "development_total": round(dev_total_days, 1),
            "fp_based": round(dev_fp_based_days, 1),
            "feature_based": round(dev_feature_days, 1),
        },
        "bs_input": {
            "department": primary_dept or DEFAULT_BS_DEPT,
            "dept_allocation": resolved_alloc,
            "hq_sga_rate_applied": f"{hq_rate:.1%}",
            "corp_sga_rate_applied": f"{corp_rate:.1%}",
            "indirect_yen_per_hour": indirect_per_hour,
            "team_ratio": team_ratio_dict,
        },
        "input_echo": {
            "profile": selected_profile.get('label'),
            "profile_description": selected_profile.get('description'),
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
        "profit_analysis": profit_data,
        "productivity": f"{prod_factor} MD/FP",
    }


def main(**kwargs) -> dict:
    # Dify Code Node entrypoint
    args = dict(kwargs)

    # list項目の前処理
    for key in ['features', 'phase2_items', 'phase3_items', 'tables']:
        val = args.get(key)
        args[key] = parse_list_from_text(val)

    # 数値項目
    for key in ['screen_count', 'table_count']:
        args[key] = parse_int(args.get(key))

    # tablesがあればtable_countを自動補完
    if args.get('tables') and (args.get('table_count') is None or args.get('table_count') == 0):
        args['table_count'] = len(args['tables'])

    # 目標営業利益率
    args['target_margin'] = parse_target_margin(args.get('target_margin'))

    # 部門
    dept = args.get('department')
    if not dept or dept not in BS_ORG_CONFIG:
        args['department'] = DEFAULT_BS_DEPT

    # 応援配分
    if isinstance(args.get('dept_allocation'), str):
        args['dept_allocation'] = parse_dept_allocation(args['dept_allocation'])

    # ランクミックス
    if isinstance(args.get('team_ratio'), str):
        args['team_ratio'] = parse_team_ratio(args['team_ratio'])

    data = main_logic(args, args.get('tables', []))
    return {"result": json.dumps(data, ensure_ascii=False, indent=2)}
