import pandas as pd

from utils import clean_name, clean_column_name


def replace_notes(df):

    replacement_dict = {

        'DBAJO': 'BJ',
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
        'DBAS': 'B',

        'DA': 'A',
        'DS': 'S'
    }
    # Apply the trimming and uppercase to each cell before replacement
    df = df.map(lambda x: str(x).strip().upper().replace('.', '').replace(' ', '') if isinstance(x, str) else x)

    df.replace(replacement_dict, inplace=True)

    # Replace all other values with None
    for column in df.columns:
        df[column] = df[column].map(lambda x: None if x not in replacement_dict.values() else x)

    df.dropna(axis=1, how='all', inplace=True)
    df.dropna(axis=0, how='all', inplace=True)

    return df


def process_workbook(route, quarter):
    df = pd.read_excel(route, sheet_name=quarter)

    df.columns = [str(col).strip() for col in df.iloc[8].tolist()]
    df = df.iloc[8:, 2:]
    try:
        df = df.loc[:, :'Total pérdidas'].iloc[:, :-1]
    except KeyError:
        df = df.loc[:, :'TP'].iloc[:, :-1]
    df = df.set_index('APELLIDOS Y NOMBRES')

    df = df.infer_objects()
    original_df = df
    df = replace_notes(df)
    return df


def extract_data(route, quarter):
    df = pd.read_excel(route, sheet_name=quarter)

    # TODO Grado must be numeric
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
        'aceleracion': 'AC',
        'brujula': 'BJ',
        'clei': 'CLEI',

    }

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
        cell = cell.split()
        data['Grado'] = numeric_grado[clean_column_name(cell[1])]
        if len(cell) >= 3:
            data['Grupo'] = cell[2]
    return data


def post_to_db(db_connection, route):
    failed_count = 0
    successful_count = 0
    cursor = db_connection.cursor()

    # El periodo 3 contiene las notas definitivas
    df = process_workbook(route, -1)
    data = extract_data(route, -1)

    for index, row in df.iterrows():
        student_name = clean_name(index)
        grado = data['Grado']

        grupo = data['Grupo']
        print(f'\n\n{student_name} from {grado}-{grupo}')
        for column in df.columns:

            materia = clean_column_name(column)

            nota = row[column]

            year = '2023'
            try:
                query = """
                    INSERT INTO Calificaciones1_11 (Nombre, Cod_asig, Nota, Grado, Grupo, Fecha)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                # cursor.execute(query, (student_name, materia, nota, grado, grupo, year))
                # print(query, (student_name, materia, nota, grado, grupo, year))
                # if not nota:
                print('\t', materia, nota, end=' ')
                successful_count += 1

            except Exception as e:
                print('Failed for student', student_name, materia, nota, e)
                failed_count += 1
    print(f'\nSuccessful insertions: {successful_count}')
    print(f'Failed insertions: {failed_count}\n')
