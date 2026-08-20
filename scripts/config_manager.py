#!/usr/bin/env python3
import argparse
import json
import os
import socket
from datetime import datetime
from pathlib import Path

APP_DIR = Path.home() / ".project-asset-insight"
CONFIG_PATH = APP_DIR / "config.json"


def is_absolute_path(p: str) -> bool:
    # Support both native absolute paths and Windows drive paths when invoked in mixed environments.
    return os.path.isabs(p) or (len(p) >= 3 and p[1] == ":" and p[2] in ("\\", "/"))


def load_config():
    if not CONFIG_PATH.exists():
        return None
    try:
        return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except Exception as exc:
        raise SystemExit(f"CONFIG_ERROR: cannot read {CONFIG_PATH}: {exc}")


def validate_output_root(path_str: str):
    if not path_str or not is_absolute_path(path_str):
        raise SystemExit("CONFIG_ERROR: output_root must be an absolute path")


def save_config(output_root: str):
    validate_output_root(output_root)
    APP_DIR.mkdir(parents=True, exist_ok=True)
    data = {
        "schema_version": "1.0",
        "output_root": output_root,
        "initialized_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "host": socket.gethostname(),
    }
    CONFIG_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return data


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("status")
    p_set = sub.add_parser("set")
    p_set.add_argument("output_root")
    sub.add_parser("get")

    args = ap.parse_args()

    if args.cmd == "status":
        cfg = load_config()
        if not cfg:
            print(json.dumps({"initialized": False, "config_path": str(CONFIG_PATH)}, ensure_ascii=False))
            return
        print(json.dumps({"initialized": True, "config_path": str(CONFIG_PATH), **cfg}, ensure_ascii=False))
        return

    if args.cmd == "set":
        print(json.dumps(save_config(args.output_root), ensure_ascii=False, indent=2))
        return

    if args.cmd == "get":
        cfg = load_config()
        if not cfg:
            raise SystemExit("CONFIG_MISSING: ask the user for this machine's output root first")
        validate_output_root(str(cfg.get("output_root", "")))
        print(cfg["output_root"])


if __name__ == "__main__":
    main()
