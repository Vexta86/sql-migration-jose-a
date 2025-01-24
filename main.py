import os

import mysql.connector

from dataframe_processing import post_to_db

import os

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


def process_folder(folder_path):
    """
    Process all SQL files in a folder and save their processed data as JSON.
    """

    if not os.path.exists(folder_path):
        print(f"Folder does not exist: {folder_path}")
        return

    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)

        if os.path.isfile(file_path) and file_name.lower().endswith('.xlsx'):
            print(f"\nProcessing file: {file_path}")

            post_to_db(db_connection, file_path)


process_folder("D:\\Projects\\Akros\\joseacevedogomez\\Notas 2024")
