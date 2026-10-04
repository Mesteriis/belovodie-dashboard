"""Compose a bounded Lovelace dashboard from existing HACS cards.

Input bindings and original cards stay on the caller's machine. No network,
credentials, device actions, or custom frontend runtime are part of this theme.
"""
from copy import deepcopy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
THEME = "Belovodie Command"


def grid(cards, columns="minmax(0,1fr)", rows=None, height=None, gap="16px"):
    layout = {"grid-template-columns": columns, "grid-gap": gap,
              "margin": "0", "padding": "0", "card_margin": "0",
              "place-items": "stretch", "min-height": "0"}
    if rows:
        layout["grid-template-rows"] = rows
    if height:
        layout["height"] = height
    return {"type": "custom:layout-card", "layout_type": "custom:grid-layout",
            "layout": layout, "cards": deepcopy(cards)}


def button(name, icon=None, action=None, template="bc_action", **kwargs):
    return {"type": "custom:button-card", "template": template,
            "name": name, "show_icon": bool(icon), "icon": icon,
            "tap_action": action or {"action": "none"}, **kwargs}


def metric(name, entity, icon, unit=None, **variables):
    return button(name, icon, {"action": "more-info"}, "bc_metric",
                  entity=entity, variables={"unit": unit, **variables})


def modal(title, icon, cards, card_id):
    return {"type": "custom:universal-card", "card_id": card_id,
            "title": title, "icon": icon, "body_mode": "modal",
            "expanded": False, "remember_expanded_state": False,
            "expand_trigger": "tap", "show_state": False,
            "show_expand_icon": True, "animation": False,
            "border_radius": "22px", "padding": "0",
            "header": {"layout": {"variant": "default"}},
            "grid": {"columns": 1, "gap": "16px"},
            "modal": {"width": "auto", "height": "auto", "max_width": "1440px",
                      "max_height": "86vh", "loading_strategy": "lazy",
                      "close_on_backdrop": True, "close_on_escape": True,
                      "show_close": True},
            "custom_css": {"scope": "global", "css": (ROOT / "src/modal.css").read_text()},
            "body": {"cards": deepcopy(cards)}}


def tabs(items, card_id, workspace=False):
    return {"type": "custom:universal-card", "card_id": card_id,
            "body_mode": "tabs", "title": "", "expanded": True,
            "expand_trigger": "none", "show_expand_icon": False,
            "remember_expanded_state": False, "remember_mode_state": False,
            "animation": False, "border_radius": "22px", "padding": "0",
            "header": {"clickable": False},
            "tabs_config": {"position": "top", "show_icons": True,
                            "show_labels": True, "content_padding": "20px",
                            "tab_min_width": "112px", "tab_alignment": "start"},
            "custom_css": {"scope": "global", "css":
                           (ROOT / "src/tabs.css").read_text() if workspace else
                           (ROOT / "src/detail-tabs.css").read_text()},
            "tabs": deepcopy(items)}


def navigation(pages, current, url_path, clock_entity=None):
    def nav(page):
        active = page["path"] == current
        return button(page["title"], action={"action": "navigate", "navigation_path":
                      f"/{url_path}/{page['path']}"}, template="bc_nav",
                      styles={"card": [{"background": "#173d50" if active else "transparent"},
                                       {"border-color": "#24576b" if active else "transparent"}],
                              "name": [{"font-weight": 600 if active else 400}]})
    main = pages[:6]
    extra = [nav(p) for p in pages[6:]] + [
        button("Редактор панели", "mdi:pencil", {"action": "navigate",
               "navigation_path": f"/{url_path}/{current}?edit=1&disable_km"}),
        button("Настройки", "mdi:cog", {"action": "navigate", "navigation_path": "/config"}),
        button("HACS", "mdi:store", {"action": "navigate", "navigation_path": "/hacs"})]
    more = modal("Ещё", "mdi:chevron-down", [grid(extra, "repeat(3,minmax(0,1fr))")],
                 f"bc-nav-{current}")
    more["custom_css"]["css"] += "\n.header{height:100%;padding:0 22px!important}.header-title{font-size:var(--bc-font)!important}.header-icon{display:none}"
    logo = button("", "mdi:home-assistant", {"action": "navigate",
                  "navigation_path": f"/{url_path}/{pages[0]['path']}"}, "bc_brand")
    clock = button("", template="bc_clock", entity=clock_entity,
                   show_label=True, show_name=False,
                   label="[[[ return new Date().toLocaleDateString(hass.locale.language,{weekday:'short',day:'numeric',month:'long',year:'numeric'}); ]]]",
                   custom_fields={"time": "[[[ return entity?.state && entity.state !== 'unavailable' ? entity.state : new Date().toLocaleTimeString(hass.locale.language,{hour:'2-digit',minute:'2-digit'}); ]]]"})
    profile = button("Профиль", "mdi:account", {"action": "navigate", "navigation_path": "/profile"},
                     "bc_brand", show_name=False)
    return grid([logo, *map(nav, main), more, clock, profile],
                "80px repeat(5,minmax(100px,1fr)) minmax(215px,1.4fr) 140px minmax(210px,1.4fr) 74px",
                height="100%", gap="12px")


