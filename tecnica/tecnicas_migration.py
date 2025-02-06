import pandas as pd
import os
import mysql.connector


def get_group_tecnica(path):
    path = path.split('_')
    return path[-1].split('.')[0]


def add_to_intesidad(connection, materia, grupo):
    cursor = connection.cursor()

    # Define the query
    get_query = """
       SELECT * 
       FROM Intensidad 
       WHERE Grado = %s
         AND Cod_asig = %s 
         AND Fecha = %s
         AND Grupo = %s
       """

    # Parameters for the query
    params = (materia['grado'], materia['codigo'], materia['fecha'], grupo)

    # Execute the query
    cursor.execute(get_query, params)

    # Fetch all results
    results = cursor.fetchall()

    # Check if any rows were returned
    if not results:
        # Define the INSERT query
        insert_query = """
        INSERT INTO Intensidad 
        (Nom_area, Cod_asig, Nombre_asig, Grado, Grupo, Fecha) 
        VALUES (%s, %s, %s, %s, %s, %s)
        """

        # Parameters for the INSERT query
        insert_params = (materia['nombre'], materia['codigo'], materia['nombre'], materia['grado'], grupo, materia['fecha'])

        # Execute the INSERT query
        cursor.execute(insert_query, insert_params)

        # Commit the transaction
        connection.commit()
        print(f"\nInserted a {materia['nombre']} for {materia['grado'], grupo, materia['fecha']} into the Intensidad table.\n")


def process_tecnica(route, quarter):
    df = pd.read_excel(route, sheet_name=quarter)

    df.columns = df.iloc[0].tolist()
    df = df.iloc[1:]
    # Set the index
    df = df.set_index('DOCUMENTO')

    return df


def get_info_materia(materia):
    info_materia = {
        'codigo': '',
        'nombre': '',
        'fecha': 0,
        'grado': 0,
    }
    materia = materia.split('_')
    info_materia['codigo'] = materia[0]
    info_materia['nombre'] = materia[1]
    info_materia['fecha'] = materia[2]
    info_materia['grado'] = materia[3]
    return info_materia


def post_to_db_tecnica(connection, path):
    cursor = connection.cursor()

    # El periodo 3 contiene las notas definitivas
    df = process_tecnica(path, -1)
    grupo = get_group_tecnica(path)

    # Initialize counters
    successful_count = 0
    failed_count = 0

    # List to store all queries
    all_queries = []

    # Iterate over the DataFrame
    for index, row in df.iterrows():
        student_name = row[0]
        student_id = index

        # Collect queries for this student
        queries = []
        for column in df.columns[1:]:
            materia = get_info_materia(column)

            add_to_intesidad(connection, materia, grupo)

            print(f'\n\n{student_name, student_id} from {materia['grado']}-{grupo} {materia['fecha']}')

            nota = row[column]

            if nota:
                queries.append((student_id, student_name, materia['codigo'], nota, materia['grado'],
                                grupo, materia['fecha']))
                print(materia['nombre'], nota, end='\t')
            else:
                failed_count += 1
                print(materia['nombre'], 'NULL', end='\t')

        # Add the queries for this student to the main list
        all_queries.extend(queries)
        successful_count += len(queries)

    # # Execute all queries at once
    # if all_queries:
    #     query = """
    #         INSERT INTO Calificaciones1_11 (Documento, Nombre, Cod_asig, Nota, Grado, Grupo, Fecha)
    #         VALUES (%s, %s, %s, %s, %s, %s, %s)
    #     """
    #     try:
    #         cursor.executemany(query, all_queries)
    #         connection.commit()  # Commit the transaction
    #         print(f'\n\nSuccessful insertions: {successful_count}')
    #     except Exception as e:
    #         connection.rollback()  # Rollback in case of failure
    #         print(f"\nError inserting data: {e}")
    # else:
    #     print("\nNo valid data to insert.")
    #
    # print(f'\n\nFailed insertions: {failed_count}\n\n')


route = "D:\\Projects\\Akros\\joseacevedogomez\\tecnicas\\2024_11_A.xlsx"

