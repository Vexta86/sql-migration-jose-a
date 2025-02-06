import os

import pandas as pd

from utils import clean_name, clean_column_name, remove_tildes

DICT_2008_2009 = {
    'I': 'INSUFICIENTE',
    'D': 'DEFICIENTE',
    'A': 'ACEPTABLE',
    'S': 'SOBRESALIENTE',
    'E': 'EXCELENTE'
}

DICT_2010_2024 = {

    'DBAJO': 'BJ',
    'DBAJOO': 'BJ',
    'BAJO': 'BJ',
    'BJO': 'BJ',
    'BAJ': 'BJ',
    'DBJO': 'BJ',
    'DAJO': 'BJ',
    'DBJ': 'BJ',
    'DBAJ': 'BJ',
    'DBAJOX': 'BJ',

    'DB': 'B',
    'BD': 'B',
    'DBA': 'B',
    'DBCO': 'B',
    'DBC': 'B',
    'DBACO': 'B',
    'DBS': 'B',
    'BS': 'B',
    'DDBS': 'B',
    'DBO': 'B',
    'DBASICO': 'B',
    'BASICO': 'B',
    'DBAS': 'B',
    'DBSC': 'B',
    'DBSCO': 'B',
    'DBASCO': 'B',
    'DBASCIO': 'B',
    'DBASI': 'B',
    'BA': 'B',

    'DA': 'A',
    'DALTO': 'A',
    'ALTO': 'A',
    'DALT': 'A',
    'DALTOD': 'A',

    'DS': 'S',
    'DSUP': 'S',
    'DSUPERIOR': 'S',
    'SUPERIOR': 'S',
    'DSUPERIO': 'S',
    'DDS': 'S'
}


def convert_number_to_note(number):
    return float(number)


