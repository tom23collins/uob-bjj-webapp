import mysql.connector

def connection_open(app):
    return mysql.connector.connect(
        host=app.config.get('DB_HOST'),
        user=app.config.get('DB_USER'),
        password=app.config.get('DB_PASSWORD'),
        database=app.config.get('DB_NAME')
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