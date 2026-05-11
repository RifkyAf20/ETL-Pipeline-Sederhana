import logging
from utils.extract import scrape_main
from utils.transform import to_dataframe, transform
from utils.load import load_to_csv

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def run_pipeline(csv_output: str = "products.csv") -> None:
    """Run the full ETL pipeline."""
    try:
        # --- EXTRACT ---
        logger.info("=== EXTRACT ===")
        raw_data = scrape_main()
        logger.info(f"Extracted {len(raw_data)} raw records.")

        # --- TRANSFORM ---
        logger.info("=== TRANSFORM ===")
        df_raw = to_dataframe(raw_data)
        df_clean = transform(df_raw)
        logger.info(f"Transformed data: {len(df_clean)} clean records.")

        # --- LOAD ---
        logger.info("=== LOAD ===")
        load_to_csv(df_clean, csv_output)
        logger.info("Pipeline complete.")

    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        raise


if __name__ == "__main__":
    run_pipeline()
