# Grading Tools
Bart Massey 2021

This repo contains miscellaneous tools for grading specific homeworks
and projects in my courses.

* The repository
  [canvas-hw](http://github.com/BartMassey/canvas-hw)
  contains tools for dealing with downloading and uploading
  assignments from Canvas.

* The repository
  [moodle-hw](http://github.com/BartMassey/moodle-hw)
  contains tools for dealing with downloading and uploading
  assignments from Moodle.

* `rust-modexp/`: Checkers for Rust `modexp` homework.
* `rust-rsa/`: Checkers for Rust `rsa` homework.
* `rust-rule110`: Checkers for Rust `rule-110` homework.
* `rust-bbow`: Checkers for Rust `bbow` homework.
* `sound-clip/`: Checkers for Sound `clip` homework.
* `grade-rust.py`: General sanity checker for Rust crates.
* `fixcaps.py`: Clean up MS-DOS type pathname capitalization
  on a directory tree.

## Grading Rust Programs

Use

    python3 <grading-tools>/grade-rust.py

where `<grading-tools>` is the path to this repo and
checker is the name of the directory in this repo where the
checker for the given assignment lives.

Use `--help` to see the available options.

* The `-b` flag, when used in the directory containing all
  submissions, allows testing all submissions while grabbing
  a cup of beverage. Use with `-l` so that failures are
  recorded. Can recommend.

* Student-supplied tests are *not* run by default:
  use the `-T` flag for that.

* You may supply your own tests with the `-t` flag, whose
  argument is a path to your `tests/`
  directory. `grade-rust.py` will potentially edit the Rust
  project directory that it is run in to add your tests.
  Use the `-c` flag to `grade-rust.py` to have the student
  work git-committed before and after these edits, so that
  you can get the original back.
