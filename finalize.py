"""
finalize.py — build the Assessment 1 submission ZIP.

Usage:
    python finalize.py --student-id 12345678
    python finalize.py --student-id 12345678 --skip-tests

Steps:
    1. Run the unit tests (stops if any fail, unless --skip-tests).
    2. Delete __pycache__ folders and stray temp files.
    3. Check the submission/ folder contains the demo video and the report.
    4. Create CSC44102_A1_<student-id>.zip containing:
           source/   — both applications, core package, tests, data, docs
           <video>   — demo video
           <report>  — technical report

GenAI declaration: This file was drafted with assistance from Claude (Anthropic)
and reviewed/modified by [Your Name]. See README.md for full GenAI statement.
"""

from __future__ import annotations

import argparse
import shutil
import sys
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SUBMISSION_DIR = ROOT / "submission"

SOURCE_ITEMS = [
    "core",
    "tests",
    "data/sample_data.json",
    "docs",
    "cli_app.py",
    "gui_app.py",
    "README.md",
    "requirements.txt",
]
VIDEO_EXTS = {".mp4", ".mov", ".mkv", ".avi", ".webm"}
REPORT_EXTS = {".pdf", ".docx"}
SKIP_NAMES = {"__pycache__", ".DS_Store", "Thumbs.db"}


def run_tests() -> bool:
    print("1) Running unit tests...")
    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"), top_level_dir=str(ROOT))
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    return result.wasSuccessful()


def clean() -> None:
    print("2) Cleaning caches...")
    for cache in ROOT.rglob("__pycache__"):
        shutil.rmtree(cache, ignore_errors=True)
    for tmp in ROOT.rglob("*.tmp"):
        tmp.unlink(missing_ok=True)


def find_one(exts: set[str], label: str) -> Path | None:
    matches = sorted(p for p in SUBMISSION_DIR.iterdir() if p.suffix.lower() in exts)
    if not matches:
        print(f"   MISSING {label}: put a {'/'.join(sorted(exts))} file in submission/")
        return None
    if len(matches) > 1:
        print(f"   NOTE: several {label} files found, using {matches[0].name}")
    print(f"   found {label}: {matches[0].name}")
    return matches[0]


def iter_source_files():
    for item in SOURCE_ITEMS:
        path = ROOT / item
        if path.is_file():
            yield path
        elif path.is_dir():
            for file in sorted(path.rglob("*")):
                if file.is_file() and not (SKIP_NAMES & set(file.parts)):
                    yield file
        else:
            print(f"   WARNING: {item} not found, skipped")


def build_zip(student_id: str, video: Path, report: Path) -> Path:
    zip_path = ROOT / f"CSC44102_A1_{student_id}.zip"
    print(f"4) Building {zip_path.name} ...")
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for file in iter_source_files():
            zf.write(file, Path("source") / file.relative_to(ROOT))
        zf.write(video, video.name)
        zf.write(report, report.name)
    size_mb = zip_path.stat().st_size / (1024 * 1024)
    print(f"   done: {zip_path.name} ({size_mb:.1f} MB)")
    return zip_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the Assessment 1 submission ZIP.")
    parser.add_argument("--student-id", required=True, help="your Keele student number")
    parser.add_argument("--skip-tests", action="store_true", help="do not run unit tests")
    args = parser.parse_args()

    if not args.skip_tests and not run_tests():
        print("Tests failed — fix them before submitting.")
        return 1
    clean()

    print("3) Checking submission/ folder...")
    SUBMISSION_DIR.mkdir(exist_ok=True)
    video = find_one(VIDEO_EXTS, "demo video")
    report = find_one(REPORT_EXTS, "technical report")
    if not (video and report):
        return 1

    build_zip(args.student_id, video, report)
    print("Upload this ZIP to the Assessment 1 drop-box on KLE.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
