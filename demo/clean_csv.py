"""A small, repeatable CSV workflow for the schema documented in README.md."""

import argparse
import csv
import io
from pathlib import Path
import sys


INPUT_COLUMNS = ["customer_id", "name", "email", "status", "city"]
OUTPUT_COLUMNS = ["customer_id", "name", "email", "city"]
REJECTED_COLUMNS = ["source_file", "source_line", *INPUT_COLUMNS, "reason"]


class InputError(ValueError):
    """The supplied CSV does not match this workflow's input contract."""


def read_inputs(paths):
    """Validate all inputs before returning rows; never infer numeric types."""
    rows = []
    for path in paths:
        try:
            with path.open("r", encoding="utf-8-sig", newline="") as source:
                reader = csv.reader(source, strict=True)
                header = next(reader, None)
                if header != INPUT_COLUMNS:
                    raise InputError(
                        f"{path}: expected header {','.join(INPUT_COLUMNS)}; got {header!r}"
                    )
                for fields in reader:
                    # A source line is the final physical line of the CSV record.
                    if len(fields) != len(INPUT_COLUMNS):
                        raise InputError(
                            f"{path}:{reader.line_num}: expected {len(INPUT_COLUMNS)} fields, "
                            f"got {len(fields)}"
                        )
                    rows.append((path.name, reader.line_num, dict(zip(INPUT_COLUMNS, fields))))
        except (UnicodeError, csv.Error) as exc:
            raise InputError(f"{path}: invalid UTF-8 CSV: {exc}") from exc
    return rows


def process_rows(rows, active_status="active"):
    """Apply the five documented rules in input order."""
    merged = []
    rejected = []
    seen = set()
    for source_file, source_line, original in rows:
        cleaned = {key: value.strip() for key, value in original.items()}
        customer_id = cleaned["customer_id"]
        if not customer_id:
            reason = "missing_customer_id"
        elif cleaned["status"] != active_status:
            reason = "filtered_status"
        elif customer_id in seen:
            reason = "duplicate_customer_id"
        else:
            seen.add(customer_id)
            merged.append({column: cleaned[column] for column in OUTPUT_COLUMNS})
            continue
        # Rejected values retain the original text, including surrounding spaces.
        rejected.append(
            {
                "source_file": source_file,
                "source_line": str(source_line),
                **original,
                "reason": reason,
            }
        )
    return merged, rejected


def render_csv(columns, rows):
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=columns, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def run_workflow(input_paths, merged_path, rejected_path, active_status="active"):
    inputs = [Path(path) for path in input_paths]
    merged_path, rejected_path = Path(merged_path), Path(rejected_path)
    if not inputs:
        raise InputError("at least one input CSV is required")
    resolved_inputs = [path.resolve() for path in inputs]
    resolved_outputs = [merged_path.resolve(), rejected_path.resolve()]
    if len(set(resolved_inputs)) != len(resolved_inputs):
        raise InputError("the same input file was supplied more than once")
    if len(set(resolved_outputs)) != 2:
        raise InputError("merged and rejected outputs must be different files")
    if set(resolved_inputs) & set(resolved_outputs):
        raise InputError("an output must not overwrite an input file")

    merged, rejected = process_rows(read_inputs(inputs), active_status)
    # Both inputs and output text are validated/generated before any output write.
    merged_text = render_csv(OUTPUT_COLUMNS, merged)
    rejected_text = render_csv(REJECTED_COLUMNS, rejected)
    for path, content in ((merged_path, merged_text), (rejected_path, rejected_text)):
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8", newline="") as destination:
            destination.write(content)
    return {"read": len(merged) + len(rejected), "accepted": len(merged), "rejected": len(rejected)}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", nargs="+", type=Path, help="CSV inputs, in processing order")
    parser.add_argument("--merged", required=True, type=Path, help="Accepted-row output CSV")
    parser.add_argument("--rejected", required=True, type=Path, help="Rejected-row output CSV")
    parser.add_argument("--active-status", default="active", help="Exact status value to keep")
    args = parser.parse_args(argv)
    try:
        counts = run_workflow(args.inputs, args.merged, args.rejected, args.active_status)
    except (InputError, OSError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    print(f"Read: {counts['read']} | Accepted: {counts['accepted']} | Rejected: {counts['rejected']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
