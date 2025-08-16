import sqlite3
from werkzeug.security import generate_password_hash

from ppweb.main import connection

connection = sqlite3.connect('ba2 (4).db', check_same_thread=False)
cursor = connection.cursor()





cursor.execute('INSERT INTO user VALUES (?,?,?,?,?)',
        (1, "Rocket", generate_password_hash("Op01op01", method="pbkdf2:sha256"),'python1@gmail.com',"24.04.25"))



cursor.execute('INSERT INTO user VALUES (?,?,?,?,?)',
        (2, "Javvi", generate_password_hash("Op02op02", method="pbkdf2:sha256"),"python2@gmail.com","25.04.25"))
cursor.execute('INSERT INTO user VALUES (?,?,?,?,?)',
        (3, "Watermelon", generate_password_hash("Op03op03", method="pbkdf2:sha256"),"python3@gmail.com","26.04.25"))
cursor.execute('INSERT INTO user VALUES (?,?,?,?,?)',
        (4, "Kostya", generate_password_hash("Op04op04", method="pbkdf2:sha256"),"python4@gmail.com","27.04.25"))
cursor.execute('INSERT INTO user VALUES (?,?,?,?,?)',
        (5, "imac34573", generate_password_hash("Op05op05", method="pbkdf2:sha256"),"python5@gmail.com","28.04.25"))





connection.commit()
connection.close()
