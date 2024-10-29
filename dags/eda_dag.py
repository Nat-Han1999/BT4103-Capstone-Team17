from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from datetime import datetime
from weasyprint import HTML

def convert_html_to_pdf(input, output):
    HTML(input).write_pdf(output)

input = "../eda/pyspark_eda.html"
output = "../eda/pyspark_eda.pdf"
# Define default arguments
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 10, 29),
}

with DAG(
    'pyspark_eda_dag',
    default_args=default_args,
    description='Run PySpark EDA with Airflow',
    schedule_interval='@daily',  # Update to your preference
    catchup=False,
) as dag:

    run_pyspark_eda = BashOperator(
        task_id='run_pyspark_eda',
        bash_command='spark-submit ../eda/pyspark_eda.py',
    )

    # Convert the EDA output to PDF
    save_eda_as_pdf = PythonOperator(
        task_id='convert_eda_to_pdf',
        python_callable=convert_html_to_pdf,
        op_kwargs={'input_path': input, 'output_path': output}
    )

run_pyspark_eda >> save_eda_as_pdf
