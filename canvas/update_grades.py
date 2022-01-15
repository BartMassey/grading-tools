#!/usr/bin/env python3

from pathlib import Path
from prettytable import PrettyTable

import argparse, csv, os
import toml


def main():
    ap = argparse.ArgumentParser(
        description="Gather grades from the submissions directory and update the gradebook"
    )
    ap.add_argument("gradebook", help="Path to the CSV gradebook")
    ap.add_argument(
        "assignment", help="The name and ID of the assignment (see gradebook CSV)"
    )
    ap.add_argument("submissions", help="Directory in which submissions reside")
    ap.add_argument(
        "-o",
        "--out",
        type=Path,
        help="CSV file to output to, if not the input file",
    )
    args = ap.parse_args()

    assignment = args.assignment

    old_grades = read_gradebook(Path(args.gradebook), assignment)
    new_grades = find_grades(Path(args.submissions), assignment)
    pretty_print_changes(old_grades, new_grades, assignment)

    if args.out:
        merged = merge_grades(old_grades, new_grades)

        out = Path(args.out) or Path(args.gradebook)
        save_gradebook(merged, out, assignment)


def find_grades(submissions_path, assignment):
    grades = dict()
    for grading_path in submissions_path.rglob("grading.toml"):
        data = toml.load(grading_path)

        if assignment not in data["grades"]:
            continue

        student_id = data["student"]["id"]
        grades[student_id] = data
    return grades


def merge_grades(old_gradebook, new_gradebook):
    gradebook = old_gradebook.copy()
    for id, new_record in new_gradebook.items():
        old_record = gradebook[id]
        for key in new_record:
            if type(new_record[key]) is dict:
                old_record[key] = {**old_record[key], **new_record[key]}
    return gradebook


def read_gradebook(path, assignment):
    grades = dict()
    with open(path, newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            # rows without "ID" contain extra metadata, skip
            # filter students with this assignment
            if row["ID"] and assignment in row:
                grades[int(row["ID"])] = {
                    "student": {
                        "id": int(row["ID"]),
                        "name": row["Student"],
                        "section": row["Section"],
                    },
                    "grades": {
                        assignment: row[assignment],
                    },
                }

    return grades


def save_gradebook(gradebook, path, assignment):
    print(f"Saving changes to {path}")

    with open(path, "w", newline="") as csv_file:
        fieldnames = ["Student", "ID", "Section", assignment]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        writer.writeheader()

        for record in gradebook.values():
            if assignment not in record["grades"]:
                continue

            student = record["student"]
            grade = record["grades"][assignment]

            writer.writerow(
                {
                    "ID": student["id"],
                    "Student": student["name"],
                    "Section": student["section"],
                    assignment: grade,
                }
            )


def pretty_print_changes(old_gradebook, new_gradebook, assignment):
    table = PrettyTable()
    table.field_names = ["ID", "Name", "Assignment", "Old", "New"]

    table.align = "l"

    table.align["Old"] = "r"
    table.align["New"] = "r"

    for id, old_record in old_gradebook.items():
        new_record = new_gradebook.get(id) or old_record

        name = old_record["student"]["name"] or new_record["student"]["name"]
        old_grade = old_record["grades"][assignment]
        new_grade = new_record["grades"][assignment]

        table.add_row([id, name, assignment, old_grade, new_grade])

    print(table)


if __name__ == "__main__":
    main()
