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
    for player in players[:6]:
        c.execute("UPDATE players SET room = ? WHERE key = ?",[room, player])

    ##print("")
    ##print("")

    #clear current state
    for player in players:
        c.execute("DELETE FROM statistics WHERE key = " + player)
    c.execute("DELETE FROM actions WHERE room = " + room)
    c.execute("DELETE FROM game WHERE room = " + room)
    c.execute("DELETE FROM coins WHERE room = " + room)


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
        c.execute("INSERT INTO statistics (key) VALUES (?)", [player])
        c.execute("INSERT INTO game (key,x,y,life,room) VALUES (?,?,?,?,?)", [player,x,y, str(health[player]), room])
    c.execute("UPDATE settings SET value = ? WHERE param = ?", ["running", "game_state"])

    #generating 10 coins
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
        #choices - dict with choices of all players
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
            
            try:
                c.execute("SELECT code FROM players WHERE key = ?", [player])
                code = c.fetchone()
                output_file = open("./bots/" + player + ".py", 'wb')
                output_file.write(code[0])
                output_file.close()
                module = imp.import_module("bots." + player)
                makeChoice = getattr(module, "make_choice")
                if len(historyMap)==1:
                    choices[player] = makeChoice(int(coords[player]["x"]), int(coords[player]["y"]), historyMap); #тут выбор
                else:
                    choices[player] = makeChoice(int(coords[player]["x"]), int(coords[player]["y"]), historyMap);  # тут выбор
            except Exception as e:
                choices[player] = "crash"
                crashes[player]+=1
                c.execute("UPDATE statistics SET crashes = ? WHERE key = ?",[crashes[player], player])
                c.execute("UPDATE statistics SET lastCrash = ? WHERE key = ?", [str(e), player])
        #Analize what each user does
        for player in players:
            x_now = coords[player]["x"]
            y_now = coords[player]["y"]
            
            #bot didn't crash but the command was bad
            #should change it later
            if choices[player] not in ("go_up","fire_up","go_down","fire_down","go_right","fire_right","go_left","fire_left","crash"):
                errors[player] += 1
                choices[player] = "error"
            
            history[player].append(choices[player])
            c.execute("INSERT INTO actions (key, value, room) VALUES (?, ?, ?)", [player, choices[player], room])
            #not error
            if choices[player] in ("error", "crash"):
                pass
            #We can say that player wants to go somewere        
            elif choices[player][:3] == "go_":
                steps[player] += 1
                y_new, x_new = y_now, x_now
                direction = choices[player][3:]
                if direction == "up":
                    y_new -= 1
                elif direction == "down":
                    y_new += 1
                elif direction == "left":
                    x_new -= 1
                elif direction == "right":
                    x_new += 1
                # weather the movement happens
                if x_new >= 0 and x_new < settings["width"] - 1 and y_new >= 0 and y_new < settings["height"] and mainMap[x_new][y_new] in ('.', '@'):
                    if mainMap[x_new][y_new] == "@":
                        coins[player] += 1
                    c.execute("DELETE FROM coins WHERE x = ? AND y = ? AND room = ?", [x_new, y_new, room])
                    mainMap[x_now][y_now] = "."
                    mainMap[x_new][y_new] = player
                    healthMap[x_now][y_now] = 0
                    healthMap[x_new][y_new] = health[player]
                    coords[player]["x"], coords[player]["y"] = x_new, y_new
                    c.execute("UPDATE game SET x = ? and y = ? WHERE key = ?", [x_new, y_new, player])
            #player wants to fire
            elif choices[player][:5] == "fire_":
                shots[player] += 1
                direction = choices[player][5:]
                step_x = -1
                step_y = -1
                to_x = x_now
                to_y = y_now
                if direction == "up":
                   to_y = -1
                elif direction == "down":
                   to_y = settings["height"]
                   step_y = 1
                elif direction == "left":
                   to_x = -1
                elif direction == "right":                   
                   to_x = settings["width"]
                   step_x = 1
                for x_change in range(x_now+1, to_x , step_x):
                    for y_change in range(y_now+1, to_y , step_y):
                        if mainMap[x_change][y_change] == '#':
                            break
                        elif mainMap[x_change][y_change] not in ('.', '@'):
                            hit_player = mainMap[x_change][y_change]
                            health[hit_player] -= 1
                            healthMap[x_change][y_change] -= 1
                            kills[player] += 1
                            c.execute("UPDATE game SET life = ? WHERE key = ?", [health[hit_player], hit_player])
                            c.execute("UPDATE statistics SET kills = ?  WHERE key = ?", [kills[player], player])
                            break
            #all comands were checked

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

        remove_list = []
        for hit_player in players:
            if health[hit_player] <= 0:
                mainMap[coords[hit_player]['x']][coords[hit_player]['y']] = '.'
                healthMap[coords[hit_player]['x']][coords[hit_player]['y']] = 0
                health[hit_player] = 0
                lifeplayers -= 1
                remove_list.append(hit_player)
        for p in remove_list:
            players.remove(p)
        #db record
        conn.commit()
        #tick ends
        time.sleep(1.2)
    #after game
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










