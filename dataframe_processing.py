import pandas as pd

from utils import clean_name, clean_column_name


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
        'DBAS': 'B',
        'DBSC': 'B',
        'DBSCO': 'B',
        'DBASCO': 'B',

        'DA': 'A',
        'DS': 'S',
        'DDS': 'S'
    }
    # Apply the trimming and uppercase to each cell before replacement
    df = df.map(lambda x: str(x).strip().upper().replace('.', '').replace(' ', '') if isinstance(x, str) else x)

    df = df.map(lambda x: convert_number_to_note(x) if isinstance(x, float) or isinstance(x, int) else x)

    df.replace(replacement_dict, inplace=True, regex=False)

    # Replace all other values with None
    df = df.map(lambda x: None if x not in replacement_dict.values() else x)

    df.dropna(axis=1, how='all', inplace=True)
    df.dropna(axis=0, how='all', inplace=True)

    return df


def process_workbook(route, quarter):
    df = pd.read_excel(route, sheet_name=quarter)

    df.columns = [clean_column_name(col) for col in df.iloc[8].tolist()]
    df = df.set_index('apellidos_y_nombres')
    df = df.iloc[8:, 2:]
    try:
        df = df.loc[:, :'total_perdidas'].iloc[:, :-1]
    except KeyError:
        df = df.loc[:, :'tp'].iloc[:, :-1]


    df = replace_notes(df)
    return df


def extract_data(route, quarter):
    df = pd.read_excel(route, sheet_name=quarter)

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
        grado = clean_column_name(cell[1])
        possible_groups = ['A', 'B', 'C', 'D', 1, 2, 3, 4]
        if grado in numeric_grado.keys():
            data['Grado'] = numeric_grado[grado]
        else:
            data['Grado'] = grado
        if len(cell) >= 3:
            data['Grupo'] = cell[2]
        elif isinstance(data['Grado'], int) and route[-6] in possible_groups:
            data['Grupo'] = route[-6]

    return data


def post_to_db(db_connection, route, year):
    failed_count = 0
    successful_count = 0
    cursor = db_connection.cursor()

    # El periodo 3 contiene las notas definitivas
    df = process_workbook(route, -1)
    data = extract_data(route, 0)

    for index, row in df.iterrows():
        student_name = clean_name(index)
        grado = data['Grado']

        grupo = data['Grupo']
        print(f'\n\n{student_name} from {grado}-{grupo} {year}')
        for column in df.columns:

            materia = column

            nota = row[column]

            try:
                query = """
                    INSERT INTO Calificaciones1_11 (Nombre, Cod_asig, Nota, Grado, Grupo, Fecha)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """

                if not nota:
                    raise Exception('NULL')
                print('\t', materia, nota, end='\t')

                cursor.execute(query, (student_name, materia, nota, grado, grupo, year))

                successful_count += 1

            except Exception as e:
                print('\t', materia, e, end='\t')
                failed_count += 1
    print(f'\n\nSuccessful insertions: {successful_count}')
    print(f'Failed insertions: {failed_count}\n')
