import pandas as pd

from utils import clean_name, clean_column_name, remove_tildes


def convert_number_to_note(number):
    if 3 > number > 0:
        return 'BJ'
    if 4 > number >= 3:
        return 'B'
    if 5 > number >= 4:
        return 'A'
    if number == 5:
        return 'S'
    return None


def replace_notes(df):
    df = df.infer_objects()
    replacement_dict = {

        'DBAJO': 'BJ',
        'BAJO': 'BJ',
        'BAJ': 'BJ',
        'DBJO': 'BJ',
        'DAJO': 'BJ',
        'DBJ': 'BJ',

        'DB': 'B',
        'DBA': 'B',
        'DBCO': 'B',
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

        'DA': 'A',
        'DALTO': 'A',
        'ALTO': 'A',
        'DALTOD': 'A',

        'DS': 'S',
        'DSUPERIOR': 'S',
        'SUPERIOR': 'S',
        'DDS': 'S'
    }
    # Apply the trimming and uppercase to each cell before replacement
    df = df.map(lambda x: remove_tildes(x).strip().upper().replace('.', '').replace(',', '').replace(' ', '').replace('-', '') if isinstance(x, str) else x)

    df = df.map(lambda x: convert_number_to_note(x) if isinstance(x, float) or isinstance(x, int) else x)

    df.replace(replacement_dict, inplace=True, regex=False)

    # Replace all other values with None
    df = df.map(lambda x: None if x not in replacement_dict.values() else x)

    df.dropna(axis=1, how='all', inplace=True)
    df.dropna(axis=0, how='all', inplace=True)

    # Drop rows with more than 7 NaN values
    # Calculate the threshold: total columns minus 8
    thresh_value = len(df.columns) - 7
    df.dropna(axis=0, thresh=thresh_value, inplace=True)

    return df


def process_workbook(route, quarter):
    df = pd.read_excel(route, sheet_name=quarter)

    # Find the index where 'apellidos_y_nombres' is located
    header_index = df[df.eq('APELLIDOS Y NOMBRES').any(axis=1)].index[0]

    # Set the column names using the found index
    df.columns = [clean_column_name(col) for col in df.iloc[header_index].tolist()]
    df = df.iloc[header_index:, 2:]

    # Set 'apellidos_y_nombres' as the index
    df = df.set_index('apellidos_y_nombres')

    try:
        df = df.loc[:, :'total_perdidas'].iloc[:, :-1]
    except KeyError:
        df = df.loc[:, :'tp'].iloc[:, :-1]

    df = replace_notes(df)
    return df


def is_digit_or_float(value):
    try:
        float(value)  # Attempt to convert to float
        return True
    except (ValueError, TypeError):
        return False


def get_grado_grupo(grado, grupo):
    possible_groups = ['A', 'B', 'C', 'D', 1, 2, 3, 4]
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
    }

    special_grado = {
        'aceleracion': 'AC',
        'brujula': 'BJ',
        'clei': 'CLEI',
    }
    if grupo in possible_groups and str(grado).isdigit():
        return int(grado), grupo
    if grupo in possible_groups and grado in numeric_grado.keys():
        return numeric_grado[grado], grupo
    if grupo in possible_groups:
        return 0, grupo
    if grado in numeric_grado.keys():
        return numeric_grado[grado], ''
    if str(grado).isdigit():
        return int(grado), ''
    if grado in special_grado.keys() and is_digit_or_float(grupo):
        return special_grado[grado], float(grupo)
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
        lambda x: isinstance(x, str) and 'grupo' in x.lower()
    )

    if not found_cells.any().any():
        found_cells = df.map(
            lambda x: isinstance(x, str) and 'grado' in x.lower()
        )

    if found_cells.any().any():
        df = df[found_cells]
        df.dropna(axis=1, how='all', inplace=True)
        df.dropna(axis=0, how='all', inplace=True)
        cell = df.iloc[0, 0]
        cell = clean_column_name(cell)
        cell = cell.split()

        if len(cell) > 2:
            grado = clean_column_name(cell[1])
            data['Grado'], data['Grupo'] = get_grado_grupo(grado, cell[2])

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
                # print(materia, nota, end='\t')
            else:
                failed_count += 1
                print(materia, 'NULL', end='\t')

        # Add the queries for this student to the main list
        all_queries.extend(queries)
        successful_count += len(queries)

    # Execute all queries at once
    if all_queries:
        query = """
            INSERT INTO Calificaciones1_11 (Nombre, Cod_asig, Nota, Grado, Grupo, Fecha)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        try:
            cursor.executemany(query, all_queries)
            db_connection.commit()  # Commit the transaction
            print(f'\n\nSuccessful insertions: {successful_count}')
        except Exception as e:
            db_connection.rollback()  # Rollback in case of failure
            print(f"\nError inserting data: {e}")
    else:
        print("\nNo valid data to insert.")

    print(f'\n\nFailed insertions: {failed_count}\n\n')