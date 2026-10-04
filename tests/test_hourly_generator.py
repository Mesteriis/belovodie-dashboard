import json
from pathlib import Path
import subprocess
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from compose import hourly_generator, styled, visual_tile


class HourlyForecastTests(unittest.TestCase):
    def generate(self, state, values):
        code = hourly_generator("precipitation")
        source = "const fn = new Function('entity','start','end'," + json.dumps(code) + ");"
        source += "console.log(JSON.stringify(fn(" + json.dumps({"state": state, "attributes": {
            "hourly": {"time": [0, 3600, 7200, 10800], "precipitation": values}}})
        source += ",new Date(3600000),new Date(10800000))));"
        return json.loads(subprocess.check_output(["node", "-e", source], text=True))

    def test_horizon_keeps_zero_and_missing_values_distinct(self):
        self.assertEqual(self.generate("1.0", [9, 0, None, 5]), [[3600000, 0], [7200000, None]])
        self.assertEqual(self.generate("1.0", [9, "0.4", "bad", 5]), [[3600000, 0.4]])

    def test_unavailable_provider_does_not_reuse_stale_forecast(self):
        self.assertEqual(self.generate("unavailable", [9, 0, 2, 5]), [])

    def test_explicit_nested_styling_does_not_mutate_card(self):
        card = {"type": "custom:apexcharts-card"}
        result = styled(card, "ha-card{border:none}", "apexcharts-card")
        self.assertIn("apexcharts-card$", result["card_mod"]["style"])
        result["card"]["name"] = "changed"
        self.assertNotIn("name", card)

    def test_native_tile_keeps_features_actions_and_private_binding(self):
        card = {"type": "tile", "entity": "input_boolean.example",
                "tap_action": {"action": "more-info"},
                "features": [{"type": "toggle"}]}
        before = json.dumps(card)
        content = visual_tile(card)["card"]
        self.assertEqual(content["entity"], card["entity"])
        self.assertEqual(content["tap_action"], card["tap_action"])
        self.assertEqual(content["features"], card["features"])
        content["features"].clear()
        self.assertEqual(json.dumps(card), before)
