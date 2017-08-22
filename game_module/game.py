import sqlite3
import random
import time
import sys
import os
import importlib as imp
import config
from random import shuffle

## Before was a great system of print information by the game i will hide it by ##

def new_battle(room_number):
    room = str(room_number)
    #работа с m файлами
    folder = config.way + 'game_module/bots'
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path) and file_path.find(".m")!=-1:
                ##print(the_file)
                os.unlink(file_path)
        except Exception as e:
            print(e)

#    conn = sqlite3.connect(config.way + "/rooms/" + numer + '/tanks.sqlite')
    conn = sqlite3.connect(config.way + '/tanks.sqlite')
    c = conn.cursor()

    #get settings
    c.execute("SELECT * FROM settings")
    result = c.fetchall()
    settings = dict()
    for string in result:
        settings[string[1]] = string[2]
    #print(settings)
    #get bots
    #change to in game
    names = dict()
    c.execute("UPDATE players SET room = -1 WHERE room IS NULL")
    c.execute("SELECT key, name FROM players WHERE state = 'ready' AND room = -1")
    result = c.fetchall()
    shuffle(result)
    players = list()
    ##print("CURRENT PLAYERS:") 
    #6 random bots
    for string in result:
        ##print(string[0]+" - "+string[1])
        players.append(string[0])
        names[string[0]]=string[1]
    for player in players:
        c.execute("UPDATE players SET room = ? WHERE key = ?",[room, player])

    ##print("")
    ##print("")

    #clear current state
    c.execute("DELETE FROM statistics WHERE room = " + str(room))
    c.execute("DELETE FROM actions WHERE room = " + str(room))
    c.execute("DELETE FROM game WHERE room = " + str(room))
    c.execute("DELETE FROM coins  WHERE room = " + str(room))


    #make map
    #mainMap = [['.' for i in range(int(settings["height"]))] for j in range(int(settings["width"]))]
    #mainMap - map with all matrix of the game with positions of some suff
    with open(config.way + 'map.txt') as map_file:
        map_data = map_file.read()
        mainMap = map_data.split('\n')
        for i in range(len(mainMap)):
            mainMap[i] = mainMap[i].split(' ')
        settings["height"] = len(mainMap[0])
        settings["width"] = len(mainMap)

        ##print("size: {0} x {1}".format(settings["width"], settings["height"]))
    # 2-nd map aff all matrix of the game (with health) 0-wal, some-player, 1-coin or wall
    healthMap = [[0 for i in range(int(settings["height"]))] for j in range(int(settings["width"]))]
    for i in range(len(mainMap)):
        for j in range(len(mainMap[0])):
            if mainMap[i][j] in ('#', '@'):
                healthMap[i][j] = -1

    history = {}
    #???? map for each parametr
    coords = dict()
    health = dict()
    errors = dict()
    coins = dict()
    crashes = dict()
    lifeplayers = len(players)
    kills = dict()
    ticks = 0
    steps = dict()
    shots = dict()
    banlist = list()


    #Set deafalt parametrs for players
    for player in players:
        coords[player] = dict()
        steps[player] = 0
        errors[player] = 0
        crashes[player] = 0
        shots[player] = 0
        health[player] = int(settings["max_health"])
        kills[player] = 0
        coins[player] = 0
        history[player]=[]
        x = random.randint(0, int(settings["width"])-1)
        y = random.randint(0, int(settings["height"])-1)
        while mainMap[x][y]!='.':
            x = random.randint(0, int(settings["width"])-1)
            y = random.randint(0, int(settings["height"])-1)
        mainMap[x][y] = player
        healthMap[x][y] = int(settings["max_health"])
        coords[player]["x"]=x
        coords[player]["y"] =y
        c.execute("INSERT INTO statistics (key, room) VALUES (?,?)", [player, room])
        c.execute("INSERT INTO game (key,x,y,life,room) VALUES (?,?,?,?,?)", [player,x,y, str(health[player]), room])
    c.execute("UPDATE settings SET value = ? WHERE param = ?", ["running", "game_state"])

    #coins
    for i in range(10):
        x = random.randint(0, int(settings["width"]) - 1)
        y = random.randint(0, int(settings["height"]) - 1)
        while mainMap[x][y]!='.':
            x = random.randint(0, int(settings["width"])-1)
            y = random.randint(0, int(settings["height"])-1)
        mainMap[x][y] = '@'
        healthMap[x][y] = 1
        c.execute("INSERT INTO coins (x,y,room) VALUES (?,?,?)", [x,y,room])
    conn.commit()
    
    print("NEW GAME IN ROOM: " + room)
    print("PLAYERS: ", players)
    print("SETTINGS: ", settings)
    # game started
    sys.path.append(os.path.dirname(__file__) + "/bots")
    while True:
        if ticks%10 == 0:
            print("current tick:"+str(ticks)+" in room:" + room)
        if (ticks>int(settings['stop_ticks']) or lifeplayers<int(settings['game_stop'])):
            break
        #chices - dict with choices of all players
        choices = dict()
        ticks += 1

        historyMap = [[0 for i in range(int(settings["height"]))] for j in range(int(settings["width"]))]

        for player in players:
            historyMap[coords[player]["x"]][coords[player]["y"]] = {"life": health[player], "history": history[player]}

        for i in range(len(mainMap)):
            for j in range(len(mainMap[0])):
                if mainMap[i][j] == '#':
                    historyMap[i][j] = -1
                if mainMap[i][j] == '@':
                    historyMap[i][j] = 1


        for player in players:
            choices[player] = ""

            if player in banlist:
                continue
            try:
                c.execute("SELECT code FROM players WHERE key = ?", [player])
                code = c.fetchone()
                output_file = open("./bots/" + player + ".py", 'wb')
                output_file.write(code[0])
                output_file.close()
                module = __import__(player, fromlist=["make_choice"])
                module = imp.reload(module)
                makeChoice = getattr(module, "make_choice")
