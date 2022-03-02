import psycopg2 as sql

conn = sql.connect(
    host='localhost',
    database='iuvs',
    user='kyle',
    password='iuvs'
)

