import argparse
import json
import pandas as pd
import sys
import importlib.resources as pkg_resources
from .mapper import ICDConverter
from .death_mapper import DeathCauseMapper

def main():
    parser = argparse.ArgumentParser(description="ICD code and cause-of-death mapping tool")
    parser.add_argument("code", nargs="?", help="Single ICD or CAUSE code to convert (optional if using --csv)")
    parser.add_argument("--csv", help="Input CSV file with code column")
    parser.add_argument("--source", choices=["auto", "icd9", "icd10"], default="auto",
                        help="Specify ICD input code type: auto (default), icd9, or icd10")
    parser.add_argument("--mode", choices=["icd", "death"], default="icd",
                        help="Choose mapping mode: icd (default) or death")
    parser.add_argument("-o", "--output", default="mapping_output.json", help="Output JSON file")
    args = parser.parse_args()

    try:
        if args.csv:
            print("\U0001F4C4 Using CSV mode")
            handle_csv_mode(args.csv, args.output, args.source, args.mode)
        elif args.code:
            print("\U0001F50D Using single code mode")
            handle_single_mode(args.code, args.output, args.source, args.mode)
        else:
            print("\u274C You must provide a code or --csv input.")
            parser.print_help()
            sys.exit(1)
    except Exception as e:
        print("\u274C Error occurred:", str(e), file=sys.stderr)
        sys.exit(1)

def handle_csv_mode(csv_path, output_path, source, mode):
    df = pd.read_csv(csv_path, dtype=str)
    column = "ICD9_CODE" if mode == "icd" else "CODE"
    if column not in df.columns:
        raise ValueError(f"CSV must contain a column named '{column}'.")

    if mode == "icd":
        with pkg_resources.path("icdmap.data", "icd_mapping.db") as db_path:
            mapper = ICDConverter(str(db_path), source=source)
    else:
        with pkg_resources.path("icdmap.data", "death_cause_mapping.db") as db_path:
            mapper = DeathCauseMapper(str(db_path))

    results = {}
    for code in df[column].dropna().unique():
        print(f"Querying: {code}")
        result = mapper.convert(code)
        results[code] = result

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\u2705 Batch query results saved to {output_path}")

def handle_single_mode(code, output_path, source, mode):
    if mode == "icd":
        with pkg_resources.path("icdmap.data", "icd_mapping.db") as db_path:
            mapper = ICDConverter(str(db_path), source=source)
    else:
        with pkg_resources.path("icdmap.data", "death_cause_mapping.db") as db_path:
            mapper = DeathCauseMapper(str(db_path))

    result = mapper.convert(code)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({code: result}, f, ensure_ascii=False, indent=2)
    print(f"\u2705 Query result saved to {output_path}")
