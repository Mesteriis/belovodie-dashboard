import json
from pathlib import Path
import subprocess
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from compose import compose, metric, modal


class CompositionTests(unittest.TestCase):
    def setUp(self):
        self.original = {"views": [{"path": "home"}, {"path": "room"}],
                         "button_card_templates": {"existing": {"show_icon": False}}}
        self.pages = [{"path": name, "title": name,
                       "metrics": [metric("Value", "sensor.example", "mdi:flash")] * 4,
                       "tabs": [{"label": "Summary", "cards": []}],
                       "dock": [modal("Details", "mdi:home", [{"type": "tile", "entity": "light.example"}], name)],
                       "footer": [], "last": metric("Value", "sensor.example", "mdi:flash")}
                      for name in ("home", "room")]

    def test_preserves_original_templates_without_mutating_input(self):
        before = json.dumps([self.original, self.pages])
        result = compose(self.original, self.pages, "dashboard-example")
        self.assertIn("existing", result["button_card_templates"])
        self.assertEqual(before, json.dumps([self.original, self.pages]))

    def test_missing_view_fails_instead_of_losing_navigation(self):
        with self.assertRaises(ValueError):
            compose(self.original, self.pages[:1], "dashboard-example")

    def test_all_pages_use_bounded_workspace_and_closed_off_flow_details(self):
        result = compose(self.original, self.pages, "dashboard-example")
        self.assertEqual([v["path"] for v in result["views"]], ["home", "room"])
        for v in result["views"]:
            self.assertIn("100dvh", v["layout"]["height"])
            dock = next(c for c in v["cards"] if c.get("view_layout", {}).get("grid-area") == "dock")
            self.assertEqual(dock["layout"]["height"], "100%")
            details = dock["cards"][0]
            self.assertEqual(details["body_mode"], "modal")
            self.assertFalse(details["expanded"])
            self.assertFalse(details["remember_expanded_state"])
            self.assertEqual(details["body"]["cards"][0]["entity"], "light.example")

    def test_formatter_distinguishes_missing_zero_and_guard_failure(self):
        templates = json.loads((Path(__file__).resolve().parents[1] / "src/button-templates.json").read_text())
        code = templates["bc_metric"]["custom_fields"]["value"][3:-3]
        script = "const fn = new Function('entity','variables','states','hass'," + json.dumps(code) + ");\n"
        script += "const h={locale:{language:'en'}}; console.log(JSON.stringify(["
        script += "fn({state:'unknown'}, {}, {},h),fn({state:'unavailable'}, {}, {},h),"
        script += "fn({state:'0'}, {}, {},h),fn({state:'12'}, {guard_entity:'sensor.guard'}, {'sensor.guard':{state:'unavailable'}},h),"
        script += "fn({state:'<img>'}, {}, {},h)]));"
        values = json.loads(subprocess.check_output(["node", "-e", script], text=True))
        self.assertEqual(values, ["—", "—", "0", "—", "&lt;img&gt;"])


if __name__ == "__main__":
    unittest.main()
