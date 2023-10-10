from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.decorators import task, dag
from datetime import datetime
#from airflow.providers.sql.operators.sql import SqlSensor, SqlOperatorfrom airflow.providers.sql.operators.sql import SqlSensor, SqlOperator
from airflow.utils.dates import days_ago
from airflow.providers.microsoft.mssql.operators.mssql import MsSqlOperator
from airflow.utils.task_group import TaskGroup

def dimension_tasks():
    with TaskGroup("dimension_layer", tooltip='Dimension/Fact layer tasks') as group:
        insert_into_dim_movie = MsSqlOperator(
        task_id='insert_into_dim_movie',
        mssql_conn_id='sqlserver',
        sql="""
            INSERT INTO dim_actor_movie_assoc (dim_actor_movie_assoc_id ,actor_id, film_id)
            SELECT stg_actor_film_id, actor_id, film_id FROM stg_actor_film_assoc s
            WHERE NOT EXISTS (SELECT 1 FROM dim_actor_movie_assoc da WHERE da.actor_id = s.actor_id AND da.film_id = s.film_id)
            """,
        autocommit=True
        )

        insert_into_dim_actor_movie_assoc = MsSqlOperator(
        task_id='insert_into_dim_actor_movie_assoc',
        mssql_conn_id='sqlserver',
        sql="""     
            INSERT INTO dim_actor_movie_assoc (dim_actor_movie_assoc_id ,actor_id, film_id)
            SELECT stg_actor_film_id, actor_id, film_id FROM stg_actor_film_assoc s
            WHERE NOT EXISTS (SELECT 1 FROM dim_actor_movie_assoc da WHERE da.actor_id = s.actor_id AND da.film_id = s.film_id)
            """,
        autocommit=True
        )

        insert_into_dim_actor = MsSqlOperator(
        task_id='insert_into_dim_actor',
        mssql_conn_id='sqlserver',
        sql="""      
            INSERT INTO dim_actor (actor_id, actor)
            SELECT s.actor_id, s.actor FROM stg_actor s
            WHERE NOT EXISTS (SELECT 1 FROM dim_actor d WHERE d.actor_id = s.actor_id)
            """,
        autocommit=True
        )

        insert_into_dim_genre_movie_assoc = MsSqlOperator(
        task_id='insert_into_dim_genre_movie_assoc',
        mssql_conn_id='sqlserver',
        sql="""      
            INSERT INTO dim_genre_movie_assoc (film_id, genre_id, dim_genre_movie_assoc_id)
            SELECT s.film_id, s.genre_id, s.stg_genre_film_id
            FROM stg_genre_film_assoc s
            WHERE NOT EXISTS (SELECT 1 FROM dim_genre_movie_assoc d WHERE d.genre_id = s.genre_id and d.film_id = s.film_id)
            """,
        autocommit=True
        )

        insert_into_dim_genre = MsSqlOperator(
        task_id='insert_into_dim_genre',
        mssql_conn_id='sqlserver',
        sql="""      
            INSERT INTO dim_genre (genre_id, genre)
            SELECT s.genre_id, s.genre FROM stg_genre s
            WHERE NOT EXISTS (SELECT 1 FROM dim_genre d WHERE d.genre_id = s.genre_id)
            """,
        autocommit=True
        )

        insert_into_dim_director = MsSqlOperator(
        task_id='insert_into_dim_director',
        mssql_conn_id='sqlserver',
        sql="""      
            INSERT INTO dim_director
            SELECT DISTINCT md.director_id, lm.director
            FROM land_movies lm
            INNER JOIN map_director md ON md.director = lm.director
            WHERE NOT EXISTS (SELECT 1 FROM dim_director dd WHERE md.director = lm.director)
            """,
        autocommit=True
        )

        insert_into_dim_year = MsSqlOperator(
        task_id='insert_into_dim_year',
        mssql_conn_id='sqlserver',
        sql="""      
            INSERT INTO dim_year
            SELECT DISTINCT md.year_id, l.Year
            FROM land_movies l
            INNER JOIN map_year md ON md.year = l.Year
            WHERE NOT EXISTS (SELECT 1 FROM dim_year dd WHERE dd.year = l.Year)
            """,
        autocommit=True
        )

        insert_into_fact_film = MsSqlOperator(
        task_id='insert_into_fact_film',
        mssql_conn_id='sqlserver',
        sql="""      
            INSERT INTO fact_film 
            SELECT s.runtime_minutes, s.rating, s.revenue_millions, s.votes, s.metascore,mf.film_id, md.director_id, my.year_id
            FROM stg_film as s
            INNER JOIN map_director md ON md.director = s.director
            INNER JOIN map_year my ON my.year = s.film_year
            INNER JOIN map_film mf ON mf.film_id = s.film_id
            WHERE NOT EXISTS (SELECT 1 FROM fact_film f WHERE f.film_id = mf.film_id and md.director_id = f.director_id and my.year_id = f.year_id)
            """,
        autocommit=True
        )

        return group