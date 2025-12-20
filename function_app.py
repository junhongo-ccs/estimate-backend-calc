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

def main_logic(req_body):
    screen_count = req_body.get('screen_count')
    complexity = req_body.get('complexity')

    # Validation
    if screen_count is None or not isinstance(screen_count, (int, float)) or screen_count <= 0:
        return {"status": "error", "message": "screen_count must be a positive number"}, 400

    config = load_config()
    diff_multipliers = config.get('difficulty_multipliers', {})
    
    if complexity not in diff_multipliers:
        return {"status": "error", "message": f"complexity must be one of {list(diff_multipliers.keys())}"}, 400

    # Calculation logic
    base_cost_per_screen = config['base_cost_per_screen']
    diff_multiplier = diff_multipliers[complexity]
    buffer_multiplier = config['buffer_multiplier']

    base_cost = screen_count * base_cost_per_screen
    diff_applied = base_cost * diff_multiplier
    final_amount = int(diff_applied * buffer_multiplier)

    # Complexity label for breakdown
    complexity_labels = {
        "low": "簡易",
        "medium": "標準",
        "high": "高難度"
    }

    response_data = {
        "status": "ok",
        "estimated_amount": final_amount,
        "currency": config['currency'],
        "screen_count": screen_count,
        "complexity": complexity,
        "breakdown": {
            "base_cost": base_cost,
            "base_cost_per_screen": base_cost_per_screen,
            "difficulty_multiplier": diff_multiplier,
            "difficulty_applied": diff_applied,
            "buffer_multiplier": buffer_multiplier,
            "final": final_amount,
            "calculation_details": {
                "formula": f"{screen_count} screens × ¥{base_cost_per_screen:,} × {diff_multiplier} (difficulty) × {buffer_multiplier} (buffer)",
                "complexity_label": complexity_labels.get(complexity, complexity)
            }
        },
        "config_version": config['config_version']
    }
    return response_data, 200

@app.route(route="calculate_estimate", methods=["POST"])
def calculate_estimate(req: func.HttpRequest) -> func.HttpResponse:
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
