from multiprocessing import Process
from game import new_battle
from time import sleep
g = 0

def make_new_room():
    global g
    doit = Process(target = new_p, args=(g, ))
    doit.start()
    g+=1

def new_p(n):
    while 1:
        print("new_battle in room", n )
        s = new_battle(n)
        time.sleep(5)

if __name__  == "__main__":
    room1 = make_new_room()
    print("join:")
    room2 = make_new_room()
    room3 = make_new_room()
    room4 = make_new_room()
    
