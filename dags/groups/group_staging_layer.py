from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.decorators import task, dag
from datetime import datetime
#from airflow.providers.sql.operators.sql import SqlSensor, SqlOperatorfrom airflow.providers.sql.operators.sql import SqlSensor, SqlOperator
from airflow.utils.dates import days_ago
from airflow.providers.microsoft.mssql.operators.mssql import MsSqlOperator
from airflow.utils.task_group import TaskGroup

def staging_tasks():
    with TaskGroup("staging_layer", tooltip='Staging layer tasks') as group:
        insert_into_stg_film = MsSqlOperator(
        task_id='insert_into_stg_film',
        mssql_conn_id='sqlserver',
        sql="""
            INSERT INTO stg_film
            SELECT  
            m.film_id
            ,l.[Title]
            ,l.[Description]
            ,l.[Director]
            ,l.Year
            ,l.[Runtime_Minutes]
            ,l.[Rating]
            ,l.[Votes]
            ,l.[Revenue_Millions]
            ,l.[Metascore]
            FROM [land_movies] AS l
            INNER JOIN map_film AS m ON m.title = l.Title 
            and m.director = l.Director 
            and m.film_year = l.Year
            WHERE NOT EXISTS (SELECT 1 FROM stg_film AS s WHERE s.film_id = m.film_id)
            """,
        autocommit=True
        )

        insert_into_stg_actor_film_assoc = MsSqlOperator(
        task_id='insert_into_stg_actor_film_assoc',
        mssql_conn_id='sqlserver',
        sql="""
            INSERT INTO stg_actor_film_assoc (actor_id, film_id)
            SELECT DISTINCT ma.actor_id, mf.film_id 
            FROM ( 
                SELECT trim(value)as Actor, Title, Year, Director
                FROM (
                    SELECT Actors, Title, Year, Director FROM land_movies 
                        ) AS sub_query
                CROSS APPLY string_split(sub_query.Actors,',') as actors_split) as t
            INNER JOIN map_actor as ma on ma.actor = t.Actor
            INNER JOIN map_film as mf on mf.Title  =  t.Title
                AND mf.film_year = t.Year
                AND mf.director = t.Director
            WHERE NOT EXISTS (SELECT 1 FROM stg_actor_film_assoc as a WHERE ma.actor_id = a.actor_id AND mf.film_id = a.film_id)
            """,
        autocommit=True
        )

        insert_into_stg_actor = MsSqlOperator(
        task_id='insert_into_stg_actor',
        mssql_conn_id='sqlserver',
        sql="""
            INSERT INTO stg_actor
            SELECT DISTINCT
            m.actor_id
            ,v.Actor
            FROM (SELECT trim(value)as Actor, Title, Year, Director
                FROM (
                    SELECT Actors, Title, Year, Director FROM land_movies 
                        ) AS sub_query
                CROSS APPLY string_split(sub_query.Actors,',') as actors_split) AS v
            INNER JOIN map_actor AS m ON m.actor = v.Actor
            WHERE NOT EXISTS (SELECT 1 FROM stg_actor AS s WHERE s.actor_id = m.actor_id);
            """,
        autocommit=True
        )

        insert_into_stg_genre = MsSqlOperator(
        task_id='insert_into_stg_genre',
        mssql_conn_id='sqlserver',
        sql="""
            INSERT INTO stg_genre (genre_id, genre)
            SELECT DISTINCT mg.genre_id, s.Genre as genre
            FROM
            (
            SELECT trim(value)as Genre, Title, Year, Director
            FROM (SELECT Genre, Title, Year, Director FROM land_movies) AS sub_query
            CROSS APPLY string_split(sub_query.Genre,',') 
            ) s
            INNER JOIN map_genre mg ON mg.genre = s.Genre
            WHERE NOT EXISTS (SELECT 1 FROM stg_genre sg WHERE sg.genre_id = mg.genre_id)
            """,
        autocommit=True
        )

        insert_into_stg_genre_film_assoc = MsSqlOperator(
        task_id='insert_into_stg_genre_film_assoc',
        mssql_conn_id='sqlserver',
        sql="""
            INSERT INTO stg_genre_film_assoc (film_id, genre_id)
            SELECT mf.film_id, mg.genre_id
            FROM
            (
            SELECT trim(value)as Genre, Title, Year, Director
            FROM (SELECT Genre, Title, Year, Director FROM land_movies) AS sub_query
            CROSS APPLY string_split(sub_query.Genre,',') 
            ) s
            INNER JOIN map_genre mg ON mg.genre = s.Genre
            INNER JOIN map_film mf ON mf.director = s.Director
                and mf.film_year = s.Year
                and mf.title = s.Title 
            WHERE NOT EXISTS (SELECT 1 FROM stg_genre_film_assoc sg WHERE sg.film_id = mf.film_id and sg.genre_id = mg.genre_id)
            """,
        autocommit=True
        )



        return group

