"""Compose a bounded Lovelace dashboard from existing HACS cards.

Input bindings and original cards stay on the caller's machine. No network,
credentials, device actions, or custom frontend runtime are part of this theme.
"""
from copy import deepcopy
import json
from pathlib import Path
import re
from screen import Screen, apply_screen
from chrome import interface_control, kiosk_config
from scale import scale_canvas, scale_controls
from weather import animated_weather

ROOT = Path(__file__).resolve().parents[1]
THEME = "Belovodie Command"


def grid(cards, columns="minmax(0,1fr)", rows=None, height=None, gap="16px", mediaquery=None):
    layout = {"grid-template-columns": columns, "grid-gap": gap,
              "margin": "0", "padding": "0", "card_margin": "0",
              "place-items": "stretch", "min-height": "0"}
    if rows:
        layout["grid-template-rows"] = rows
    if height:
        layout["height"] = height
    if mediaquery:
        # Layout Card indexes by MediaQueryList.media, which normalizes colons.
        layout["mediaquery"] = {re.sub(r":\s*", ": ", query): deepcopy(value)
                                for query, value in mediaquery.items()}
    return {"type": "custom:layout-card", "layout_type": "custom:grid-layout",
            "layout": layout, "cards": deepcopy(cards)}


def button(name, icon=None, action=None, template="bc_action", **kwargs):
    return {"type": "custom:button-card", "template": template,
            "name": name, "show_icon": bool(icon), "icon": icon,
            "tap_action": action or {"action": "none"}, **kwargs}


def metric(name, entity, icon, unit=None, **variables):
    return button(name, icon, {"action": "more-info"}, "bc_metric",
                  entity=entity, variables={"unit": unit, **variables})


def styled(card, css, selector=None, surface=False):
    """Apply card-mod explicitly to nested cards created by another custom card."""
    base = ":host{display:block;height:100%;min-height:0}ha-card{height:100%;box-sizing:border-box;box-shadow:none;"
    base += ("background:#102b38;border:1px solid #1b4353;padding:16px 18px;overflow:hidden;}"
             if surface else "background:none;border:none;padding:0;}")
    reset = "ha-card::before,ha-card::after{display:none!important;content:none!important}"
    styles = {".": base + reset}
    if selector:
        styles[f"{selector}$"] = css + reset
    else:
        styles["."] += css
    return {"type": "custom:mod-card", "card": deepcopy(card), "card_mod": {"style": styles}}


def hourly_generator(field):
    return (ROOT / "src/hourly-generator.js").read_text().replace("__FIELD__", json.dumps(field))


def visual_tile(card):
    """Keep native actions/features with compact control typography."""
    if card.get("type") != "tile":
        raise ValueError("visual_tile requires a native tile card")
    content = deepcopy(card)
    content["vertical"] = False
    return styled(content, (ROOT / "src/native-tile.css").read_text(), "hui-tile-card")


