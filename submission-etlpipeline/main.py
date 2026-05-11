import logging
from utils.extract import scrape_main
from utils.transform import to_dataframe, transform
from utils.load import load_to_csv
from utils.load import (
    load_to_csv,
    load_to_google_sheets
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SPREADSHEET_ID = "1r2NIRfH-Fk94ZNxbfVBqv6nnwrKR8hAbYZNxC_lDxaA"

def run_pipeline(csv_output: str = "products.csv") -> None:
    """Run the full ETL pipeline."""
    try:
        logger.info("=== EXTRACT ===")
        raw_data = scrape_main()
        logger.info(f"Extracted {len(raw_data)} raw records.")

        logger.info("=== TRANSFORM ===")
        df_raw = to_dataframe(raw_data)
        df_clean = transform(df_raw)
        logger.info(f"Transformed data: {len(df_clean)} clean records.")

        logger.info("=== LOAD ===")
        load_to_csv(df_clean, csv_output)
        logger.info("Pipeline complete.")

        logger.info("=== LOAD GOOGLE SHEETS ===")
        load_to_google_sheets(
            df_clean,
            spreadsheet_id=SPREADSHEET_ID,
            credentials_path="google-sheets-api.json"
        )

    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        raise


if __name__ == "__main__":
    run_pipeline()
