import sqlite3
conn = sqlite3.connect("authenticate.sqlite")
cur = conn.cursor()
sql_query = """Create table authorize(
     username text PRIMARY KEY,
     password text NOT NULL
     )"""
cur.execute(sql_query)  