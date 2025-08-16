import sqlite3

from ppweb.main import connection

connection = sqlite3.connect('ba2 (4).db')
cursor = connection.cursor()

cursor.execute('''
    CREATE TABLE like (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL );
    ''')

connection.commit()
connection.close()