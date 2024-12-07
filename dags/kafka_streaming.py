import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from src.functions import *

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime.datetime(2024, 10, 4),
}

with DAG('user_automation',
         default_args=default_args,
         schedule_interval="@hourly",
         catchup=False
) as dag:
    
    start_task = EmptyOperator(
        task_id='start'
    )
    
    # Tâche qui stream depuis l'API vers Redpanda
    streaming_task = PythonOperator(
        task_id='stream_data_from_api',
        python_callable=stream_data
    )

    # Tâche Spark qui va consommer depuis Redpanda et écrire dans Postgres
    # Assurez-vous que le chemin vers votre script spark_streaming.py soit correct
    # et accessible dans l'environnement où Spark s'exécute.
    spark_task = SparkSubmitOperator(
    task_id='spark_submit_task',
    application='/opt/airflow/dags/spark_streaming.py',
    conn_id='spark_default',  # Utilise la connexion Spark configurée dans Airflow
    packages='org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0',
    executor_cores=2,
    executor_memory='1g',
    driver_memory='1g',
    verbose=True,
    dag=dag
    )


    cleanup_task = PythonOperator(
        task_id='cleanup_files',
        python_callable=clean_up_files
    )
    
    end_task = EmptyOperator(
        task_id='end'
    )
    
    # L'ordre d'exécution : 
    # 1. On récupère les données et on les envoie vers Redpanda
    # 2. Ensuite on lance Spark pour consommer depuis Redpanda et écrire dans Postgres
    # 3. On nettoie les fichiers
    # 4. On termine
    start_task >> streaming_task >> spark_task >> cleanup_task >> end_task
