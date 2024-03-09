# Grading Tools
Bart Massey 2021

This repo contains miscellaneous tools for grading specific homeworks
and projects in my courses. The repository
[moodle-hw](http://github.com/BartMassey/moodle-hw) contains
tools for dealing with downloading and uploading assignments
from Moodle.

* `canvas/`: Tools for grading Canvas assignments.
* `rust-modexp/`: Checkers for Rust `modexp` homework.
* `rust-rsa/`: Checkers for Rust `rsa` homework.
* `sound-clipped/`: Checkers for Sound `clipped` homework.
* `grade-rust.py`: General sanity checker for Rust crates.

## Grading Rust Programs

Use

    python3 <grading-tools>/grade-rust.py

where `<grading-tools>` is the path to this repo and
checker is the name of the directory in this repo where the
checker for the given assignment lives.

Use `--help` to see the available options.

* Student-supplied tests are *not* run by default:
  use the `-T` flag for that.

* You may supply your own tests with the `-t` flag, whose
  argument is a path to your `tests/`
  directory. `grade-rust.py` will potentially edit the Rust
  project directory that it is run in to add your tests.
  Use the `-c` flag to `grade-rust.py` to have the student
  work git-committed before and after these edits, so that
  you can get the original back.
