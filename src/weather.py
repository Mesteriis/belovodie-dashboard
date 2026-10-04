"""Animate the owned weather measurement using the existing Atmo HACS card."""
from copy import deepcopy


def animated_weather(card):
    templates = card.get("template", [])
    if isinstance(templates, str):
        templates = [templates]
    if card.get("type") != "custom:button-card" or "bc_weather" not in templates:
        return deepcopy(card)
    result = deepcopy(card)
    entity = card.get("entity")
    if not isinstance(entity, str) or not entity.startswith("weather."):
        raise ValueError("Animated weather requires the existing weather entity")
    sky = {
        "type": "custom:atmo-weather-card", "weather_entity": entity,
        "sun_entity": card.get("variables", {}).get("sun_entity", "sun.sun"),
        "card_style": "standalone", "card_height": "auto", "card_padding": "0px",
        "card_hide_text": True, "card_color_mode": "force_dark",
        "card_filter_clouds": "muted",
        "celestial_alignment": "right", "celestial_x": "82", "celestial_size": 48,
        "perf_fps": 20, "perf_cloud_quality": 1, "perf_effects": 1,
        "perf_dpr": 1, "perf_fauna": 0,
    }
    # Card Mod reaches Atmo's shadow root; no weather drawing/runtime is vendored.
    sky = {"type": "custom:mod-card", "card": sky, "card_mod": {"style": {
        ".": ":host{display:block;height:100%;min-height:0}"
             ":host,ha-card{pointer-events:none!important}"
             "ha-card{height:100%;padding:0;border:0;background:none;box-shadow:none}",
        "atmo-weather-card$": ":host{height:100%!important;min-height:0!important}"
                 ":host,*{pointer-events:none!important}"
                 "#card-root{height:100%!important;border:0;box-shadow:none;border-radius:0}"
                 "#card-root.weather-overcast{background-image:var(--bc-weather-art)!important;"
                 "background-size:auto 100%;background-position:right top;background-repeat:no-repeat}"
                 "#card-root::after{content:'';position:absolute;inset:0;pointer-events:none;"
                 "background:linear-gradient(90deg,#102b38 0%,rgba(16,43,56,.8) 28%,"
                 "rgba(16,43,56,.22) 100%);z-index:5;opacity:1}",
    }}}
    result.setdefault("custom_fields", {})["sky"] = {"card": sky, "do_not_eval": True}
    styles = result.setdefault("styles", {})
    # The original card owns sizing, labels and actions. The sky occupies no grid track.
    styles["card"] = [d for d in styles.get("card", [])
                      if not any(k.startswith("background-") for k in d)]
    styles["card"] += [{"overflow": "hidden"}, {"isolation": "isolate"}]
    styles.setdefault("custom_fields", {})["sky"] = [
        {"position": "absolute"}, {"inset": "0"}, {"z-index": "0"},
        {"pointer-events": "none"},
        {"display": "[[[ return entity && !['unknown','unavailable'].includes(entity.state) ? 'block' : 'none'; ]]]"},
    ]
    result["extra_styles"] = result.get("extra_styles", "") + (
        "#container>div:not(#sky){z-index:1}"
        "#sky{inset:calc(-1 * var(--bc-padding-y,24px)) "
        "calc(-1 * var(--bc-padding-x,28px))!important}"
        "@media(prefers-reduced-motion:reduce){#sky{display:none!important}"
        "ha-card{background-image:var(--bc-weather-art);background-size:auto 100%;"
        "background-position:right top;background-repeat:no-repeat}}"
    )
    return result
