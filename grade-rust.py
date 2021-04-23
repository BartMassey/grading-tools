#!/usr/bin/python3
# Do basic Rust HW tests

import argparse
from pathlib import Path
import shutil, subprocess

ap = argparse.ArgumentParser("Grade a Rust assignment.")
ap.add_argument(
    "-t", "--tests",
    help = "file of tests to run with student's assignment"
)
args = ap.parse_args()

def round(name, cmd):
    print(f"* checking {name}")
    result = subprocess.run(cmd.split())
    if result.returncode != 0:
        print(f"* {name} check failed")

def clean():
    subprocess.run("cargo clean".split())

clean()
round("rustfmt", "cargo fmt -- --check")
round("clippy", "cargo clippy -q -- -D warnings")
if args.tests:
    auxtests = Path(args.tests)
    testsdir = Path("tests")
    testsdir.mkdir(mode=0o700, exist_ok=True)
    test_target = testsdir / Path("grading-tests.rs")
    if test_target.exists():
        print(f"{test_target}: exists, not overwriting")
    else:
        shutil.copy(auxtests, test_target)
round("cargo test", "cargo test -- -q")
clean()
