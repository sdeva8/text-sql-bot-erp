from werkzeug._reloader import run_with_reloader
from werkzeug._reloader import reloader_loops
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from socketserver import ThreadingTCPServer
from http.server import SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from db import create_tables, connect_to_database, query_to_json, query_to_dict_list
from llm_schema import llm_schema_context
from llm import Seq2SeqGenerator
import json



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


class MyHandlerWithReload(MyHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.change_handler = ServerChangeHandler(self, watch_path='.')




def run_server():
    PORT = 8000
    server = ThreadingTCPServer(("", PORT), MyHandlerWithReload)
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
    run_with_reloader(run_server, reloader_loops)
    
else:
    print("Connection to the database failed.")
