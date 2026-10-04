import json
from pathlib import Path
import subprocess
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from chrome import interface_control, interface_state, kiosk_config


class InterfaceTests(unittest.TestCase):
    def run_js(self, script):
        return json.loads(subprocess.check_output(["node", "-e", script], text=True))

    def test_defaults_and_preferences_are_scoped_to_the_browser_and_dashboard(self):
        state = json.dumps(interface_state("dashboard-example") + "return shown;")
        hidden = json.dumps(kiosk_config("dashboard-example")["hide_header"][3:-3])
        result = self.run_js(f"""
const visible = new Function('window', {state});
const hidden = new Function('window', {hidden});
const values = new Map();
const window = {{location: {{search: ''}}, localStorage: {{getItem: key => values.get(key)}}}};
const defaults = [visible(window), hidden(window)];
values.set('belovodie:ha-ui:other-dashboard', 'shown');
const otherDashboard = visible(window);
values.set('belovodie:ha-ui:dashboard-example', 'shown');
const remembered = [visible(window), hidden(window)];
window.localStorage = {{getItem: () => null}};
console.log(JSON.stringify([defaults, otherDashboard, remembered, visible(window)]));
""")
        self.assertEqual(result, [[False, True], False, [True, False], False])

    def test_toggle_survives_navigation_and_reload_and_preserves_other_url_values(self):
        control = interface_control("dashboard-example")
        action = json.dumps(control["tap_action"]["javascript"][3:-3])
        state = json.dumps(interface_state("dashboard-example") + "return shown;")
        result = self.run_js(f"""
const toggle = new Function('window', {action});
const visible = new Function('window', {state});
const values = new Map();
let url = new URL('https://example.invalid/dashboard-example/home?edit=1&other=value#section');
const window = {{localStorage: {{getItem: key => values.get(key), setItem: (key, value) => values.set(key, value)}},
  location: {{get search() {{ return url.search; }}, get href() {{ return url.href; }}, assign: value => {{url = new URL(value);}}}}}};
toggle(window);
const showing = [visible(window), url.searchParams.has('disable_km'), url.searchParams.has('edit'), url.searchParams.get('other'), url.hash];
url = new URL('https://example.invalid/dashboard-example/rooms');
const afterNavigation = visible(window);
toggle(window);
const hiding = [visible(window), url.searchParams.has('kiosk'), url.searchParams.has('disable_km')];
url = new URL('https://example.invalid/dashboard-example/home');
console.log(JSON.stringify([showing, afterNavigation, hiding, visible(window)]));
""")
        self.assertEqual(result, [[True, True, False, "value", "#section"], True,
                                  [False, True, False], False])

    def test_url_override_and_blocked_storage_still_allow_both_actions(self):
        action = json.dumps(interface_control("dashboard-example")["tap_action"]["javascript"][3:-3])
        state = json.dumps(interface_state("dashboard-example") + "return shown;")
        result = self.run_js(f"""
const visible = new Function('window', {state});
const toggle = new Function('window', 'console', {action});
let url = new URL('https://example.invalid/dashboard-example/home?disable_km');
const window = {{localStorage: {{getItem: () => {{throw new Error('Blocked');}}, setItem: () => {{throw new Error('Blocked');}}}},
  location: {{get search() {{return url.search;}}, get href() {{return url.href;}}, assign: value => {{url = new URL(value);}}}}}};
const explicitOverride = visible(window);
toggle(window, {{warn: () => {{}}}});
const hidden = visible(window);
toggle(window, {{warn: () => {{}}}});
console.log(JSON.stringify([explicitOverride, hidden, visible(window)]));
""")
        self.assertEqual(result, [True, False, True])

    def test_control_labels_match_the_current_state_without_device_actions(self):
        control = interface_control("dashboard-example")
        name = json.dumps(control["name"][3:-3])
        result = self.run_js(f"""
const name = new Function('window', {name});
const window = {{location: {{search: ''}}, localStorage: {{getItem: () => null}}}};
const hidden = name(window);
window.location.search = '?disable_km';
console.log(JSON.stringify([hidden, name(window)]));
""")
        self.assertEqual(result, ["Показать интерфейс HA", "Скрыть интерфейс HA"])
        self.assertEqual(control["tap_action"]["action"], "javascript")
        self.assertNotIn("service", control["tap_action"])


if __name__ == "__main__":
    unittest.main()
