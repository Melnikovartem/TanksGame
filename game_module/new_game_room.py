from multiprocessing import Process
import game
from time import sleep
g = 1

def make_new_room():
    global g
    doit = Process(target = new_p, args=(g, ))
    doit.start()
    g+=1
    return doit

def new_p(n):
    while 1:
        print("new_battle in room", n )
        s = game.new_battle(n)
        sleep(5)

if __name__  == "__main__":
    room1 = make_new_room()
    room2 = make_new_room()
    room3 = make_new_room()
    room4 = make_new_room()
    room1.join()
    room2.join()
    room3.join()
    room4.join()

