# movie_db_airflow
This repository contains Python code using Airflow to orchestrate an ETL process in Azure SQL. This code uses DAGs to orchestrate different tasks, which contain SQL code that does the transformations. 

## Table of Contents

- [Introduction](#introduction)
- [Data Model](#data-model)
- [SQL Files](#sql-files)

## Introduction 
This code uses the Apache-Airflow tool called TaskGroups to organize and group the code by layer: mapping, staging, and dimension. Airflow is being run inside a Docker container by using a docker-compose.yaml file. 

Dockerfile has been used to establish a connection to SQL Server. This was necessary because the base Airflow setup did not include the specific configurations and dependencies required for this project's needs.

## Data Model 

![Screenshot](Star_Schema_Movie_Data_Set.png)

- **Landing Table:**
  - `land_movies`: Landing table containing raw movie data.
 
- **Staging Tables:**
  - `stg_actor`
  - `stg_genre`
  - `stg_film`
  - `stg_actor_film_assoc`
  - `stg_genre_film_assoc`
 
- **Mapping Tables:**
  - `map_actor`
  - `map_director`
  - `map_genre`
  - `map_film`
  - `map_year`
 
- **Dimension Tables:**
  - `dim_actor`
  - `dim_director`
  - `dim_genre`
  - `dim_movie`
  - `dim_year`:
 
- **Fact Table:** `fact_film`
  - Contains movie-related metrics and measures such as runtime, rating, revenue, votes, metascore, etc.
  - Foreign keys to connect with dimension tables.
