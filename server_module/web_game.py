#downloading and showing game in this file

import config
import json 
import sqlite3
import tornado.web

def get_GameHandler(self):
    conn = sqlite3.connect(config.way + 'tanks.sqlite')
    c = conn.cursor()
    c.execute("SELECT * FROM settings")
    result = c.fetchall()
    settings = dict()
    for string in result:
        settings[string[1]] = string[2]
    with open(config.way + 'map.txt') as map_file:
        map_data = map_file.read()
        mainMap = map_data.split('\n')
        for i in range(len(mainMap)):
            mainMap[i] = mainMap[i].split(' ')
        settings["height"] = len(mainMap[0])
        settings["width"] = len(mainMap)
    self.render(config.way + "server_module/html/game.html", width=settings["width"], height=settings["height"])
        
def get_StateHandler(self):
    conn = sqlite3.connect(config.way + 'tanks.sqlite')
    c = conn.cursor()
    c.execute("SELECT * FROM settings")
    result = c.fetchall()
    settings = dict()
    for string in result:
        settings[string[1]] = string[2]
    with open(config.way + 'map.txt') as map_file:
        map_data = map_file.read()
        mainMap = map_data.split('\n')
        for i in range(len(mainMap)):
            mainMap[i] = mainMap[i].split(' ')
        settings["height"] = len(mainMap[0])
        settings["width"] = len(mainMap)
        
    c.execute("SELECT * FROM players WHERE room = 0")
    result = c.fetchall()
    names=dict()
    for record in result:
        names[record[2]]=record[1]

    c.execute("SELECT * FROM game WHERE room = 0")
    result = c.fetchall()
    for record in result:
        x = record[2]
        y = record[3]
        life = record[4]
        name = names[record[1]]
        mainMap[x][y] = {'name': name, 'life': life, 'hit': 0}
    for record in result:
        x = record[2]
        y = record[3]
        c.execute("SELECT value FROM actions WHERE key = ? AND room = 0 ORDER BY id DESC LIMIT 1", [record[1]])
        action = c.fetchall()
        if len(action)<1:
            continue
        action=action[0]
        
        #draw an error
        if action[0][:5] == "fire_":
            shots[player] += 1
            direction = action[5:]
            step_x = -1
            step_y = -1
            list_x = [x]
            list_y = [y]
            type_arr = "."
            if direction == "up":
                list_y = range(y_now - 1, -1 , -1)
                type_arr = '&uarr;'
            elif direction == "down":
                list_x = range(x_now + 1, settings["height"], 1)
                type_arr = '&darr;'
            elif direction == "left":
                list_x = range(x_now - 1, -1 , -1)
                type_arr = '&larr;'
            elif direction == "right":                   
                list_x = range(x_now + 1, settings["width"], 1)
                type_arr = '&rarr;'
            for x_change, y_change in product(list_x, list_y):
                if mainMap[x][i] != '.' and mainMap[x][i] != '&uarr;' and mainMap[x][i] != '&darr;' and mainMap[x][i] != '&larr;' and mainMap[x][i] != '&rarr;' and mainMap[x][i] != '#' and mainMap[x][i] != '@':
                    mainMap[x][i]['hit']=1
                    break
                elif mainMap[x][i] == '#' or mainMap[x][i] == '@':
                    break
                else:
                    mainMap[x][i] = type_arr
                    
    for record in result:
        if record[4]<=0:
            c.execute("DELETE FROM game WHERE id = ? AND room = 0", [record[0]])
    c.execute("SELECT * FROM coins WHERE room = 0")
    result = c.fetchall()
    for record in result:
        x = record[0]
        y = record[1]
        mainMap[x][y]='@'
    conn.commit()
    self.write(json.dumps(mainMap))

def get_StatsHandler(self):
        conn = sqlite3.connect(config.way + 'tanks.sqlite')
        gamestate=[]
        c = conn.cursor()
        c.execute("SELECT * FROM players WHERE room = 0" )
        result = c.fetchall()
        names = dict()
        stat = []
        for record in result:
            names[record[2]] = record[1]
            c.execute("SELECT * FROM statistics WHERE key = " + record[2])
            stat.append(c.fetchall())
        for record_tuple in stat:
            record = record_tuple[0]
            name = names[record[1]]
            kills = record[2]
            lifetime = record[3]
            shots = record[5]
            steps = record[4]
            crashes = record[6]
            errors = record[7]
            lastCrash = record[8]
            coins = record[9]
            quality = "good"
            quality_class = "label-success"
            if (crashes>0):
                quality_class = "label-danger"
                quality = "crash"
            elif (errors>0):
                quality = "errors"
                quality_class = "label-warning"
            points = coins*50 + kills*20+lifetime-crashes*5
            life = 0
            c.execute("SELECT life FROM game WHERE key = ? AND room = 0", [record[1]])
            l = c.fetchall()
            if len(l)>0 :
                life = l[0][0]
            gamestate.append({"name": name,"hp":life, "kills": kills, "lifetime": lifetime, "score": points, "shots": shots, "steps": steps, "quality": quality, "quality_class": quality_class, "lastCrash": lastCrash, "coins": coins})
            self.render(config.way + "server_module/html/stats.html", gamestate = sorted(gamestate, key=lambda k: -k['score']))
            
            
            
