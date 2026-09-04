#!/usr/bin/env python3
import argparse
import json
import os
import struct
import sys
from pathlib import Path

ALLOWED_CAPTURE = {"CAPTURED", "NO_VISUAL_SURFACE", "CAPTURE_BLOCKED"}
ALLOWED_REVIEW = {"VISION_REVIEWED", "VISION_UNAVAILABLE"}
ALLOWED_LEVELS = {"L0", "L1", "L2", "L3"}
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def png_dimensions(path: Path):
    try:
        data = path.read_bytes()[:24]
        if len(data) >= 24 and data[:8] == PNG_MAGIC and data[12:16] == b"IHDR":
            return struct.unpack(">II", data[16:24])
    except Exception:
        pass
    return None, None


def nonempty_list(value):
    return isinstance(value, list) and any(str(x).strip() for x in value)


def resolve_shot(manifest_path: Path, item):
    raw = str(item.get("path", "")).strip()
    if not raw:
        return None
    p = Path(raw)
    if p.is_absolute():
        return p
    return manifest_path.parent / p


def validate(manifest_path: Path, screenshot_root=None, expected_scale=None, report_path=None):
    errors = []
    warnings = []

    if not manifest_path.exists() or not manifest_path.is_file():
        return [f"visual evidence manifest not found: {manifest_path}"], warnings

    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return [f"invalid visual evidence JSON: {exc}"], warnings

    capture_status = data.get("capture_status")
    review_status = data.get("review_status")
    level = data.get("verification_level")

    if capture_status not in ALLOWED_CAPTURE:
        errors.append(f"invalid capture_status: {capture_status}")
    if review_status not in ALLOWED_REVIEW:
        errors.append(f"invalid review_status: {review_status}")
    if level not in ALLOWED_LEVELS:
        errors.append(f"invalid verification_level: {level}")

    manifest_scale = data.get("screenshot_scale")
    if expected_scale is not None:
        try:
            expected_scale_num = float(expected_scale)
            if not 0.5 <= expected_scale_num <= 4.0:
                errors.append("expected screenshot scale must be between 0.5 and 4.0")
        except (TypeError, ValueError):
            expected_scale_num = None
            errors.append("expected screenshot scale must be numeric")
    else:
        expected_scale_num = None

    if capture_status == "CAPTURED":
        try:
            scale_num = float(manifest_scale)
            if not 0.5 <= scale_num <= 4.0:
                errors.append("screenshot_scale must be between 0.5 and 4.0")
            if expected_scale_num is not None and abs(scale_num - expected_scale_num) > 1e-9:
                errors.append(
                    f"screenshot_scale does not match machine config: manifest={scale_num}, expected={expected_scale_num}"
                )
        except (TypeError, ValueError):
            errors.append("CAPTURED evidence requires numeric screenshot_scale")

        shots = data.get("screenshots")
        if not isinstance(shots, list) or not shots:
            errors.append("CAPTURED evidence requires at least one screenshot")
        else:
            for item in shots:
                if not isinstance(item, dict):
                    errors.append("each screenshots entry must be an object")
                    continue
                shot = resolve_shot(manifest_path, item)
                if not shot:
                    errors.append("screenshot entry missing path")
                    continue
                if not shot.exists() or not shot.is_file():
                    errors.append(f"screenshot not found: {shot}")
                    continue
                size = shot.stat().st_size
                if size < 1000:
                    errors.append(f"screenshot too small (<1000 bytes): {shot}")
                if shot.suffix.lower() == ".png":
                    w, h = png_dimensions(shot)
                    if not w or not h:
                        errors.append(f"cannot read PNG dimensions: {shot}")
                    elif w < 320 or h < 200:
                        errors.append(f"screenshot dimensions too small: {shot} ({w}x{h})")
                if report_path and report_path.exists():
                    report_text = report_path.read_text(encoding="utf-8")
                    if shot.name not in report_text:
                        errors.append(f"report does not reference screenshot: {shot.name}")

        if level == "L0":
            errors.append("CAPTURED evidence must be at least verification_level L1")

    elif capture_status == "NO_VISUAL_SURFACE":
        if not str(data.get("reason", "")).strip():
            errors.append("NO_VISUAL_SURFACE requires reason")
        if not nonempty_list(data.get("checked_entries")):
            errors.append("NO_VISUAL_SURFACE requires checked_entries")
        if not nonempty_list(data.get("evidence")):
            errors.append("NO_VISUAL_SURFACE requires evidence")

    elif capture_status == "CAPTURE_BLOCKED":
        if not str(data.get("reason", "")).strip():
            errors.append("CAPTURE_BLOCKED requires reason")
        attempts = data.get("capture_attempts")
        if not isinstance(attempts, list) or not attempts:
            errors.append("CAPTURE_BLOCKED requires capture_attempts")
        if not nonempty_list(data.get("fallbacks_checked")):
            errors.append("CAPTURE_BLOCKED requires fallbacks_checked")
        if not nonempty_list(data.get("errors")):
            errors.append("CAPTURE_BLOCKED requires errors")

    if screenshot_root:
        root = os.path.normcase(os.path.abspath(screenshot_root))
        try:
            manifest_abs = os.path.normcase(os.path.abspath(str(manifest_path)))
            if os.path.isabs(screenshot_root) and os.path.isabs(str(manifest_path)):
                common = os.path.commonpath([root, manifest_abs])
                if common != root:
                    errors.append("visual evidence manifest is outside screenshot_root")
        except Exception:
            warnings.append("could not verify screenshot_root relationship on this OS")

    if report_path:
        if not report_path.exists():
            errors.append(f"report not found: {report_path}")
        else:
            text = report_path.read_text(encoding="utf-8")
            if "## 11｜真实运行与视觉验证" not in text:
                errors.append("report missing visual verification section")
            if capture_status and capture_status not in text:
                errors.append(f"report does not state capture status: {capture_status}")

    return errors, warnings


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("manifest")
    ap.add_argument("--screenshot-root")
    ap.add_argument("--expected-scale", required=True, type=float)
    ap.add_argument("--report")
    args = ap.parse_args()

    manifest = Path(args.manifest)
    report = Path(args.report) if args.report else None
    errors, warnings = validate(manifest, args.screenshot_root, args.expected_scale, report)

    for warning in warnings:
        print(f"WARNING: {warning}")
    for error in errors:
        print(f"ERROR: {error}")

    if errors:
        sys.exit(1)
    print("OK: visual evidence validation passed")


if __name__ == "__main__":
    main()
