Pohjis IoT Server
=================
This is a small server that provides an API for entering data into a database for viewing and analysing. Intended for usage in the IoT course at Pohjois-Tapiolan lukio. Currently under development.

API
---

| URL                              | Description                                            |
|----------------------------------|--------------------------------------------------------|
| `/api/v1/<name>/create/<types>`  | Creates a new table `<name>` with columns of `<types>` |
|                                  | Eg. /foo/create/int;real;real                          |
| `/api/v1/<name>/insert/<values>` | Inserts `<values>` into the table `<name>`             |
|                                  | Eg. /foo/insert/42;1.41;3.14                           |
| `/api/v1/<name>/print`           | Prints out the content of the table `<name>` as HTML   |

Development setup
-----------------
Prerequisites:
- Python 3
- PostgreSQL

Python prerequisites (installable with pip):
- flask
- psycopg2
- gevent

1. Check that you have installed all the prerequisites.
2. Create PostgreSQL database named "pohjisiot" owned by the postgres user. If you want a different naming configuration, change `DB_NAME` and `DB_USER` at the top of `server.py`.
3. Run `server.py`. The server will serve at port 5000 by default (can be changed at the top of `server.py`, by changing the `PORT` variable), so you can call the API by sending requests to [http://localhost:5000/api/v1/command/to/run](http://localhost:5000/api/v1/command/to/run).
