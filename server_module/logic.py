import tornado.web
import tornado.httpserver
import sqlite3
import sys
import os
import json
import logic

from time import gmtime, strftime

def post_MainHandler(self):
    try:
        file = self.request.files['file'][0]
        conn = sqlite3.connect('../tanks.sqlite')
        c = conn.cursor()
        c.execute("SELECT * FROM players WHERE key = '%s'"%self.get_argument("key"))
        player = c.fetchone()
        c.execute("SELECT * FROM settings")
        result = c.fetchall()
        settings = dict()
        for string in result:
            settings[string[1]] = string[2]
        if settings["mode"] == "sandbox":
            if player[3]=="waiting":
                print(strftime("%Y-%m-%d %H:%M:%S", gmtime())+": "+player[2]+" ("+player[1]+") has loaded new bot")
            else:
                print(strftime("%Y-%m-%d %H:%M:%S", gmtime())+": "+player[2] + " (" + player[1] + ") has reloaded bot")
            c.execute("UPDATE players SET code = ? WHERE key = ?", [file['body'], player[2]])
            c.execute("UPDATE players SET state = ? WHERE key = ?", ["ready", player[2]])
            conn.commit()
        else:
            if player[3]=="waiting" or settings['game_state']!="running":
                c.execute("UPDATE players SET state = ?", ["ready"])
                c.execute("UPDATE players SET code = ?", [file['body']])
                conn.commit()
            else:
                self.write("<script>alert('Игра уже запущена!');location.href=location.href;</script>")
                return

        self.redirect("/game")

    except Exception as e:
        print(e)
        self.write("<script>alert('Ошибка загрузки!');location.href=location.href;</script>")

    sys.path.append(os.path.dirname(__file__) + "/../bots")



