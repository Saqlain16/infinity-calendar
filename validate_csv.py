"""
validate_csv.py
----------------
Sanity-checks employees.csv before you deploy. Run this after editing the
CSV in Excel to catch the classic "Excel silently reformatted my dates"
problem before it causes 0 records (or dropped rows) in the dashboard.

Usage:
    python validate_csv.py employees.csv
"""

import csv
import re
import sys

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
REQUIRED_HEADERS = ["Name", "Date of Birth", "Designation", "Date of Joining", "Branch Name"]


def looks_like_wrong_order(value: str) -> bool:
    """Detect DD-MM-YYYY or MM-DD-YYYY (or with '/') so we can give a
    specific hint instead of just 'invalid'."""
    return bool(re.match(r"^\d{2}[-/]\d{2}[-/]\d{4}$", value))


def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_csv.py <path-to-csv>")
        sys.exit(1)

    path = sys.argv[1]
    try:
        with open(path, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames or []
            rows = list(reader)
    except FileNotFoundError:
        print(f"Error: '{path}' not found.")
        sys.exit(1)

    problems = 0

    missing_headers = [h for h in REQUIRED_HEADERS if h not in headers]
    if missing_headers:
        print(f"✗ Missing/misspelled header(s): {missing_headers}")
        print(f"  Found headers: {headers}")
        problems += 1

    print(f"Checked {len(rows)} row(s) in '{path}'.\n")

    for i, row in enumerate(rows, start=2):  # +2 to account for header row, 1-index
        name = (row.get("Name") or "").strip()
        for field in ["Date of Birth", "Date of Joining"]:
            value = (row.get(field) or "").strip()
            if not value:
                continue
            if not DATE_RE.match(value):
                problems += 1
                hint = " (looks like DD-MM-YYYY or MM-DD-YYYY — re-save as YYYY-MM-DD)" if looks_like_wrong_order(value) else ""
                print(f"✗ Row {i} ({name or 'no name'}): {field} = '{value}'{hint}")
        if not name:
            problems += 1
            print(f"✗ Row {i}: missing Name")
        if not (row.get("Date of Birth") or "").strip() and not (row.get("Date of Joining") or "").strip():
            problems += 1
            print(f"✗ Row {i} ({name or 'no name'}): no Date of Birth AND no Date of Joining — this row won't show up at all")

    print()
    if problems == 0:
        print("✓ All good — this CSV is ready to deploy.")
    else:
        print(f"Found {problems} issue(s) above. Fix these in a plain text editor "
              f"(Notepad/VS Code) or by formatting the date columns as Text in Excel "
              f"before re-typing the dates, then re-run this check.")


if __name__ == "__main__":
    main()
