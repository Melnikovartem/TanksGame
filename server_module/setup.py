import random
import string
import sqlite3

def getKey(N):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(N))

conn = sqlite3.connect('../tanks.sqlite')
c = conn.cursor()
#c.execute("DELETE FROM players")
names = ['test' ]
for name in names:
    key = getKey(8)
    print(name," - ", key)
    c.execute("INSERT INTO players (name, key, state) VALUES (?,?,?)", [name, key, "waiting"])

conn.commit();
