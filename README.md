# Grading Tools
Bart Massey 2021

This repo contains miscellaneous tools for grading specific homeworks
and projects in my courses. The repository
[moodle-hw](http://github.com/BartMassey/moodle-hw) contains
tools for dealing with downloading and uploading assignments
from Moodle.

* `canvas/`: Tools for grading Canvas assignments.
* `rust-modexp/`: Checkers for Rust `modexp` homework.
* `sound-clipped/`: Checkers for Sound `clipped` homework.
* `grade-rust.py`: General sanity checker for Rust crates.

## Grading Rust Programs

Use

    python3 <grading-tools>/grade-rust.py -t <grading-tools>/rust-rsa

where `<grading-tools>` is the path to this repo.

Note that `grade-rust.py` will potentially edit the Rust
project directory that it is run in to add tests. Use the
`-c` flag to `grade-rust.py` to have the student work
git-committed before and after these edits.
