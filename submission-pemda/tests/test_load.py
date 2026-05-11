import pytest
import pandas as pd
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.load import load_to_csv, load_to_google_sheets, load_to_postgresql

SAMPLE_DF = pd.DataFrame({
    "Title": ["Cool T-Shirt", "Summer Pants"],
    "Price": [479840.0, 799840.0],
    "Rating": [4.5, 4.0],
    "Colors": [3, 2],
    "Size": ["M", "L"],
    "Gender": ["Men", "Women"],
    "timestamp": ["2024-01-01T00:00:00", "2024-01-01T00:00:00"],
})


class TestLoadToCsv:
    def test_creates_csv_file(self, tmp_path):
        output = str(tmp_path / "test_output.csv")
        load_to_csv(SAMPLE_DF, output)
        assert os.path.exists(output)

    def test_csv_has_correct_rows(self, tmp_path):
        output = str(tmp_path / "test_output.csv")
        load_to_csv(SAMPLE_DF, output)
        loaded = pd.read_csv(output)
        assert len(loaded) == len(SAMPLE_DF)

    def test_csv_has_correct_columns(self, tmp_path):
        output = str(tmp_path / "test_output.csv")
        load_to_csv(SAMPLE_DF, output)
        loaded = pd.read_csv(output)
        for col in SAMPLE_DF.columns:
            assert col in loaded.columns

    def test_returns_filepath(self, tmp_path):
        output = str(tmp_path / "test_output.csv")
        result = load_to_csv(SAMPLE_DF, output)
        assert result == output

    def test_empty_dataframe_raises(self, tmp_path):
        output = str(tmp_path / "empty.csv")
        with pytest.raises(Exception):
            load_to_csv(pd.DataFrame(), output)

    def test_none_dataframe_raises(self, tmp_path):
        output = str(tmp_path / "none.csv")
        with pytest.raises(Exception):
            load_to_csv(None, output)

    def test_invalid_directory_raises(self, tmp_path):
        output = str(tmp_path / "nonexistent_dir" / "output.csv")
        with pytest.raises(Exception):
            load_to_csv(SAMPLE_DF, output)


class TestLoadToGoogleSheets:
    def test_missing_credentials_file_raises(self):
        with pytest.raises(FileNotFoundError):
            load_to_google_sheets(SAMPLE_DF, "fake-id", credentials_path="nonexistent.json")

    def test_empty_dataframe_raises(self):
        with pytest.raises(ValueError):
            load_to_google_sheets(pd.DataFrame(), "fake-id", credentials_path="nonexistent.json")

    def test_none_dataframe_raises(self):
        with pytest.raises((ValueError, AttributeError)):
            load_to_google_sheets(None, "fake-id", credentials_path="nonexistent.json")


class TestLoadToPostgresql:
    def test_empty_connection_string_raises(self):
        with pytest.raises(ValueError):
            load_to_postgresql(SAMPLE_DF, connection_string="")

    def test_empty_dataframe_raises(self):
        with pytest.raises(ValueError):
            load_to_postgresql(pd.DataFrame(), connection_string="postgresql://user:pass@localhost/db")

    def test_none_dataframe_raises(self):
        with pytest.raises((ValueError, AttributeError)):
            load_to_postgresql(None, connection_string="postgresql://user:pass@localhost/db")

    def test_invalid_connection_string_raises(self):
        with pytest.raises(Exception):
            load_to_postgresql(SAMPLE_DF, connection_string="invalid-connection-string")
