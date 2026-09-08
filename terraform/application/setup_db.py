import sqlite3
conn = sqlite3.connect('users.db')
c = conn.cursor()
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password TEXT NOT NULL
)
''')
c.execute("INSERT INTO users (username, password) VALUES (?, ?)", ('testuser', 'Password123'))
conn.commit()
conn.close()
print('Done')