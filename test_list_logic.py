
import json
from estimate_logic import main

test_input = {
    "method": "screen",
    "complexity": "high",
    # "screen_count" is omitted to test auto-calculation
    "screens": [
        "Login", "Dashboard", "UserList", "UserDetail", "Settings"
    ],
    "features": ["auth", "crud"],
    "phase2_items": ["ia_design"],
    "phase3_items": ["ui_design"],
    "confidence": "medium"
}

print("Testing with screen list input...")
result = main(test_input)
print(json.dumps(result, indent=2, ensure_ascii=False))
