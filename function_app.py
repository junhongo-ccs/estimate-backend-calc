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

# 工数マスタ（RAGから取得する想定だが、ここではハードコード）
FEATURE_MAN_DAYS = {
    "ユーザー認証": 5,
    "一覧表示・検索": 3,
    "詳細表示": 2,
    "CRUD操作": 4,
    "決済機能": 8,
    "プッシュ通知": 3,
    "リアルタイム機能": 5,
    "外部API連携": 3,
    "データ移行": 5,
    "管理画面": 10,
}

PHASE2_ITEMS = {
    "IA設計": {"type": "fixed", "man_days": 3},
    "WF作成": {"type": "per_screen", "man_days": 0.5},
    "Figma化": {"type": "per_screen", "man_days": 0.3},
}

PHASE3_ITEMS = {
    "UIデザイン": {"type": "per_screen", "man_days": 1.0},
    "デザインシステム": {"type": "fixed", "man_days": 5},
    "プロトタイプ": {"type": "fixed", "man_days": 2},
    "アイコン・ロゴ": {"type": "fixed", "man_days": 3},
}

def main_logic(req_body):
    screen_count = req_body.get('screen_count', 10)
    complexity = req_body.get('complexity', 'medium')
    
    # 選択された項目
    selected_features = req_body.get('features', [])
    selected_phase2 = req_body.get('phase2_items', [])
    selected_phase3 = req_body.get('phase3_items', [])

    config = load_config()
    diff_multipliers = config.get('difficulty_multipliers', {})
    
    if complexity not in diff_multipliers:
        complexity = 'medium'
    
    diff_multiplier = diff_multipliers.get(complexity, 1.0)
    buffer_multiplier = config.get('buffer_multiplier', 1.1)
    
    # 単価
    sier_rate = config.get('sier_daily_rate', 50000)
    outsource_rate = config.get('outsource_daily_rate', 80000)
    mgmt_fee_rate = config.get('phase3_management_fee_rate', 0.15)
    dev_screen_rate = config.get('dev_man_days_per_screen', 1.5)

    # ===== 開発費用計算 =====
    dev_feature_days = sum(FEATURE_MAN_DAYS.get(f, 0) for f in selected_features)
    dev_screen_days = screen_count * dev_screen_rate * diff_multiplier
    dev_total_days = dev_feature_days + dev_screen_days
    dev_cost = int(dev_total_days * sier_rate)

    # ===== Phase 2費用計算（SIer内製） =====
    phase2_fixed_days = 0
    phase2_screen_days = 0
    for item in selected_phase2:
        item_info = PHASE2_ITEMS.get(item, {})
        if item_info.get("type") == "fixed":
            phase2_fixed_days += item_info.get("man_days", 0)
        else:
            phase2_screen_days += item_info.get("man_days", 0) * screen_count
    
    phase2_total_days = phase2_fixed_days + phase2_screen_days
    phase2_cost = int(phase2_total_days * sier_rate)

    # ===== Phase 3費用計算（外注） =====
    phase3_fixed_days = 0
    phase3_screen_days = 0
    for item in selected_phase3:
        item_info = PHASE3_ITEMS.get(item, {})
        if item_info.get("type") == "fixed":
            phase3_fixed_days += item_info.get("man_days", 0)
        else:
            phase3_screen_days += item_info.get("man_days", 0) * screen_count
    
    phase3_total_days = phase3_fixed_days + phase3_screen_days
    phase3_base_cost = int(phase3_total_days * outsource_rate)
    phase3_management_fee = int(phase3_base_cost * mgmt_fee_rate)
    phase3_cost = phase3_base_cost + phase3_management_fee

    # ===== 総額 =====
    subtotal = dev_cost + phase2_cost + phase3_cost
    final_amount = int(subtotal * buffer_multiplier)

    complexity_labels = {
        "low": "簡易",
        "medium": "標準",
        "high": "高難度"
    }

    response_data = {
        "status": "ok",
        "estimated_amount": final_amount,
        "currency": config.get('currency', 'JPY'),
        "screen_count": screen_count,
        "complexity": complexity,
        "breakdown": {
            "development": {
                "feature_days": dev_feature_days,
                "screen_days": dev_screen_days,
                "total_days": dev_total_days,
                "cost": dev_cost,
                "selected_features": selected_features
            },
            "phase2_design": {
                "fixed_days": phase2_fixed_days,
                "screen_days": phase2_screen_days,
                "total_days": phase2_total_days,
                "cost": phase2_cost,
                "selected_items": selected_phase2
            },
            "phase3_visual": {
                "fixed_days": phase3_fixed_days,
                "screen_days": phase3_screen_days,
                "total_days": phase3_total_days,
                "base_cost": phase3_base_cost,
                "management_fee": phase3_management_fee,
                "cost": phase3_cost,
                "selected_items": selected_phase3
            },
            "subtotal": subtotal,
            "buffer_multiplier": buffer_multiplier,
            "final": final_amount,
            "complexity_label": complexity_labels.get(complexity, complexity)
        },
        "config_version": config.get('config_version', '2025-12')
    }
    return response_data, 200

@app.route(route="calculate_estimate", methods=["POST", "OPTIONS"])
def calculate_estimate(req: func.HttpRequest) -> func.HttpResponse:
    # CORS preflight
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
