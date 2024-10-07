"""
Pipieline runs every week, checking for changes in the webpage
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

from scraper.main import main  # Ensure this imports correctly

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 9, 27),  # Update as needed
}

dag = DAG(
    'webscraper_dag',
    default_args=default_args,
    description='A DAG to run web scraping periodically',
    schedule_interval=None,  # Manual trigger
    catchup=False
    )

def wrapper_main():
    try:
        logger.info("Calling main function...")
        main()
    except Exception as e:
        logger.error(f"Error while running the main function: {e}")
        raise

run_scraper = PythonOperator(
    task_id='run_scraper_task',
    python_callable=wrapper_main,  # Use a wrapper to handle logging and errors
    dag=dag,
)

run_scraper
