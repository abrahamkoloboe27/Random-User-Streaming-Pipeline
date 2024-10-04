import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator
from src.functions import *

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime.datetime(2024, 10, 4 ),
}

with DAG('user_automation',
         default_args=default_args,
         schedule_interval='*/5 * * * *',
         catchup=False
)as dag:
    
    start_task = EmptyOperator(
        task_id='start'
    )
    streaming_task = PythonOperator(
        task_id='stream_data_from_api',
        python_callable=stream_data
    )
    connect_to_postgres_task = PythonOperator(
        task_id='connect_to_postgres',
        python_callable=connect_to_postgres
    )
    put_data_in_postgres_database_task = PythonOperator(
        task_id='put_data_in_postgres_database',
        python_callable=put_data_in_postgres_database
    )
    end_task = EmptyOperator(
        task_id='end'
    )
    
    start_task >> streaming_task >> connect_to_postgres_task >> put_data_in_postgres_database_task >> end_task