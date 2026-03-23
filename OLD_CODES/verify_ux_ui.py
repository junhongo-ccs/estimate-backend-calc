from function_app import main_logic
import yaml
import os

def test_backend():
    print("--- Testing Backend UX/UI Scoping ---")
    
    cases = [
        {
            "name": "Standard (Phase 2 & 3 included)",
            "req": {"screen_count": 10, "complexity": "medium", "include_phase2": True, "include_phase3": True}
        },
        {
            "name": "Phase 3 only (Client has wireframes)",
            "req": {"screen_count": 10, "complexity": "medium", "include_phase2": False, "include_phase3": True}
        },
        {
            "name": "Phase 2 only (No UI design needed)",
            "req": {"screen_count": 10, "complexity": "medium", "include_phase2": True, "include_phase3": False}
        },
        {
            "name": "Zero Design (Ready for dev)",
            "req": {"screen_count": 10, "complexity": "medium", "include_phase2": False, "include_phase3": False}
        }
    ]
    
    for case in cases:
        data, status = main_logic(case["req"])
        print(f"\nCase: {case['name']}")
        print(f"Request: {case['req']}")
        if status == 200:
            print(f"Total: {data['estimated_amount']:,} {data['currency']}")
            print(f"Breakdown: P2={data['breakdown']['phase2_internal_sier']:,}, P3={data['breakdown']['phase3_external_outsource']:,}")
        else:
            print(f"Error: {data}")

if __name__ == "__main__":
    test_backend()
