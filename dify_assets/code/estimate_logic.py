import json
import math

# =========================================================
# CONFIGURATION & CONSTANTS
# =========================================================

CONFIG = {
    "config_version": "2026-02", # Updated version for Flex-Mode
    "daily_rates": {
        "sier_internal": 100000,     # SIer内製 (S推進室基準): ¥100,000/人日 (間接費・販管費込)
        "outsource": 80000           # 外注基準単価: ¥80,000/人日 (ここから実勢価格へ換算)
    },
    "policy": {
        "require_explicit_productivity_for_step_fp": True,
        "calc_must_ignore_reference_productivity": True,
        "require_explicit_vendor_confidence": True
    },
    "development": {
        "man_days_per_screen": 1.5   # 1画面あたりの開発工数（人日） - Legacy/Fallback
    },
    # ---------------------------------------------------------
    # Phase 5: Estimation Profiles (Productivity Standards)
    # ---------------------------------------------------------
    "estimation_profiles": {
        "poc": {
            "label": "PoC/開発重視型",
            "productivity_factor": 0.075,  # 20FP -> 1.5人日 (実装中心)
            "description": "スピード重視のプロトタイプ開発。管理工数を抑えた設定。"
        },
        "enterprise": {
            "label": "エンタープライズ型",
            "productivity_factor": 1.4,   # ~15FP/人月相当 (全工程網羅)
            "description": "要件定義〜品質保証を含む、社内標準のエンタープライズ開発基準。"
        },
        "mission_critical": {
            "label": "高信頼性型",
            "productivity_factor": 2.2,   # 10FP/人月相当 (極めて高い品質基準)
            "description": "金融・基幹システム等の、極めて高い品質とドキュメントが必要な案件。"
        }
    },
    "fp_simplified": {
        "screen_weight": 20,         # 1画面あたりの標準FP (Avg)
        "table_weight": 15,          # 1テーブルあたりの標準FP (Avg)
        "default_productivity": 0.075 
    },
    "difficulty_multipliers": {
        "low": 0.8,
        "medium": 1.0,
        "high": 1.5,
        "very_high": 2.0
    },
    "duration_multipliers": {
        "short": 1.2,
        "normal": 1.0,
        "long": 0.9
    },
    "dev_type_multipliers": {
        "new": {
            "design": 1.0,
            "dev": 1.0
        },
        "porting": {
            "design": 0.5,           # 既存資産活用で設計50%減
            "dev": 0.8               # 既存資産活用で開発20%減
        }
    },
    "platform_multipliers": {
        "web_b2e": 1.0,
        "web_b2c": 1.2,              # セキュリティ・負荷対策増
        "mobile": 1.5,               # 2OS対応・申請工数増
        "all": 1.8                   # Web+Mobile
    },
    "buffer_multiplier": 1.1,
    # ---------------------------------------------------------
    # Phase 2: Profit Calculation Config (Manager's View)
    # ---------------------------------------------------------
    "profit_config": {
        "rank_costs": {
            "Rank1": 1344000,        # シニアマネージャ
            "Rank2": 1088000,        # マネージャ (avg used for cost)
            "Rank3": 832000,         # リーダー (avg used for cost)
            "Rank4": 576000,         # メンバー
            "Rank5": 512000          # 初級
        },
        "standard_team_ratio": {
            "Rank2": 0.2,            # PM/Management
            "Rank3": 0.8             # Execution
        },
        "indirect_cost_rate": 0.38,   # 直接労務費に対する間接費率 (38%)
        "sga_rates": {
            "division": 0.186,       # 事業部販管費率 (18.6%)
            "corporate": 0.095       # 全社販管費率 (9.5%)
        }
    }
}

# ---------------------------------------------------------
# Feature & Phase Item Maps (Same as original)
# ---------------------------------------------------------
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
    "multi_language": 3.0
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
    "多言語対応 (i18n)": "multi_language"
}

PHASE2_ITEMS = {
    "basic_design": 1000000,
    "detail_design": 1500000,
    "infra_design": 800000,
    "security_review": 500000,
    "standardization": 1200000
}

