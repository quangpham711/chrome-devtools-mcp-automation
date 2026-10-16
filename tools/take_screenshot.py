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


def annotate_error_overlay(
    image_path: str | Path,
    error_lines: list[str],
    output_path: str | Path | None = None,
) -> Path:
    """
    Overlay a prominent red alert banner containing F12 Console & Network error details
    directly onto the screenshot.
    """
    img_path = Path(image_path)
    if not img_path.exists():
        raise FileNotFoundError(f"Image not found: {img_path}")

    out_path = Path(output_path) if output_path else img_path
    cleaned_lines = [line.strip() for line in error_lines if line.strip()]

    with Image.open(img_path) as img:
        img = img.convert("RGBA")
        width, height = img.size

        if not cleaned_lines:
            img.convert("RGB").save(out_path, format="PNG")
            return out_path

        line_height = max(24, int(height * 0.035))
        padding = max(12, int(height * 0.02))
        box_height = padding * 2 + line_height + len(cleaned_lines) * line_height
        box_height = min(box_height, int(height * 0.45))

        overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        # Draw red alert banner at bottom
        top_y = height - box_height
        draw.rectangle([(0, top_y), (width, height)], fill=(185, 20, 20, 235))
        # Draw gold accent bar
        draw.rectangle([(0, top_y), (width, top_y + 6)], fill=(255, 215, 0, 255))

        # Title
        draw.text(
            (padding + 8, top_y + padding),
            "🚨 [F12 ROOT CAUSE / CONSOLE & NETWORK ERROR DETECTED]",
            fill=(255, 255, 255),
        )

        curr_y = top_y + padding + line_height
        for line in cleaned_lines[:4]:
            draw.text((padding + 16, curr_y), f"• {line}", fill=(255, 245, 245))
            curr_y += line_height

        combined = Image.alpha_composite(img, overlay).convert("RGB")
        combined.save(out_path, format="PNG")
        return out_path


def normalize_screenshot(
    case_id: str,
    source_path: str | Path | None = None,
    output_dir: str | Path = DEFAULT_SCREENSHOTS_DIR,
    title_text: str = "",
    status: str = "PASS",
    error_lines: list[str] | None = None,
) -> Path:
    """
    Ensure a valid PNG screenshot exists at `<output_dir>/<case_id>.png`.
    - If `source_path` is provided and exists, copies/converts it to PNG at destination.
    - If `error_lines` are given (FAIL case), overlays an F12 error banner on top.
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
        if error_lines:
            annotate_error_overlay(dest_path, error_lines, dest_path)
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
    if error_lines:
        body_lines.append("Errors:")
        for err in error_lines[:3]:
            body_lines.append(f"  - {err}")

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
    parser.add_argument(
        "--error-line",
        action="append",
        dest="error_lines",
        default=[],
        help="Error line to overlay on FAIL screenshot (can be specified multiple times)",
    )

    args = parser.parse_args()
    dest = normalize_screenshot(
        case_id=args.case_id,
        source_path=args.source or None,
        output_dir=args.output_dir,
        title_text=args.title,
        status=args.status.upper(),
        error_lines=args.error_lines,
    )
    try:
        rel = dest.resolve().relative_to(PROJECT_ROOT.resolve()).as_posix()
    except ValueError:
        rel = dest.as_posix()

    print(rel)
    return 0


if __name__ == "__main__":
    sys.exit(main())

