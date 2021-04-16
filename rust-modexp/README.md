# rust-modexp: checks for modexp homework
Bart Massey 2021

`checkmodexp.py` runs the user's `modexp` homework and
checks that it produces the correct output on various test
values. The heuristic for finding the user's answer is not
very robust against output format issues.

`gentests.py` was used to generate the randomized tests
currently hardcoded into `checkmodexp.py`. It should
normally be ignored.

See also `grade-rust.py` in this repo for crate sanity checks.
