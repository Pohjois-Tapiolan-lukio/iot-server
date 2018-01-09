#!/bin/python

# This is a small API for entering data into a PostgreSQL database.
# Current usage:
# - /<name>/create/<types>    Creates a new table <name> with columns of <types>
#                             Eg. /foo/create/int;real;real
# - /<name>/insert/<values>   Inserts <values> into the table <name>
#                             Eg. /foo/insert/42;1.41;3.14
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
    return "Pohjis IoT Server"

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
    try:
        cur.execute("INSERT INTO " + name + " VALUES (" + values + ");")
        conn.commit()
        return "Ok! Inserted \"" + values + "\" into the table \"" + name + "\"."
    except psycopg2.Error as e:
        content = "Error! Is the URL valid?"
        content += "<br>" + e.pgerror
        conn.rollback()
        return content, 400

@app.route("/api/v1/<name>/create/<params>")
def create(name, params):
    param_list = []
    for param in params.split(";"):
        param_list.append(param + " varchar")
    params = ", ".join(param_list)
    try:
        cur.execute("DROP TABLE IF EXISTS " + name + ";")
        cur.execute("CREATE TABLE " + name + " (" + params + ");")
        conn.commit()
        return "Ok! Created the table \"" + name + "\"."
    except psycopg2.Error as e:
        content = "Error! Is the URL valid? (Params: " + params + ")"
        content += "<br>" + e.pgerror
        conn.rollback()
        return content, 400


## Server ##
server = WSGIServer(("", PORT), app)
server.serve_forever()
