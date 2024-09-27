from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from datetime import timedelta
from pymongo import MongoClient
import sys
import os

sys.path.insert(0, 'scraper/src/main.py')  
from ...scraper.src.main import main  

default_args = {
    'owner': 'nathaniel',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG
dag = DAG(
    'web_scraping_with_mongo_comparison',
    default_args=default_args,
    description='A DAG to scrape website weekly and compare with MongoDB content',
    schedule_interval=timedelta(weeks=1),  # Schedule weekly
    start_date=days_ago(1),
    catchup=False,
)

# Task 1: Scrape the website
def run_scraper(**context):
    # Call the existing scrape_data function from src/main.py
    scraped_data = main()
    
    # Push scraped data to XCom (for passing between tasks)
    context['task_instance'].xcom_push(key='scraped_data', value=scraped_data)

# Task 2: Compare with MongoDB
def compare_with_mongo(**context):
    # Retrieve MongoDB credentials from Airflow Connections
    mongo_conn_id = 'mongo_default'  # Replace with the ID you set in Airflow UI
    mongo_conn = context['ti'].xcom_pull(task_ids='get_mongo_connection')

    client = MongoClient(mongo_conn['host'], mongo_conn['port'])
    db = client[mongo_conn['database']]
    collection = db[mongo_conn['collection']]
    
    # Fetch base content from MongoDB
    base_content = collection.find_one({'_id': 'your_document_id'})  # Customize this query

    # Get the newly scraped content from XCom
    new_content = context['task_instance'].xcom_pull(task_ids='run_scraper', key='scraped_data')

    # Compare the content
    if base_content != new_content:
        print("Content has changed! Updating MongoDB.")
        collection.update_one({'_id': 'your_document_id'}, {'$set': new_content})
    else:
        print("No changes detected.")

# Task to get MongoDB connection (Best Practice)
def get_mongo_connection(**kwargs):
    from airflow.models import Connection
    mongo_conn = Connection.get_connection_from_secrets('mongo_default')
    return {
        'host': mongo_conn.host,
        'port': mongo_conn.port,
        'database': mongo_conn.schema,
        'collection': 'your_collection_name'  # Replace with actual collection name
    }

# Define tasks
get_mongo_conn_task = PythonOperator(
    task_id='get_mongo_connection',
    python_callable=get_mongo_connection,
    provide_context=True,
    dag=dag,
)

scrape_task = PythonOperator(
    task_id='run_scraper',
    python_callable=run_scraper,
    provide_context=True,
    dag=dag,
)

compare_task = PythonOperator(
    task_id='compare_with_mongo',
    python_callable=compare_with_mongo,
    provide_context=True,
    dag=dag,
)

# Define task dependencies
get_mongo_conn_task >> scrape_task >> compare_task
