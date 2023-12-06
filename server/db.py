import sqlite3
import json

__test_db = 'aircraft'

import logging

# Configure the logging settings (adjust as needed)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add a FileHandler to save logs to a file
file_handler = logging.FileHandler('query_to_dict_list.log')
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


def connect_to_database(database_name):
    try:
        connection = sqlite3.connect(database_name)
        return connection
    except sqlite3.Error as e:
        print(f"Error connecting to SQLite database: {e}")
        return None

def execute_query(connection, query):
    try:
        cursor = connection.cursor()
        # Split the query into individual statements
        statements = query.split(';')
        for statement in statements:
            if statement.strip():  # Skip empty statements
                cursor.execute(statement)
        connection.commit()  # Commit changes after executing all statements
        return cursor.fetchall(), cursor.description
    except sqlite3.Error as e:
        print(f"Error executing query: {e}")
        return None, None
    finally:
        if cursor:
            cursor.close()


def create_tables(connection, schema_file):
    try:
        with open(schema_file, 'r') as file:
            schema_query = file.read()
            execute_query(connection, schema_query)
        print("Tables created successfully.")
    except FileNotFoundError:
        print(f"Error: Schema file '{schema_file}' not found.")
    except sqlite3.Error as e:
        print(f"Error executing schema: {e}")


def get_columns(description):
    if description is not None:
        columns = [column[0] for column in description]
        return columns
    else:
        return None

def query_to_dict_list(connection, query, param_value):
    try:
        # Log the query and param_value
        logger.info(f"Executing query: {query}, Param value: {param_value}")

        results, description = execute_query(connection, query)
        if results is not None:
            # Check if there are any rows
            if len(results) > 0:
                columns = get_columns(description)
                dict_list = [{columns[i]: row[i] for i in range(len(columns))} for row in results]

                # Log the dict_list
                logger.info(f"Result: {dict_list}")

                return dict_list
            else:
                # Log when there is no data
                logger.info("No data returned by the query.")
                return None
        else:
            return None
    except Exception as e:
        # Log the error
        logger.error(f"Error executing query: {e}")
        return None


def query_to_json(connection, query):
    results, description = execute_query(connection, query)
    if results is not None:
        # Check if there are any rows
        if len(results) > 0:
            columns = get_columns(description)
            dict_list = [{columns[i]: row[i] for i in range(len(columns))} for row in results]
            json_result = json.dumps(dict_list, indent=2)
            return json_result
        else:
            print("No data returned by the query.")
            return None
    else:
        return None

if __name__ == "__main__":
    # Replace 'your_database.db' with the actual name of your SQLite database file
    db_file = __test_db + '.db'
    db_connection = connect_to_database(db_file)

    if db_connection:
        # Create tables and insert sample data if they don't exist
        create_tables(db_connection,'aircraft.sql')

        # Example query - replace with your own SQL query
        query = "SELECT max(age) FROM pilot;"
        
        json_result = query_to_json(db_connection, query)

        if json_result is not None:
            print(json_result)
        else:
            print("Query execution failed.")

        db_connection.close()
    else:
        print("Connection to the database failed.")
