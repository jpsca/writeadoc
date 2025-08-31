import argparse
from pathlib import Path

import hecto


BLUEPRINT = Path(__file__).parent / "blueprint"

def init(dst: Path | None = None):
    dst = Path(dst).resolve() if dst else Path.cwd()
    hecto.render_blueprint(BLUEPRINT, dst)


def run():
    parser = argparse.ArgumentParser(prog="writeadoc", description="Writeadoc CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Initialize a new project")
    init_parser.add_argument("path", nargs="?", default=None, help="Destination path (optional)")

    args = parser.parse_args()

    if args.command == "init":
        init(args.path)
