#downloading and showing game in this file

import config
import json 
import sqlite3
import tornado.web
from itertools import product


def get_GameHandler(self):
    room = "0"
    try:
        room = self.get_argument("room")
    except:
        pass
    style = "roctbb"
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
    try:
        c.execute("SELECT style FROM cookies WHERE cookie = ?", [self.get_cookie("TanksGame")])
        style = c.fetchone()[0]
    except:
        pass
    conn.close()
    self.render(config.way + "server_module/html/game.html", width=settings["width"], height=settings["height"], style = style, url ="/state?room=" + room )
        
def get_StateHandler(self):
    room = "0"
    try:
        room = self.get_argument("room")
    except:
        pass
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
        
    c.execute("SELECT * FROM players WHERE room = ?", [room])
    result = c.fetchall()
    names=dict()
    stat = []
    for record_main in result:
        names[record_main[2]] = record_main[1]
        c.execute("SELECT * FROM game WHERE key = ?", [record_main[2]])
        record = c.fetchone()
        name = names[record[1]]
        x = record[2]
        y = record[3]
        life = record[4]
        name = names[record[1]]
        mainMap[x][y] = {'name': name, 'life': life, 'hit': 0}
    for record_main in result:
        c.execute("SELECT * FROM game WHERE key = ?", [record_main[2]])
        record = c.fetchone()
        name = names[record[1]]
        x = int(record[2])
        y = int(record[3])
        c.execute("SELECT value FROM actions WHERE key = ? AND room = ? ORDER BY id", [record[1], room])
        try:
            action = c.fetchone()[0]
        except:
            action = "None"
        #draw an error
        if action[:5] == "fire_": 
            direction = action[5:]
            list_x = [x]
            list_y = [y]
            type_arr = "."
            if direction == "up":
                list_y = range(y - 1, -1 , -1)
                type_arr = '&uarr;'
            elif direction == "down":
                list_y = range(y + 1, settings["height"], 1)
                type_arr = '&darr;'
            elif direction == "left":
                list_x = range(x - 1, -1 , -1)
                type_arr = '&larr;'
            elif direction == "right":                   
                list_x = range(x + 1, settings["width"], 1)
                type_arr = '&rarr;'
            for x_change, y_change in product(list_x, list_y):
                if not mainMap[x_change][y_change] in ('.', '&uarr;', '&darr;', '&larr;', '&rarr;', '#', '@'):
                    mainMap[x_change][y_change]['hit']=1
                    break
                elif mainMap[x_change][y_change] == '#' or mainMap[x_change][y_change] == '@':
                    break
                else:
                    mainMap[x_change][y_change] = type_arr
    
    for record in stat:
        if record[4]<=0:
            c.execute("DELETE FROM game WHERE id = ?", [record[0]])
    c.execute("SELECT * FROM coins WHERE room = ?", [room])
    result = c.fetchall()
    for record in result:
        x = record[0]
        y = record[1]
        mainMap[x][y]='@'
    conn.commit()
    self.write(json.dumps(mainMap))

def get_StatsHandler(self):
    room = "0"
    try:
        room = self.get_argument("room")
    except:
        pass
    conn = sqlite3.connect(config.way + 'tanks.sqlite')
    gamestate=[]
    c = conn.cursor()
    c.execute("SELECT * FROM players WHERE room = ?", [room])
    result = c.fetchall()
    names = dict()
    stat = []
    for record_main in result:
        names[record_main[2]] = record_main[1]
        c.execute("SELECT * FROM statistics WHERE key = ?", [record_main[2]])
        record = c.fetchone()
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
        c.execute("SELECT life FROM game WHERE key = ? AND room = ?", [record[1], room])
        l = c.fetchall()
        if len(l)>0 :
            life = l[0][0]
        gamestate.append({"name": name,"hp":life, "kills": kills, "lifetime": lifetime, "score": points, "shots": shots, "steps": steps, "quality": quality, "quality_class": quality_class, "lastCrash": lastCrash, "coins": coins})
    c.execute("SELECT name FROM rooms WHERE key = ?", [room])
    name_room = c.fetchone()[0]
    conn.close()
    self.render(config.way + "server_module/html/stats.html", gamestate = sorted(gamestate, key=lambda k: -k['score']), name_room = name_room)
            
def get_GameListHandler(self):
    conn = sqlite3.connect(config.way + 'tanks.sqlite')
    c = conn.cursor()
    c.execute("SELECT * FROM rooms ORDER BY id" )
    results = c.fetchall()
    all_ = []
    # i - room
    for i in results:
        players = []
        try:
            for j in i[5].split("&"):
                if j != "":
                    c.execute("SELECT name FROM players WHERE key = ?", [j])
                    name = c.fetchone()
                    players.append(name[0])
        except:
            pass
        all_.append({"name":i[1], "game":"/game?room="+str(i[2]), "stats":"/stats?room="+str(i[2]), "status":i[3], "tick": i[4], "players":" | ".join(players), "map":i[6]
            })
    conn.close()
    self.render(config.way + "server_module/html/gamelist.html", rooms = all_)
    
def get_LeaderBoardHandler(self):
    conn = sqlite3.connect(config.way + 'tanks.sqlite')
    c = conn.cursor()
    c.execute("SELECT * FROM players ORDER BY id" )
    results = c.fetchall()
    all_ = []
    scores = []
    # i - player
    for i in results:
        if i[8] != 0:
            score = round(int(i[7])/int(i[8]), 2)
        else:
            score = 0
        scores.append([score, i[1]])
    scores.sort()
    for j in scores[::-1]:    
        all_.append({"player": j[1], "score":j[0]})
    self.render(config.way + "server_module/html/leaderboard.html", board = all_)
