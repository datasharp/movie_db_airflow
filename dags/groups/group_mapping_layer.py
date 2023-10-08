from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.decorators import task, dag
from datetime import datetime
#from airflow.providers.sql.operators.sql import SqlSensor, SqlOperatorfrom airflow.providers.sql.operators.sql import SqlSensor, SqlOperator
from airflow.utils.dates import days_ago
from airflow.providers.microsoft.mssql.operators.mssql import MsSqlOperator
from airflow.utils.task_group import TaskGroup

def mapping_tasks():
    with TaskGroup("mapping_layer", tooltip='Mapping layer tasks') as group:
        insert_into_map_film = MsSqlOperator(
        task_id='insert_into_map_film',
        mssql_conn_id='sqlserver',
        sql="""
            INSERT INTO map_film (title, director, film_year)
            SELECT Title, Director, Year
            FROM land_movies l
            WHERE NOT EXISTS (SELECT 1 FROM map_film m WHERE m.title = l.Title and m.director = l.Director and m.film_year = l.Year)
            """,
        autocommit=True
        )

        insert_into_map_actor = MsSqlOperator(
        task_id='insert_into_map_actor',
        mssql_conn_id='sqlserver',
        sql="""
            INSERT INTO map_actor
            SELECT DISTINCT Actor
            FROM (SELECT trim(value)as Actor, Title, Year, Director
                FROM (
                    SELECT Actors, Title, Year, Director FROM land_movies 
                        ) AS sub_query
                CROSS APPLY string_split(sub_query.Actors,',') as actors_split) as v
            WHERE NOT EXISTS (SELECT 1 FROM map_actor m WHERE m.actor = v.Actor)
            """,
        autocommit=True
        )

        insert_into_map_genre = MsSqlOperator(
        task_id='insert_into_map_genre',
        mssql_conn_id='sqlserver',
        sql="""
            INSERT INTO map_genre (genre)
            SELECT DISTINCT Genre as genre FROM
            (
            SELECT trim(value)as Genre, Title, Year, Director
            FROM (SELECT Genre, Title, Year, Director FROM land_movies) AS sub_query
            CROSS APPLY string_split(sub_query.Genre,',') 
            ) s
            WHERE NOT EXISTS (SELECT 1 FROM map_genre mg WHERE mg.genre = s.Genre)
            """,
        autocommit=True
        )

        insert_into_map_year = MsSqlOperator(
        task_id='insert_into_map_year',
        mssql_conn_id='sqlserver',
        sql="""
            INSERT INTO map_year (year)
            SELECT DISTINCT l.Year 
            FROM land_movies l
            WHERE NOT EXISTS (SELECT 1 FROM map_year my WHERE my.year = l.Year)
            """,
        autocommit=True
        )

        insert_into_map_director = MsSqlOperator(
        task_id='insert_into_map_director',
        mssql_conn_id='sqlserver',
        sql="""
            INSERT INTO map_director (director)
            SELECT DISTINCT l.director 
            FROM land_movies l
            WHERE NOT EXISTS (SELECT 1 FROM map_director md WHERE md.director = l.director)
            """,
        autocommit=True
        )

        return group

        #all these tasks go before the staging layer
        

  



    