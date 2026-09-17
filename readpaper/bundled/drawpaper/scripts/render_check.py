#!/usr/bin/env python3
"""Render a one-page architecture PDF and collect evidence for manual review.

Requires Python 3 and Poppler: pdfinfo, pdftoppm, pdftotext, pdffonts,
pdfimages. It does not edit the PDF or certify visual/scientific correctness.
"""

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import statistics
import subprocess
import sys
import xml.etree.ElementTree as ET


def run_tool(name, args, tool_dir):
    executable = str(tool_dir / name) if tool_dir else shutil.which(name)
    if not executable or not Path(executable).is_file():
        raise RuntimeError(f"Missing Poppler tool: {name}; use PATH or --poppler-dir")
    result = subprocess.run(
        [executable, *map(str, args)], capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=60,
        env={**os.environ, "LC_ALL": "C"},
    )
    if result.returncode:
        raise RuntimeError(f"{name} failed: {result.stderr.strip()}")
    return result.stdout


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--tex-log", type=Path)
    parser.add_argument("--poppler-dir", type=Path)
    parser.add_argument("--full-width", type=int, default=3300)
    parser.add_argument("--screen-width", type=int, default=1100)
    parser.add_argument("--overwrite", action="store_true",
                        help="Replace only this PDF's three named QA outputs")
    args = parser.parse_args()
    pdf = args.pdf.expanduser().resolve(strict=True)
    out_dir = args.out_dir.expanduser().resolve()
    tool_dir = args.poppler_dir.expanduser().resolve() if args.poppler_dir else None
    if min(args.full_width, args.screen_width) < 200:
        parser.error("Render widths must be at least 200 pixels")
    if args.full_width < args.screen_width:
        parser.error("--full-width must be at least --screen-width")
    if args.tex_log and not args.tex_log.expanduser().is_file():
        parser.error("The supplied TeX log does not exist")

    preview = out_dir / f"{pdf.stem}.png"
    screen = out_dir / f"{pdf.stem}-screen.png"
    report_path = out_dir / f"{pdf.stem}-qa.json"
    for path in (preview, screen, report_path):
        if path.exists() and not args.overwrite:
            raise RuntimeError(f"Output exists: {path}; choose a new directory or --overwrite")

    info = run_tool("pdfinfo", [pdf], tool_dir)
    page_match = re.search(r"^Pages:\s+(\d+)", info, re.MULTILINE)
    if not page_match or int(page_match.group(1)) != 1:
        raise RuntimeError("Expected a single-page architecture PDF; no preview was exported")
    bbox_xml = run_tool("pdftotext", ["-bbox-layout", "-enc", "UTF-8", pdf, "-"], tool_dir)
    root = ET.fromstring(bbox_xml)
    page = root.find(".//{*}page")
    if page is None:
        raise RuntimeError("Poppler did not return page bounds")
    width, height = float(page.attrib["width"]), float(page.attrib["height"])
    words = page.findall(".//{*}word")
    outside = []
    word_heights = []
    for word in words:
        x0, y0, x1, y1 = (float(word.attrib[key]) for key in ("xMin", "yMin", "xMax", "yMax"))
        if x0 < -0.5 or y0 < -0.5 or x1 > width + 0.5 or y1 > height + 0.5:
            outside.append({"text": "".join(word.itertext()), "bbox": [x0, y0, x1, y1]})
        word_heights.append((y1 - y0) * args.screen_width / width)

    fonts = run_tool("pdffonts", [pdf], tool_dir)
    images = run_tool("pdfimages", ["-list", pdf], tool_dir)
    log_issues = []
    log_hints = []
    if args.tex_log:
        for number, line in enumerate(args.tex_log.expanduser().read_text(errors="replace").splitlines(), 1):
            if re.search(r"^!|Missing character:|Overfull \\[hv]box|Font .*not found|fontspec Error", line):
                log_issues.append({"line": number, "message": line.strip()})
            elif re.search(r"Underfull \\[hv]box|LaTeX .*Warning:|Package .*Warning:", line):
                log_hints.append({"line": number, "message": line.strip()})

    out_dir.mkdir(parents=True, exist_ok=True)
    for target, pixel_width in ((preview, args.full_width), (screen, args.screen_width)):
        run_tool("pdftoppm", ["-f", "1", "-l", "1", "-png", "-singlefile",
                              "-scale-to-x", pixel_width, "-scale-to-y", "-1",
                              pdf, target.with_suffix("")], tool_dir)
        if not target.is_file() or target.stat().st_size == 0:
            raise RuntimeError(f"Renderer did not produce {target}")

    issues = []
    if not words:
        issues.append("No extractable words: inspect whether the diagram is raster-only or text is outlined")
    if outside:
        issues.append("Text bounds extend outside the PDF page")
    if log_issues:
        issues.append("TeX log findings require inspection and correction where applicable")
    report = {
        "source_pdf": str(pdf), "pages": 1,
        "page_size_pt": [width, height], "word_count": len(words),
        "text_outside_page": outside,
        "median_word_box_height_at_screen_px": round(statistics.median(word_heights), 2) if word_heights else None,
        "word_height_note": "A size hint only; scripts and math affect bounding boxes. Inspect normal-width text visually.",
        "tex_log_checked": bool(args.tex_log), "tex_log_issues": log_issues,
        "tex_log_hints": log_hints, "fonts_evidence": fonts.strip(),
        "raster_images_evidence": images.strip(), "structural_findings": issues,
        "visual_review": "REQUIRED: latest full figure at screen width and dense regions at high resolution",
        "scientific_review": "REQUIRED: compare content, formulas and connections with the paper",
        "limitations": "Does not detect all internal overlaps or establish scientific correctness; no final approval is implied.",
        "outputs": {"preview": str(preview), "screen": str(screen), "report": str(report_path)},
    }
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"structural_findings": issues, "manual_review_required": True,
                      "outputs": report["outputs"]}, ensure_ascii=False, indent=2))
    return 2 if issues else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, RuntimeError, ValueError, subprocess.TimeoutExpired, ET.ParseError) as exc:
        print(f"render_check: {exc}", file=sys.stderr)
        sys.exit(1)