PHASE2_LABEL_MAP = {
    "基本設計書作成": "basic_design",
    "詳細設計書作成": "detail_design",
    "インフラ・クラウド設計": "infra_design",
    "セキュリティ審査・対策案": "security_review",
    "開発標準化・共通部設計": "standardization"
}

PHASE3_ITEMS = {
    "logo_creation": {"fixed": 650000, "range": [500000, 800000]},
    "brand_guideline": {"fixed": 1200000, "range": [1000000, 1500000]},
    "ui_prototype": {"fixed": 800000, "range": [600000, 1200000]},
    "marketing_asset": {"fixed": 450000, "range": [300000, 600000]}
}

PHASE3_LABEL_MAP = {
    "企業/プロダクトロゴ制作 (S推進室基準)": "logo_creation",
    "ブランドガイドライン策定": "brand_guideline",
    "高精度UIプロトタイプ": "ui_prototype",
    "マーケティング素材/LP": "marketing_asset"
}

# =========================================================
# HELPER FUNCTIONS
# =========================================================

def resolve_keys(input_list, label_map, item_dict):
    """
    Resolve descriptive labels or raw keys back to internal keys.
    """
    if not isinstance(input_list, list):
        return []
    
    resolved = []
    # Inverted map for labels -> keys
    for x in input_list:
        if not x: continue
        # Try finding as label first
        if x in label_map:
            resolved.append(label_map[x])
        # Then try as raw key
        elif x in item_dict:
            resolved.append(x)
    return list(set(resolved))

def calculate_profitability(total_price: int, total_man_days: float, outsourcing_cost: int, target_margin_input: float = None) -> dict:
    """
    Calculate profitability metrics and optional target-based suggested price.
    """
    conf = CONFIG.get("profit_config", {})
    
    # 1. Calculate Weighted Average Monthly Cost
    avg_monthly_cost = 0
    rank_costs = conf.get("rank_costs", {})
    team_ratio = conf.get("standard_team_ratio", {})
    for rank, ratio in team_ratio.items():
        avg_monthly_cost += rank_costs.get(rank, 0) * ratio
        
    # 2. Calculate Direct Labor Cost
    man_months = total_man_days / 20.0
    direct_labor_cost = int(man_months * avg_monthly_cost)
    
    # 3. Calculate Indirect Cost
    indirect_rate = conf.get("indirect_cost_rate", 0.38)
    indirect_cost = int(direct_labor_cost * indirect_rate)
    
    # 4. Calculate COGS (Cost of Goods Sold)
    cogs = direct_labor_cost + indirect_cost + outsourcing_cost
    
    # 5. Calculate Gross Profit
    gross_profit = total_price - cogs
    gross_margin = (gross_profit / total_price) if total_price > 0 else 0
    
    # 6. Calculate SG&A
    sga_rates = conf.get("sga_rates", {})
    sga_div_rate = sga_rates.get("division", 0)
    sga_corp_rate = sga_rates.get("corporate", 0)
    sga_total_rate = sga_div_rate + sga_corp_rate
    
    total_sga = int(total_price * sga_total_rate)
    
    # 7. Calculate Operating Profit
    operating_profit = gross_profit - total_sga
    operating_margin = (operating_profit / total_price) if total_price > 0 else 0

    # 8. Phase 6: Reverse Calculation (Suggested Price for Target Margin)
    suggested_price = 0
    if target_margin_input is not None:
        # Formula: Price = COGS / (1 - SG&A_rate - Target_Margin)
        divider = (1.0 - sga_total_rate - target_margin_input)
        if divider > 0:
            suggested_price = int(cogs / divider)

    return {
        "sales": total_price,
        "cogs": cogs,
        "gross_profit": gross_profit,
        "gross_margin": f"{gross_margin:.1%}",
        "operating_profit": operating_profit,
        "operating_margin": f"{operating_margin:.1%}",
        "suggested_price_to_attain_target": suggested_price,
        "target_margin_specified": f"{target_margin_input:.1%}" if target_margin_input is not None else None,
        "breakdown": {
            "direct_labor": direct_labor_cost,
            "indirect_cost": indirect_cost,
            "outsourcing": outsourcing_cost,
            "total_sga_cost": total_sga
        }
    }

