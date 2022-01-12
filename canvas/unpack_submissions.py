#!/usr/bin/env python3

# Adapted from
# https://github.com/BartMassey/moodle-hw/blob/master/unpack-rust-hw.py

from pathlib import Path

import argparse, os, sys, zipfile
import shutil, toml


def main():
    ap = argparse.ArgumentParser(description="Unpack submission files from Canvas")
    ap.add_argument(
        "archive",
        help="zip archive containing submissions (example: submissions.zip)",
    )
    ap.add_argument(
        "assignment", help="name of the assignment as defined in the CSV gradebook"
    )
    ap.add_argument(
        "-o",
        "--out",
        type=Path,
        help="Directory in which to output submissions",
    )
    ap.add_argument("--rust", action="store_true", help="Fix Cargo issues")
    args = ap.parse_args()

    unzip_submissions(Path(args.archive), args.assignment, args.out)


def unzip_submissions(path, assignment, out_dir=None, rust=False):
    submissions_dir = unzip(path, out_dir)

    for filename in os.listdir(submissions_dir):
        path = submissions_dir / filename

        if os.path.isdir(path):
            continue

        if filename.endswith(".zip"):
            sub_dir = unzip(path, remove=True)
            prepare_submission(sub_dir, assignment)
            if rust:
                prepare_cargo_project(sub_dir)
        else:
            print(f'warning: File "{filename}" does not appear to be a zip')


def unzip(path, out_dir=None, remove=False):
    if out_dir is None:
        out_dir = Path(os.path.splitext(path)[0])

    with zipfile.ZipFile(path, "r") as zip_file:
        zip_file.extractall(out_dir)

    if remove:
        os.remove(path)

    return out_dir


def prepare_submission(sub_dir, assignment):
    # infer student name and ID from submission directory
    # this might IndexError, but we'll take the risk
    parts = sub_dir.resolve().name.split("_")
    student_name = parts[0]
    student_id = int(parts[2] if parts[1] == "LATE" else parts[1])

    # write grading.toml
    with open(sub_dir / "grading.toml", "w") as grading_file:
        data = {
            "student": {"id": student_id, "short_name": student_name},
            "grades": {assignment: 0.0},
        }
        print(toml.dumps(data), file=grading_file, end="")

    # touch grading_comments.txt
    Path(sub_dir / "grading_comments.txt").touch()


def prepare_cargo_project(sub_dir):
    # pull up cargo project to be top-level
    if not (sub_dir / Path("Cargo.toml")).is_file():
        if not pull_cargo_up(sub_dir):
            return

    # move top-level main.rs to src
    main_file_path = Path("main.rs")
    main_path = sub_dir / main_file_path
    if main_path.is_file():
        src_path = sub_dir / Path("src")
        if not src_path.is_dir():
            src_path.mkdir()
        main_path.rename(sub_dir / Path("src") / main_file_path)


# https://stackoverflow.com/a/1724723
def find_cargo(gpath):
    result = []
    for root, _, files in os.walk(gpath):
        if "Cargo.toml" in files:
            result.append(Path(root))
    return result


def pull_cargo_up(gpath):
    actuals = find_cargo(gpath)

    if len(actuals) != 1:
        print(f"{gpath}: cannot pull up ({actuals})", file=sys.stderr)
        return False

    actual = actuals[0]
    for obj in actual.iterdir():
        obj.rename(gpath / obj.name)

    killme = Path(".").joinpath(*actual.parts[:3])
    for _, _, files in os.walk(killme):
        if len(files) > 0:
            print(f"{gpath}: warning: files remaining", file=sys.stderr)
            return True
    shutil.rmtree(killme)

    return True


if __name__ == "__main__":
    main()
