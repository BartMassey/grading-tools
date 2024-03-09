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
ap.add_argument(
    "-T", "--do-tests",
    help = "run cargo test",
    action = "store_true",
)
ap.add_argument(
    "-l", "--error-logfile",
    help = "file to log any clippy, rustfmt, test errors",
)
ap.add_argument(
    "cargo_flags",
    help = "additional flags for cargo",
    nargs = "*",
)
args = ap.parse_args()

logfile = None
def log_message(message):
    global logfile
    if not args.error_logfile:
        return
    if not logfile:
        logfile = open(args.error_logfile, "w")
    print(message, file=logfile)

def cargo_flags():
    if args.cargo_flags:
        return ' '.join(args.cargo_flags)
    return ""

def run_cmd(cmd):
    result = subprocess.run(
        cmd.split(),
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        encoding="utf-8",
    )
    if not result:
        return None
    return str(result.stdout)

def run_tests(cmd):
    result = run_cmd(cmd)
    if not result:
        return None
    messages = ""
    for line in result.stdout.split("\n"):
        if line.strip() == "":
            continue
        record = json.loads(line)
        if record["type"] == "test" and record["event"] == "failed":
            messages += f'test failed: {record["name"]}\n'
            messages += record["stdout"]
    return messages

def test_round(name, cmd, filtered=None):
    print(f"* checking {name}")
    if filtered is None:
        result = run_cmd(cmd)
    else:
        result = filtered(cmd)
    if result:
        message = f"* {name} failed\n"
        message += result
        print(message, file=sys.stdout)
        log_message(message)

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
    test_round(
        "cargo test (grading-tests)",
        f"cargo test {cargo_flags()} -- -Zunstable-options --format=json --report-time",
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

test_round("rustfmt", "cargo fmt -- --check")
test_round("clippy", f"cargo clippy -q {cargo_flags()} -- -D warnings")
if args.do_tests:
    test_round(
        "cargo test",
        "cargo test -- -Zunstable-options --format=json --report-time",
        filtered=run_tests,
    )

if args.tests:
    tests_dir = Path(sys.argv[0]).parent
    run_grading_tests(tests_dir / args.tests)

if args.commit:
    git_commit('added grading stuff')

clean()