# =========================================================
# MAIN LOGIC
# =========================================================

def main_logic(req_body, tables=[]):
    config = CONFIG
    
    # Phase 5: Optional Variables & Defaults (Robustness)
    method = req_body.get('method', 'screen') 
    complexity = req_body.get('complexity') or 'medium'
    duration = req_body.get('duration') or 'normal'
    dev_type = req_body.get('dev_type') or 'new'
    target_platform = req_body.get('target_platform') or 'web_b2e'
    profile_key = req_body.get('estimation_profile') or 'poc'
    
    # Target Margin (Phase 6)
    target_margin = req_body.get('target_margin') # Can be None
    
    # Defaults for counts
    screen_count = req_body.get('screen_count')
    if screen_count is None: screen_count = 10
    
    table_count = req_body.get('table_count')
    if table_count is None: table_count = 0
        
    confidence = req_body.get('confidence') # Optional
    
    # Policy Check
    policy = config.get('policy', {})
    require_explicit_prod = policy.get('require_explicit_productivity_for_step_fp', True)
    require_explicit_conf = policy.get('require_explicit_vendor_confidence', True)

    # Validate Confidence if Phase 3 (Vendor Design) items present
    has_phase3_items = (len(req_body.get('phase3_items', [])) > 0)
    if require_explicit_conf and has_phase3_items and not confidence:
         return {"status": "error", "message": "Missing required param: confidence (Required for Phase 3 / Vendor Design estimation)"}

    # Resolve keys
    selected_features = resolve_keys(req_body.get('features', []), FEATURE_LABEL_MAP, FEATURE_MAN_DAYS)
    selected_phase2 = resolve_keys(req_body.get('phase2_items', []), PHASE2_LABEL_MAP, PHASE2_ITEMS)
    selected_phase3 = resolve_keys(req_body.get('phase3_items', []), PHASE3_LABEL_MAP, PHASE3_ITEMS)

    # Config Values
    diff_multipliers = config.get('difficulty_multipliers', {})
    diff_multiplier = diff_multipliers.get(complexity, 1.0)
    
    dur_multipliers = config.get('duration_multipliers', {})
    dur_multiplier = dur_multipliers.get(duration, 1.0)
    
    # Dev Type Multipliers
    dev_type_mults_config = config.get('dev_type_multipliers', {})
    current_dev_type_mults = dev_type_mults_config.get(dev_type, {"design": 1.0, "dev": 1.0})
    dev_type_design_mult = current_dev_type_mults.get("design", 1.0)
    dev_type_dev_mult = current_dev_type_mults.get("dev", 1.0)

    plat_mults_config = config.get('platform_multipliers', {})
    platform_multiplier = plat_mults_config.get(target_platform, 1.0)
    
    buffer_multiplier = config.get('buffer_multiplier', 1.1)
    
    daily_rates = config.get('daily_rates', {})
    sier_rate = daily_rates.get('sier_internal', 100000)
    outsource_rate = daily_rates.get('outsource', 80000)
    
    # Profile & Productivity (Phase 5)
    profiles = config.get('estimation_profiles', {})
    selected_profile = profiles.get(profile_key, profiles['poc']) 
    prod_factor = selected_profile.get('productivity_factor', 0.075)

    # ===== Development Cost =====
    dev_feature_days = sum(FEATURE_MAN_DAYS.get(f, 0) for f in selected_features)
    
    fp_conf = config.get('fp_simplified', {})
    screen_weight = fp_conf.get('screen_weight', 20)
    table_weight = fp_conf.get('table_weight', 15)
    
    screen_fp = screen_count * screen_weight
    table_fp = table_count * table_weight
    total_ufp = screen_fp + table_fp
    
    dev_fp_based_days = total_ufp * prod_factor
    dev_base_days = dev_feature_days + dev_fp_based_days

    dev_total_days = dev_base_days * diff_multiplier * dev_type_dev_mult
    dev_cost = int(dev_total_days * sier_rate)

    # ===== Phase 2: Design & Consulting (Fixed Costs) =====
    p2_base_cost = sum(PHASE2_ITEMS.get(p, 0) for p in selected_phase2)
    p2_total_cost = int(p2_base_cost * diff_multiplier * dev_type_design_mult)

    # ===== Phase 3: Vendor Design Fees (Range based) =====
    p3_total_min = 0
    p3_total_max = 0
    p3_total_fixed = 0
    for p in selected_phase3:
        item = PHASE3_ITEMS.get(p, {})
        p3_total_fixed += item.get('fixed', 0)
        p3_total_min += item.get('range', [0, 0])[0]
        p3_total_max += item.get('range', [0, 0])[1]

    # Apply confidence to Phase 3
    conf_multiplier = 1.0
    if confidence == 'low': conf_multiplier = 1.3
    elif confidence == 'high': conf_multiplier = 1.0

    p3_final_cost = int(p3_total_fixed * conf_multiplier)

    # ===== Final Total (Before Profit Analysis) =====
    # Note: Platform and Duration multipliers apply to the REVENUE side as a Risk Premium
    base_estimated_amount = dev_cost + p2_total_cost + p3_final_cost
    final_amount = int(base_estimated_amount * platform_multiplier * dur_multiplier * buffer_multiplier)

    # Profitability Calculation (Phase 2 & 6)
    outsourcing_sum = p3_final_cost # Simplification: Phase 3 is outsourced
    profit_data = calculate_profitability(final_amount, dev_total_days, outsourcing_sum, target_margin)

    return {
        "status": "success",
        "estimated_amount": f"¥{final_amount:,}",
        "estimated_range": f"¥{int(final_amount*0.9):,} - ¥{int(final_amount*1.2):,}",
        "man_days": {
            "development_total": round(dev_total_days, 1),
            "fp_based": round(dev_fp_based_days, 1),
            "feature_based": round(dev_feature_days, 1)
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
            "phase3_items": selected_phase3
        },
        "profit_analysis": profit_data,
        "productivity": f"{prod_factor} MD/FP"
    }

