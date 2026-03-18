import azure.functions as func
import logging
import json
import yaml
import os

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "estimate_config.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

# 工数マスタ
FEATURE_MAN_DAYS = {
    "auth": 5,              # ユーザー認証
    "list_search": 3,       # 一覧表示・検索
    "detail_view": 2,       # 詳細表示
    "crud": 4,              # CRUD操作
    "payment": 8,           # 決済機能
    "push_notification": 3, # プッシュ通知
    "realtime": 5,          # リアルタイム機能
    "external_api": 3,      # 外部API連携
    "data_migration": 5,    # データ移行
    "admin_panel": 10,      # 管理画面
}

# JP Label -> English Key
FEATURE_LABEL_MAP = {
    "ユーザー認証": "auth",
    "一覧表示・検索": "list_search",
    "詳細表示": "detail_view",
    "CRUD操作": "crud",
    "決済機能": "payment",
    "プッシュ通知": "push_notification",
    "リアルタイム機能": "realtime",
    "外部API連携": "external_api",
    "データ移行": "data_migration",
    "管理画面": "admin_panel",
}

PHASE2_ITEMS = {
    "ia_design": {"type": "fixed", "man_days": 3},      # IA設計
    "wireframe": {"type": "per_screen", "man_days": 0.5}, # WF作成
    "figma": {"type": "per_screen", "man_days": 0.3},   # Figma化
}

PHASE2_LABEL_MAP = {
    "IA設計": "ia_design",
    "WF作成": "wireframe",
    "Figma化": "figma",
}

PHASE3_ITEMS = {
    "ui_design": {"type": "per_screen", "man_days": 1.0}, # UIデザイン
    "design_system": {"type": "fixed", "man_days": 5},    # デザインシステム
    "prototype": {"type": "fixed", "man_days": 2},        # プロトタイプ
    "logo_icon": {"type": "fixed", "man_days": 3},        # アイコン・ロゴ
}

PHASE3_LABEL_MAP = {
    "UIデザイン": "ui_design",
    "デザインシステム": "design_system",
    "プロトタイプ": "prototype",
    "アイコン・ロゴ": "logo_icon",
}

def resolve_keys(input_list, label_map, item_dict):
    """JPラベルを英語キーに変換し、有効なキーのみを抽出する"""
    resolved = []
    for item in input_list:
        if item in item_dict:
            resolved.append(item)
            continue
        mapped = label_map.get(item)
        if mapped and mapped in item_dict:
            resolved.append(mapped)
    return list(set(resolved))

