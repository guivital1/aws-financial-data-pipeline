from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class InfrastructureSafetyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.template = (ROOT / "template.yaml").read_text(encoding="utf-8")

    def test_serverless_cost_guardrails_are_declared(self):
        self.assertIn("ReservedConcurrentExecutions: 1", self.template)
        self.assertIn("BytesScannedCutoffPerQuery: 10000000", self.template)
        self.assertIn("MaxConcurrentRuns: 1", self.template)
        self.assertIn("- s3:ListBucket\n", self.template)

    def test_analytics_layer_is_managed_as_code(self):
        self.assertIn("Type: AWS::Glue::Job", self.template)
        self.assertIn("Type: AWS::Glue::Table", self.template)
        self.assertIn("Type: AWS::Athena::WorkGroup", self.template)
        self.assertIn("Name: bcb_curated", self.template)

    def test_schedule_starts_safe_and_can_be_enabled_explicitly(self):
        self.assertIn('Default: "false"', self.template)
        self.assertIn("State: !If [DailyScheduleEnabled, ENABLED, DISABLED]", self.template)
        self.assertNotIn("AWS::QuickSight", self.template)


if __name__ == "__main__":
    unittest.main()
