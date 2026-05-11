import pandas as pd
import logging
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def load_to_csv(df: pd.DataFrame, filepath: str = "products.csv") -> str:
    """Save DataFrame to a CSV file."""
    try:
        if df is None or df.empty:
            raise ValueError("DataFrame is empty or None. Nothing to save.")
        df.to_csv(filepath, index=False)
        logger.info(f"Data saved to CSV: {filepath} ({len(df)} rows)")
        return filepath
    except PermissionError as e:
        logger.error(f"Permission denied writing to {filepath}: {e}")
        raise
    except OSError as e:
        logger.error(f"OS error writing to {filepath}: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error saving CSV: {e}")
        raise


def load_to_google_sheets(df: pd.DataFrame, spreadsheet_id: str, credentials_path: str = "google-sheets-api.json") -> str:
    """Save DataFrame to a Google Sheets spreadsheet."""
    try:
        import gspread
        from google.oauth2.service_account import Credentials

        if df is None or df.empty:
            raise ValueError("DataFrame is empty or None. Nothing to save.")

        if not os.path.exists(credentials_path):
            raise FileNotFoundError(f"Google Sheets credentials not found: {credentials_path}")

        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        creds = Credentials.from_service_account_file(credentials_path, scopes=scopes)
        client = gspread.authorize(creds)

        spreadsheet = client.open_by_key(spreadsheet_id)
        worksheet = spreadsheet.sheet1

        # Clear and update
        worksheet.clear()
        data = [df.columns.tolist()] + df.values.tolist()
        worksheet.update(data)

        logger.info(f"Data saved to Google Sheets (ID: {spreadsheet_id}) — {len(df)} rows")
        return spreadsheet_id
    except FileNotFoundError as e:
        logger.error(f"Credentials file not found: {e}")
        raise
    except ImportError as e:
        logger.error(f"Missing library for Google Sheets: {e}")
        raise
    except Exception as e:
        logger.error(f"Error saving to Google Sheets: {e}")
        raise


def load_to_postgresql(df: pd.DataFrame, connection_string: str, table_name: str = "products") -> str:
    """Save DataFrame to a PostgreSQL database."""
    try:
        from sqlalchemy import create_engine

        if df is None or df.empty:
            raise ValueError("DataFrame is empty or None. Nothing to save.")

        if not connection_string:
            raise ValueError("Connection string cannot be empty.")

        engine = create_engine(connection_string)
        df.to_sql(table_name, engine, if_exists="replace", index=False)
        logger.info(f"Data saved to PostgreSQL table '{table_name}' — {len(df)} rows")
        return table_name
    except ImportError as e:
        logger.error(f"Missing library for PostgreSQL: {e}")
        raise
    except Exception as e:
        logger.error(f"Error saving to PostgreSQL: {e}")
        raise
