#!/usr/bin/env python3
import argparse
import json
import os
import socket
from datetime import datetime
from pathlib import Path

APP_DIR = Path.home() / ".project-asset-insight"
CONFIG_PATH = APP_DIR / "config.json"
SCHEMA_VERSION = "1.1"
REQUIRED_FIELDS = ("output_root", "screenshot_root", "screenshot_scale")


def is_absolute_path(p: str) -> bool:
    # Support native absolute paths and Windows drive paths in mixed environments.
    return os.path.isabs(p) or (len(p) >= 3 and p[1] == ":" and p[2] in ("\\", "/"))


def load_config():
    if not CONFIG_PATH.exists():
        return None
    try:
        return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except Exception as exc:
        raise SystemExit(f"CONFIG_ERROR: cannot read {CONFIG_PATH}: {exc}")


def validate_path(name: str, path_str: str):
    if not path_str or not is_absolute_path(path_str):
        raise SystemExit(f"CONFIG_ERROR: {name} must be an absolute path")


def validate_scale(value) -> float:
    try:
        scale = float(value)
    except (TypeError, ValueError):
        raise SystemExit("CONFIG_ERROR: screenshot_scale must be a number")
    if not 0.5 <= scale <= 4.0:
        raise SystemExit("CONFIG_ERROR: screenshot_scale must be between 0.5 and 4.0")
    return scale


def missing_fields(cfg):
    if not cfg:
        return list(REQUIRED_FIELDS)
    missing = []
    for field in REQUIRED_FIELDS:
        if cfg.get(field) in (None, ""):
            missing.append(field)
    return missing


def invalid_fields(cfg):
    if not cfg:
        return []
    invalid = []
    if cfg.get("output_root") not in (None, "") and not is_absolute_path(str(cfg.get("output_root"))):
        invalid.append("output_root")
    if cfg.get("screenshot_root") not in (None, "") and not is_absolute_path(str(cfg.get("screenshot_root"))):
        invalid.append("screenshot_root")
    if cfg.get("screenshot_scale") not in (None, ""):
        try:
            scale = float(cfg.get("screenshot_scale"))
            if not 0.5 <= scale <= 4.0:
                invalid.append("screenshot_scale")
        except (TypeError, ValueError):
            invalid.append("screenshot_scale")
    return invalid


def validate_complete_config(cfg):
    missing = missing_fields(cfg)
    if missing:
        raise SystemExit(
            "CONFIG_INCOMPLETE: ask the user for the missing machine-level settings first: "
            + ", ".join(missing)
        )
    invalid = invalid_fields(cfg)
    if invalid:
        raise SystemExit(
            "CONFIG_INVALID: ask the user to correct these machine-level settings: "
            + ", ".join(invalid)
        )
    validate_path("output_root", str(cfg["output_root"]))
    validate_path("screenshot_root", str(cfg["screenshot_root"]))
    validate_scale(cfg["screenshot_scale"])


def save_config(output_root: str, screenshot_root: str, screenshot_scale) -> dict:
    validate_path("output_root", output_root)
    validate_path("screenshot_root", screenshot_root)
    scale = validate_scale(screenshot_scale)

    APP_DIR.mkdir(parents=True, exist_ok=True)
    old = load_config() or {}
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data = {
        "schema_version": SCHEMA_VERSION,
        "output_root": output_root,
        "screenshot_root": screenshot_root,
        "screenshot_scale": scale,
        "initialized_at": old.get("initialized_at", now),
        "updated_at": now,
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
    p_set.add_argument("--screenshot-root", required=True)
    p_set.add_argument("--screenshot-scale", required=True, type=float)

    p_get = sub.add_parser("get")
    p_get.add_argument(
        "--field",
        choices=["all", "output_root", "screenshot_root", "screenshot_scale"],
        default="all",
    )

    args = ap.parse_args()

    if args.cmd == "status":
        cfg = load_config()
        if not cfg:
            print(json.dumps({
                "initialized": False,
                "complete": False,
                "missing_fields": list(REQUIRED_FIELDS),
                "invalid_fields": [],
                "config_path": str(CONFIG_PATH),
            }, ensure_ascii=False))
            return
        missing = missing_fields(cfg)
        invalid = invalid_fields(cfg)
        print(json.dumps({
            "initialized": True,
            "complete": not missing and not invalid,
            "missing_fields": missing,
            "invalid_fields": invalid,
            "config_path": str(CONFIG_PATH),
            **cfg,
        }, ensure_ascii=False))
        return

    if args.cmd == "set":
        data = save_config(args.output_root, args.screenshot_root, args.screenshot_scale)
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return

    if args.cmd == "get":
        cfg = load_config()
        if not cfg:
            raise SystemExit(
                "CONFIG_MISSING: ask the user for output_root, screenshot_root, and screenshot_scale first"
            )
        validate_complete_config(cfg)
        if args.field == "all":
            print(json.dumps(cfg, ensure_ascii=False, indent=2))
        else:
            print(cfg[args.field])


if __name__ == "__main__":
    main()
