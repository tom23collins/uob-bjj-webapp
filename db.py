import mysql.connector
import config

def connection_open(app):
    return mysql.connector.connect(
        host=config.DB_HOST,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        database=config.DB_NAME,
    )

def db_update(app, sql, values):
    try:
        connection = connection_open(app)
        cursor = connection.cursor()
        cursor.execute(sql, values)
        connection.commit()

    except mysql.connector.Error as err:
        print(f"Error: {err}")

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def db_query(app, sql):
    connection = connection_open(app)
    cursor = connection.cursor()
    cursor.execute(sql)
    return cursor.fetchall()

def db_query_values(app, sql, values):
    connection = connection_open(app)
    cursor = connection.cursor()
    cursor.execute(sql, values)
    return cursor.fetchall()