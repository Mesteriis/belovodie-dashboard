"""Offline renderer. The supplied input/output files contain private HA bindings."""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from compose import compose

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("original", type=Path)
parser.add_argument("pages", type=Path)
parser.add_argument("output", type=Path)
parser.add_argument("--url-path", required=True)
parser.add_argument("--clock-entity")
args = parser.parse_args()
dashboard = compose(json.loads(args.original.read_text()), json.loads(args.pages.read_text()),
                    args.url_path, args.clock_entity)
args.output.write_text(json.dumps(dashboard, ensure_ascii=False, indent=2) + "\n")
args.output.chmod(0o600)
