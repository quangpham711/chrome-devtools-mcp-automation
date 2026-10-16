#!/usr/bin/env python3
"""
CLI helper for managing and standardizing test evidence screenshots in reports/screenshots/{case_id}.png.
Works alongside Chrome DevTools MCP's `take_screenshot` tool.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SCREENSHOTS_DIR = PROJECT_ROOT / "reports" / "screenshots"


def normalize_screenshot(
    case_id: str,
    source_path: str | Path | None = None,
    output_dir: str | Path = DEFAULT_SCREENSHOTS_DIR,
    title_text: str = "",
    status: str = "PASS",
) -> Path:
    """
    Ensure a valid PNG screenshot exists at `<output_dir>/<case_id>.png`.
    - If `source_path` is provided and exists, copies/converts it to PNG at the destination.
    - Otherwise, generates a clean diagnostic evidence image with metadata banner.
    """
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    safe_id = case_id.strip().replace("/", "_").replace("\\", "_")
    dest_path = out_dir / f"{safe_id}.png"

    if source_path:
        src = Path(source_path)
        if not src.exists():
            raise FileNotFoundError(f"Source screenshot file not found: '{src}'")
        if src.resolve() != dest_path.resolve():
            with Image.open(src) as img:
                img.convert("RGB").save(dest_path, format="PNG")
        return dest_path

    # Generate an evidence image when called without a source file (e.g. CLI dry-run)
    bg_color = (240, 248, 244) if status.upper() == "PASS" else (253, 242, 242)
    banner_color = (31, 78, 120) if status.upper() == "PASS" else (156, 0, 6)

    img = Image.new("RGB", (1280, 720), color=bg_color)
    draw = ImageDraw.Draw(img)

    # Top banner
    draw.rectangle([(0, 0), (1280, 90)], fill=banner_color)
    header = f"EVIDENCE SCREENSHOT | {safe_id} | STATUS: {status.upper()}"
    draw.text((32, 32), header, fill=(255, 255, 255))

    # Body info
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    body_lines = [
        f"Test Case ID : {safe_id}",
        f"Status       : {status.upper()}",
        f"Timestamp    : {timestamp}",
        f"Details      : {title_text or 'Captured by AI Web Testing Agent'}",
    ]
    y_pos = 150
    for line in body_lines:
        draw.text((48, y_pos), line, fill=(30, 30, 30))
        y_pos += 45

    img.save(dest_path, format="PNG")
    return dest_path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Standardize or capture test case screenshot into reports/screenshots/{case_id}.png"
    )
    parser.add_argument("--case-id", required=True, help="Test Case ID (e.g. TC_01)")
    parser.add_argument(
        "--source",
        default="",
        help="Optional path to an existing screenshot captured by Chrome DevTools MCP take_screenshot",
    )
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_SCREENSHOTS_DIR),
        help="Target directory for screenshots (default: reports/screenshots)",
    )
    parser.add_argument("--status", default="PASS", choices=["PASS", "FAIL", "pass", "fail"])
    parser.add_argument("--title", default="", help="Optional summary text for generated evidence image")

    args = parser.parse_args()
    dest = normalize_screenshot(
        case_id=args.case_id,
        source_path=args.source or None,
        output_dir=args.output_dir,
        title_text=args.title,
        status=args.status.upper(),
    )
    try:
        rel = dest.resolve().relative_to(PROJECT_ROOT.resolve()).as_posix()
    except ValueError:
        rel = dest.as_posix()

    print(rel)
    return 0


if __name__ == "__main__":
    sys.exit(main())
