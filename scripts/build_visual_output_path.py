#!/usr/bin/env python3
import argparse
import re
import sys
from datetime import datetime
from pathlib import Path, PureWindowsPath

INVALID = r'[<>:"/\\|?*]'


def safe_name(name: str) -> str:
    name = re.sub(INVALID, "-", name).strip().strip(".")
    name = re.sub(r"\s+", " ", name)
    return name or "未命名项目"


def safe_summary(summary: str) -> str:
    summary = re.sub(INVALID, "-", summary).strip().strip(".")
    summary = re.sub(r"\s+", " ", summary)
    return summary[:30] if summary else "项目"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("screenshot_root")
    ap.add_argument("project_name")
    ap.add_argument("--summary", default="")
    ap.add_argument("--date", help="YYYY-MM-DD; defaults to current local date")
    ap.add_argument("--create", action="store_true", help="Create the asset directory")
    ap.add_argument("--manifest", action="store_true", help="Print visual-evidence.json path instead of directory")
    args = ap.parse_args()

    dt = datetime.strptime(args.date, "%Y-%m-%d") if args.date else datetime.now()
    month = dt.strftime("%Y-%m")
    date_str = dt.strftime("%Y-%m-%d")
    stem = f"{date_str}-{safe_name(args.project_name)}-{safe_summary(args.summary)}-项目资产解读.assets"

    if len(args.screenshot_root) >= 2 and args.screenshot_root[1] == ":":
        asset_dir = PureWindowsPath(args.screenshot_root) / month / stem
    else:
        asset_dir = Path(args.screenshot_root) / month / stem

    if args.create:
        Path(str(asset_dir)).mkdir(parents=True, exist_ok=True)
        print(f"Visual asset directory ensured: {asset_dir}", file=sys.stderr)

    if args.manifest:
        print(str(asset_dir / "visual-evidence.json"))
    else:
        print(str(asset_dir))


if __name__ == "__main__":
    main()
