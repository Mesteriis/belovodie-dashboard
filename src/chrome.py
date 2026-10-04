"""Per-browser dashboard chrome using Kiosk Mode and Button Card templates."""
import json


def interface_state(url_path):
    key = json.dumps(f"belovodie:ha-ui:{url_path}")
    return f"""const parameters = new URLSearchParams(window.location.search);
let shown = parameters.has('disable_km');
if (!shown) {{
  try {{ shown = window.localStorage.getItem({key}) === 'shown'; }}
  catch (error) {{ shown = false; }} // Storage unavailable: use the URL or default.
}}
"""


def kiosk_config(url_path):
    hidden = "[[[ " + interface_state(url_path) + "return !shown; ]]]"
    return {"hide_header": hidden, "hide_sidebar": hidden}


def interface_control(url_path):
    state = interface_state(url_path)
    key = json.dumps(f"belovodie:ha-ui:{url_path}")
    action = state + f"""const next = !shown;
const url = new URL(window.location.href);
// Explicit URL overrides remain a fallback if the browser blocks storage.
for (const parameter of ['disable_km', 'kiosk', 'hide_header', 'hide_sidebar', 'cache', 'edit']) {{
  url.searchParams.delete(parameter);
}}
url.searchParams.set(next ? 'disable_km' : 'kiosk', '');
try {{ window.localStorage.setItem({key}, next ? 'shown' : 'hidden'); }}
catch (error) {{ console.warn('Belovodie: interface choice uses the URL because browser storage is unavailable.'); }}
// Reload resources as well as the Kiosk Mode configuration.
window.location.assign(url.href);
"""
    return {"type": "custom:button-card", "template": "bc_action",
            "name": "[[[ " + state + "return shown ? 'Скрыть интерфейс HA' : 'Показать интерфейс HA'; ]]]",
            "show_icon": True,
            "icon": "[[[ " + state + "return shown ? 'mdi:fullscreen' : 'mdi:page-layout-sidebar-left'; ]]]",
            "tap_action": {"action": "javascript", "javascript": "[[[ " + action + " ]]]"}}
