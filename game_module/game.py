#old
import random
import time
import os
#new
import sqlite3
import sys
import importlib as imp
from config import way
from random import shuffle, randint
from itertools import product
from time import sleep
## Before was a great system of print information by the game i will hide it by ##

def new_battle(room_number, map_):
    room = str(room_number)
    
    #работа с m файлами
    folder = config.way + 'game_module/bots'
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path) and file_path.find(".m")!=-1:
                os.unlink(file_path)
        except Exception as e:
            pass

#    conn = sqlite3.connect(config.way + "/rooms/" + numer + '/tanks.sqlite')
    conn = sqlite3.connect(config.way + '/tanks.sqlite')
    c = conn.cursor()

    #get settings
    c.execute("SELECT * FROM settings")
    result = c.fetchall()
    settings = dict()
    for string in result:
        settings[string[1]] = string[2]
    #get bots
    #change to in game
    names = dict()
    c.execute("SELECT key, name FROM players WHERE state = 'ready' AND room = -1")
    result = c.fetchall()
    shuffle(result)
    players_not = list() 
    #6 random bots
    for string in result:
        players_not.append(string[0])
        names[string[0]]=string[1]
    players = []
    for player in players_not[:6]:
        c.execute("UPDATE players SET room = ? WHERE key = ?",[room, player])
        players.append(player)


    #clear current state
    c.execute("DELETE FROM statistics WHERE room = ?",  [room] )
    c.execute("DELETE FROM actions WHERE room = ?",  [room] )
    c.execute("DELETE FROM game WHERE room = ?",  [room] )
    c.execute("DELETE FROM coins WHERE room = ?",  [room] )


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
        c.execute("INSERT INTO statistics (key, room) VALUES (?, ?)", [player, room])
        c.execute("INSERT INTO game (key,x,y,life,room) VALUES (?,?,?,?,?)", [player,x,y, str(health[player]), room])

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
    c.execute("UPDATE rooms SET players=? WHERE key = ?", ["&".join(players), room])
    c.execute("UPDATE rooms SET status=? WHERE key = ?", ["game", room])
    conn.commit()
    
    print("NEW GAME IN ROOM: " + room, str(len(players)) + "players")
    
    
    
    
    
    
    
    
    
    
    # game started
    sys.path.append(os.path.dirname(__file__) + "/bots")
    
    while True:
        if (ticks>int(settings['stop_ticks']) or lifeplayers<int(settings['game_stop'])):
            break
        #choices - dict with choices of all players
        choices = dict()
        ticks += 1
        c.execute("UPDATE rooms SET tick=? WHERE key = ?", [ticks, room])


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
                output_file = open(config.way + "game_module/bots/" + player + ".py", 'wb')
                output_file.write(code[0])
                output_file.close()
                module = imp.import_module("bots." + player)
                makeChoice = getattr(module, "make_choice")
                choices[player] = makeChoice(int(coords[player]["x"]), int(coords[player]["y"]), historyMap) # тут выбор
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
                if x_new >= 0 and x_new < settings["width"] - 1 and y_new >= 0 and y_new < settings["height"] and mainMap[x_new][y_new] in ('.', '@') and mainMap[x_new][y_new] in (".", "@"):
                    if mainMap[x_new][y_new] == "@":
                        coins[player] += 1
                        c.execute("DELETE FROM coins WHERE x = ? AND y = ? AND room = ?", [x_new, y_new, room])
                    mainMap[x_now][y_now] = "."
                    mainMap[x_new][y_new] = player
                    healthMap[x_now][y_now] = 0
                    healthMap[x_new][y_new] = health[player]
                    coords[player]["x"], coords[player]["y"] = x_new, y_new
                    c.execute("UPDATE game SET x = ? WHERE key = ?", [x_new, player])
                    c.execute("UPDATE game SET y = ? WHERE key = ?", [y_new, player])
            #player wants to fire
            elif choices[player][:5] == "fire_":
                shots[player] += 1
                direction = choices[player][5:]
                list_x = [x_now]
                list_y = [y_now]
                if direction == "up":
                    list_y = range(y_now - 1, -1 , -1)
                elif direction == "down":
                    list_x = range(x_now + 1, settings["height"], 1)
                elif direction == "left":
                    list_x = range(x_now - 1, -1 , -1)
                elif direction == "right":                   
                    list_x = range(x_now + 1, settings["width"], 1)
                for x_change, y_change in product(list_x, list_y):
                    if mainMap[x_change][y_change] == '#':
                        break
                    elif mainMap[x_change][y_change] not in ('.', '@') and (x_change != x_now or y_change != y_now):
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
        time.sleep(0.5)
    #after game
    for player in players:
        c.execute("SELECT sum_score, games FROM players WHERE key = ?", [player])
        result = c.fetchone()
        c.execute("SELECT lifetime FROM statistics WHERE key = ?", [player])
        points = coins[player]*50 + kills[player]*20+c.fetchone()[0]-crashes[player]*5
        sum_score = result[0] + points
        games = result[1] + 1
        c.execute("UPDATE players SET sum_score = ? WHERE key = ?", [sum_score, player])
        c.execute("UPDATE players SET games = ? WHERE key = ?", [games, player])
    c.execute("UPDATE rooms SET status=? WHERE key = ?", ["ready", room])
    c.execute("UPDATE rooms SET tick=? WHERE key = ?", [-1, room])
    c.execute("UPDATE settings SET value = ? WHERE param = ?", ["stop", "game_state"])
    c.execute("UPDATE players SET room = -1 WHERE room = " + room)
    conn.commit()
    return settings










































