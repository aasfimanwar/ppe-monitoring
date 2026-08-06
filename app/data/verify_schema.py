import sqlite3

conn = sqlite3.connect('violations.db')
conn.executescript(open('schema.sql').read())
conn.commit()

tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
print(tables)

conn.close()