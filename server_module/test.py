import sqlite3

conn = sqlite3.connect('players.sqlite')
c = conn.cursor()
c.execute('INSERT Name')
