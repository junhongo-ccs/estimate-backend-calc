import unittest
import json
import os
import yaml
from function_app import main_logic

class TestEstimateCalculation(unittest.TestCase):
    def setUp(self):
        # Load config to verify expected values
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "estimate_config.yaml")
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)

    def test_calculate_medium_complexity(self):
        # 15 screens * 120,000 * 1.0 (medium) * 1.1 (buffer) = 1,980,000
        req_body = {'screen_count': 15, 'complexity': 'medium'}
        data, status_code = main_logic(req_body)
        
        self.assertEqual(status_code, 200)
        self.assertEqual(data['status'], 'ok')
        self.assertEqual(data['estimated_amount'], 1980000)
        self.assertEqual(data['breakdown']['difficulty_multiplier'], 1.0)

    def test_calculate_low_complexity(self):
        # 10 screens * 120,000 * 0.8 (low) * 1.1 (buffer) = 1,056,000
        req_body = {'screen_count': 10, 'complexity': 'low'}
        data, status_code = main_logic(req_body)
        
        self.assertEqual(status_code, 200)
        self.assertEqual(data['estimated_amount'], 1056000)
        self.assertEqual(data['breakdown']['difficulty_multiplier'], 0.8)

    def test_calculate_high_complexity(self):
        # 20 screens * 120,000 * 1.3 (high) * 1.1 (buffer) = 3,432,000
        req_body = {'screen_count': 20, 'complexity': 'high'}
        data, status_code = main_logic(req_body)
        
        self.assertEqual(status_code, 200)
        self.assertEqual(data['estimated_amount'], 3432000)
        self.assertEqual(data['breakdown']['difficulty_multiplier'], 1.3)

    def test_invalid_complexity(self):
        req_body = {'screen_count': 10, 'complexity': 'impossible'}
        data, status_code = main_logic(req_body)
        
        self.assertEqual(status_code, 400)
        self.assertEqual(data['status'], 'error')

    def test_invalid_screen_count(self):
        req_body = {'screen_count': 0, 'complexity': 'medium'}
        data, status_code = main_logic(req_body)
        
        self.assertEqual(status_code, 400)

if __name__ == '__main__':
    unittest.main()
