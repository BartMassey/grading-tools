#!/usr/bin/python3
# Do basic Rust HW tests

import argparse, json, os, pygit2, shutil, subprocess, sys, toml
from pathlib import Path

ap = argparse.ArgumentParser("Grade a Rust assignment.")
ap.add_argument(
    "-t", "--tests",
    help = "file of tests to run with student's assignment",
)
ap.add_argument(
    "-c", "--commit",
    help = "make a git repo and commit before editing student work",
    action = "store_true",
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

def merge_to(src, dest):
    for key, val in src.items():
        if key == "dev-dependencies":
            assert type(val) is dict
            if key not in dest:
                dest[key] = dict()
            for subkey, subval in val.items():
                if "dependencies" in dest and subkey in dest["dependencies"]:
                    dest["dependencies"][subkey] = subval
                else:
                    dest[key][subkey] = val
        elif key == "test":
            assert type(val) is list
            if key in dest:
                dest[key] += val
            else:
                dest[key] = val
        else:
            print(f"test Cargo.toml: key {key} ignored", file=sys.stderr)

def rewrite_cargo_toml(tests):
    cml = toml.load("Cargo.toml")
    cmlt = toml.load(tests / "Cargo.toml")
    merge_to(cmlt, cml)
    os.rename("Cargo.toml", "Cargo.toml.orig")
    toml.dump(cml, open("Cargo.toml", "w"))

def run_grading_tests(tests):
    if not Path("Cargo.toml.orig").is_file():
        auxtests = Path(tests)
        shutil.copy(auxtests / Path("grading-tests.rs"), ".")
        rewrite_cargo_toml(auxtests)
    round(
        "cargo test (grading-tests)",
        "cargo test -- -Zunstable-options --format=json --report-time",
        filtered=run_tests,
    )


def git_commit(message):
    repo_path = pygit2.discover_repository(os.getcwd())
    if repo_path is None:
        repo = pygit2.init_repository(".")
    else:
        repo = pygit2.Repository(repo_path)
    index = repo.index
    index.add_all()
    index.write()
    author = pygit2.Signature('Rust Grading', 'bart@cs.pdx.edu')
    committer = pygit2.Signature('Rust Grading', 'bart@cs.pdx.edu')
    tree = index.write_tree()
    if repo.head_is_unborn:
        parent = []
    else:
        parent = [repo.head.target]
    commit = repo.create_commit(
        'HEAD',
        author,
        committer,
        message,
        tree,
        parent
    )
    index.write()

clean()
if args.commit:
    git_commit('student homework assignment')
round("rustfmt", "cargo fmt -- --check")
round("clippy", "cargo clippy -q -- -D warnings")
round(
    "cargo test",
    "cargo test -- -Zunstable-options --format=json --report-time",
    filtered=run_tests,
)
if args.tests:
    run_grading_tests(args.tests)
if args.commit:
    git_commit('added grading stuff')
clean()
