import unittest
import sqlite3
import importlib.resources as pkg_resources

class TestDatabaseStructure(unittest.TestCase):
    def test_icd_mapping_table_exists(self):
        with pkg_resources.path("icdmap", "icd_mapping.db") as db_path:
            conn = sqlite3.connect(str(db_path))
            cur = conn.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='icd_mapping'")
            table = cur.fetchone()
            self.assertIsNotNone(table, "Table 'icd_mapping' does not exist in the database.")
            conn.close()

    def test_icd_mapping_columns(self):
        expected_columns = {
            "ICD-9", "ICD-9 English", "ICD-9 Chinese",
            "ICD-10", "ICD-10 English", "ICD-10 Chinese", "Mapping Code"
        }
        with pkg_resources.path("icdmap", "icd_mapping.db") as db_path:
            conn = sqlite3.connect(str(db_path))
            cur = conn.cursor()
            cur.execute("PRAGMA table_info(icd_mapping)")
            columns = {row[1] for row in cur.fetchall()}
            self.assertTrue(expected_columns.issubset(columns), f"Missing columns: {expected_columns - columns}")
            conn.close()

if __name__ == '__main__':
    unittest.main()
