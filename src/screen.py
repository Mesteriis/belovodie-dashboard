"""Screen calibration and responsive density for an existing dashboard."""
from dataclasses import dataclass
import re


@dataclass(frozen=True)
class Screen:
    width: int = 2200
    height: int = 1440

    def __post_init__(self):
        if any(type(v) is not int or not 320 <= v <= 8192 for v in (self.width, self.height)):
            raise ValueError("Screen dimensions must be integers between 320 and 8192 CSS pixels")

    @classmethod
    def parse(cls, value):
        match = re.fullmatch(r"(\d+)[x×](\d+)", value)
        if not match:
            raise ValueError("Screen must use WIDTHxHEIGHT, for example 2200x1440")
        return cls(*map(int, match.groups()))

    def size(self, maximum, minimum):
        return (f"clamp({minimum}px,min({maximum * 100 / self.width:.4f}vw,"
                f"{maximum * 100 / self.height:.4f}dvh),{maximum}px)")

    def css(self):
        sizes = {"font": (30, 16), "small": (23, 13), "value": (78, 30),
                 "unit": (32, 16), "padding-x": (28, 10), "padding-y": (24, 8),
                 "action-icon-column": (72, 32), "arrow-column": (24, 16),
                 "metric-icon-column": (60, 28), "metric-title-row": (40, 20),
                 "metric-label-row": (46, 24), "metric-gap": (12, 4),
                 "weather-icon": (110, 40), "weather-condition-row": (35, 20),
                 "weather-label-row": (36, 22), "weather-gap": (8, 3),
                 "small-value": (36, 20), "small-title-row": (30, 18),
                 "small-label-row": (30, 20), "small-padding-y": (18, 8),
                 "small-padding-x": (22, 10), "brand-icon": (70, 36),
                 "mini-chart-height": (80, 24), "chart-bottom": (60, 28),
                 "decor-size": (100, 32), "route-value": (42, 24),
                 "route-icon-column": (64, 32), "route-icon": (48, 24)}
        declarations = ";".join(f"--bc-{k}:{self.size(*v)}" for k, v in sizes.items())
        result = ":host{" + declarations + "}"
        if self != Screen():
            # A small calibration must not enlarge text beyond compact slots.
            baseline = Screen()
            caps = ";".join(f"--bc-{k}:min({self.size(*v)},{baseline.size(*v)})"
                            for k, v in sizes.items())
            result += "@media(max-width:1650px),(max-height:900px){:host{" + caps + "}}"
        return result


def apply_screen(cards, screen):
    """Only style this preset's cards; source cards and action bindings are retained."""
    if isinstance(cards, list):
        for card in cards:
            apply_screen(card, screen)
    elif isinstance(cards, dict):
        kind = cards.get("type")
        if kind == "custom:universal-card" and cards.get("card_id", "").startswith("bc-"):
            cards["custom_css"]["css"] += screen.css()
        elif kind == "custom:mod-card":
            styles = cards.get("card_mod", {}).get("style")
            if isinstance(styles, dict):
                styles["."] = styles.get(".", "") + screen.css()
        for value in list(cards.values()):
            if isinstance(value, (list, dict)):
                apply_screen(value, screen)
