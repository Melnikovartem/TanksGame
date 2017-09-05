#logic -> all other web stuff
# ssry for all this try
import random
import config
import sqlite3
import tornado.web


def get_MainHandler(self):
    name = ""
    conn = sqlite3.connect(config.way +'tanks.sqlite')
    c = conn.cursor()
    if self.get_cookie("TanksGame"):
        try:
            c.execute("SELECT key FROM cookies where cookie = ?", [self.get_cookie("TanksGame")])
            key = key = str(c.fetchone()[0])
            c.execute("SELECT name FROM players where key = ?", [key])
            name = c.fetchone()[0]
        except Exception as e:
            pass
    conn.close()
    self.render(config.way + "server_module/html/index.html", name = name)
    
def get_PlayerLobboyHandler(self):
    name = "Error"
    status = "error"
    conn = sqlite3.connect(config.way +'tanks.sqlite')
    c = conn.cursor()
    if self.get_cookie("TanksGame"):
        try:
            c.execute("SELECT key FROM cookies WHERE cookie = ?", [self.get_cookie("TanksGame")])
            key = key = str(c.fetchone()[0])
            c.execute("SELECT name FROM players WHERE key = ?", [key])
            name = c.fetchone()[0]
        except Exception as e:
            pass
    
    try:
        c.execute("SELECT room FROM players WHERE key = ?", [key])
        room = c.fetchone()[0]
        if room == "-1":
            status = "бот отдыхает"
        else:
            c.execute("SELECT name FROM rooms WHERE key = ?", [room])
            room_name = c.fetchone()[0]
            status = 'бот в комнате "' + room_name + '"'
    except Exception as e:
        pass
    
    c.execute("SELECT key, name FROM styles")
    styles = c.fetchall()
    conn.close()
    self.render(config.way + "server_module/html/playerlobby.html", name = name, styles = styles, status = status)
    
def post_PlayerLobboyHandler(self): 
    conn = sqlite3.connect(config.way +'tanks.sqlite')
    c = conn.cursor()
    upd_style = False
    cookie = self.get_cookie("TanksGame")
    try:
        style = self.get_argument("style")
        upd_style = True
    except Exception as e:
        pass
    if upd_style:
        c.execute("UPDATE cookies SET style = ? WHERE cookie = ?", [style, cookie])
    else:
        try:
            c.execute("SELECT key FROM cookies WHERE cookie = ?", [self.get_cookie("TanksGame")])
            key = str(c.fetchone()[0])
            file = self.request.files['file'][0]
            c.execute("SELECT * FROM players WHERE key = ?", [key])
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
                    self.write("<script>alert('Игра уже запущена!');</script>")
                    return
        except Exception as e:
            self.write("<script>alert('Ошибка загрузки!');</script>")
    self.write("<script>location.href=location.href;</script>")
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
        for i in range(30):
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
        c.execute("SELECT password FROM players WHERE name = ?",[name])
        password_real = c.fetchall()
        if password_real[0][0] != password:
            self.write("<script>alert('Неправильный пароль');location.href=location.href;</script>")
        elif password_real[0][0] == password:
            c.execute("SELECT key FROM players WHERE name = ?",[name])
            key_ = c.fetchall()[0][0]
            if not self.get_cookie("TanksGame"):
                cookie = ''
                for i in range(50):
                    cookie = cookie + str(random.randint(0, 10))
                self.set_cookie("TanksGame", cookie)
                c.execute("INSERT INTO cookies (cookie, key, style) VALUES (?,?,?)", [cookie, key_, "roctbb"])
            else:
                cookie = self.get_cookie("TanksGame")
                c.execute("UPDATE cookies SET key = ? WHERE cookie = ?", [key_, cookie])
            conn.commit()
            
            self.redirect('/playerlobby')
    except Exception as e:
        self.write("<script>alert('Пользователь с таким именем нет');location.href=location.href;</script>")
    conn.close()
    
