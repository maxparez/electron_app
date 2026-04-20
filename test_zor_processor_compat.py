import sys
import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT / "src" / "python"))

from tools.zor_spec_dat_processor import ZorSpecDatProcessor  # noqa: E402


class CompatDataFrame(pd.DataFrame):
    @property
    def _constructor(self):
        return CompatDataFrame

    def applymap(self, func):
        raise AttributeError("'DataFrame' object has no attribute 'applymap'")


class ZorProcessorCompatTests(unittest.TestCase):
    def test_calculate_subreport_handles_dataframes_without_applymap(self) -> None:
        processor = ZorSpecDatProcessor()

        source_df = CompatDataFrame(
            {
                "ca": [1],
                "jmena": [" Jana Novakova "],
                "datum": ["01.01.2025"],
                "pocet_hodin": [2],
                "forma": [" online "],
                "tema": [" formativní hodnocení "],
            }
        )

        with patch("tools.zor_spec_dat_processor.pd.read_excel", return_value=source_df), patch.object(
            processor, "_get_template_name", return_value="Test Template"
        ):
            normalized_df, subreport = processor._calculate_subreport("/tmp/test.xlsx")

        self.assertEqual("jana novakova", normalized_df.iloc[0]["jmena"])
        self.assertEqual("online", normalized_df.iloc[0]["forma"])
        self.assertEqual("formativní hodnocení", normalized_df.iloc[0]["tema"])
        self.assertEqual("Test Template", normalized_df.iloc[0]["sablona"])
        self.assertFalse(subreport.empty)


if __name__ == "__main__":
    unittest.main()
