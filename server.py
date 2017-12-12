#!/bin/python

# This is a small API for entering data into a PostgreSQL database.
# Current usage:
# - /<name>/create/<types>    Creates a new table <name> with columns of <types>
#                             Eg. /foo/create/int,real,real
# - /<name>/insert/<values>   Inserts <values> into the table <name>
#                             Eg. /foo/insert/42,1.41,3.14
# - /<name>/print             Prints out the contents of the table <name> as HTML

import psycopg2
import atexit
from flask import Flask
from gevent.wsgi import WSGIServer

DB_NAME = "pohjisiot"
DB_USER = "postgres"
PORT = 5000

## DB ##
conn = psycopg2.connect("dbname=" + DB_NAME + " user=" + DB_USER)
cur = conn.cursor()
def close_db():
    cur.close()
    conn.close()
    print("Exited gracefully.")
atexit.register(close_db)


## API ##
app = Flask(__name__)

@app.route("/")
def root():
    return "The <a href='https://github.com/pohjois-tapiolan-lukio/iot-server'>Pohjis IoT server</a> is running."

# Testing url
@app.route("/api/v1/command/to/run")
def api_example():
    return "The Pohjis IoT server is running properly, congratulations!"

# Prints out the values contained in the table <name>
@app.route("/api/v1/<name>/print")
def api_print(name):
    output = "<div>"
    output += "<h3>" + name + "</h3>"
    output += "<table>"
    cur.execute("SELECT * FROM " + name + ";")
    for record in cur:
        output += "<tr>"
        for value in (record):
            output += "<td>" + str(value) + "</td>"
        output += "</tr>"
    output += "</table>"
    return output

@app.route("/api/v1/<name>/insert/<values>")
def insert(name, values):
    values = ", ".join(values.split(";"))
    cur.execute("INSERT INTO " + name + " VALUES (" + values + ");")
    conn.commit()
    return "Ok!"

@app.route("/api/v1/<name>/create/<types>")
def create(name, types):
    types_sql = ""
    i = 0
    for type in types.split(","):
        # Create a name
        var_name = "var" + str(i)
        i += 1
        # Add the variable to the list
        types_sql += var_name + " " + type + ", "
    types_sql = types_sql[:-2]
    cur.execute("DROP TABLE IF EXISTS " + name + ";")
    cur.execute("CREATE TABLE " + name + " (" + types_sql + ");")
    conn.commit()
    return "Ok!"


## Server ##
server = WSGIServer(("", PORT), app)
server.serve_forever()