class MainGame:
    list_parameters = ["moves", "shots", "coins", "hits", "crash", "error"]
    list_commands = ["go_up","fire_up","go_down","fire_down","go_right",
                     "fire_right","go_left","fire_left","crash"]
    current_tick = 0 
    def __init__(self, room_id):
        self.room_id = str(room_id)
        self.new()
        
    def new(self):
        # connection with db
        self.conn = sqlite3.connect(way + 'game_module/data_game.sqlite')
        self.cursor = self.conn.cursor()
        #way + 'game_module/bots'
        #get settings
        self.cursor.execute("SELECT * FROM settings WHERE id = 1")
        settings = self.cursor.fetchone()
        self.max_ticks = settings[3]
        #generate map
        self.generate_field(settings[1])
        self.generate_players(settings[2])
        self.generate_coins(20)
        self.conn.commit()
        
    def generate_field(self, field_id):
        field_text = self.get_field_from_file(field_id)
        self.field = [[Land(i, j) for i in range(self.width)]for j in range(self.height)]
        for i in product(range(self.height), range(self.width)):
            if field_text[i[0]][i[1]] == "#":
                self.field[i[0]][i[1]] = Wall(i[0], i[1])
    
    def get_field_from_file(self, field_id):
        with open(way + field_id) as map_file:
            map_data = map_file.read()
            result = map_data.split('\n')
            for i in range(len(result)):
                result[i] = result[i].split(' ')
            self.height = len(result)
            self.width = len(result[0])
        return result
    
    def generate_players(self, health):
        self.players = []
        #get players
        result = self.cursor.execute("SELECT id FROM players WHERE room_id = -1").fetchall()
        shuffle(result)
        game_ids_list = [str(i) for i in range(10)]
        #6 random bots
        for player_settings in result:
            x = randint(0, self.width - 1)
            y = randint(0, self.height - 1)
            while not self.field[y][x].move:
                x = randint(0, self.width - 1)
                y = randint(0, self.height - 1)
            player = Player(x, y, health, game_ids_list[0])
            self.field[y][x] = player
            self.players.append(player)
            self.cursor.execute(
                "INSERT INTO player_status (id, InGame_id, last_action, health) VALUES (%s, %s, '%s', %s)" %
                    (player_settings[0], player.game_id, "some", health))
            self.cursor.execute("UPDATE players SET room_id = %s" % self.room_id )
            self.db_update_code(player)
            game_ids_list.pop(0)
            
    def generate_coins(self, numer):
        for iter_coin in range(numer):
            x = randint(0, self.width - 1)
            y = randint(0, self.height - 1)
            while not self.field[y][x].move:
                x = randint(0, self.width - 1)
                y = randint(0, self.height - 1)
            self.field[y][x] = Coin(x, y)
   
    
    def play(self):
        sys.path.append(os.path.dirname(__file__) + "/bots")
        while True:
            while self.current_tick < self.max_ticks and len(players) > 1:
                self.tick()
                sleep(0.5)
            self.close()
            self.new()
        
    def tick(self):
        self.current_tick += 1
        for player in self.players:
            player.work(self)
        self.save_history()
        self.db_update_game_status()
        self.conn.commit()
        
    def save_history(self):
        history_file = open(way+"/history/"+self.room_id, 'w')
        history_file.write(self.get_text_field())
        history_file.close()
        
