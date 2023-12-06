from socketserver import ThreadingTCPServer
from http.server import SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from db import create_tables, connect_to_database, query_to_json, query_to_dict_list
from llm_schema import llm_schema_context
from llm import Seq2SeqGenerator
import json
import sqlite3
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import re
from os import path


__test_db = 'aircraft'

import logging
from werkzeug._reloader import run_with_reloader
from werkzeug._reloader import reloader_loops
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from socketserver import ThreadingTCPServer
from http.server import SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json

llm_schema_context = """
PRAGMA foreign_keys = ON;
CREATE TABLE `Customers` (
`customer_id` INTEGER PRIMARY KEY,
`customer_first_name` VARCHAR(50),
`customer_middle_initial` VARCHAR(1),
`customer_last_name` VARCHAR(50),
`gender` VARCHAR(1),
`email_address` VARCHAR(255),
`login_name` VARCHAR(80),
`login_password` VARCHAR(20),
`phone_number` VARCHAR(255),
`town_city` VARCHAR(50),
`state_county_province` VARCHAR(50),
`country` VARCHAR(50)
);


CREATE TABLE `Orders` (
`order_id` INTEGER PRIMARY KEY,
`customer_id` INTEGER NOT NULL,
`date_order_placed` DATETIME NOT NULL,
`order_details` VARCHAR(255),
FOREIGN KEY (`customer_id` ) REFERENCES `Customers`(`customer_id` )
);


CREATE TABLE `Invoices` (
`invoice_number` INTEGER PRIMARY KEY,
`order_id` INTEGER NOT NULL,
`invoice_date` DATETIME,
FOREIGN KEY (`order_id` ) REFERENCES `Orders`(`order_id` )
);

CREATE TABLE `Accounts` (
`account_id` INTEGER PRIMARY KEY,
`customer_id` INTEGER NOT NULL,
`date_account_opened` DATETIME,
`account_name` VARCHAR(50),
`other_account_details` VARCHAR(255),
FOREIGN KEY (`customer_id` ) REFERENCES `Customers`(`customer_id` )
);




CREATE TABLE `Product_Categories` (
`production_type_code` VARCHAR(15) PRIMARY KEY,
`product_type_description` VARCHAR(80),
`vat_rating` DECIMAL(19,4)
);
CREATE TABLE `Products` (
`product_id` INTEGER PRIMARY KEY,
`parent_product_id` INTEGER,
`production_type_code` VARCHAR(15) NOT NULL,
`unit_price` DECIMAL(19,4),
`product_name` VARCHAR(80),
`product_color` VARCHAR(20),
`product_size` VARCHAR(20),
FOREIGN KEY (`production_type_code` ) REFERENCES `Product_Categories`(`production_type_code` )
);


CREATE TABLE `Financial_Transactions` (
`transaction_id` INTEGER NOT NULL ,
`account_id` INTEGER NOT NULL,
`invoice_number` INTEGER,
`transaction_type` VARCHAR(15) NOT NULL,
`transaction_date` DATETIME,
`transaction_amount` DECIMAL(19,4),
`transaction_comment` VARCHAR(255),
`other_transaction_details` VARCHAR(255),
FOREIGN KEY (`invoice_number` ) REFERENCES `Invoices`(`invoice_number` ),
FOREIGN KEY (`account_id` ) REFERENCES `Accounts`(`account_id` )
);
CREATE TABLE `Order_Items` (
`order_item_id` INTEGER PRIMARY KEY,
`order_id` INTEGER NOT NULL,
`product_id` INTEGER NOT NULL,
`product_quantity` VARCHAR(50),
`other_order_item_details` VARCHAR(255),
FOREIGN KEY (`product_id` ) REFERENCES `Products`(`product_id` ),
FOREIGN KEY (`order_id` ) REFERENCES `Orders`(`order_id` )
);



CREATE TABLE `Invoice_Line_Items` (
`order_item_id` INTEGER NOT NULL,
`invoice_number` INTEGER NOT NULL,
`product_id` INTEGER NOT NULL,
`product_title` VARCHAR(80),
`product_quantity` VARCHAR(50),
`product_price` DECIMAL(19,4),
`derived_product_cost` DECIMAL(19,4),
`derived_vat_payable` DECIMAL(19,4),
`derived_total_cost` DECIMAL(19,4),
FOREIGN KEY (`order_item_id` ) REFERENCES `Order_Items`(`order_item_id` ),
FOREIGN KEY (`invoice_number` ) REFERENCES `Invoices`(`invoice_number` ),
FOREIGN KEY (`product_id` ) REFERENCES `Products`(`product_id` )
);


"""

