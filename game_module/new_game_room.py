from multiprocessing import Process
import game
import sqlite3
import config
from time import sleep
g = 1

def make_new_room(name, map_):
    key = ''
    for i in range(10):
        key = key + str(random.randint(0, 10))
    conn = sqlite3.connect(config.way + 'tanks.sqlite')
    c = conn.cursor()
    c.execute("INSERT INTO room (name, key, status, map) VALUES (?, ?, ?, ?)", [name, key, "ready", map_])
    conn.commit()
    doit = Process(target = new_p, args=(key, map_ )
    doit.start()
    return doit

def new_p(n, map_):
    while 1:
        s = game.new_battle(n, map_)
        sleep(5)

if __name__  == "__main__":
    room1 = make_new_room("")
    room2 = make_new_room("")
    room3 = make_new_room("")
    room4 = make_new_room("")
    room1.join()
    room2.join()
    room3.join()
    room4.join()

