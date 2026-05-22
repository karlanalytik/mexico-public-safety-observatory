"""
Data access module for the Streamlit application.
"""

import logging

import awswrangler as wr
import pandas as pd


logger = logging.getLogger(__name__)

LOCATION = "mexico-public-safety-observatory/outputs"


def load_app_data(bucket: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Load datasets required by the application.

    Args:
        bucket: Source S3 bucket name.

    Returns:
        Tuple containing:
        - yearly violence scores
        - latest violence scores
    """
    logger.info("Loading application datasets from S3")

    yearly_path = (
        f"s3://{bucket}/{LOCATION}/violence_scores_yearly.csv"
    )
    latest_path = (
        f"s3://{bucket}/{LOCATION}/violence_scores.csv"
    )

    try:
        year_scores = wr.s3.read_csv(yearly_path)
        violence_scores = wr.s3.read_csv(latest_path)

        # year_scores["anio"] = year_scores["anio"].astype(int)
        # year_scores["violence_score"] = (
        #     year_scores["violence_score"].astype(float)
        # )

        # violence_scores["violence_score"] = (
        #     violence_scores["violence_score"].astype(float)
        # )
        # violence_scores["cluster"] = (
        #     violence_scores["cluster"].astype(int)
        # )

        logger.info("Datasets loaded successfully")

        return year_scores, violence_scores

    except Exception:
        logger.exception("Failed loading datasets from S3")
        raise