def replace_notes(df, replacement_dict):
    df = df.infer_objects()

    # Apply the trimming and uppercase to each cell before replacement
    df = df.map(
        lambda x: remove_tildes(x).strip().upper().replace('.', '').replace(',', '').replace(' ', '').replace('-',
                                                                                                              '') if isinstance(
            x, str) else x)

    df = df.map(lambda x: convert_number_to_note(x) if isinstance(x, float) or isinstance(x, int) else x)

    df.replace(replacement_dict, inplace=True, regex=False)

    # Replace all other values with None
    df = df.map(lambda x: None if x not in replacement_dict.values() else x)

    df.dropna(axis=1, how='all', inplace=True)
    df.dropna(axis=0, how='all', inplace=True)

    # Drop rows with more or equal than half of the column as NaN values
    # Calculate the threshold: total columns minus half of the columns minus one
    thresh_value = len(df.columns) - (len(df.columns) // 2 - 1)
    df.dropna(axis=0, thresh=thresh_value, inplace=True)

    return df


def process_workbook(route, quarter):
    df = pd.read_excel(route, sheet_name=quarter)

    # Find the index where 'apellidos_y_nombres' is located
    header_index = df[df.eq('APELLIDOS Y NOMBRES').any(axis=1)].index[0]

    # Set the column names using the found index
    df.columns = [clean_column_name(col) for col in df.iloc[header_index].tolist()]
    df = df.iloc[header_index:]

    # Set 'apellidos_y_nombres' as the index
    df = df.set_index('apellidos_y_nombres')

    try:
        df = df.loc[:, :'total_perdidas'].iloc[:, :-1]
    except KeyError:
        pass
    try:
        df = df.loc[:, :'tp'].iloc[:, :-1]
    except KeyError:
        pass
    try:
        df = df.loc[:, :'total_ganadas'].iloc[:, :-1]
    except KeyError:
        pass
    try:
        df = df.loc[:, :'tg'].iloc[:, :-1]
    except KeyError:
        pass

    df = replace_notes(df, DICT_2008_2009)
    return df


def is_digit_or_float(value):
    try:
        float(value)  # Attempt to convert to float
        return True
    except (ValueError, TypeError):
        return False


def get_grado_grupo(grado, grupo):
    possible_groups = ['A', 'B', 'C', 'D', 'E', 'F', 1, 2, 3, 4]
    numeric_grado = {
        'primero': 1,
        'segundo': 2,
        'tercero': 3,
        'cuarto': 4,
        'quinto': 5,
        'sexto': 6,
        'septimo': 7,
        'octavo': 8,
        'noveno': 9,
        'decimo': 10,
        'décimo': 10,
        'DÉCIMO': 10,
        'undecimo': 11,
        'once': 11,
        'procesos': 'PB'
    }

    special_grado = {
        'aceleracion': 'AC',
        'brujula': 'BJ',
        'clei': 'CLEI',
    }
    if grupo.upper() in possible_groups and str(grado).isdigit():
        return int(grado), grupo.upper()
    if grupo.upper() in possible_groups and grado in numeric_grado.keys():
        return numeric_grado[grado], grupo.upper()
    if grupo.upper() in possible_groups:
        return 0, grupo.upper()
    if grado in numeric_grado.keys():
        return numeric_grado[grado], ''
    if str(grado).isdigit():
        return int(grado), ''
    if grado in special_grado.keys() and is_digit_or_float(grupo):
        if float(grupo) > 10:
            return special_grado[grado], float(grupo) / 10
        else:
            return special_grado[grado], int(grupo)

    if grado in special_grado.keys():
        return special_grado[grado], ''
    return 0, ''


def extract_data(route, quarter):
    df = pd.read_excel(route, sheet_name=quarter)

    data = {
        'Grado': 0,
        'Grupo': ''
    }
    # Search for the cell containing the word "grupo" (case-insensitive)
    found_cells = df.map(
        lambda x: isinstance(x, str) and 'grado' in x.lower()
    )

    if not found_cells.any().any():
        found_cells = df.map(
            lambda x: isinstance(x, str) and 'grupo' in x.lower()
        )

    if found_cells.any().any():

        df = df[found_cells]
        df.dropna(axis=1, how='all', inplace=True)
        df.dropna(axis=0, how='all', inplace=True)
        cell = df.iloc[0, 0]
        cell = clean_column_name(cell)
        cell = cell.split('_')

        if len(cell) > 2:
            grado = clean_column_name(cell[1])

            data['Grado'], data['Grupo'] = get_grado_grupo(grado, cell[2])
        if len(cell) == 2:
            grado = cell[1][:-1]
            grupo = clean_column_name(cell[1][-1])
            data['Grado'], data['Grupo'] = get_grado_grupo(grado, grupo)

    if data['Grado'] == 0 and not data['Grupo']:
        last_str_in_route = (route.split('_')[-1].split('.')[0])
        data['Grado'], data['Grupo'] = get_grado_grupo(last_str_in_route[0], last_str_in_route[-1])

    if data['Grado'] == 0 and not data['Grupo']:
        last_str_in_route = (route.split()[-1].split('.')[0])
        data['Grado'], data['Grupo'] = get_grado_grupo(last_str_in_route[0], last_str_in_route[-1])

    return data


def post_to_db(db_connection, route, year):
    cursor = db_connection.cursor()

    # El periodo 3 contiene las notas definitivas
    df = process_workbook(route, -1)
    data = extract_data(route, 0)

    # Initialize counters
    successful_count = 0
    failed_count = 0

    # List to store all queries
    all_queries = []

    # Iterate over the DataFrame
    for index, row in df.iterrows():
        student_name = clean_name(index)
        grado = data['Grado']
        grupo = data['Grupo']

        print(f'\n\n{student_name} from {grado}-{grupo} {year}')

        # Collect queries for this student
        queries = []
        for column in df.columns:
            materia = column
            nota = row[column]

            if nota:
                queries.append((student_name, materia, nota, grado, grupo, year))
                print(materia, nota, end='\t')
            else:
                failed_count += 1
                print(materia, 'NULL', end='\t')

        # Add the queries for this student to the main list
        all_queries.extend(queries)
        successful_count += len(queries)

    # Execute all queries at once
    # if all_queries:
    #     query = """
    #         INSERT INTO Calificaciones1_11 (Nombre, Cod_asig, Nota, Grado, Grupo, Fecha)
    #         VALUES (%s, %s, %s, %s, %s, %s)
    #     """
    #     try:
    #         cursor.executemany(query, all_queries)
    #         db_connection.commit()  # Commit the transaction
    #         print(f'\n\nSuccessful insertions: {successful_count}')
    #     except Exception as e:
    #         db_connection.rollback()  # Rollback in case of failure
    #         print(f"\nError inserting data: {e}")
    # else:
    #     print("\nNo valid data to insert.")

    print(f'\n\nFailed insertions: {failed_count}\n\n')


def process_folder_1_11(folder_path, year, connection):
    """Process all SQL files in a folder and save their processed data in the db.
    """

    if not os.path.exists(folder_path):
        print(f"Folder does not exist: {folder_path}")
        return

    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)

        if os.path.isfile(file_path) and file_name.lower().endswith('.xlsx'):
            print(f"\n{'-' * 100}")
            print(f"{file_path}")
            post_to_db(connection, file_path, year)
            print(f"{file_path}")
