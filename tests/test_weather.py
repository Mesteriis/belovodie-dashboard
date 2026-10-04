import json
from pathlib import Path
import subprocess
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from weather import animated_weather


class AnimatedWeatherTests(unittest.TestCase):
    def card(self):
        return {"type": "custom:button-card", "template": "bc_weather",
                "entity": "weather.example", "name": "Weather",
                "variables": {"feels_like_entity": "sensor.feels", "sun_entity": "sun.example"},
                "label": "existing humidity and wind formatter",
                "tap_action": {"action": "more-info"},
                "custom_fields": {"existing": "keep"},
                "styles": {"card": [{"background-image": "old art"}, {"padding": "12px"}]}}

    def test_existing_data_actions_and_dimensions_are_retained(self):
        original = self.card()
        before = json.dumps(original)
        result = animated_weather(original)
        self.assertEqual(json.dumps(original), before)
        for key in ["entity", "name", "variables", "label", "tap_action"]:
            self.assertEqual(result[key], original[key])
        self.assertEqual(result["custom_fields"]["existing"], "keep")
        self.assertIn({"padding": "12px"}, result["styles"]["card"])
        self.assertTrue(result["custom_fields"]["sky"]["do_not_eval"])
        atmo = result["custom_fields"]["sky"]["card"]["card"]
        self.assertEqual(atmo["weather_entity"], original["entity"])
        self.assertEqual(atmo["sun_entity"], "sun.example")

    def test_unavailable_data_hides_weather_animation(self):
        result = animated_weather(self.card())
        display = next(x["display"] for x in result["styles"]["custom_fields"]["sky"] if "display" in x)[3:-3]
        script = "const fn=new Function('entity'," + json.dumps(display) + ");"
        script += "console.log(JSON.stringify([null,{state:'unknown'},{state:'unavailable'},{state:'rainy'},{state:'clear-night'}].map(fn)));"
        self.assertEqual(json.loads(subprocess.check_output(["node", "-e", script], text=True)),
                         ["none", "none", "none", "block", "block"])

    def test_reduced_motion_and_non_weather_metrics(self):
        result = animated_weather(self.card())
        self.assertIn("prefers-reduced-motion:reduce", result["extra_styles"])
        self.assertIn("#sky{display:none!important}", result["extra_styles"])
        other = {"type": "custom:button-card", "template": "bc_metric", "entity": "sensor.example"}
        self.assertEqual(animated_weather(other), other)
        bad = self.card()
        bad["entity"] = "sensor.example"
        with self.assertRaises(ValueError):
            animated_weather(bad)
