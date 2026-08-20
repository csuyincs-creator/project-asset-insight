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
    """Clean summary for filename: remove invalid chars, collapse whitespace, limit length."""
    summary = re.sub(INVALID, "-", summary).strip().strip(".")
    summary = re.sub(r"\s+", " ", summary)
    # Limit summary to 30 chars to keep filename reasonable
    return summary[:30] if summary else "项目"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("output_root")
    ap.add_argument("project_name")
    ap.add_argument("--summary", default="", help="AI-generated one-line summary in Chinese or English")
    ap.add_argument("--date", help="YYYY-MM-DD; defaults to current local date")
    ap.add_argument("--create-month-dir", action="store_true", help="Auto-create month directory if missing")
    args = ap.parse_args()

    dt = datetime.strptime(args.date, "%Y-%m-%d") if args.date else datetime.now()
    month = dt.strftime("%Y-%m")
    date_str = dt.strftime("%Y-%m-%d")

    # Build filename: YYYY-MM-DD-项目名-一句话总结-项目资产解读.md
    project_part = safe_name(args.project_name)
    summary_part = safe_summary(args.summary)
    filename = f"{date_str}-{project_part}-{summary_part}-项目资产解读.md"

    # Build full path
    if len(args.output_root) >= 2 and args.output_root[1] == ":":
        month_dir = PureWindowsPath(args.output_root) / month
        full_path = month_dir / filename
    else:
        month_dir = Path(args.output_root) / month
        full_path = month_dir / filename

    # Auto-create month directory if requested (use Path for filesystem ops)
    if args.create_month_dir:
        Path(str(month_dir)).mkdir(parents=True, exist_ok=True)
        print(f"Month directory ensured: {month_dir}", file=sys.stderr)

    print(str(full_path))


if __name__ == "__main__":
    main()
