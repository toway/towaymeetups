import sqlite3

db = sqlite3.connect('./mba.db')
#http://www.pythoncentral.io/introduction-to-sqlite-in-python/
cursor = db.cursor()
#cursor.execute('''
#    CREATE TABLE users(id INTEGER PRIMARY KEY, name TEXT,
#                       phone TEXT, email TEXT unique, password TEXT)
#''')
cursor.execute('''DROP TABLE students''')
cursor.execute('''DROP TABLE mba_users''')
db.commit()

db.close()
