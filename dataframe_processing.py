import pandas as pd

from utils import clean_name, clean_column_name


def replace_notes(df):
    # TODO: Check possible variants for notes
    replacement_dict = {
        ' ': ' ',
        'DBAJO': 'BJ',
        'DBJO': 'BJ',

        'DB': 'B',
        'DBA': 'B',
        'DBCO': 'B',
        'DBACO': 'B',
        'DBS': 'B',
        'BS': 'B',
        'DDBS': 'B',
        'DBO': 'B',
        'DBASICO': 'B',

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

    df.columns = df.iloc[8].tolist()
    df = df.iloc[9:, 2:]
    df = df.loc[:, 'APELLIDOS Y NOMBRES':'Total pérdidas'].iloc[:, :-1]
    df = df.set_index('APELLIDOS Y NOMBRES')

    df = df.infer_objects()
    original_df = df
    df = replace_notes(df)
    return df


def extract_data(route, quarter):
    df = pd.read_excel(route, sheet_name=quarter)

    data = {
        'Grado': '',
        'Grupo': ''
    }
    # Search for the cell containing the word "grupo" (case insensitive)
    found_cells = df.map(
        lambda x: isinstance(x, str) and 'grupo' in x.lower()
    )

    # Get the first occurrence of the word "grupo"
    if found_cells.any().any():
        df = df[found_cells]
        df.dropna(axis=1, how='all', inplace=True)
        df.dropna(axis=0, how='all', inplace=True)
        cell = df.iloc[0, 0]
        cell = cell.split()
        data['Grado'] = cell[1]
        if len(cell) >= 3:
            data['Grupo'] = cell[2]

    return data


def post_to_db(db_connection, route):
    failed_count = 0
    successful_count = 0
    cursor = db_connection.cursor()
    # El periodo 3 contiene las notas definitivas
    df = process_workbook(route, 2)
    data = extract_data(route, 2)

    for index, row in df.iterrows():
        student_name = clean_name(index)
        grado = clean_column_name(data['Grado'])

        grupo = data['Grupo']
        # print(f'\n{student_name} from {grado}-{grupo}')
        for column in df.columns:
            print(f'Students added: {successful_count}', end='\r')

            materia = clean_column_name(column)

            nota = row[column]

            year = '2024'
            try:
                query = """
                    INSERT INTO Calificaciones1_11 (Nombre, Cod_asig, Nota, Grado, Grupo, Fecha)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                # cursor.execute(query, (student_name, materia, nota, grado, grupo, year))
                print(query, (student_name, materia, nota, grado, grupo, year))
                # print('\t', materia, nota)
                successful_count += 1

            except Exception as e:
                print('Failed for student', student_name, materia, nota, e)
                failed_count += 1
    print(f'\nSuccessful insertions: {successful_count}')
    print(f'Failed insertions: {failed_count}\n')
