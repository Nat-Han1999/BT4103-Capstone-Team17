"""
Pipeline runs every week, checking for new links in domain
"""
import sys
import os
import logging
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

os.environ['NO_PROXY'] = '*'

# Add logging to ensure we capture any issues
logger = logging.getLogger("airflow.task")
logger.setLevel(logging.INFO)

# Ensure the correct path is added
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from scraper.src.scraper_action import get_all_links  # Ensure this imports correctly
from scraper.src.utils.scraper_utils import load_json_file

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 9, 27),  # Update as needed
}

dag = DAG(
    'webcrawler_dag',
    default_args=default_args,
    description='A DAG to run web cawler periodically',
    schedule=None,  # Manual trigger
    catchup=False
    )

def wrapper_get_links_sync():
    try:
        config_file = 'scraper/config.json'
        config = load_json_file(config_file)
        base_url = "https://www.svf.gov.lk/index.php?lang=en"
        max_depth = 2

        logger.info("Calling crawler function...")
        # Run the synchronous function directly
        urls = get_all_links(base_url, config, max_depth, delay=2)
        logger.info("CRAWLED LINKS: %s", urls)
    except Exception as e:
        logger.error(f"Error while running the main function: {e}")
        raise

run_crawler = PythonOperator(
    task_id='run_crawler_task',
    python_callable=wrapper_get_links_sync,  # Use a wrapper to handle logging and errors
    dag=dag,
)

run_crawler
