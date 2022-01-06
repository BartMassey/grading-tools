# canvas: tools for grading Canvas assignments

## Scripts

* `unpack_submissions.py` takes a zipped collection of submissions and extracts
  them to individual directories with added grading metadata. With the `--rust`
  flag enabled, Cargo projects in submissions are cleaned up to a more
  consistent format.
* `update_grades.py` extracts any grading metadata from submissions (see
  previous script) and updates a CSV gradebook.
* `locate_comments.py` (TODO) locates all non-empty `grading_comments.txt` and
  prints them.
