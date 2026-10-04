import json
from pathlib import Path
import subprocess
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from compose import compact_controls, compose, grid, metric, modal, visual_tile
from screen import Screen


class CompositionTests(unittest.TestCase):
    def content(self, view):
        return view["cards"][0]["custom_fields"]["dashboard"]["card"]

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
            self.assertIn("--kiosk-header-height", v["layout"]["height"])
            content = self.content(v)
            navigation = content["cards"][0]
            more = next(c for c in navigation["cards"] if c.get("view_layout", {}).get("grid-area") == "more")
            control = more["body"]["cards"][0]["cards"][0]
            self.assertEqual(control["tap_action"]["action"], "javascript")
            self.assertIn("belovodie:ha-ui:dashboard-example", control["tap_action"]["javascript"])
            dock = next(c for c in content["cards"] if c.get("view_layout", {}).get("grid-area") == "dock")
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
        script += "fn({state:'<img>'}, {}, {},h),"
        script += "fn({state:'0'}, {guard_entities:['sensor.a','sensor.b']}, {'sensor.a':{state:'0'},'sensor.b':{state:'unknown'}},h),"
        script += "fn({state:'0'}, {guard_entities:['sensor.a','sensor.b']}, {'sensor.a':{state:'0'},'sensor.b':{state:'0'}},h)]));"
        values = json.loads(subprocess.check_output(["node", "-e", script], text=True))
        self.assertEqual(values, ["—", "—", "0", "—", "&lt;img&gt;", "—", "0"])

    def test_optional_last_card_releases_footer_space_on_both_layouts(self):
        for missing in (True, False):
            with self.subTest(missing=missing):
                pages = json.loads(json.dumps(self.pages))
                if missing:
                    pages[0].pop("last")
                else:
                    pages[0]["last"] = None
                result = compose(self.original, pages, "dashboard-example")
                home = self.content(result["views"][0])
                self.assertFalse(any(c.get("view_layout", {}).get("grid-area") == "last"
                                     for c in home["cards"]))
                self.assertIn('"footer footer footer footer"', home["layout"]["grid-template-areas"])
                compact = home["layout"]["mediaquery"]["(max-width: 1056px)"]
                self.assertIn('"footer footer"', compact["grid-template-areas"])
                other = self.content(result["views"][1])
                self.assertEqual(other, self.content(compose(self.original, self.pages,
                                                           "dashboard-example")["views"][1]))

    def test_screen_parameter_changes_calibration_without_fixed_page_dimensions(self):
        desktop = compose(self.original, self.pages, "dashboard-example")
        tablet = compose(self.original, self.pages, "dashboard-example", screen=Screen(1280, 800))
        desktop_metric = self.content(desktop["views"][0])["cards"][1]
        tablet_metric = self.content(tablet["views"][0])["cards"][1]
        desktop_css = desktop["button_card_templates"]["bc_action"]["extra_styles"]
        tablet_css = tablet["button_card_templates"]["bc_action"]["extra_styles"]
        self.assertIn("1.3636vw", desktop_css)
        self.assertIn("2.3438vw", tablet_css)
        self.assertIn("@media(max-width:1650px),(max-height:900px)", tablet_css)
        self.assertIn("--bc-value:min(clamp", tablet_css)
        self.assertNotIn("extra_styles", tablet_metric)
        self.assertEqual(desktop_metric["tap_action"], tablet_metric["tap_action"])
        self.assertEqual(desktop_metric["entity"], tablet_metric["entity"])
        self.assertEqual(desktop["views"][0]["layout"], tablet["views"][0]["layout"])
        self.assertIn("100dvh", tablet["views"][0]["layout"]["height"])

    def test_compact_navigation_retains_routes_hidden_from_header(self):
        more_pages = self.pages + [{**self.pages[0], "path": "third", "title": "Third"}]
        original = {"views": [{"path": p["path"]} for p in more_pages]}
        result = compose(original, more_pages, "dashboard-example")
        content = self.content(result["views"][0])
        navigation = content["cards"][0]
        more = next(c for c in navigation["cards"] if c.get("view_layout", {}).get("grid-area") == "more")
        links = more["body"]["cards"][0]["cards"]
        routes = {c.get("tap_action", {}).get("navigation_path") for c in links}
        self.assertIn("/dashboard-example/room", routes)
        self.assertIn("/dashboard-example/third", routes)
        self.assertIn("/config", routes)
        compact = content["layout"]["mediaquery"]["(max-width: 1056px)"]
        self.assertIn('"dock dock"', compact["grid-template-areas"])
        self.assertIn('"stat0 stat1" "stat2 stat3"', compact["grid-template-areas"])

    def test_invalid_screen_configuration_fails_before_rendering(self):
        self.assertEqual(Screen.parse("1280x800"), Screen(1280, 800))
        self.assertEqual(Screen.parse("2200×1440"), Screen())
        for value in ("0x800", "1280x-1", "1280x800px", "20000x1440", "auto"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                Screen.parse(value)
        with self.assertRaises(ValueError):
            compose(self.original, self.pages, "dashboard-example", screen=0)

    def test_grid_media_queries_match_browser_normalized_feature_keys(self):
        queries = {"(max-width:1056px)": {"grid-template-columns": "1fr 1fr"}}
        result = grid([], mediaquery=queries)
        self.assertIn("(max-width: 1056px)", result["layout"]["mediaquery"])
        self.assertIn("(max-width:1056px)", queries)

    def test_compact_controls_retain_actions_and_do_not_stretch_entity_rows(self):
        tile = visual_tile({"type": "tile", "entity": "light.example", "features": [{"type": "light-brightness"}],
                            "tap_action": {"action": "toggle"}})
        source = grid([tile, tile], "1fr 1fr", rows="repeat(2,minmax(0,1fr))", height="100%",
                      mediaquery={"(max-width: 1056px)": {"grid-template-rows": "repeat(2,1fr)"}})
        before = json.dumps(source)
        result = compact_controls(source, dialog=False)
        self.assertEqual(before, json.dumps(source))
        self.assertEqual(result["layout"]["grid-auto-rows"], "max-content")
        self.assertEqual(result["layout"]["mediaquery"]["(max-width: 1056px)"]["grid-template-rows"], "none")
        self.assertFalse(result["cards"][0]["card"]["vertical"])
        self.assertEqual(result["cards"][0]["card"]["tap_action"], {"action": "toggle"})
        self.assertEqual(result["cards"][0]["card"]["features"], [{"type": "light-brightness"}])
        self.assertEqual(compact_controls(result, dialog=False), result)


if __name__ == "__main__":
    unittest.main()
