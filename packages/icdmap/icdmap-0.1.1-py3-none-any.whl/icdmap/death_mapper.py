import sqlite3
import importlib.resources as pkg_resources
import pandas as pd
from tqdm import tqdm
import re

class DeathCauseMapper:
    def __init__(self, db_path=None):
        if db_path is None:
            with pkg_resources.path("icdmap.data", "death_cause_mapping.db") as path:
                db_path = str(path)
        self.conn = sqlite3.connect(db_path)

    def convert(self, codes, source="auto"):
        if isinstance(codes, str):
            return self._query_code(codes, source)
        elif isinstance(codes, (list, pd.Series)):
            result = {}
            for code in tqdm(pd.Series(codes).dropna().unique(), desc="Death Cause Mapping"):
                result[code] = self._query_code(code, source)
            return result
        else:
            raise TypeError("Unsupported input type. Use str, list, or pandas Series.")
        
    def _match_range(self, code, range_str):
        """
        Check if a code is within a defined ICD range.
        Supports numerical ranges (e.g., "410-414") and alphanumerical (e.g., "C00-C97").
        """
        code = code.upper().strip()
        for segment in re.split(r"[,\s]+", range_str):
            if "-" in segment:
                start, end = segment.split("-")
                try:
                    # Try numeric comparison
                    code_num = int(re.sub(r"[^\d]", "", code)[:3])
                    start_num = int(re.sub(r"[^\d]", "", start))
                    end_num = int(re.sub(r"[^\d]", "", end))
                    if start_num <= code_num <= end_num:
                        return True
                except ValueError:
                    # Fall back to lexicographic for non-numeric codes
                    if start <= code <= end:
                        return True
            elif code.startswith(segment):
                return True
        return False

    def _query_code(self, code, source):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM death_cause_mapping")
        rows = cur.fetchall()
        col_names = [desc[0] for desc in cur.description]

        results = []
        for row in rows:
            row_dict = dict(zip(col_names, row))
            icd9_match = self._match_range(code, str(row_dict["ICD9_RANGE"]))
            icd10_match = self._match_range(code, str(row_dict["ICD10_RANGE"]))
            cause_match = str(row_dict["CAUSE"]).strip() == str(code).strip()

            if source == "auto":
                if icd9_match or icd10_match or cause_match:
                    results.append(row_dict)
            elif source.lower() == "icd9" and icd9_match:
                results.append(row_dict)
            elif source.lower() == "icd10" and icd10_match:
                results.append(row_dict)
            elif source.lower() == "cause" and cause_match:
                results.append(row_dict)

        return results
