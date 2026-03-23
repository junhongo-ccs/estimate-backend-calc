# -*- coding: utf-8 -*-
import json
import math

# ==============================================================================
# CONFIGURATION: FY2026 BS事業部 財務・生産性基準 (Certified V2.1 - Dify Optimized)
# ==============================================================================
# [FY2026 BS Standard (Propa Labor SGA Model)]
CONFIG = {
    "config_version": "2026-03-BS-Certified-V2.1",
    "daily_rates": {"outsource": 80000},
    "estimation_profiles": {
        "poc": {
            "label": "Prototyping/Manufacturing Only",
            "productivity_factor": 1.0,
            "description": "製造/実制作のみ。SI案件の全工程（要件定義〜QA）には非適用。"
        },
        "standard": {
            "label": "SIer標準（全工程網羅）",
            "productivity_factor": 1.5,
            "description": "要件定義〜品質保証までの標準SIプロセス（約13.3 FP/人月）を包含。"
        },
        "enterprise": {
            "label": "エンタープライズ型",
            "productivity_factor": 2.0,
            "description": "金融・基幹等の厳格な品質管理基準（約10.0 FP/人月）を適用。"
        }
    },
    "fp_weights": {"screen": 20, "table": 15},
    "difficulty_multipliers": {"low": 0.8, "medium": 1.0, "high": 1.3},
    "buffer_multiplier": 1.1,
    "profit_config": {
        "rank_costs": {
            "Rank4": 1098000, "Rank3": 944000, "Rank2": 758000, "Rank1": 541000,
        },
        "standard_team_ratio": {"Rank3": 0.8, "Rank2": 0.2}
    }
}

FEATURE_MAN_DAYS = {
    "auth": 3.0, "payment": 5.0, "search": 2.0, "admin": 5.0, "api_external": 4.0,
}

BS_ORG_CONFIG = {
    "ビジ・企画営業部": {"indirect_h": 2340, "sga_on_propa_labor_rate": 0.751},
    "ビジ・システム開発部": {"indirect_h": 2340, "sga_on_propa_labor_rate": 0.751},
    "ビジネスイノベーション事業部共通": {"indirect_h": 2340, "sga_on_propa_labor_rate": 0.751},
    "ＳＦ＆Ｍ第１システム開発部": {"indirect_h": 2030, "sga_on_propa_labor_rate": 0.741},
    "ＣＳ第１システム開発部": {"indirect_h": 1940, "sga_on_propa_labor_rate": 0.787},
    "ＤＴ第１開発部": {"indirect_h": 2320, "sga_on_propa_labor_rate": 0.859},
    "社会・科学システム部": {"indirect_h": 2220, "sga_on_propa_labor_rate": 0.886},
    "ソリューションビジネス推進室": {"indirect_h": 3570, "sga_on_propa_labor_rate": 1.415},
}

def calculate_profitability_ccs(total_price, cogs, direct_labor_cost, sga_rate_on_labor, target_margin_input):
    total_sga = int(direct_labor_cost * sga_rate_on_labor)
    operating_profit = total_price - cogs - total_sga
    operating_margin = (operating_profit / total_price) if total_price > 0 else 0.0
    suggested_price = 0
    if target_margin_input is not None:
        denom = 1.0 - target_margin_input
        if denom > 0: suggested_price = int((cogs + total_sga) / denom)
    return {
        "sales": total_price, "cogs": cogs, "operating_profit": operating_profit,
        "operating_margin": f"{operating_margin:.1%}", "total_sga_cost": total_sga,
        "sga_rate_applied": f"{sga_rate_on_labor:.1%}", "suggested_price_to_attain_target": suggested_price
    }

