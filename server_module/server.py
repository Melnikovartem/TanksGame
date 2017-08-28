__author__ = 'hi_melnikov'
import tornado.web
import tornado.httpserver 
import web_game
import web_site  
import os

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        web_site.get_MainHandler(self)
    def post(self):
        web_site.post_MainHandler(self)
        
class LoginHandler(tornado.web.RequestHandler):
    def get(self):
        web_site.get_LoginHandler(self)
    def post(self):
        web_site.post_LoginHandler(self)

class RegHandler(tornado.web.RequestHandler):
    def get(self):
        web_site.get_RegHandler(self)
    def post(self):
        web_site.post_RegHandler(self)

class PlayerLobboyHandler(tornado.web.RequestHandler):
    def get(self):
        web_site.get_PlayerLobboyHandler(self)
    def post(self):
        web_site.post_PlayerLobboyHandler(self)

class GameHandler(tornado.web.RequestHandler):
    def get(self):
        web_game.get_GameHandler(self)

class GameListHandler(tornado.web.RequestHandler):
    def get(self):
        web_game.get_GameListHandler(self)

class StateHandler(tornado.web.RequestHandler):
    def get(self):
        web_game.get_StateHandler(self)

class StatsHandler(tornado.web.RequestHandler):
    def get(self):
        web_game.get_StatsHandler(self)

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [(r"/", MainHandler),
                (r"/login", LoginHandler),
                (r"/regestration", RegHandler), 
                (r"/playerlobby", PlayerLobboyHandler),
                (r"/game", GameHandler),
                (r"/gamelist", GameListHandler),
                (r"/state", StateHandler), 
                (r"/stats", StatsHandler),
                (r'/styles/(.*)', tornado.web.StaticFileHandler, 
                {'path': os.path.dirname(__file__)+"styles/"}),]
        settings = {}
        super(Application, self).__init__(handlers, **settings)

def main():
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(8000)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
