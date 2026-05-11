import pytest
import pandas as pd
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.transform import (
    to_dataframe, clean_price, clean_rating, clean_colors,
    clean_size, clean_gender, transform, EXCHANGE_RATE
)

SAMPLE_PRODUCTS = [
    {
        "Title": "Cool T-Shirt",
        "Price": "$29.99",
        "Rating": "Rating: 4.5 / 5",
        "Colors": "3 Colors",
        "Size": "Size: M",
        "Gender": "Gender: Men",
        "timestamp": "2024-01-01T00:00:00",
    },
    {
        "Title": "Summer Pants",
        "Price": "$49.99",
        "Rating": "Rating: 4.0 / 5",
        "Colors": "2 Colors",
        "Size": "Size: L",
        "Gender": "Gender: Women",
        "timestamp": "2024-01-01T00:00:00",
    },
]


class TestToDataframe:
    def test_returns_dataframe(self):
        df = to_dataframe(SAMPLE_PRODUCTS)
        assert isinstance(df, pd.DataFrame)

    def test_correct_row_count(self):
        df = to_dataframe(SAMPLE_PRODUCTS)
        assert len(df) == 2

    def test_columns_present(self):
        df = to_dataframe(SAMPLE_PRODUCTS)
        for col in ["Title", "Price", "Rating", "Colors", "Size", "Gender", "timestamp"]:
            assert col in df.columns

    def test_empty_list_raises(self):
        with pytest.raises(Exception):
            to_dataframe([])


class TestCleanPrice:
    def test_usd_to_idr(self):
        result = clean_price("$29.99")
        assert result == pytest.approx(29.99 * EXCHANGE_RATE, rel=1e-2)

    def test_none_input(self):
        assert clean_price(None) is None

    def test_nan_input(self):
        assert clean_price(float("nan")) is None

    def test_non_string(self):
        assert clean_price(123) is None

    def test_zero_price(self):
        result = clean_price("$0.00")
        assert result == 0.0

    def test_large_price(self):
        result = clean_price("$100.00")
        assert result == pytest.approx(100.0 * EXCHANGE_RATE, rel=1e-2)


class TestCleanRating:
    def test_valid_rating(self):
        assert clean_rating("Rating: 4.5 / 5") == 4.5

    def test_none_input(self):
        assert clean_rating(None) is None

    def test_nan_input(self):
        assert clean_rating(float("nan")) is None

    def test_invalid_string(self):
        assert clean_rating("Invalid Rating") is None

    def test_integer_rating(self):
        assert clean_rating("Rating: 4 / 5") == 4.0

    def test_non_string(self):
        assert clean_rating(4.5) is None


class TestCleanColors:
    def test_valid_colors(self):
        assert clean_colors("3 Colors") == 3

    def test_single_color(self):
        assert clean_colors("1 Colors") == 1

    def test_none_input(self):
        assert clean_colors(None) is None

    def test_nan_input(self):
        assert clean_colors(float("nan")) is None

    def test_non_string(self):
        assert clean_colors(3) is None

    def test_no_number(self):
        assert clean_colors("No number here") is None


class TestCleanSize:
    def test_valid_size(self):
        assert clean_size("Size: M") == "M"

    def test_size_xl(self):
        assert clean_size("Size: XL") == "XL"

    def test_none_input(self):
        assert clean_size(None) is None

    def test_nan_input(self):
        assert clean_size(float("nan")) is None

    def test_empty_after_strip(self):
        assert clean_size("Size:") is None


class TestCleanGender:
    def test_valid_gender(self):
        assert clean_gender("Gender: Men") == "Men"

    def test_gender_women(self):
        assert clean_gender("Gender: Women") == "Women"

    def test_none_input(self):
        assert clean_gender(None) is None

    def test_nan_input(self):
        assert clean_gender(float("nan")) is None

    def test_empty_after_strip(self):
        assert clean_gender("Gender:") is None


class TestTransform:
    def test_returns_dataframe(self):
        df = to_dataframe(SAMPLE_PRODUCTS)
        result = transform(df)
        assert isinstance(result, pd.DataFrame)

    def test_price_in_idr(self):
        df = to_dataframe(SAMPLE_PRODUCTS)
        result = transform(df)
        expected = round(29.99 * EXCHANGE_RATE, 2)
        assert result["Price"].iloc[0] == pytest.approx(expected, rel=1e-2)

    def test_no_null_values(self):
        df = to_dataframe(SAMPLE_PRODUCTS)
        result = transform(df)
        assert result.isnull().sum().sum() == 0

    def test_no_duplicates(self):
        doubled = SAMPLE_PRODUCTS + SAMPLE_PRODUCTS
        df = to_dataframe(doubled)
        result = transform(df)
        assert len(result) == len(result.drop_duplicates())

    def test_removes_unknown_product(self):
        data = SAMPLE_PRODUCTS + [
            {
                "Title": "Unknown Product",
                "Price": "$10.00",
                "Rating": "Rating: 3.0 / 5",
                "Colors": "1 Colors",
                "Size": "Size: S",
                "Gender": "Gender: Men",
                "timestamp": "2024-01-01T00:00:00",
            }
        ]
        df = to_dataframe(data)
        result = transform(df)
        assert "Unknown Product" not in result["Title"].values

    def test_rating_is_float(self):
        df = to_dataframe(SAMPLE_PRODUCTS)
        result = transform(df)
        assert result["Rating"].dtype == float

    def test_colors_is_int(self):
        df = to_dataframe(SAMPLE_PRODUCTS)
        result = transform(df)
        assert result["Colors"].dtype == int

    def test_size_no_prefix(self):
        df = to_dataframe(SAMPLE_PRODUCTS)
        result = transform(df)
        for size in result["Size"]:
            assert "Size:" not in size

    def test_gender_no_prefix(self):
        df = to_dataframe(SAMPLE_PRODUCTS)
        result = transform(df)
        for gender in result["Gender"]:
            assert "Gender:" not in gender

    def test_empty_dataframe_raises(self):
        df = pd.DataFrame()
        with pytest.raises(Exception):
            transform(df)
