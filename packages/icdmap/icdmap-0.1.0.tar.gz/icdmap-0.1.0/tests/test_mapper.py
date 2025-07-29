import unittest
import pandas as pd
from icdmap import ICDConverter

class TestICDConverter(unittest.TestCase):
    def setUp(self):
        self.converter = ICDConverter()

    def test_single_icd9_code(self):
        result = self.converter.convert("250.00")
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        self.assertIn("ICD-10", result[0])

    def test_single_icd10_code(self):
        converter = ICDConverter(source="icd10")
        result = converter.convert("E11.9")
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        self.assertIn("ICD-9", result[0])

    def test_invalid_source_raises(self):
        converter = ICDConverter(source="invalid")
        with self.assertRaises(ValueError):
            converter.convert("250.00")

    def test_code_normalization(self):
        normalized = self.converter._normalize_code("25000")
        self.assertEqual(normalized, "250.00")

    def test_batch_input(self):
        result = self.converter.convert(["250.00", "401.9"])
        self.assertIsInstance(result, dict)
        self.assertIn("250.00", result)
        self.assertIsInstance(result["250.00"], list)

if __name__ == '__main__':
    unittest.main()