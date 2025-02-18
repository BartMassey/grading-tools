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
    "-s", "--script",
    help = "directory containing check.py script to run on student's assignment",
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
    "-b", "--batch",
    help = "run on all subdirectories of cwd that have Cargo.toml",
    action = "store_true",
)
ap.add_argument(
    "--ignore-package-type",
    help = "do not do checks dependent on lib vs binary crate heuristic",
    action = "store_true",
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

def run_cmd(cmd, env = None):
    run_env = None
    if env:
        run_env = dict(os.environ)
        run_env.update(env)
    
    result = subprocess.run(
        cmd.split(),
        env = run_env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        encoding="utf-8",
    )
    if result.returncode == 0:
        return None
    return str(result.stdout)

def run_tests(cmd, env=None):
    result = run_cmd(cmd, env)
    if not result:
        return None
    messages = ""
    for line in result.split("\n"):
        l = line.strip()
        if l == "" or l[0] != "{":
            continue
        record = json.loads(l)
        if record["type"] == "test" and record["event"] == "failed":
            messages += f'test failed: {record["name"]}\n'
            messages += record["stdout"]
    return messages

def test_round(name, cmd, filtered=None, env=None):
    print(f"* checking {name}")
    if filtered is None:
        result = run_cmd(cmd, env=env)
    else:
        result = filtered(cmd, env=env)
    if result is not None:
        message = f"* {name} failed\n"
        message += result
        print(message, file=sys.stdout)
        log_message(message)
        return False
    return True

def clean():
    subprocess.run("cargo clean -q".split())

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
        f"cargo +nightly test {cargo_flags()} -- -Zunstable-options --format=json --report-time",
        filtered=run_tests,
    )

def run_grading_script(script):
    test_round(
        "grading test python script",
        f"python {script}",
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

def grade_cwd():
    cargo_lock = Path('Cargo.lock')
    has_cargo_lock = False
    if cargo_lock.is_file():
        has_cargo_lock = True

    target_dir = Path("target")
    if target_dir.is_dir():
        message = '* target directory in submission'
        print(message)
        log_message(message)
    clean()

    if not args.ignore_package_type:
        src = Path('src')
        if (src / 'main.rs').is_file():
            if not has_cargo_lock:
                message = '* no Cargo.lock in bin crate submission'
                print(message)
                log_message(message)

    if args.commit:
        git_commit('student homework assignment')

    built = test_round("compile", 'cargo check -q')
    if built:
        built_clean = test_round(
            "warnings",
            'cargo check -q',
            env={'RUSTFLAGS': '-D warnings'},
        )
        if built_clean:
            test_round("rustfmt", "cargo fmt -- --check --color=never")
            test_round("clippy", f"cargo clippy -q {cargo_flags()} -- -D warnings")
            if args.do_tests:
                test_round(
                    "cargo test",
                    "cargo +nightly test -- -Zunstable-options --format=json --report-time",
                    filtered=run_tests,
                )

        if args.tests:
            tests_dir = Path(sys.argv[0]).parent
            run_grading_tests(tests_dir / args.tests)

        if args.script:
            tests_dir = Path(sys.argv[0]).parent
            run_grading_script(tests_dir / args.script / "check.py")

    if args.commit:
        git_commit('added grading stuff')

    clean()
    if not has_cargo_lock:
        cargo_lock.unlink()

if args.batch:
    for subdir in sorted(list(Path(".").iterdir())):
        logfile = None
        if not (subdir / "Cargo.toml").exists():
            continue
        print(f"batch grading: subdir {subdir}")
        os.chdir(subdir)
        grade_cwd()
        os.chdir("..")
else:
    grade_cwd()
