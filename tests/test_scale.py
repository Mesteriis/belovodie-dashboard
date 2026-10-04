import json
from pathlib import Path
import subprocess
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from scale import scale_action, scale_canvas, scale_controls, scale_state


class ScaleTests(unittest.TestCase):
    def run_js(self, script):
        return json.loads(subprocess.check_output(["node", "-e", script], text=True))

    def test_default_saved_value_and_url_are_bounded_to_five_point_steps(self):
        state = json.dumps(scale_state("dashboard-example") + "return scale;")
        result = self.run_js(f"""
const read = new Function('window', {state});
const window = {{location: {{search: ''}}, localStorage: {{getItem: () => null}}}};
const defaults = read(window);
const values = [50, 75, 100, 150, 5, 200, 78, 'invalid', ''];
const saved = values.map(value => {{window.localStorage.getItem = () => value; return read(window);}});
window.location.search = '?bc_scale=65';
const override = read(window);
window.localStorage.getItem = () => {{throw new Error('Blocked');}};
const blocked = read(window);
window.location.search = '';
console.log(JSON.stringify([defaults, saved, override, blocked, read(window)]));
""")
        self.assertEqual(result, [100, [50, 75, 100, 150, 50, 150, 80, 100, 100], 65, 65, 100])

    def test_changes_apply_live_to_this_panel_and_dialog_value_without_reload(self):
        minus = json.dumps(scale_action("dashboard-example", -5))
        plus = json.dumps(scale_action("dashboard-example", 5))
        reset = json.dumps(scale_action("dashboard-example"))
        result = self.run_js(f"""
const minus = new Function('window', 'document', {minus});
const plus = new Function('window', 'document', {plus});
const reset = new Function('window', 'document', {reset});
let url = new URL('https://example.invalid/dashboard-example/home?other=kept#section');
const saved = new Map();
const window = {{location: {{get search() {{return url.search;}}, get href() {{return url.href;}}}},
  localStorage: {{getItem: key => saved.get(key) ?? null, setItem: (key, value) => saved.set(key, value)}},
  history: {{state: {{existing: true}}, replaceState: (state, _, value) => {{url = new URL(value);}}}}}};
const properties = new Map();
const canvas = {{getAttribute: name => name === 'data-bc-viewport' ? 'dashboard-example' : null,
  style: {{setProperty: (name, value) => properties.set(name, value)}}}};
const label = {{getAttribute: name => name === 'data-bc-scale-control' ? 'dashboard-example' : null,
  textContent: '100%'}};
const other = {{getAttribute: () => 'other-dashboard',
  style: {{setProperty: () => {{throw new Error('Unrelated panel changed');}}}}}};
const parent = {{getAttribute: () => null, shadowRoot: {{querySelectorAll: () => [canvas, label, other]}}}};
const document = {{querySelectorAll: () => [parent]}};
minus(window, document);
const step = [saved.get('belovodie:scale:dashboard-example'), properties.get('--bc-ui-scale'), label.textContent];
for(let i = 0; i < 30; i++) minus(window, document);
const low = url.searchParams.get('bc_scale');
for(let i = 0; i < 30; i++) plus(window, document);
const high = url.searchParams.get('bc_scale');
reset(window, document);
console.log(JSON.stringify([step, low, high, url.searchParams.get('bc_scale'),
  url.searchParams.get('other'), url.hash, properties.get('--bc-ui-scale')]));
""")
        self.assertEqual(result, [["95", "0.95", "95%"], "50", "150", "100", "kept", "#section", "1"])

    def test_blocked_storage_keeps_current_view_usable(self):
        action = json.dumps(scale_action("dashboard-example", -5))
        result = self.run_js(f"""
const action = new Function('window', 'document', 'console', {action});
let url = new URL('https://example.invalid/dashboard-example/home?bc_scale=75');
const window = {{location: {{get search() {{return url.search;}}, get href() {{return url.href;}}}},
  localStorage: {{getItem: () => {{throw new Error('Blocked');}}, setItem: () => {{throw new Error('Blocked');}}}},
  history: {{state: null, replaceState: (_, __, value) => {{url = new URL(value);}}}}}};
action(window, {{querySelectorAll: () => []}}, {{warn: () => {{}}}});
console.log(JSON.stringify(url.searchParams.get('bc_scale')));
""")
        self.assertEqual(result, "70")

    def test_canvas_preserves_child_template_context_and_actions(self):
        child = {"type": "tile", "entity": "light.example", "name": "[[[ return entity.state; ]]]",
                 "tap_action": {"action": "toggle"}, "features": [{"type": "light-brightness"}]}
        before = json.dumps(child)
        canvas = scale_canvas(child, "dashboard-example")
        field = canvas["custom_fields"]["dashboard"]
        self.assertTrue(field["do_not_eval"])
        self.assertEqual(field["card"], child)
        self.assertEqual(before, json.dumps(child))
        self.assertNotIn("entity", canvas)
        self.assertEqual(canvas["tap_action"], {"action": "none"})
        for control in scale_controls("dashboard-example"):
            self.assertNotIn("entity", control)
        with self.assertRaises(ValueError):
            scale_action("dashboard-example", 10)


if __name__ == "__main__":
    unittest.main()