def compose(original, pages, url_path, clock_entity=None):
    """Only the supplied pages/cards are published to Lovelace, never to GitHub."""
    if not pages or len({p["path"] for p in pages}) != len(pages):
        raise ValueError("Pages need unique, non-empty paths")
    if {p["path"] for p in pages} != {p["path"] for p in original["views"]}:
        raise ValueError("Every original view must be accounted for")
    result = {k: deepcopy(v) for k, v in original.items() if k != "views"}
    result.setdefault("button_card_templates", {}).update(
        json.loads((ROOT / "src/button-templates.json").read_text()))
    result["kiosk_mode"] = {"hide_header": True, "hide_sidebar": True}
    result["views"] = []
    for page in pages:
        if len(page["metrics"]) != 4:
            raise ValueError("Exactly four primary metric slots are required")
        dock = deepcopy(page["dock"])
        if not dock:
            raise ValueError("A detail/navigation dock is required")
        cards = [navigation(pages, page["path"], url_path, clock_entity)]
        cards[0]["view_layout"] = {"grid-area": "nav"}
        for i, m in enumerate(page["metrics"]):
            m = deepcopy(m)
            m["view_layout"] = {"grid-area": f"stat{i}"}
            cards.append(m)
        work = tabs(page["tabs"], f"bc-work-{page['path']}", workspace=True)
        work["view_layout"] = {"grid-area": "work"}
        cards.append(work)
        sidebar = grid(dock, rows=f"repeat({len(dock)},minmax(0,1fr))", height="100%", gap="10px")
        sidebar["view_layout"] = {"grid-area": "dock"}
        cards.append(sidebar)
        footer = grid(page["footer"], "repeat(3,minmax(0,1fr))", height="100%")
        footer["view_layout"] = {"grid-area": "footer"}
        cards.append(footer)
        last = deepcopy(page["last"])
        last["view_layout"] = {"grid-area": "last"}
        cards.append(last)
        result["views"].append({"path": page["path"], "title": page["title"],
            "icon": page.get("icon", "mdi:view-dashboard"),
            "theme": THEME, "type": "custom:grid-layout", "cards": cards,
            "layout": {"height": "calc(100dvh - 32px)", "margin": "0", "padding": "16px 24px",
                "box-sizing": "border-box", "grid-template-columns": "repeat(4,minmax(0,1fr))",
                "grid-template-rows": "minmax(78px,8vh) minmax(180px,22vh) minmax(0,1fr) minmax(100px,11vh)",
                "grid-template-areas": '"nav nav nav nav" "stat0 stat1 stat2 stat3" "work work work dock" "footer footer footer last"',
                "grid-gap": "20px", "card_margin": "0", "place-items": "stretch",
                "mediaquery": {"(max-width: 1050px)": {
                    "height": "calc(100dvh - 16px)", "padding": "8px", "grid-gap": "8px",
                    "grid-template-columns": "repeat(4,minmax(0,1fr))",
                    "grid-template-rows": "64px minmax(130px,22vh) minmax(0,1fr) 86px"}}}})
    return result
