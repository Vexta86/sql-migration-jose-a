import mysql.connector

from databaseCleaning import update_intensidad, insert_intensidad_from_calificaciones, insert_indice_calificaciones
from dataframe_processing import post_to_db, process_folder_1_11

import os

from preescolar.preescolar_migration import process_folder_0
from tecnica.tecnicas_migration import post_to_db_tecnica

# Access environment variables
db_host = os.getenv("DB_HOST")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_name = os.getenv("DB_NAME")

# Connect to MySQL
db_connection = mysql.connector.connect(
    host=db_host,
    user=db_user,
    password=db_password,
    database=db_name
)

YEAR = 2008


# path = "D:\\Projects\\Akros\\joseacevedogomez\\tecnicas\\2024_11_A.xlsx"
path = "D:\\Projects\\Akros\\joseacevedogomez\\preescolar"

# process_folder_1_11(f"D:\\Projects\\Akros\\joseacevedogomez\\Notas {YEAR}", YEAR, db_connection)

# post_to_db_tecnica(db_connection, path)

process_folder_0(path, db_connection)
