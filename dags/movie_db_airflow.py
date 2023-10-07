from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.decorators import task, dag
from datetime import datetime
#from airflow.providers.sql.operators.sql import SqlSensor, SqlOperatorfrom airflow.providers.sql.operators.sql import SqlSensor, SqlOperator
from airflow.utils.dates import days_ago
from airflow.providers.microsoft.mssql.operators.mssql import MsSqlOperator


with DAG('movie_db_etl', start_date=datetime(2023, 1, 1), 
        schedule_interval='@daily', catchup=False) as dag:
    
    insert_into_map_film = MsSqlOperator(
    task_id='insert_into_map_film',
    mssql_conn_id='sqlserver',
    sql="""
        INSERT INTO map_film (title, director, film_year)
        SELECT Title, Director, Year
        FROM [IMDB-Movie-Data_no_double_quotes] l
        WHERE NOT EXISTS (SELECT 1 FROM map_film m WHERE m.title = l.Title and m.director = l.Director and m.film_year = l.Year)
        """,
    autocommit=True
    #dag=dag,
)