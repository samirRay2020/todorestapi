import sqlite3
conn = sqlite3.connect("todo.sqlite")
cur = conn.cursor()
sql_query = """Create table todos(
     toId integer PRIMARY KEY,
     description text NOT NULL,
     due_by_date text NOT NULL,
     status text NOT NULL)"""
cur.execute(sql_query)  