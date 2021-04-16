#!/usr/bin/python3
# Do basic Rust HW tests

import subprocess

def round(name, cmd):
    print(f"* checking {name}")
    result = subprocess.run(cmd.split())
    if result.returncode != 0:
        print(f"* {name} check failed")

def clean():
    subprocess.run("cargo clean".split())

clean()
round("rustfmt", "cargo fmt -- --check")
round("clippy", "cargo clippy -D warnings")
round("cargo test", "cargo test -- -q")
clean()