# maybe i could do it by 2 list comp. but it was too big 
    def get_text_field(self):
        result = ""
        for line in self.field:
            for element in line:
                result += element.get_symbol() + "|"
            result+="\n"
        return result
    
    def db_update_parameters(self, player):
        self.cursor.execute("UPDATE player_status SET last_action = '%s' WHERE InGame_id = %s" 
                    % (player.choice, player.game_id))
        self.cursor.execute("UPDATE player_status SET health = %s WHERE InGame_id = %s" 
                    % (player.health, player.game_id))
        for param in self.list_parameters:
            self.cursor.execute("UPDATE player_status SET %s = %s WHERE InGame_id = %s" 
                        % (param, player.parameters[param], player.game_id))
        
    def db_update_game_status(self):
        self.cursor.execute("UPDATE rooms SET tick = %s WHERE id = %s" 
                            % (self.current_tick, self.room_id))
            
    def db_update_code(self, player):
        player.code = self.cursor.execute("SELECT code FROM players WHERE id = %s" 
                    % self.cursor.execute("SELECT id FROM player_status WHERE InGame_id = %s" 
                                    % player.game_id).fetchone()[0]).fetchone()[0]
        
    
    def move_player(self, player, x, y):
        self.field[y][x].effect_player(player)
        # Player can move just over Land
        self.field[y][x], self.field[player.y][player.x] = player, Land(player.x, player.y)
        player.x, player.y = x, y 
        
        
    def close(self): 
        self.cursor.execute("UPDATE rooms SET tick = -1 WHERE id = %s" % self.room_id)
        # bad way CHANGE P.S. i don't know how
        for player_id in self.cursor.execute("SELECT id FROM players WHERE room_id = %s" 
            % self.room_id).fetchall():
            self.cursor.execute("DELETE FROM player_status WHERE id = %s" % player_id[0])
        self.cursor.execute("UPDATE players SET room_id = -1 WHERE room_id = " + self.room_id)
        self.conn.commit()
        self.conn.close()
    
#! evrything is object -> remember it
class Game_object:
    move = True
    # 0-pass; -1 - stop; 1 - hurt
    fire = 0
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def effect_player(self, player):
        pass
    # can be __str__(), but i like this way
    def get_symbol():
        return "_N_"
    
#way change parametrs
class Land(Game_object):
    def get_symbol(self):
        return "_L_"
    
class Wall(Game_object):
    move = False
    fire = -1
    def get_symbol(self):
        return "_W_"
    
class Coin(Game_object):
    def get_symbol(self):
        return "_C_"
    def effect_player(self, player):
        player.parameters["coins"] += 1
        
    

