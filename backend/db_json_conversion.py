import json
import sqlite3
from database import User, Problem, Annotation, Dataset
import pdb

table_name2SQLModel = {
    "user": User,
    "problem": Problem,
    "annotation": Annotation,
    "dataset": Dataset
}

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

# connect to the SQlite databases
def openConnection(pathToSqliteDb):
    connection = sqlite3.connect(pathToSqliteDb)
    cursor = connection.cursor()
    return connection, cursor


def getAllRecordsInTable(table_name, connection, cursor):
    # connection.row_factory = dict_factory
    cursor.execute("SELECT * FROM '{}' ".format(table_name))
    # fetchall as result
    results = cursor.fetchall()
    # close connection
    # connection.close()
    return json.dumps(results)


def db_to_json(pathToSqliteDb):
    connection, cursor = openConnection(pathToSqliteDb)
    # select all the tables from the database
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    # for each of the tables , select all the records from the table
    results_all_table = {}
    for table in tables:
        # Get the records in table
        table_name = table[0]
        results = getAllRecordsInTable(table_name, connection, cursor)
        results_all_table[table_name] = json.loads(results)

    # close connection
    connection.close()
    return results_all_table

def json_to_db(json_file, db_file):
    with open(json_file, "r") as fp:
        data = json.load(fp)

    conn, cursor = openConnection(db_file)

    for table_name, rows in data.items():
        if len(rows) > 0:
            SQLModelClass = table_name2SQLModel.get(table_name, None)
            if SQLModelClass is None:
                print("No SQLModelClass found for {}".format(table_name))
            
            columns = SQLModelClass.model_fields.keys()

            # columns = rows[0].keys()
            column_definition = ", ".join(f"{col} TEXT" for col in columns)
            cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({column_definition});")
            for row in rows:
                placeholders = ", ".join("?" * len(row))
                all_columns = ", ".join(columns)
                insert_sql_command = f"INSERT INTO {table_name} ({all_columns}) VALUES ({placeholders});"
                cursor.execute(insert_sql_command, row)
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    db_file = "prmbench_database.db"
    json_file = "prmbench_database.json"

    db2json = False

    if db2json:
        json_data = db_to_json(db_file)

        with open(json_file, "w") as fp:
            json.dump(json_data, fp)
    else:
        json_to_db(json_file, db_file)

    pdb.set_trace()