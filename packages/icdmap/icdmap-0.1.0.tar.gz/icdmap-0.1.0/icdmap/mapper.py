import sqlite3
import pandas as pd
from tqdm import tqdm
import importlib.resources as pkg_resources

class ICDConverter:
    def __init__(self, db_path=None, source="auto"):
        if db_path is None:
            with pkg_resources.path("icdmap.data", "icd_mapping.db") as path:
                db_path = str(path)
        self.conn = sqlite3.connect(db_path)
        self.source = source.lower()

    def convert(self, codes):
        if isinstance(codes, str):
            return self._query_code(codes)
        elif isinstance(codes, (list, pd.Series)):
            result = {}
            for code in tqdm(pd.Series(codes).dropna().unique(), desc="ICD Mapping"):
                result[code] = self._query_code(code)
            return result
        else:
            raise TypeError("Unsupported input type. Use str, list, or pandas Series.")

    def _normalize_code(self, code):
        if "." in code or not code.isdigit() or len(code) <= 3:
            return code
        return code[:3] + "." + code[3:]

    def _query_code(self, code):
        normalized_code = self._normalize_code(code)

        direction = self.source
        if direction == "auto":
            direction = "icd9" if normalized_code[:1].isdigit() else "icd10"

        if direction == "icd9":
            query = "SELECT * FROM icd_mapping WHERE `ICD-9` = ?"
            column_map = [
                "ICD-9", "ICD-10", "ICD-9 Chinese", "ICD-9 English",
                "ICD-10 Chinese", "ICD-10 English", "Mapping Code"
            ]
        elif direction == "icd10":
            query = "SELECT * FROM icd_mapping WHERE `ICD-10` = ?"
            column_map = [
                "ICD-10", "ICD-9", "ICD-10 Chinese", "ICD-10 English",
                "ICD-9 Chinese", "ICD-9 English", "Mapping Code"
            ]
        else:
            raise ValueError("Invalid source type. Use 'auto', 'icd9', or 'icd10'.")

        df = pd.read_sql_query(query, self.conn, params=(normalized_code,))
        if df.empty:
            return [{col: pd.NA for col in column_map} | {column_map[0]: code}]

        return df[column_map].to_dict("records")
