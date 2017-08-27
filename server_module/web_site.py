#logic -> all other web stuff

import random
import config
import sqlite3
import tornado.web


def get_MainHandler(self):
    name = ""
    if self.get_cookie("TanksGame"):
        try:
            c.execute("SELECT name FROM cookies where cookie = " +  self.get_cookie("TanksGame"))
            name = c.fetchall()
        except:
            pass
    self.render(config.way + "server_module/html/index.html", name = name)
    
def get_PlayerLobboyHandler(self):
    name = "Hi"
    try:
        c.execute("SELECT key FROM cookies where cookie = " +  self.get_cookie("TanksGame"))
        key = c.fetchall()
        c.execute("SELECT name FROM players where key = " + key)
        name = c.fetchall()
    except:
        pass
    self.render(config.way + "server_module/html/playerlobby.html", name = name)
    
def post_PlayerLobboyHandler(self): 
    conn = sqlite3.connect(config.way +'tanks.sqlite')
    c = conn.cursor()
    style = self.get_argument("button")
    print(style)
    try:
        file = self.request.files['file'][0]
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
      
#problems with cookies in login and regestration      else:
                self.write("<script>alert('Игра уже запущена!');location.href=location.href;</script>")
                return
        self.redirect("/game")
    except Exception as e:
        self.write("<script>alert('Ошибка загрузки!');location.href=location.href;</script>")
    conn.commit()
    conn.close()
    
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
        if not self.get_cookie("TanksGame"):
            cookie = ''
            for i in range(50):
                cookie = cookie + str(random.randint(0, 10))
            self.set_cookie("TanksGame", cookie)
            c.execute("INSERT INTO cookies (cookie, key, style) VALUES (?,?,?)", [cookie, key, "roctbb"])
        else:
            cookie = self.get_cookie("TanksGame")
            c.execute("UPDATE cookies SET key = ? WHERE cookie = ?", [key, cookie])
        
        c.execute("INSERT INTO players (name, key, password) VALUES (?,?,?)", [name, key, password])
        conn.commit()
        conn.close()
        self.redirect('/playerlobby')
    
def get_LoginHandler(self):
    self.render(config.way + "server_module/html/login.html")
    
def post_LoginHandler(self):
    login = self.get_arguments("login")
    name = login[0]
    password = login[1]
    conn = sqlite3.connect(config.way +'tanks.sqlite')
    c = conn.cursor()
    try:
        c.execute("SELECT (key, password) FROM players WHERE name = " +  name)
        password_real = c.fetchall()
        print("here")
        if password_real[0][0] != password:
            self.write("<script>alert('Неправильный пароль');location.href=location.href;</script>")
        elif password_real[0][0] == password:
            print(self.get_cookie("TanksGame"))
            if not self.get_cookie("TanksGame"):
                cookie = ''
                for i in range(50):
                    cookie = cookie + str(random.randint(0, 10))
                self.set_cookie("TanksGame", cookie)
                c.execute("INSERT INTO cookies (cookie, key, style) VALUES (?,?,?)", [cookie, password_real[0][1], "roctbb"])
            else:
                cookie = self.get_cookie("TanksGame")
                c.execute("UPDATE cookies SET key = ? WHERE cookie = ?", [key, cookie])
            conn.commit()
            conn.close()
            
            self.redirect('/playerlobby')
    except Exception as e:
        print(e)
        self.write("<script>alert('Пользователь с таким именем нет');location.href=location.href;</script>")
    conn.close()
    
