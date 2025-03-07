from airflow import DAG

from airflow.utils.dates import days_ago

from airflow.operators.python import PythonOperator

from datetime import timedelta

from data_modules.data_load import create_table, insert_csv_data, create_index

defaultArguments = {
    "owner": "Artur Tiburski", 
    "start_date": days_ago(1), 
    "retries": 1,
    "retry_delay": timedelta(hours=1),
    "depends_on_past": True
}

dag = DAG(
    "Load_data_to_elastic_search_rag",
    default_args=defaultArguments, 
    schedule_interval="0 0 * * *",
    catchup=False,
    max_active_runs=1,
    description="Extracts and Loads data to RAG Elastic Search" 
)

create_table_postgres = PythonOperator(
    task_id="create_table_postgres",  
    python_callable=create_table, 
    dag=dag                         
)

loads_csv_data = PythonOperator(
    task_id="loads_csv_data", 
    python_callable=insert_csv_data, 
    dag=dag                               
)

creates_index = PythonOperator(
    task_id="creates_index",    
    python_callable=create_index,  
    dag=dag                          
)

create_table_postgres >> loads_csv_data >> creates_index
