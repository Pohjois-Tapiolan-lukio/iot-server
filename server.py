#!/bin/python

# This is a small API for entering data into a PostgreSQL database.
# It's also extremely insecure, and easy to fiddle with. Have fun hacking!
# Current usage:
# - /<name>/create/<types>    Creates a new table <name> with columns of <types>
#                             Eg. /foo/create/int;real;real
# - /<name>/insert/<values>   Inserts <values> into the table <name>
#                             Eg. /foo/insert/42;1.41;3.14
# - /<name>/print             Prints out the contents of the table <name> as HTML

import psycopg2
import atexit
from flask import Flask, send_file
from gevent.wsgi import WSGIServer
from io import BytesIO

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
    return "<a href='https://github.com/pohjois-tapiolan-lukio/iot-server'>Pohjis IoT server</a>"

@app.route("/heippa")
def heippa():
    return "Moikka!"

# Testing url
@app.route("/api/v1/command/to/run")
def api_example():
    return "Pohjis IoT Server"

# Exports the table as a .csv
@app.route("/api/v1/<name>.csv")
def api_csv(name):
    csv = ""
    def write_cur_to_output(titles):
        nonlocal csv
        for record in cur:
            csv += ",".join(record)
            if titles:
                csv += ","
            else:
                csv += "\n"
        csv += "\n"
    try:
        cur.execute("SELECT column_name FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name = %s", (name, ))
        write_cur_to_output(True)
        cur.execute("SELECT * FROM " + name + ";")
        write_cur_to_output(False)
        return send_file(BytesIO(csv.encode()), attachment_filename = name + ".csv", mimetype = "text/csv")
    except psycopg2.Error as e:
        content = "Error! Is the URL valid?"
        content += "<br>" + e.pgerror
        conn.rollback()
        print("[INFO] Failed to export csv from table: " + name)
        return content, 400

# Prints out the values contained in the table <name>
@app.route("/api/v1/<name>/print")
def api_print(name):
    name = name.replace("-", "_")
    def write_cur_to_output(one_line):
        nonlocal output
        if one_line: output += "<tr>"
        for record in cur:
            if not one_line: output += "<tr>"
            for value in (record):
                output += "<td style='margin-right:1em'>" + str(value) + "</td>"
            if not one_line: output += "</tr>"
        if one_line: output += "</tr>"
    output = "<div>"
    output += "<h2>" + name + "</h2>"
    output += "<a href='/api/v1/" + name + ".csv'><button>Export to .csv</button></a>"
    output += "<table>"
    try:
        cur.execute("SELECT column_name FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name = %s", (name, ))
        write_cur_to_output(True)
        cur.execute("SELECT * FROM " + name + ";")
        write_cur_to_output(False)
        output += "</table>"
        print("[INFO] Printed table " + name)
        return output
    except psycopg2.Error as e:
        content = "Error! Is the URL valid?"
        content += "<br>" + e.pgerror
        conn.rollback()
        print("[INFO] Failed to print table: " + name)
        return content, 400


@app.route("/api/v1/<name>/insert/<values>")
def insert(name, values):
    name = name.replace("-", "_")
    values = ", ".join(values.split(";"))
    try:
        cur.execute("INSERT INTO " + name + " VALUES (" + values + ");")
        conn.commit()
        print("[INFO] Inserted \"" + values + "\" into the table " + name)
        return "Ok! Inserted \"" + values + "\" into the table \"" + name + "\"."
    except psycopg2.Error as e:
        content = "Error! Is the URL valid?"
        content += "<br>" + e.pgerror
        conn.rollback()
        print("[INFO] Failed to insert \"" + values + "\" into table " + name)
        return content, 400

@app.route("/api/v1/<name>/create/<params>")
def create(name, params):
    name = name.replace("-", "_")
    param_list = []
    for param in params.split(";"):
        param_list.append(param + " varchar")
    params = ", ".join(param_list)
    try:
        cur.execute("DROP TABLE IF EXISTS " + name + ";")
        cur.execute("CREATE TABLE " + name + " (" + params + ");")
        conn.commit()
        print("[INFO] Created table " + name)
        return "Ok! Created the table \"" + name + "\"."
    except psycopg2.Error as e:
        content = "Error! Is the URL valid? (Params: " + params + ")"
        content += "<br>" + e.pgerror
        conn.rollback()
        print("[INFO] Failed when creating table " + name)
        return content, 400


## Server ##
server = WSGIServer(("", PORT), app)
server.serve_forever()
