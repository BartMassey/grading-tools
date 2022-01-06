#!/usr/bin/env python3

# Adapted from
# https://github.com/BartMassey/moodle-hw/blob/master/unpack-rust-hw.py

import argparse, os, sys, zipfile
import shutil
from pathlib import Path


def main():
    ap = argparse.ArgumentParser(
        description='Unpack submission files from Canvas')
    ap.add_argument(
        'archive',
        help='zip archive containing submissions (example: submissions.zip)',
    )
    ap.add_argument('-o',
                    '--out',
                    help='Directory in which to output submissions')
    args = ap.parse_args()

    unzip_submissions(Path(args.archive), Path('staged'))
    Path('graded').mkdir(exist_ok=True)


def unzip_submissions(path, out_dir):
    submissions_dir = unzip(path, out_dir)

    for filename in os.listdir(submissions_dir):
        path = submissions_dir / filename

        if os.path.isdir(path):
            continue
        elif filename.endswith('.zip'):
            print("-" * 72)
            sub_dir = unzip(path, remove=True)
            clean_submission(Path(sub_dir))
        else:
            print(f'warning: File "{filename}" does not appear to be a zip')


def unzip(path, out_dir=None, remove=False):
    if out_dir is None:
        out_dir = Path(os.path.splitext(path)[0])

    print(f'unzipping {path}')
    with zipfile.ZipFile(path, 'r') as zip_file:
        zip_file.extractall(out_dir)

    if remove:
        print(f'removing {path}')
        os.remove(path)

    return out_dir


# https://stackoverflow.com/a/1724723
def find_cargo(gpath):
    result = []
    for root, _, files in os.walk(gpath):
        if "Cargo.toml" in files:
            result.append(Path(root))
    return result


def pull_up(gpath):
    actuals = find_cargo(gpath)

    if len(actuals) != 1:
        print(f"{gpath}: cannot pull up ({actuals})", file=sys.stderr)
        return False

    actual = actuals[0]
    for obj in actual.iterdir():
        obj.rename(gpath / obj.name)

    killme = Path('.').joinpath(*actual.parts[:3])
    for _, _, files in os.walk(killme):
        if len(files) > 0:
            print(f"{gpath}: warning: files remaining", file=sys.stderr)
            return True
    shutil.rmtree(killme)

    return True


def clean_submission(sub_dir):
    # pull up cargo project to be top-level
    if not (sub_dir / Path("Cargo.toml")).is_file():
        print('attempting to pull up inner Cargo project')
        if not pull_up(sub_dir):
            return

    # move top-level main.rs to src
    main_file_path = Path("main.rs")
    main_path = sub_dir / main_file_path
    if main_path.is_file():
        print(f'moving top-level main.rs to src directory')
        src_path = sub_dir / Path("src")
        if not src_path.is_dir():
            src_path.mkdir()
        main_path.rename(sub_dir / Path("src") / main_file_path)


if __name__ == '__main__':
    main()
