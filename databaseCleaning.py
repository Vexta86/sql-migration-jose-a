import mysql


def update_intensidad(db_connection):
    """
    Updates the 'Intensidad' table with new subject names and areas in a MySQL database.

    Parameters:
        db_connection (mysql.connector.connection_cext.CMySQLConnection): Active MySQL database connection.

    Returns:
        None
    """
    updates = {
        "artistica": ("Artística", "Artística"),
        "biologia": ("Biología", "Biología"),
        "ciencias_sociales": ("Ciencias Sociales", "Ciencias Sociales"),
        "economia_y_politica": ("Economía y Política", "Economía y Política"),
        "educacion_fisica": ("Educación Física", "Educación Física"),
        "etica": ("Ética", "Ética"),
        "filosofia": ("Filosofía", "Filosofía"),
        "fisica": ("Física", "Física"),
        "ingles": ("Inglés", "Inglés"),
        "lengua_castellana": ("Lengua Castellana", "Lengua Castellana"),
        "matematicas": ("Matemáticas", "Matemáticas"),
        "media_tecnica": ("Media Técnica", "Media Técnica"),
        "quimica": ("Química", "Química"),
        "religion": ("Religión", "Religión"),
        "tecnologia": ("Tecnología", "Tecnología"),
    }
    cursor = db_connection.cursor()
    try:
        query = """
        UPDATE Intensidad
        SET Nombre_asig = %s, Nom_area = %s
        WHERE Cod_asig = %s;
        """

        # Execute all updates in a loop
        cursor.executemany(query, [(v[0], v[1], k) for k, v in updates.items()])

        db_connection.commit()
        print("✅ Update successful!")

    except Exception as e:
        db_connection.rollback()
        print(f"❌ MySQL Error: {e}")

    finally:
        cursor.close()


def insert_intensidad_from_calificaciones(db_connection, year):
    """
    Inserts records into the 'Intensidad' table from 'Calificaciones1_11',
    filtering by the specified year.

    Parameters:
        db_connection (mysql.connector.connection_cext.CMySQLConnection): Active MySQL database connection.
        year (int): The year to filter records by.

    Returns:
        None
    """
    query = """
    INSERT INTO Intensidad (Cod_asig, Grado, Grupo, Fecha)
    SELECT Cod_asig, Grado, Grupo, Fecha
    FROM Calificaciones1_11
    WHERE YEAR(Fecha) = %s
    GROUP BY Cod_asig, Grado, Grupo, Fecha;
    """
    cursor = db_connection.cursor()
    try:

        cursor.execute(query, (year,))
        db_connection.commit()
        print(f"✅ Successfully inserted records for year {year}!")

    except Exception as e:
        db_connection.rollback()
        print(f"❌ MySQL Error: {e}")

    finally:
        cursor.close()


def insert_indice_calificaciones(db_connection, year):
    """
    Inserts records into the 'Indice_calificaciones' table from 'Calificaciones1_11',
    filtering by the specified year.

    Parameters:
        db_connection (mysql.connector.connection_cext.CMySQLConnection): Active MySQL database connection.
        year (int): The year to filter records by.

    Returns:
        None
    """
    query = """
    INSERT INTO Indice_calificaciones (Nombre, Grado, Fecha)
    SELECT Nombre, Grado, Fecha 
    FROM Calificaciones1_11
    WHERE YEAR(Fecha) = %s
    GROUP BY Nombre, Grado, Fecha;
    """
    cursor = db_connection.cursor()
    try:

        cursor.execute(query, (year,))
        db_connection.commit()
        print(f"✅ Successfully inserted records for year {year}!")

    except Exception as e:
        db_connection.rollback()
        print(f"❌ MySQL Error: {e}")

    finally:
        cursor.close()