class Seq2SeqGenerator:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Seq2SeqGenerator, cls).__new__(cls, *args, **kwargs)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, model_path='gaussalgo/T5-LM-Large-text2sql-spider'):
        if not self._initialized:
            self.model = AutoModelForSeq2SeqLM.from_pretrained(model_path)
            self.tokenizer = AutoTokenizer.from_pretrained(model_path)
            self._initialized = True
    
    def extract_sql_query(self,input_string):
    # Regular expression pattern to match SQL queries
        sql_pattern = re.compile(r'\b(SELECT|INSERT|UPDATE)\b.*$', re.IGNORECASE)

        # Find the first match
        match = sql_pattern.search(input_string)

        # Extract the matched SQL query
        if match:
            return match.group()
        else:
            return None

    def generateSQL(self, question, schema):

        input_text = " ".join(["Question: ", question, "Schema:", schema])

        model_inputs = self.tokenizer(input_text, return_tensors="pt")
        outputs = self.model.generate(**model_inputs, max_length=512)
        flat_outputs = outputs.view(-1).tolist()
        val = {}
        output_text = self.tokenizer.decode(flat_outputs, skip_special_tokens=True)
        val['llm_Sql'] = output_text
        ex = self.extract_sql_query(output_text)
        val['extract_Sql'] = ex
        return val

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

generator = Seq2SeqGenerator()


class ServerChangeHandler(FileSystemEventHandler):
    def __init__(self, server_handler, watch_path='.'):
        self.server_handler = server_handler
        self.watch_path = watch_path
        self.server_observer = Observer()
        self.server_observer.schedule(self, self.watch_path, recursive=True)
        self.server_observer.start()

    def on_any_event(self, event):
        if event.is_directory:
            return

        # Check if the changed file is not a log file
        if not event.src_path.endswith('.log'):
            # Restart the server only for non-log file changes
            self.server_handler.server_close()
            self.server_handler.server_observer.stop()
            self.server_handler.server_observer.join()


class MyHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        # Handle GET requests here
        if self.path.startswith('/site/'):
            # Serve files from the /site/ directory
            return self.serve_static_file()

        # Create a list to store error messages
        error_messages = []

        # Initialize the response structure
        resp = {
            "gen": [{
                "llm_Sql": "",
                "extract_Sql": ""
            }],
            "data": [{
                "data": "No Data Available"
            }],
            "errors" :[{
                "error" : "No Error"
            }]
        }

        # Attempt to connect to the database
        db_connection = connect_to_database(db_file)
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        url_parts = urlparse(self.path)
        query_params = parse_qs(url_parts.query)

        # Accessing specific parameters
        param_value = query_params.get('q', [''])[0]


        if db_connection:
            try:
                # Your existing code for handling database queries
                query = generator.generateSQL(param_value, llm_schema_context)
                resp['gen'] = [query]
                print(query)
                db_output = query_to_dict_list(db_connection, query['extract_Sql'],param_value)
                resp['data'] = db_output
            except Exception as e:
                # Append the error message to the list
                error_messages.append({"Error": str(e)})
            finally:
                # Close the database connection
                db_connection.close()
        else:
            # Append the connection error message to the list
            error_messages.append({"Error": "Connection to the database failed."})

        # If there are errors, add them to the response
        if len(error_messages) > 0:
            resp['errors'] = error_messages

        # Convert the response to a JSON string
        resp_json = json.dumps(resp)
        print(resp_json)
        self.wfile.write(resp_json.encode('utf-8'))
        # Print or send the JSON response


def run_server():
    PORT = 8000
    server = ThreadingTCPServer(("", PORT), MyHandler)
    print(f"Server running on port {PORT}")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        # Handle Ctrl+C interrupt
        print("Server interrupted. Shutting down.")
    finally:
        # Close the server socket
        server.server_close()



# Replace 'your_database.db' with the actual name of your SQLite database file
db_name = 'customer_invoices'
db_path = 'customer_invoices.db'
schema_file = 'customer_invoices.sql'
db_file = db_path
db_connection = connect_to_database(db_file)

if db_connection:
    # Create tables and insert sample data if they don't exist
    create_tables(db_connection, schema_file)

    # Example query - replace with your own SQL query
    llm_gen_value = generator.generateSQL('who all are the customers', llm_schema_context)
    print(llm_gen_value)
    json_result = query_to_json(db_connection, llm_gen_value['extract_Sql'])

    if json_result is not None:
        print(json_result)
    else:
        print("Query execution failed.")

    # Use the werkzeug run_with_reloader to enable auto-reloading
    ##run_with_reloader(run_server, reloader_loops)
    run_server()
    
else:
    print("Connection to the database failed.")
