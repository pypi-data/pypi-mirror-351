import subprocess
import json
import os
import unittest
import tempfile
import pandas as pd
from shutil import which

class TestCLI(unittest.TestCase):
    def setUp(self):
        self.cli_path = which("icdmap")
        self.assertIsNotNone(self.cli_path, "❌ 'icdmap' CLI not found in PATH")

    def test_cli_single(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "out.json")
            result = subprocess.run(
                [self.cli_path, "250.00", "-o", output_path],
                capture_output=True, text=True
            )

            print("STDOUT:", result.stdout.strip())
            print("STDERR:", result.stderr.strip())

            self.assertEqual(result.returncode, 0)
            self.assertTrue(os.path.exists(output_path))

            with open(output_path, encoding="utf-8") as f:
                data = json.load(f)
                self.assertIn("250.00", data)

    def test_cli_csv(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = os.path.join(tmpdir, "input.csv")
            output_path = os.path.join(tmpdir, "out.json")

            df = pd.DataFrame({"ICD9_CODE": ["250.00"]})
            df.to_csv(csv_path, index=False)

            result = subprocess.run(
                [self.cli_path, "--csv", csv_path, "-o", output_path],
                capture_output=True, text=True
            )

            print("STDOUT:", result.stdout.strip())
            print("STDERR:", result.stderr.strip())

            self.assertEqual(result.returncode, 0)
            self.assertTrue(os.path.exists(output_path))

            with open(output_path, encoding="utf-8") as f:
                data = json.load(f)
                self.assertIn("250.00", data)

    def test_cli_csv_missing_column(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            bad_csv = os.path.join(tmpdir, "bad.csv")
            output = os.path.join(tmpdir, "bad_out.json")

            pd.DataFrame({"wrong_col": ["12345"]}).to_csv(bad_csv, index=False)

            result = subprocess.run(
                [self.cli_path, "--csv", bad_csv, "-o", output],
                capture_output=True, text=True
            )

            print("STDOUT:", result.stdout.strip())
            print("STDERR:", result.stderr.strip())

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("ICD9_CODE", result.stderr)

    def test_cli_no_input(self):
        result = subprocess.run(
            [self.cli_path],
            capture_output=True, text=True
        )

        print("STDOUT:", result.stdout.strip())
        print("STDERR:", result.stderr.strip())

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("usage", (result.stderr + result.stdout).lower())

if __name__ == '__main__':
    unittest.main()