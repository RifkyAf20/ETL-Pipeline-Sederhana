import pandas as pd
import logging
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

EXCHANGE_RATE = 16000


def to_dataframe(products: list[dict]) -> pd.DataFrame:
    """Convert list of product dicts to a DataFrame."""
    try:
        if not products:
            raise ValueError("Product list is empty.")
        df = pd.DataFrame(products)
        logger.info(f"Created DataFrame with {len(df)} rows and columns: {list(df.columns)}")
        return df
    except Exception as e:
        logger.error(f"Error converting products to DataFrame: {e}")
        raise


def clean_price(price_str) -> float | None:
    """Convert price string '$XX.XX' to float in IDR."""
    try:
        if pd.isna(price_str) or not isinstance(price_str, str):
            return None
        match = re.search(r"[\d,]+\.?\d*", price_str.replace(",", ""))
        if match:
            usd = float(match.group())
            return round(usd * EXCHANGE_RATE, 2)
        return None
    except Exception as e:
        logger.warning(f"Error cleaning price '{price_str}': {e}")
        return None


def clean_rating(rating_str) -> float | None:
    """Extract float rating from string like 'Rating: 4.8 / 5'."""
    try:
        if pd.isna(rating_str) or not isinstance(rating_str, str):
            return None
        match = re.search(r"(\d+\.?\d*)\s*/\s*5", rating_str)
        if match:
            return float(match.group(1))
        return None
    except Exception as e:
        logger.warning(f"Error cleaning rating '{rating_str}': {e}")
        return None


def clean_colors(colors_str) -> int | None:
    """Extract integer number from string like '3 Colors'."""
    try:
        if pd.isna(colors_str) or not isinstance(colors_str, str):
            return None
        match = re.search(r"(\d+)", colors_str)
        if match:
            return int(match.group(1))
        return None
    except Exception as e:
        logger.warning(f"Error cleaning colors '{colors_str}': {e}")
        return None


def clean_size(text):
    if not isinstance(text, str):
        return None

    if "Size:" not in text:
        return None

    size = text.replace("Size:", "").strip()

    return size if size else None


def clean_gender(text):
    if not isinstance(text, str):
        return None

    if "Gender:" not in text:
        return None

    gender = text.replace("Gender:", "").strip()

    return gender if gender else None


def transform(df: pd.DataFrame) -> pd.DataFrame:
    """Apply all transformations to the raw DataFrame."""
    try:
        logger.info(f"Starting transformation on {len(df)} rows.")

        invalid_titles = ["Unknown Product", ""]
        df = df[~df["Title"].isin(invalid_titles)]
        df = df[df["Title"].notna()]

        df["Price"] = df["Price"].apply(clean_price)
        df["Rating"] = df["Rating"].apply(clean_rating)
        df["Colors"] = df["Colors"].apply(clean_colors)
        df["Size"] = df["Size"].apply(clean_size)
        df["Gender"] = df["Gender"].apply(clean_gender)

        before = len(df)
        df = df.dropna()
        logger.info(f"Dropped {before - len(df)} rows with null values.")

        before = len(df)
        df = df.drop_duplicates()
        logger.info(f"Dropped {before - len(df)} duplicate rows.")

        df["Price"] = df["Price"].astype(float)
        df["Rating"] = df["Rating"].astype(float)
        df["Colors"] = df["Colors"].astype(int)
        df["Size"] = df["Size"].astype(str)
        df["Gender"] = df["Gender"].astype(str)
        df["Title"] = df["Title"].astype(str)
        df["timestamp"] = df["timestamp"].astype(str)

        df = df.reset_index(drop=True)

        logger.info(f"Transformation complete. {len(df)} clean rows remaining.")
        return df
    except Exception as e:
        logger.error(f"Error during transformation: {e}")
        raise
