#logic -> all other web stuff

import random
import config
import sqlite3
import tornado.web

def get_MainHandler(self):
    self.render(config.way + "server_module/html/index.html")
    
def post__MainHandler(self):    
    try:
        file = self.request.files['file'][0]
        conn = sqlite3.connect(config.way +'tanks.sqlite')
        c = conn.cursor()
        c.execute("SELECT * FROM players WHERE key = '%s'"%self.get_argument("key"))
        player = c.fetchone()
        c.execute("SELECT * FROM settings")
        result = c.fetchall()
        settings = dict()
        for string in result:
            settings[string[1]] = string[2]
        if settings["mode"] == "sandbox":
            c.execute("UPDATE players SET code = ? WHERE key = ?", [file['body'], player[2]])
            c.execute("UPDATE players SET state = ? WHERE key = ?", ["ready", player[2]])
            c.execute("UPDATE players SET room = ? WHERE key = ?", ["-1", player[2]])
        else:
            if player[3]=="waiting" or settings['game_state']!="running":
                c.execute("UPDATE players SET state = ?", ["ready"])
                c.execute("UPDATE players SET code = ?", [file['body']])
            else:
                self.write("<script>alert('Игра уже запущена!');location.href=location.href;</script>")
                return
        conn.commit()
        conn.close()
        self.redirect("/game")
    except Exception as e:
        self.write("<script>alert('Ошибка загрузки!');location.href=location.href;</script>")
        
def get_AddPlayer(self):
    key = self.get_argument("key", "")
    self.render("add.html", key=key)
    
def post_AddPlayer(self):
        s=''
        for i in range(6):
            s=s+str(random.randint(0, 10))
        key=s
        name = self.get_argument("name", "")
        conn = sqlite3.connect(config.way + 'tanks.sqlite')
        c = conn.cursor()
        c.execute("SELECT key FROM players WHERE name = '%s'"% name)
        key_ = c.fetchall()
        if len(key_) == 0:
            c.execute("INSERT INTO players (name,key) VALUES (?,?)", [name,key])
        else:
            key = key_[0][0]
        conn.commit()
        conn.close()
        self.redirect('/add?key='+key)
        
def get_RegHandler(self):
    self.render(config.way + "server_module/html/regestration.html")

def post_RegHandler(self):
    login = self.get_arguments("login")
    name = login[0]
    password = login[1]
    if name == '' or password == '' or login[2] == '':
        self.write("<script>alert('Заполните все поля');location.href=location.href;</script>")
    elif password != login[2]:
        self.write("<script>alert('Пароли не совпадают');location.href=location.href;</script>")
    try:
        c.execute("SELECT * FROM players where name = " +  name)
        self.write("<script>alert('Пользователь с таким именем уже есть');location.href=location.href;</script>")
        conn.close()
    except:
        key = ''
        for i in range(6):
            key = key + str(random.randint(0, 10))
        conn = sqlite3.connect(config.way +'tanks.sqlite')
        c = conn.cursor()
        c.execute("INSERT INTO players (name, key, password) VALUES (?,?,?)", [name, key, password])
        
        cookie = self.request.cookies
        try:
            c.execute("UPDATE cookies SET key = ? WHERE cookie = ?", [key, cookies])
        except:
            c.execute("INSERT INTO cookies (cookie, key, style) VALUES (?,?,?)", [cookie, key,"roctbb"])
        conn.commit()
        conn.close()
        self.redirect('/playerlobby)
