import sqlite3
import random 
conn = sqlite3.connect('tanks.sqlite')
c = conn.cursor()
for i in range(9):
    name = "random" + str(i)
    key = ''
    for i in range(30):
        key = key + str(random.randint(0, 10))
    password = "test"
    state = "ready"
    c.execute("SELECT code FROM players WHERE name='random'")
    code = c.fetchone()[0]
    c.execute("INSERT INTO players (name, key, password, state, code) VALUES (?, ?, ?, ?, ?)", [name, key, password, state, code] )
    
    
conn.commit()
conn.close()
