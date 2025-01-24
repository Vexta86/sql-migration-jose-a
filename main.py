import os

from dataframe_processing import process_df


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
            # El periodo 3 contiene las notas definitivas
            print(len(process_df(file_path)))


process_folder("D:\\Projects\\Akros\\joseacevedogomez\\Notas 2024")
