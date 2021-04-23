#!/usr/bin/python3
# Do basic Rust HW tests

import argparse, json, shutil, subprocess
from pathlib import Path

ap = argparse.ArgumentParser("Grade a Rust assignment.")
ap.add_argument(
    "-t", "--tests",
    help = "file of tests to run with student's assignment",
)
args = ap.parse_args()

def run_tests(cmd):
    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        encoding="utf-8",
    )
    if result.returncode != 0:
        for line in result.stdout.split("\n"):
            if line.strip() == "":
                continue
            record = json.loads(line)
            if record["type"] == "test" and record["event"] == "failed":
                print(f'test failed: {record["name"]}')
                print(record["stdout"], end="")
    return result

def round(name, cmd, filtered=None):
    print(f"* checking {name}")
    cmd = cmd.split()
    if filtered is None:
        result = subprocess.run(cmd)
    else:
        result = filtered(cmd)
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
round(
    "cargo test",
    "cargo test -- -Zunstable-options --format=json --report-time",
    filtered=run_tests,
)
clean()