##                print("Now running:" +player+" ("+names[player]+")")
                if len(historyMap)==1:
                    choices[player] = makeChoice(int(coords[player]["x"]), int(coords[player]["y"]), historyMap); #тут выбор
                else:
                    choices[player] = makeChoice(int(coords[player]["x"]), int(coords[player]["y"]), historyMap);  # тут выбор

            except Exception as e:
##                print(player+" ("+names[player]+") has crashed :( :"+str(e))
                history[player].append("crash")
                choices[player] = "crash"
                crashes[player]+=1
                c.execute("INSERT INTO actions (key, value, room) VALUES (?, ?, ?)", [player, choices[player], room])
                c.execute(
                    "UPDATE statistics SET crashes = " + str(crashes[player]) + " WHERE key = ?",
                    [player])
                c.execute(
                    "UPDATE statistics SET lastCrash = ? WHERE key = ?",
                    [str(e), player])
        conn.commit()

        #print(historyMap)
        #Analize what each user does
        for player in players:
            x_now = coords[player]["x"]
            y_now = coords[player]["y"]

            if choices[player]=="go_up":
                steps[player]+=1
                if int(y_now) > 0 and mainMap[x_now][y_now - 1] in ('.', '@'):
                    if mainMap[x_now][y_now - 1] == '@':
                        coins[player] += 1
                    mainMap[x_now][y_now] = '.'
                    healthMap[x_now][y_now] = 0
                    coords[player]["y"] -= 1


            if choices[player] == "go_down":
                steps[player]+=1
                if int(y_now) < int(settings["height"]) - 1 and mainMap[x_now][y_now + 1] in ('.', '@'):
                    if mainMap[x_now][y_now + 1] == '@':
                        coins[player] += 1
                    mainMap[x_now][y_now] = '.'
                    healthMap[x_now][y_now] = 0
                    coords[player]["y"] += 1


            if choices[player] == "go_left":
                steps[player]+=1
                if int(x_now) > 0 and mainMap[x_now - 1][y_now] in ('.', '@'):
                    if mainMap[x_now - 1][y_now] == '@':
                        coins[player] += 1
                    mainMap[x_now][y_now] = '.'
                    healthMap[x_now][y_now] = 0
                    coords[player]["x"] -= 1


            if choices[player] == "go_right":
                steps[player] += 1
                if int(x_now) < int(settings["height"]) - 1 and mainMap[x_now + 1][y_now] in ('.', '@'):
                    if mainMap[x_now + 1][y_now] == '@':
                        coins[player] += 1
                    mainMap[x_now][y_now] = '.'
                    healthMap[x_now][y_now] = 0
                    coords[player]["x"] -= 1
                    
            #make for each movement    
            if choices[player][:3] == "go_":
                    y_now = coords[player]["y"]
                    x_now = coords[player]["x"]
                    mainMap[x_now][y_now] = player
                    healthMap[x_now][y_now] = health[player]
                    c.execute("UPDATE game SET y = " + str(coords[player]["y"]) + " WHERE key = ?", [player])
                    c.execute(
                        "DELETE FROM coins WHERE x = ? AND y = ? AND room = ?",
                        [coords[player]["x"], coords[player]["y"], room])
                


            if choices[player]!="error":
                c.execute("INSERT INTO actions (key, value, room) VALUES (?, ?, ?)", [player, choices[player], room])
                history[player].append(choices[player])
            else:
##                print(player+" ("+names[player]+") sent incorrect command: "+str(choices[player]))
                errors[player] += 1
                history[player].append("error")
            #db record
        for player in players:
            if player in banlist:
                continue
            px = coords[player]["x"]
            py = coords[player]["y"]
            if choices[player] == "fire_up":
                shots[player] += 1
                for y in range(py-1, -1, -1):
                    if mainMap[px][y] == '#':
                        break;
                    if mainMap[px][y] not in ('.', '@'):
                        hit_player = mainMap[px][y]

                        health[hit_player]-=1
                        healthMap[px][y] -= 1

                        kills[player]+=1