def main_logic(req_body):
    config = load_config()
    
    # Common Params
    method = req_body.get('method', 'screen') 
    complexity = req_body.get('complexity', 'medium')
    screen_count = req_body.get('screen_count', 10) 
    confidence = req_body.get('confidence') 
    
    # Method-specific Params
    man_days_per_unit = req_body.get('man_days_per_unit') 
    loc = req_body.get('loc') 
    fp_count = req_body.get('fp_count') 

    # Resolve keys
    selected_features = resolve_keys(req_body.get('features', []), FEATURE_LABEL_MAP, FEATURE_MAN_DAYS)
    selected_phase2 = resolve_keys(req_body.get('phase2_items', []), PHASE2_LABEL_MAP, PHASE2_ITEMS)
    selected_phase3 = resolve_keys(req_body.get('phase3_items', []), PHASE3_LABEL_MAP, PHASE3_ITEMS)

    # Policy Check
    policy = config.get('policy', {})
    require_explicit_prod = policy.get('require_explicit_productivity_for_step_fp', True)
    require_explicit_conf = policy.get('require_explicit_vendor_confidence', True)

    # Validate Confidence if Phase 3 (Vendor Design) items present
    has_phase3_items = (len(selected_phase3) > 0)
    if require_explicit_conf and has_phase3_items and not confidence:
         return {"status": "error", "message": "Missing required param: confidence (Required for Phase 3 / Vendor Design estimation)"}, 400

    # Config Values
    diff_multipliers = config.get('difficulty_multipliers', {})
    if complexity not in diff_multipliers: complexity = 'medium'
    diff_multiplier = diff_multipliers.get(complexity, 1.0)
    
    buffer_multiplier = config.get('buffer_multiplier', 1.1)
    
    daily_rates = config.get('daily_rates', {})
    sier_rate = daily_rates.get('sier_internal', 50000)
    outsource_rate = daily_rates.get('outsource', 80000)
    
    design_config = config.get('design', {})
    mgmt_fee_rate = design_config.get('phase3_management_fee_rate', 0.15)
    vendor_variance_map = design_config.get('vendor_variance', {})
    
    # Variance Factor (Only for Phase 3)
    variance = 0.0
    if has_phase3_items:
        variance = vendor_variance_map.get(confidence, 0.2) 

    dev_config = config.get('development', {})
    dev_screen_rate = dev_config.get('man_days_per_screen', 1.5)

    # ===== Development Cost (Fixed) =====
    dev_feature_days = 0 
    dev_screen_days = 0
    dev_base_days = 0 

    if method == 'step':
        if require_explicit_prod and (loc is None or man_days_per_unit is None):
             return {"status": "error", "message": "Missing required params for STEP: loc, man_days_per_unit"}, 400
        dev_base_days = loc * man_days_per_unit
        
    elif method == 'fp':
        if require_explicit_prod and (fp_count is None or man_days_per_unit is None):
             return {"status": "error", "message": "Missing required params for FP: fp_count, man_days_per_unit"}, 400
        dev_base_days = fp_count * man_days_per_unit
        
    else:
        dev_feature_days = sum(FEATURE_MAN_DAYS.get(f, 0) for f in selected_features)
        dev_screen_days = screen_count * dev_screen_rate
        dev_base_days = dev_feature_days + dev_screen_days

    dev_total_days = dev_base_days * diff_multiplier
    dev_cost = int(dev_total_days * sier_rate)

    # ===== Phase 2 (Design) (Fixed - Internal) =====
    phase2_total_days = 0
    phase2_cost = 0
    
    if selected_phase2:
        p2_fixed = 0
        p2_screen = 0
        for item in selected_phase2:
            item_info = PHASE2_ITEMS.get(item, {})
            if item_info.get("type") == "fixed":
                p2_fixed += item_info.get("man_days", 0)
            else:
                p2_screen += item_info.get("man_days", 0) * screen_count
        
        phase2_total_days = p2_fixed + p2_screen
        phase2_cost = int(phase2_total_days * sier_rate)

    # ===== Phase 3 (Visual) (Range - Vendor) =====
    phase3_total_days = 0
    phase3_cost = 0
    phase3_range = {"min": 0, "max": 0, "cost": 0}

    if selected_phase3:
        p3_fixed = 0
        p3_screen = 0
        for item in selected_phase3:
            item_info = PHASE3_ITEMS.get(item, {})
            if item_info.get("type") == "fixed":
                p3_fixed += item_info.get("man_days", 0)
            else:
                p3_screen += item_info.get("man_days", 0) * screen_count
        
        phase3_total_days = p3_fixed + p3_screen
        phase3_base_cost = int(phase3_total_days * outsource_rate)
        phase3_management_fee = int(phase3_base_cost * mgmt_fee_rate)
        phase3_cost = phase3_base_cost + phase3_management_fee
        
        # Apply Variance
        phase3_range = {
            "min": int(phase3_cost * (1 - variance)),
            "max": int(phase3_cost * (1 + variance)),
            "cost": phase3_cost
        }

    # ===== Total =====
    # Dev: Fixed. P2: Fixed. P3: Range.
    subtotal_nominal = dev_cost + phase2_cost + phase3_cost
    subtotal_min = dev_cost + phase2_cost + phase3_range.get("min", 0)
    subtotal_max = dev_cost + phase2_cost + phase3_range.get("max", 0)

    final_nominal = int(subtotal_nominal * buffer_multiplier)
    final_min = int(subtotal_min * buffer_multiplier)
    final_max = int(subtotal_max * buffer_multiplier)

    complexity_labels = {
        "low": "簡易", "medium": "標準", "high": "高難度"
    }

    response_data = {
        "status": "ok",
        "estimated_amount": final_nominal,
        "estimated_range": {"min": final_min, "max": final_max},
        "currency": config.get('currency', 'JPY'),
        "method": method,
        "screen_count": screen_count,
        "complexity": complexity,
        "confidence": confidence,
        "breakdown": {
            "development": {
                "method": method,
                "base_days": dev_base_days,
                "total_days": dev_total_days,
                "cost": dev_cost,
                "details": {
                    "loc": loc,
                    "fp_count": fp_count,
                    "man_days_per_unit": man_days_per_unit,
                    "feature_days": dev_feature_days,
                    "screen_days": dev_screen_days
                }
            },
            "phase2_design": {
                "total_days": phase2_total_days,
                "cost": phase2_cost,
                "selected_items": selected_phase2
            },
            "phase3_visual": {
                "total_days": phase3_total_days,
                "cost": phase3_cost,
                "range": phase3_range,
                "selected_items": selected_phase3
            },
            "subtotal": subtotal_nominal,
            "buffer_multiplier": buffer_multiplier,
            "final": final_nominal,
            "complexity_label": complexity_labels.get(complexity, complexity)
        },
        "config_version": config.get('config_version', '2026-01')
    }
    return response_data, 200

@app.route(route="calculate_estimate", methods=["POST", "OPTIONS"])
def calculate_estimate(req: func.HttpRequest) -> func.HttpResponse:
    if req.method == "OPTIONS":
        return func.HttpResponse(
            "",
            status_code=200,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type"
            }
        )
    
    logging.info('Processing estimation calculation request.')

    try:
        req_body = req.get_json()
    except ValueError:
        return func.HttpResponse(
            json.dumps({"status": "error", "message": "Invalid JSON"}),
            status_code=400,
            mimetype="application/json"
        )

    result_data, status_code = main_logic(req_body)

    return func.HttpResponse(
        json.dumps(result_data, ensure_ascii=False),
        status_code=status_code,
        mimetype="application/json",
        headers={
            "Access-Control-Allow-Origin": "*"
        }
    )