def compact_controls(cards, dialog=True):
    """Refresh preset tiles and compact preset dialog actions, retaining bindings."""
    result = deepcopy(cards)

    def visual(node):
        return (node.get("type") == "custom:mod-card" and
                node.get("card", {}).get("type") == "tile" and
                isinstance(node.get("card_mod", {}).get("style"), dict) and
                "hui-tile-card$" in node["card_mod"]["style"])

    def visit(node, inside_dialog):
        if isinstance(node, list):
            for child in node:
                visit(child, inside_dialog)
        elif isinstance(node, dict):
            styles = node.get("card_mod", {}).get("style", {})
            if visual(node):
                node["card"]["vertical"] = False
                styles["hui-tile-card$"] = (ROOT / "src/native-tile.css").read_text()
                compact = ":host{height:auto!important}ha-card{height:auto!important}"
                if compact not in styles.get(".", ""):
                    styles["."] = styles.get(".", "") + compact
            children = node.get("cards", [])
            if (node.get("type") == "custom:layout-card" and node.get("layout_type") == "custom:grid-layout"
                    and children and all(isinstance(child, dict) and visual(child) for child in children)):
                layout = node.setdefault("layout", {})
                for profile in [layout, *layout.get("mediaquery", {}).values()]:
                    profile["grid-template-rows"] = "none"
                    profile["grid-auto-rows"] = "max-content"
                    profile["align-content"] = "start"
                layout["grid-gap"] = "10px"
            if (inside_dialog and node.get("type") == "custom:button-card" and
                    node.get("template") in ("bc_action", "bc_nav")):
                style = node.setdefault("styles", {})
                for part, declarations in {
                    "card": [{"height": "56px"}, {"padding": "8px 12px"}, {"border-radius": "12px"}],
                    "name": [{"font-size": "18px"}], "label": [{"font-size": "14px"}],
                    "icon": [{"width": "26px"}],
                    "grid": [{"grid-template-columns": "minmax(0,1fr)" if node["template"] == "bc_nav"
                              else "32px minmax(0,1fr) 20px"}]
                }.items():
                    replaced = {key for item in declarations for key in item}
                    style[part] = [item for item in style.get(part, []) if not replaced.intersection(item)] + declarations
            owns_dialog = (node.get("type") == "custom:universal-card" and
                           node.get("card_id", "").startswith("bc-") and node.get("body_mode") == "modal")
            for key, value in list(node.items()):
                if isinstance(value, (dict, list)):
                    visit(value, inside_dialog or (owns_dialog and key == "body"))
    visit(result, dialog)
    return result


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
            "body": {"cards": compact_controls(cards)}}


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
    # Compact navigation hides secondary tabs; every route remains in this menu.
    preferences = modal("Настройки панели", "mdi:tune", [*scale_controls(url_path),
                        interface_control(url_path)], f"bc-settings-{current}")
    preferences["modal"]["max_width"] = "560px"
    extra = [interface_control(url_path), preferences, *[nav(p) for p in pages if p["path"] != current],
        button("Редактор панели", "mdi:pencil", {"action": "navigate",
               "navigation_path": f"/{url_path}/{current}?edit=1&disable_km"}),
        button("Настройки HA", "mdi:cog", {"action": "navigate", "navigation_path": "/config"}),
        button("HACS", "mdi:store", {"action": "navigate", "navigation_path": "/hacs"})]
    more = modal("Ещё", "mdi:chevron-down", [grid(extra, "repeat(3,minmax(0,1fr))")],
                 f"bc-nav-{current}")
    more["custom_css"]["css"] += "\n.header{height:100%;padding:0 12px!important;gap:8px!important}.header-left{display:none!important}.header-title{font-size:var(--bc-font)!important}.header-icon{display:none}.expand-icon{transform:none!important}"
    logo = button("", "mdi:home-assistant", {"action": "navigate",
                  "navigation_path": f"/{url_path}/{pages[0]['path']}"}, "bc_brand")
    clock = button("", template="bc_clock", entity=clock_entity,
                   show_label=True, show_name=False,
                   label="[[[ return new Date().toLocaleDateString(hass.locale.language,{weekday:'short',day:'numeric',month:'long',year:'numeric'}); ]]]",
                   custom_fields={"time": "[[[ return entity?.state && entity.state !== 'unavailable' ? entity.state : new Date().toLocaleTimeString(hass.locale.language,{hour:'2-digit',minute:'2-digit'}); ]]]"})
    profile = button("Профиль", "mdi:account", {"action": "navigate", "navigation_path": "/profile"},
                     "bc_brand", show_name=False)
    main_cards = list(map(nav, main))
    for i, card in enumerate(main_cards):
        card["view_layout"] = {"grid-area": f"nav{i}"}
        if i >= 3:
            card["view_layout"]["show"] = {"mediaquery": "(min-width: 1651px)"}
        elif i >= 1:
            card["view_layout"]["show"] = {"mediaquery": "(min-width: 1057px)"}
    for card, area in ((logo, "brand"), (more, "more"), (clock, "clock"), (profile, "profile")):
        card["view_layout"] = {"grid-area": area}
    result = grid([logo, *main_cards, more, clock, profile],
                "80px repeat(5,minmax(100px,1fr)) minmax(215px,1.4fr) 140px minmax(210px,1.4fr) 74px",
                height="100%", gap="12px")
    result["layout"]["grid-template-areas"] = '"brand nav0 nav1 nav2 nav3 nav4 nav5 more clock profile"'
    result["layout"]["mediaquery"] = {
        "(max-width: 1056px)": {
            "grid-template-columns": "44px minmax(0,1fr) 104px minmax(140px,1.4fr) 44px",
            "grid-template-areas": '"brand nav0 more clock profile"', "grid-gap": "6px"},
        "(max-width: 1650px)": {
            "grid-template-columns": "50px repeat(3,minmax(0,1fr)) 100px minmax(170px,1.4fr) 50px",
            "grid-template-areas": '"brand nav0 nav1 nav2 more clock profile"', "grid-gap": "8px"}}
    return result