def main(**kwargs) -> dict:
    """
    Dify Code Node entrypoint.
    """
    args = kwargs
    
    # Pre-processing list strings from Dify
    for key in ['features', 'phase2_items', 'phase3_items', 'tables']:
        val = args.get(key)
        if isinstance(val, str):
            # Split by comma or newline
            items = []
            for line in val.replace('\r', '').split('\n'):
                items.extend([x.strip() for x in line.split(',') if x.strip()])
            
            # Filter out generic terms
            valid_items = [x for x in items if x not in ['なし', '未定', '不明', 'N/A', '-']]
            args[key] = valid_items
    
    # Processing numeric fields with defaults
    for key in ['screen_count', 'table_count']:
        val = args.get(key)
        if isinstance(val, str) and val.strip():
            try: args[key] = int(val)
            except: args[key] = None
        elif isinstance(val, (int, float)):
            args[key] = int(val)
        else:
            args[key] = None
            
    # Auto-count table_count if tables list is provided and count is zero
    if args.get('tables') and (args.get('table_count') is None or args.get('table_count') == 0):
        args['table_count'] = len(args['tables'])

    # Target Margin (Handle percentage/float string)
    tm_val = args.get('target_margin')
    if isinstance(tm_val, str) and tm_val.strip():
        try:
            tm_val = tm_val.replace('%', '').strip()
            val = float(tm_val)
            # If the value is > 1, assume it's a percentage like "20" (0.2)
            args['target_margin'] = val / 100.0 if val > 1.0 else val
        except:
            args['target_margin'] = None
    elif isinstance(tm_val, (int, float)):
        args['target_margin'] = float(tm_val)
    else:
        args['target_margin'] = None

    data = main_logic(args, args.get('tables', []))
    return {"result": json.dumps(data, ensure_ascii=False, indent=2)}
