#logic -> all other web stuff

import random
import config
import sqlite3
import tornado.web

def get_MainHandler(self):
    self.render(config.way + "server_module/html/upload.html")
    
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
        print(name, "Получил ключ:", key)
        conn.commit()
        conn.close()
        self.redirect('/add?key='+key)
    
