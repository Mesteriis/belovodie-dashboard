"""Browser-local panel scale, composed with the existing Button Card runtime."""
from copy import deepcopy
import json


def scale_state(url_path):
    key = json.dumps(f"belovodie:scale:v2:{url_path}")
    legacy_key = json.dumps(f"belovodie:scale:{url_path}")
    return f"""const normalize = value => {{
  const number = Number(value);
  return value === null || value === '' || !Number.isFinite(number)
    ? 100 : Math.max(50, Math.min(150, Math.round(number / 5) * 5));
}};
const migrate = value => value === null || value === '' || !Number.isFinite(Number(value))
  ? 100 : normalize(Number(value) / 0.8);
let stored = null;
try {{
  stored = window.localStorage.getItem({key});
  if (stored === null) stored = migrate(window.localStorage.getItem({legacy_key}));
}}
catch (error) {{ /* The explicit URL remains usable without browser storage. */ }}
const parameters = new URLSearchParams(window.location.search);
const override = parameters.get('bc_scale');
const scale = override === null ? normalize(stored)
  : parameters.get('bc_scale_base') === '80' ? normalize(override) : migrate(override);
"""


def scale_action(url_path, delta=None):
    """Update only marked preset elements; leave native HA/browser zoom alone."""
    if delta not in (-5, 5, None):
        raise ValueError("Scale changes use five-point steps or reset")
    scope = json.dumps(url_path)
    key = json.dumps(f"belovodie:scale:v2:{url_path}")
    target = "100" if delta is None else f"normalize(scale + ({delta}))"
    return scale_state(url_path) + f"""const next = {target};
try {{ window.localStorage.setItem({key}, String(next)); }}
catch (error) {{ console.warn('Belovodie: scale uses the URL because browser storage is unavailable.'); }}
const url = new URL(window.location.href);
url.searchParams.set('bc_scale', String(next));
url.searchParams.set('bc_scale_base', '80');
window.history.replaceState(window.history.state, '', url.href);
// Dialogs are portalled outside the canvas, so find our controls in open roots.
const visit = root => {{
  for (const element of root.querySelectorAll('*')) {{
    if (element.getAttribute('data-bc-viewport') === {scope}) {{
      element.style.setProperty('--bc-ui-scale', String(next * 80 / 10000));
    }}
    if (element.getAttribute('data-bc-scale-control') === {scope}) {{
      element.textContent = next + '%';
    }}
    if (element.shadowRoot) visit(element.shadowRoot);
  }}
}};
visit(document);
"""


def scale_controls(url_path):
    scope = json.dumps(url_path)
    state = scale_state(url_path)

    def control(name, icon=None, delta=None, reset=False, value=False):
        card = {"type": "custom:button-card", "show_icon": bool(icon),
                "show_name": True, "show_state": False, "name": name,
                "styles": {"card": [{"height": "56px"}, {"padding": "8px 12px"},
                                    {"border-radius": "12px"}, {"background": "#173d50"},
                                    {"border": "1px solid #24576b"}],
                           "name": [{"font-size": "18px"}, {"color": "#dceef5"}],
                           "icon": [{"width": "24px"}, {"color": "#48c7ef"}]},
                "tap_action": {"action": "none"},
                "extra_styles": "ha-card::before,ha-card::after{display:none!important;content:none!important}"}
        if icon:
            card["icon"] = icon
            card["styles"]["grid"] = [{"grid-template-areas": '"i n"'},
                                     {"grid-template-columns": "28px minmax(0,1fr)"}]
        if value:
            card["show_name"] = False
            card["custom_fields"] = {"value": "[[[ " + state +
                "return html`<output data-bc-scale-control=${" + scope + "}>${scale}%</output>`; ]]]"}
            card["styles"]["grid"] = [{"grid-template-areas": '"value"'}, {"grid-template-columns": "1fr"}]
            card["styles"]["custom_fields"] = {"value": [{"font-size": "18px"}, {"color": "#dceef5"}]}
        elif delta is not None or reset:
            card["tap_action"] = {"action": "javascript", "javascript":
                                  "[[[ " + scale_action(url_path, delta) + " ]]]"}
        return card

    return [{"type": "custom:layout-card", "layout_type": "custom:grid-layout",
             "layout": {"grid-template-columns": "minmax(0,1fr) 100px minmax(0,1fr)",
                        "grid-gap": "8px", "margin": "0", "padding": "0", "card_margin": "0"},
             "cards": [control("Уменьшить", "mdi:minus", -5), control("100%", value=True),
                       control("Увеличить", "mdi:plus", 5)]},
            control("Сбросить к 100%", "mdi:restore", reset=True)]


def scale_canvas(card, url_path):
    scope = json.dumps(url_path)
    state = scale_state(url_path)
    return {"type": "custom:button-card", "show_icon": False, "show_name": False,
            "show_state": False, "tap_action": {"action": "none"},
            "hold_action": {"action": "none"}, "double_tap_action": {"action": "none"},
            # Button Card must not evaluate the nested cards' templates with the
            # wrapper's empty entity context. Each child evaluates its own config.
            "custom_fields": {"dashboard": {"card": deepcopy(card), "do_not_eval": True}},
            "styles": {"card": [{"zoom": "var(--bc-ui-scale,0.8)"},
                                {"width": "100%"}, {"height": "100%"},
                                {"box-sizing": "border-box"}, {"padding": "0"},
                                {"border": "none"}, {"background": "transparent"},
                                {"box-shadow": "none"}, {"border-radius": "0"}],
                       "grid": [{"height": "100%"}, {"grid-template-areas": '"dashboard"'},
                                {"grid-template-columns": "minmax(0,1fr)"},
                                {"grid-template-rows": "minmax(0,1fr)"}],
                       "custom_fields": {"dashboard": [{"height": "100%"}, {"min-height": "0"},
                                                       {"min-width": "0"}, {"text-align": "initial"}]}},
            "extra_styles": "[[[ " + state + f"this.setAttribute('data-bc-viewport', {scope}); " +
                            "this.style.setProperty('--bc-ui-scale', String(scale * 80 / 10000)); return " +
                            json.dumps(":host{display:block;width:100%!important;max-width:none!important;"
                                       "height:100%;min-height:0;min-width:0}"
                                       "ha-card::before,ha-card::after{display:none!important;content:none!important}") + "; ]]]"}