def compose(original, pages, url_path, clock_entity=None, screen=None):
    """Only the supplied pages/cards are published to Lovelace, never to GitHub."""
    screen = Screen() if screen is None else screen
    if not isinstance(screen, Screen):
        raise ValueError("screen must be a Screen calibration profile")
    if not pages or len({p["path"] for p in pages}) != len(pages):
        raise ValueError("Pages need unique, non-empty paths")
    if {p["path"] for p in pages} != {p["path"] for p in original["views"]}:
        raise ValueError("Every original view must be accounted for")
    result = {k: deepcopy(v) for k, v in original.items() if k != "views"}
    templates = json.loads((ROOT / "src/button-templates.json").read_text())
    # Button Card collects extra_styles through its template inheritance chain.
    # Share calibration once instead of duplicating it in every route/button.
    for template in templates.values():
        parents = template.get("template", [])
        parents = [parents] if isinstance(parents, str) else parents
        if not any(parent.startswith("bc_") for parent in parents):
            template["extra_styles"] = template.get("extra_styles", "") + screen.css()
    result.setdefault("button_card_templates", {}).update(templates)
    result["kiosk_mode"] = kiosk_config(url_path)
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
            m = animated_weather(m)
            m["view_layout"] = {"grid-area": f"stat{i}"}
            cards.append(m)
        work = tabs(page["tabs"], f"bc-work-{page['path']}", workspace=True)
        work["view_layout"] = {"grid-area": "work"}
        cards.append(work)
        sidebar = grid(dock, rows=f"repeat({len(dock)},minmax(0,1fr))", height="100%", gap="10px")
        sidebar["layout"]["mediaquery"] = {"(max-width: 1056px)": {
            "grid-template-columns": f"repeat({len(dock)},minmax(0,1fr))",
            "grid-template-rows": "minmax(0,1fr)", "grid-gap": "6px"}}
        sidebar["view_layout"] = {"grid-area": "dock"}
        cards.append(sidebar)
        footer_label = button("Быстрые сцены", template="bc_nav", styles={
            "card": [{"border": "none"}, {"background": "transparent"}, {"padding": "0"}],
            "name": [{"justify-self": "start"}, {"font-size": "var(--bc-small)"}, {"color": "#9fc5d6"}]})
        footer_buttons = deepcopy(page["footer"])
        for control in footer_buttons:
            if control.get("type") == "custom:button-card":
                control["extra_styles"] = control.get("extra_styles", "") + (
                    '@media(max-width:1056px){#container{grid-template-areas:"i n"!important;'
                    'grid-template-columns:24px minmax(0,1fr)!important;column-gap:6px!important}'
                    '#arrow{display:none!important}#name{overflow-wrap:normal!important;'
                    'font-size:14px!important;white-space:nowrap!important}ha-card{padding:8px!important}}')
        footer = grid([footer_label, grid(footer_buttons, "repeat(3,minmax(0,1fr))", height="100%")],
                      rows="30px minmax(0,1fr)", height="100%", gap="12px",
                      mediaquery={"(max-width: 1650px)": {
                          "grid-template-rows": "20px minmax(0,1fr)", "grid-gap": "8px"}})
        footer["view_layout"] = {"grid-area": "footer"}
        cards.append(footer)
        last = deepcopy(page["last"])
        last["view_layout"] = {"grid-area": "last"}
        cards.append(last)
        result["views"].append({"path": page["path"], "title": page["title"],
            "icon": page.get("icon", "mdi:view-dashboard"),
            "theme": THEME, "background": "var(--primary-background-color)", "type": "custom:grid-layout", "cards": cards,
            "layout": {"height": "calc(100dvh - var(--kiosk-header-height,var(--header-height,56px)) - clamp(16px,2.222222dvh,32px))", "background": "#092430", "margin": "0", "padding": "clamp(8px,1.111111dvh,16px) clamp(8px,1.09091vw,24px)",
                "box-sizing": "border-box", "grid-template-columns": "repeat(4,minmax(0,1fr))",
                "grid-template-rows": "minmax(78px,8vh) minmax(180px,22vh) minmax(0,1fr) minmax(100px,11vh)",
                "grid-template-areas": '"nav nav nav nav" "stat0 stat1 stat2 stat3" "work work work dock" "footer footer footer last"',
                "grid-gap": "20px", "card_margin": "0", "--masonry-view-card-margin": "0px", "place-items": "stretch",
                "mediaquery": {"(max-width: 1056px)": {
                    "grid-gap": "8px",
                    "grid-template-columns": "repeat(2,minmax(0,1fr))",
                    "grid-template-rows": "56px minmax(144px,12dvh) minmax(144px,12dvh) minmax(0,1fr) clamp(64px,8dvh,92px) clamp(88px,10dvh,130px)",
                    "grid-template-areas": '"nav nav" "stat0 stat1" "stat2 stat3" "work work" "dock dock" "footer last"'},
                    "(max-width: 1650px), (max-height: 900px)": {
                    "grid-gap": "12px",
                    "grid-template-rows": "60px minmax(160px,22dvh) minmax(0,1fr) 100px"}}}})
        # Refresh privately supplied preset cards without regenerating bindings.
        cards = compact_controls(cards, dialog=False)
        apply_screen(cards, screen)
        view = result["views"][-1]
        layout = view["layout"]
        content = {"type": "custom:layout-card", "layout_type": "custom:grid-layout",
                   "layout": {**deepcopy(layout), "height": "calc(100% - clamp(16px,2.222222dvh,32px))"}, "cards": cards}
        view["cards"] = [scale_canvas(content, url_path)]
        view["layout"] = {"height": "calc(100dvh - var(--kiosk-header-height,var(--header-height,56px)))",
                          "margin": "0", "padding": "0",
                          "grid-template-columns": "minmax(0,1fr)",
                          "grid-template-rows": "minmax(0,1fr)", "card_margin": "0",
                          "grid-gap": "0", "place-items": "stretch"}
    return result
