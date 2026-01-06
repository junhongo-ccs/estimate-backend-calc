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
    include_phase2 = req_body.get('include_phase2', True) # SIer Figma Bridge
    include_phase3 = req_body.get('include_phase3', True) # Outsourced UI

    # Validation
    if screen_count is None or not isinstance(screen_count, (int, float)) or screen_count <= 0:
        return {"status": "error", "message": "screen_count must be a positive number"}, 400

    config = load_config()
    diff_multipliers = config.get('difficulty_multipliers', {})
    
    if complexity not in diff_multipliers:
        return {"status": "error", "message": f"complexity must be one of {list(diff_multipliers.keys())}"}, 400

    # Calculation logic
    diff_multiplier = diff_multipliers[complexity]
    buffer_multiplier = config['buffer_multiplier']

    # Design Phase Calculation
    phase2_cost = 0
    phase3_cost = 0
    phase3_management_fee = 0

    if include_phase2:
        phase2_unit = config.get('phase2_cost_per_screen', 40000)
        phase2_cost = int(screen_count * phase2_unit * diff_multiplier)

    if include_phase3:
        phase3_unit = config.get('phase3_cost_per_screen', 80000)
        mgmt_rate = config.get('phase3_management_fee_rate', 0.15)
        phase3_base = int(screen_count * phase3_unit * diff_multiplier)
        phase3_management_fee = int(phase3_base * mgmt_rate)
        phase3_cost = phase3_base + phase3_management_fee

    # Development Cost (Simplified for this version, using remaining of base_cost_per_screen logic if not purely design)
    # If using full base_cost_per_screen, it includes dev + design phases.
    # We'll treat the new logic as an override.
    
    # Final Amount
    design_total = phase2_cost + phase3_cost
    final_amount = int(design_total * buffer_multiplier)

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
        "include_phase2": include_phase2,
        "include_phase3": include_phase3,
        "breakdown": {
            "phase2_internal_sier": phase2_cost,
            "phase3_external_outsource": phase3_cost,
            "phase3_management_fee": phase3_management_fee,
            "design_subtotal": design_total,
            "difficulty_multiplier": diff_multiplier,
            "buffer_multiplier": buffer_multiplier,
            "final": final_amount,
            "calculation_details": {
                "formula": f"({phase2_cost:,} [P2] + {phase3_cost:,} [P3]) × {buffer_multiplier} (buffer)",
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