class Player(Game_object):
    parameters = {"moves":0, "shots":0, "coins":0, "hits":0, "crash":0, "error":0}
    move = False
    fire = 1
    def __init__(self, x, y, health, game_id):
        self.x = x
        self.y = y
        self.health = health
        #work with db
        self.game_id = game_id
        
    def get_symbol(self):
        return "P" + self.game_id + "_"
        
    def effect_player(self, player):
        # Maybe hit???
        pass
    
    def make_choice(self, field):
        self.choice = ""
        # random name) need to change it(
        name = str(randint(0, 10000000))
        output_file = open(way + "game_module/bots/" + name + ".py", 'wb')
        output_file.write(bytes(self.code, encoding = "UTF-8"))
        output_file.close()
        # need to make_getting code from db
        try:
            module = imp.import_module("bots." + name)
            makeChoice = getattr(module, "make_choice")
            self.choice = makeChoice(int(self.x), int(self.y), field) # тут выбор
        except Exception as e:
            self.choice = "crash"
            self.parameters["crash"] += 1
        
    def work(self, game):
        if game.current_tick % 20 == 0:
            game.update_code(self)
        self.make_choice(game.field)
        #Analize what each user does
            
         
        if self.choice not in game.list_commands:
            self.change_health(-1)
            self.choice = "error"
            self.parameters["error"] += 1
        #We can say that player wants to go somewere 
        elif self.choice[:3] == "go_":
            self.movement(game)
        #player wants to fire
        elif self.choice[:5] == "fire_":
            self.atack(game)
        
        # update all parametrs
        game.db_update_parameters(self)
        
        #all comands were checked
                
        
        
    def change_health(self, value):
        self.health += value
    
        
    def movement(self, game):
        x_new, y_new = self.x, self.y
        direction = self.choice[3:]
        if direction == "up":
            y_new -= 1
        elif direction == "down":
            y_new += 1
        elif direction == "left":
            x_new -= 1
        elif direction == "right":
            x_new += 1
        # weather the movement happens
        if x_new > -1 and x_new < game.width and y_new > -1 and y_new < game.height:
            if game.field[y_new][x_new].move:
                self.parameters["moves"] += 1
                game.move_player(self, x_new, y_new)
            
        
    
    def atack(self, game):
        self.parameters["shots"] += 1
        direction = self.choice[5:]
        list_x = [self.x]
        list_y = [self.y]
        if direction == "up":
            list_x = range(self.x - 1, -1 , -1)
        elif direction == "down":
            list_x = range(self.x + 1, game.width, 1)
        elif direction == "left":
            list_y = range(self.y - 1, -1 , -1)
        elif direction == "right":                   
            list_y = range(self.y + 1, game.height, 1)
        for x_change, y_change in product(list_x, list_y):
            if game.field[y_change][x_change].fire == 1:
                self.parameters["hits"] += 1
                game.field[y_change][x_change].change_health(-1)
                break
            elif game.field[y_change][x_change].fire == -1:
                break
                
    
    
































if __name__ == "__main__":
    print("START")
    hi = MainGame(1)
    print(hi.get_text_field())
    for i in range(10):
        hi.tick()
    print(hi.get_text_field())
    for player in hi.players:
        print(player.code)
        print(player.parameters)
    hi.close()
    print("END")
    
    
    
    
    
    
    
'''
    print("clear-clear all players hist rooms \nelse-start a game in test(0) room")
    x = input()
    if x == "clear":
        conn = sqlite3.connect(config.way + '/tanks.sqlite')
        c = conn.cursor() 
        c.execute("UPDATE players SET room = -1")
        c.execute("DELETE FROM statistics")
        c.execute("DELETE FROM actions")
        c.execute("DELETE FROM game")
        c.execute("DELETE FROM coins")
        c.execute("DELETE FROM rooms")
        conn.commit()
        conn.close()
    else:
        conn = sqlite3.connect(config.way + '/tanks.sqlite')
        c = conn.cursor()
        c.execute("DELETE FROM rooms WHERE key = ?",["0"])
        c.execute("INSERT INTO rooms (name, key, status, map) VALUES (?, ?, ?, ?)", ["test_zone", 0, "ready", ""])
        conn.commit()
        conn.close()
        while 1:
            s = new_battle(0, "")
            if s['mode']!='sandbox':
                break
            time.sleep(5)


'''







