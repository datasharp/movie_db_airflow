from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.decorators import task, dag
from datetime import datetime
from airflow.utils.dates import days_ago
from airflow.providers.microsoft.mssql.operators.mssql import MsSqlOperator
from groups.group_mapping_layer import mapping_tasks
from groups.group_staging_layer import staging_tasks
from groups.group_dimension_layer import dimension_tasks


with DAG('group_dag', start_date=datetime(2023, 1, 1), 
        schedule_interval='@daily', catchup=False) as dag:
    
    args = {'start_date':dag.start_date,'schedule_interval':dag.schedule_interval,'catchup':dag.catchup}

    mapping_layer = mapping_tasks()

    staging_layer = staging_tasks()

    dimension_layer = dimension_tasks()

    mapping_layer >> staging_layer >> dimension_layer