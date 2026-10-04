"""Embed forecast photographs in the HACS theme; no local URLs are published."""
import argparse
import base64
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
NAMES = ('clear-day', 'clear-night', 'cloudy-day', 'cloudy-night', 'rain-day',
         'rain-night', 'snow', 'fog', 'storm')


def build():
    path = ROOT / 'themes/belovodie-command.yaml'
    old = path.read_text()
    clean = re.sub(r'^  bc-forecast-[a-z-]+:.*\n', '', old, flags=re.MULTILINE)
    lines = []
    for name in NAMES:
        data = (ROOT / 'assets/forecast' / (name + '.webp')).read_bytes()
        value = base64.b64encode(data).decode()
        lines.append(f'  bc-forecast-{name}: \'url("data:image/webp;base64,{value}")\'')
    return path, old, clean.replace('  modes:\n', '\n'.join(lines) + '\n  modes:\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    path, old, new = build()
    if args.check:
        if old != new:
            raise SystemExit('Theme assets differ: run python3 tools/build_theme_assets.py')
        print('Embedded forecast assets match source files')
    else:
        path.write_text(new)
