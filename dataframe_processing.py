import pandas as pd

from utils import clean_name, clean_column_name


def process_workbook(route, quarter):
    df = pd.read_excel(route, sheet_name=quarter)

    df.columns = df.iloc[8].tolist()
    df = df.iloc[9:, 2:]
    df = df.loc[:, 'APELLIDOS Y NOMBRES':'Total pérdidas'].iloc[:, :-1]
    df = df.set_index('APELLIDOS Y NOMBRES')

    df = df.infer_objects()
    replacement_dict = {
        'DBAJO': 'BJ',
        'DB': 'B',
        'DA': 'A',
        'DS': 'S'

    }
    df.replace(replacement_dict, inplace=True)

    # Replace all other values with None
    for column in df.columns:
        df[column] = df[column].map(lambda x: None if x not in replacement_dict.values() else x)

    df.dropna(axis=1, how='all', inplace=True)
    df.dropna(axis=0, how='all', inplace=True)

    return df


def extract_data(route, quarter):
    df = pd.read_excel(route, sheet_name=quarter)

    data = {
        'Grado': None,
        'Grupo': None,
        'Periodo': None
    }
    grado_grupo = df.iloc[4, 1]

    if len(grado_grupo.split(': ')) > 1:
        grado_grupo = grado_grupo.split(': ')[1]

    if len(df.iloc[5, 1].split(': ')) > 1:
        data['Periodo'] = df.iloc[5, 1].split(': ')[1].strip()
    else:
        data['Periodo'] = df.iloc[5, 1]
    if len(grado_grupo.split()) > 1:
        data['Grado'] = grado_grupo.split()[0]
        data['Grupo'] = grado_grupo.split()[1]
    else:
        data['Grado'] = grado_grupo.strip()
    return data


def process_df(route):
    output = []
    df = process_workbook(route, 2)
    data = extract_data(route, 2)
    for index, row in df.iterrows():
        for column in df.columns:
            estudiante = clean_name(index)

            materia = clean_column_name(column)

            nota = row[column]

            grado = clean_column_name(data['Grado'])

            grupo = data['Grupo']

            output.append((estudiante, materia, nota, grado, grupo))
    return output
