#!/usr/bin/env python3
import argparse
import json
import os
import shutil
import struct
import subprocess
import sys
from datetime import datetime
from pathlib import Path

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def parse_viewport(value: str):
    try:
        w, h = value.lower().split("x", 1)
        width, height = int(w), int(h)
    except Exception:
        raise SystemExit("ARG_ERROR: --viewport must look like 1440x900")
    if width < 320 or height < 200:
        raise SystemExit("ARG_ERROR: viewport must be at least 320x200")
    return width, height


def validate_scale(value: float) -> float:
    if not 0.5 <= value <= 4.0:
        raise SystemExit("ARG_ERROR: --scale must be between 0.5 and 4.0")
    return value


def browser_candidates():
    env_paths = [
        os.environ.get("CHROME_PATH"),
        os.environ.get("CHROMIUM_PATH"),
        os.environ.get("EDGE_PATH"),
    ]
    for item in env_paths:
        if item:
            yield item

    for cmd in ("chromium", "chromium-browser", "google-chrome", "google-chrome-stable", "chrome", "msedge"):
        found = shutil.which(cmd)
        if found:
            yield found

    if sys.platform.startswith("win"):
        roots = [
            os.environ.get("PROGRAMFILES"),
            os.environ.get("PROGRAMFILES(X86)"),
            os.environ.get("LOCALAPPDATA"),
        ]
        rels = [
            r"Google\Chrome\Application\chrome.exe",
            r"Microsoft\Edge\Application\msedge.exe",
        ]
        for root in roots:
            if root:
                for rel in rels:
                    yield str(Path(root) / rel)
    elif sys.platform == "darwin":
        yield "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        yield "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"
        yield "/Applications/Chromium.app/Contents/MacOS/Chromium"


def find_browser(explicit: str | None):
    if explicit:
        path = Path(explicit)
        if path.exists():
            return str(path)
        found = shutil.which(explicit)
        if found:
            return found
        raise SystemExit(f"BROWSER_NOT_FOUND: {explicit}")

    seen = set()
    for candidate in browser_candidates():
        if not candidate or candidate in seen:
            continue
        seen.add(candidate)
        p = Path(candidate)
        if p.exists() and p.is_file():
            return str(p)
    raise SystemExit(
        "BROWSER_NOT_FOUND: no Chrome/Chromium/Edge executable found; use --browser or another capture method"
    )


def png_dimensions(path: Path):
    try:
        data = path.read_bytes()[:24]
        if len(data) >= 24 and data[:8] == PNG_MAGIC and data[12:16] == b"IHDR":
            return struct.unpack(">II", data[16:24])
    except Exception:
        pass
    return None, None


def load_manifest(path: Path):
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_manifest(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description="Capture a web visual surface with local Chrome/Chromium/Edge.")
    ap.add_argument("--url", required=True)
    ap.add_argument("--output-dir", required=True)
    ap.add_argument("--scale", required=True, type=float, help="Must come from screenshot_scale machine config")
    ap.add_argument("--viewport", default="1440x900")
    ap.add_argument("--name", default="01-overview.png")
    ap.add_argument("--wait-ms", type=int, default=2500)
    ap.add_argument("--browser")
    ap.add_argument("--manifest", help="Defaults to <output-dir>/visual-evidence.json")
    args = ap.parse_args()

    scale = validate_scale(args.scale)
    width, height = parse_viewport(args.viewport)
    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    screenshot_path = output_dir / args.name
    manifest_path = Path(args.manifest).expanduser().resolve() if args.manifest else output_dir / "visual-evidence.json"

    browser = find_browser(args.browser)
    command = [
        browser,
        "--headless=new",
        "--no-first-run",
        "--disable-extensions",
        "--hide-scrollbars",
        "--run-all-compositor-stages-before-draw",
        f"--window-size={width},{height}",
        f"--force-device-scale-factor={scale}",
        f"--virtual-time-budget={max(0, args.wait_ms)}",
        f"--screenshot={screenshot_path}",
        args.url,
    ]
    if hasattr(os, "geteuid") and os.geteuid() == 0:
        command.insert(1, "--no-sandbox")

    started_at = datetime.now().isoformat(timespec="seconds")
    manifest = load_manifest(manifest_path)
    attempts = manifest.setdefault("capture_attempts", [])

    try:
        proc = subprocess.run(command, capture_output=True, text=True, timeout=45)
    except Exception as exc:
        attempts.append({
            "method": "chrome-headless-cli",
            "url": args.url,
            "started_at": started_at,
            "success": False,
            "error": str(exc),
        })
        manifest.update({
            "schema_version": "1.0",
            "capture_status": "CAPTURE_BLOCKED",
            "review_status": manifest.get("review_status", "VISION_UNAVAILABLE"),
            "verification_level": manifest.get("verification_level", "L0"),
            "asset_dir": str(output_dir),
            "screenshot_scale": scale,
            "fallbacks_checked": manifest.get("fallbacks_checked", []),
            "errors": manifest.get("errors", []) + [str(exc)],
        })
        save_manifest(manifest_path, manifest)
        raise SystemExit(f"CAPTURE_FAILED: {exc}")

    success = proc.returncode == 0 and screenshot_path.exists() and screenshot_path.stat().st_size > 0
    attempts.append({
        "method": "chrome-headless-cli",
        "url": args.url,
        "started_at": started_at,
        "success": success,
        "browser": browser,
        "exit_code": proc.returncode,
        "stderr_tail": proc.stderr[-2000:],
    })

    if not success:
        error = f"browser exit={proc.returncode}; screenshot_exists={screenshot_path.exists()}"
        manifest.update({
            "schema_version": "1.0",
            "capture_status": "CAPTURE_BLOCKED",
            "review_status": manifest.get("review_status", "VISION_UNAVAILABLE"),
            "verification_level": manifest.get("verification_level", "L0"),
            "asset_dir": str(output_dir),
            "screenshot_scale": scale,
            "fallbacks_checked": manifest.get("fallbacks_checked", []),
            "errors": manifest.get("errors", []) + [error],
        })
        save_manifest(manifest_path, manifest)
        raise SystemExit(f"CAPTURE_FAILED: {error}")

    img_w, img_h = png_dimensions(screenshot_path)
    screenshots = manifest.setdefault("screenshots", [])
    screenshots = [x for x in screenshots if x.get("path") != screenshot_path.name]
    screenshots.append({
        "path": screenshot_path.name,
        "bytes": screenshot_path.stat().st_size,
        "width": img_w,
        "height": img_h,
        "purpose": "overview" if screenshot_path.name.startswith("01-") else "visual-evidence",
    })

    manifest.update({
        "schema_version": "1.0",
        "capture_status": "CAPTURED",
        "review_status": manifest.get("review_status", "VISION_UNAVAILABLE"),
        "verification_level": manifest.get("verification_level", "L1"),
        "asset_dir": str(output_dir),
        "source_url": args.url,
        "viewport": {"width": width, "height": height},
        "screenshot_scale": scale,
        "browser_executable": browser,
        "screenshots": screenshots,
        "runtime_checks": {
            **manifest.get("runtime_checks", {}),
            "browser_exit_code": proc.returncode,
            "capture_file_exists": True,
        },
    })
    save_manifest(manifest_path, manifest)
    print(str(screenshot_path))
    print(str(manifest_path))


if __name__ == "__main__":
    main()
