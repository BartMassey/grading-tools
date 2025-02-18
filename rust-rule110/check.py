#!/usr/bin/python3
# Do basic Rust HW tests
# Bart Massey 2021

import difflib, subprocess

def clean():
    subprocess.run(
        "cargo clean".split(),
        capture_output=True,
    )

expected_output = [
    "*.*..*..",
    "***.**.*",
    "..******",
    ".**....*",
    "***...**",
    "..*..**.",
    ".**.***.",
    "*****.*.",
    "*...****",
    "*..**...",
]

def test(*args, expect=None, expect_fail=False):
    cmd = "cargo run --".split()
    cmd += map(lambda i: str(i), args)
    cmdstr = ' '.join(cmd)

    print("*", cmdstr)

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=3,
        )
    except TimeoutExpired:
        print("* program hung for 3 seconds")
        return False

    ok = True

    fail = result.returncode != 0
    if fail != expect_fail:
        print("*", cmdstr, "failed")
        print(result.stderr, end="")
        ok = False

    outputs = result.stdout.splitlines()

    noutputs = len(outputs)
    if noutputs == 0:
        print(f"* no output (expected {expect})")
        return False
    if noutputs != 10:
        print(f"* {noutputs} output lines: expected 10")
        ok = False
    if outputs != expected_output:
        print("* incorrect output")
        lines = difflib.context_diff(
            expected_output,
            outputs,
            fromfile="expected",
            tofile="got",
        )
        for line in list(lines)[3:]:
            print(f"*   {line}")
        ok = False
    return ok

ok = test()
clean()
if not ok:
    exit(1)
