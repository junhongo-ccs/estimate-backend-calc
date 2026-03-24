import unittest

from pricing_simulator_input import (
    attach_pricing_simulator_input,
    build_pricing_simulator_input,
)


class TestPricingSimulatorInput(unittest.TestCase):
    def test_build_pricing_simulator_input_uses_total_business_cost(self):
        estimation_result = {
            "profit_analysis": {
                "sales": 53337500,
                "cogs": 35337500,
                "total_sga_cost": 8000000,
            },
            "input_echo": {
                "target_margin": "20.0%",
            },
        }

        payload = build_pricing_simulator_input(
            estimation_result,
            project_name="案件A",
            currency="JPY",
        )

        self.assertEqual(payload["project_name"], "案件A")
        self.assertEqual(payload["cost"], 43337500)
        self.assertEqual(payload["current_sales"], 53337500)
        self.assertEqual(payload["target_margin"], 0.2)
        self.assertEqual(payload["currency"], "JPY")

    def test_explicit_target_margin_takes_priority(self):
        estimation_result = {
            "profit_analysis": {
                "sales": 60000000,
                "cogs": 30000000,
                "total_sga_cost": 5000000,
            },
            "input_echo": {
                "target_margin": "15.0%",
            },
        }

        payload = build_pricing_simulator_input(
            estimation_result,
            project_name="案件B",
            target_margin=0.25,
            currency="JPY",
        )

        self.assertEqual(payload["target_margin"], 0.25)

    def test_attach_pricing_simulator_input_to_success_result(self):
        estimation_result = {
            "status": "success",
            "profit_analysis": {
                "sales": 31921098,
                "cogs": 29019180,
                "total_sga_cost": 15424804,
            },
            "input_echo": {
                "target_margin": "20.0%",
            },
        }

        enriched = attach_pricing_simulator_input(estimation_result)

        self.assertIn("pricing_simulator_input", enriched)
        self.assertEqual(enriched["pricing_simulator_input"]["current_sales"], 31921098)
        self.assertEqual(enriched["pricing_simulator_input"]["cost"], 44443984)
        self.assertEqual(enriched["pricing_simulator_input"]["target_margin"], 0.2)

    def test_existing_pricing_simulator_input_is_preserved(self):
        estimation_result = {
            "status": "success",
            "pricing_simulator_input": {
                "project_name": "既存案件",
                "cost": 1,
                "current_sales": 2,
                "currency": "JPY",
            },
        }

        enriched = attach_pricing_simulator_input(estimation_result)

        self.assertEqual(enriched["pricing_simulator_input"]["project_name"], "既存案件")


if __name__ == "__main__":
    unittest.main()