def main_logic(req_body):
    config = CONFIG
    # Dify UI変数 (profile / estimation_profile 両対応)
    profile_key = req_body.get('profile') or req_body.get('estimation_profile') or 'standard'
    screen_count = int(req_body.get('screen_count') or 0)
    table_count = int(req_body.get('table_count') or 0)
    dept_name = req_body.get('department') or "ビジネスイノベーション事業部共通"

    # target_margin 文字列パース (e.g. "15%" -> 0.15)
    target_margin_raw = req_body.get('target_margin')
    target_margin = None
    if isinstance(target_margin_raw, str) and target_margin_raw.strip():
        try:
            v = target_margin_raw.replace('%', '').strip()
            num = float(v)
            target_margin = num / 100.0 if num > 1.0 else num
        except:
            target_margin = None
    elif isinstance(target_margin_raw, (int, float)):
        target_margin = float(target_margin_raw)

    # features パース (リスト または カンマ区切り文字列)
    features_raw = req_body.get('features') or []
    if isinstance(features_raw, str):
        features = [f.strip() for f in features_raw.split(',') if f.strip()]
    else:
        features = features_raw

    dept_cfg = BS_ORG_CONFIG.get(dept_name, BS_ORG_CONFIG["ビジネスイノベーション事業部共通"])
    selected_profile = config["estimation_profiles"].get(profile_key, config["estimation_profiles"]["standard"])
    prod_factor = selected_profile["productivity_factor"]

    total_fp = (screen_count * config["fp_weights"]["screen"]) + (table_count * config["fp_weights"]["table"])
    dev_fp_days = total_fp * prod_factor
    dev_feature_days = sum(FEATURE_MAN_DAYS.get(f, 0) for f in features)
    
    dev_base_days = (dev_fp_days + dev_feature_days)
    dev_total_days = dev_base_days * config["difficulty_multipliers"].get(req_body.get('complexity', 'medium'), 1.0)

    rank_costs = config["profit_config"]["rank_costs"]
    team_ratio = config["profit_config"]["standard_team_ratio"]
    man_months = dev_total_days / 20.0
    direct_labor_cost = int(man_months * sum(rank_costs.get(r, 0) * w for r, w in team_ratio.items()))
    indirect_cost = int(dev_total_days * 8.0 * dept_cfg["indirect_h"])
    cogs = direct_labor_cost + indirect_cost

    nominal_price = int(cogs * config["buffer_multiplier"])
    profit_analysis = calculate_profitability_ccs(nominal_price, cogs, direct_labor_cost, dept_cfg["sga_on_propa_labor_rate"], target_margin)
    
    estimated_range = { "min": int(nominal_price * 0.85), "max": int(nominal_price * 1.15) }

    return {
        "status": "success", "estimated_amount": nominal_price, "total_man_days": round(dev_total_days, 1),
        "estimated_range": f"¥{estimated_range['min']:,} 〜 ¥{estimated_range['max']:,}",
        "profile": selected_profile["label"], "profile_description": selected_profile["description"],
        "profit_analysis": profit_analysis,
        "input_echo": {
            "profile": selected_profile["label"], "department": dept_name, "screen_count": screen_count,
            "table_count": table_count, "features": features, "complexity": req_body.get('complexity', 'medium'),
            "target_margin": f"{target_margin*100:.1f}%" if target_margin is not None else "未指定"
        },
        "details": {
            "direct_labor": direct_labor_cost, "indirect_cost": indirect_cost, "total_fp": total_fp,
            "fp_days": round(dev_fp_days, 1), "feature_days": round(dev_feature_days, 1)
        }
    }

# --- 統合実行エントリポイント (Dify最適化) ---
def main(screen_count=0, table_count=0, profile='standard', estimation_profile='standard', 
         department='ビジネスイノベーション事業部共通', complexity='medium', features='', 
         target_margin=None, **kwargs):
    
    # 全入力を一つの辞書に統合
    args = {
        "screen_count": screen_count,
        "table_count": table_count,
        "profile": profile or estimation_profile,
        "department": department,
        "complexity": complexity,
        "features": features,
        "target_margin": target_margin
    }
    args.update(kwargs)
    
    try:
        # ロジック実行
        result = main_logic(args)
        return {"calc_json": json.dumps(result, ensure_ascii=False, indent=2)}
    except Exception as e:
        import traceback
        # エラーが発生した場合は、AIがそれを認識できる形式で返す
        err_data = {
            "status": "error",
            "message": str(e),
            "trace": traceback.format_exc(),
            "input_echo": args # デバッグ用に受け取った値を返す
        }
        return {"calc_json": json.dumps(err_data, ensure_ascii=False, indent=2)}