##                      print(player + " (" + str(health[player]) + ") hits " + str(hit_player) + " (" + str(
##                              health[hit_player]) + ")" + " [" + str(px) + " ," + str(py) + "] -> [" + str(px) + ", " + str(
##                              y) + "] " + choices[player])
                        c.execute("UPDATE game SET life = " + str(health[hit_player]) + " WHERE key = ?", [hit_player])
                        break
            if choices[player] == "fire_down":
                shots[player] += 1
                for y in range(py+1, int(settings["height"])):
                    if mainMap[px][y] == '#':
                        break
                    if mainMap[px][y] not in ('.', '@'):
                        hit_player = mainMap[px][y]

                        health[hit_player] -= 1
                        healthMap[px][y] -= 1

                        kills[player] += 1

##                        print(player + " ("+str(health[player])+") hits " + str(hit_player) + " (" + str(
##                              health[hit_player]) + ")" + " [" + str(px) + " ," + str(py) + "] -> ["+str(px)+", "+str(y)+"] " + choices[player])



                        c.execute("UPDATE game SET life = " + str(health[hit_player]) + " WHERE key = ?", [hit_player])
                        break
            if choices[player] == "fire_left":
                shots[player] += 1
                for x in range(px-1, -1, -1):
                    if mainMap[x][py] == '#':
                        break
                    if mainMap[x][py] not in ('.', '@'):
                        hit_player = mainMap[x][py]

                        health[hit_player] -= 1
                        healthMap[x][py] -= 1

                        kills[player] += 1

##                        print(player + " (" + str(health[player]) + ") hits " + str(hit_player) + " (" + str(
##                            health[hit_player]) + ")" + " [" + str(px) + " ," + str(py) + "] -> [" + str(x) + ", " + str(
##                            py) + "] " + choices[player])



                        c.execute("UPDATE game SET life = " + str(health[hit_player]) + " WHERE key = ?", [hit_player])
                        break
            if choices[player] == "fire_right":
                shots[player] += 1
                for x in range(px+1, int(settings["width"])):
                    if mainMap[x][py] == '#':
                        break
                    if mainMap[x][py] not in ('.', '@'):
                        hit_player = mainMap[x][py]

                        health[hit_player] -= 1
                        healthMap[x][py] -= 1

                        kills[player] += 1

##                        print(player + " (" + str(health[player]) + ") hits " + str(hit_player) + " (" + str(
##                            health[hit_player]) + ")" + " [" + str(px) + " ," + str(py) + "] -> [" + str(x) + ", " + str(
##                            py) + "] " + choices[player])




                        c.execute("UPDATE game SET life = " + str(health[hit_player]) + " WHERE key = ?", [hit_player])
                        break
            
            if choices[player][:5] == "fire_":
                c.execute(
                    "UPDATE statistics SET kills = " + str(kills[player]) + " WHERE key = ?",
                    [player])
                #print(player + " sent "+choices[player])

                # db record

            if int(health[player])>0:
                c.execute(
                    "UPDATE statistics SET lifetime = " + str(ticks) + " WHERE key = ?",
                    [player])
                c.execute(
                    "UPDATE statistics SET shots = " + str(shots[player]) + " WHERE key = ?",
                    [player])
                c.execute(
                    "UPDATE statistics SET coins = " + str(coins[player]) + " WHERE key = ?",
                    [player])
                c.execute(
                    "UPDATE statistics SET steps = " + str(steps[player]) + " WHERE key = ?",
                    [player])
                c.execute(
                    "UPDATE statistics SET errors = " + str(errors[player]) + " WHERE key = ?",
                    [player])


            conn.commit()

        remove_list = []
        for hit_player in players:
##            print(hit_player+" "+str(health[hit_player])+" - check")
            if health[hit_player] <= 0:
                mainMap[coords[hit_player]['x']][coords[hit_player]['y']] = '.'
                healthMap[coords[hit_player]['x']][coords[hit_player]['y']] = 0
                health[hit_player] = 0
                lifeplayers -= 1
##                print(hit_player + " is dead!")
                remove_list.append(hit_player)
        for p in remove_list:
##            print(p + " - try to remove")
##            print(players)
            players.remove(p)
##            print(players)
        conn.commit()
        time.sleep(1.2)

    c.execute("UPDATE settings SET value = ? WHERE param = ?", ["stop", "game_state"])
    c.execute("UPDATE players SET room = -1 WHERE room = " + room)
    conn.commit()
    return settings
if __name__ == "__main__":
    print("clear-clear all players hist rooms \nelse-start a game in test(0) room")
    x = input()
    if x == "clear":
        conn = sqlite3.connect(config.way + '/tanks.sqlite')
        c = conn.cursor() 
        c.execute("UPDATE players SET room = -1")
        conn.commit()
        conn.close()
    else:
        while 1:
            s = new_battle(0)
            if s['mode']!='sandbox':
                break
            time.sleep(5)










