__author__ = 'hi_melnikov'
import tornado.web
import tornado.httpserver 
import web_game
import web_site  

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        web_site.get_MainHandler(self)
    def post(self):
        web_site.post_MainHandler(self)

class StatsHandler(tornado.web.RequestHandler):
    def get(self):
        web_game.StatsHandler(self)

class GameHandler(tornado.web.RequestHandler):
    def get(self):
        web_game.get_GameHandler(self)

class StateHandler(tornado.web.RequestHandler):
    def get(self):
        web_game.get_StateHandler(self)

class AddPlayer(tornado.web.RequestHandler):
    def get(self):
        web_site.post_AddPlayer(self)
    def post(self):
        web_site.post_AddPlayer(self)

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [(r"/", MainHandler),
                (r"/game", GameHandler),
                (r"/state", StateHandler), 
                (r"/stats", StatsHandler),
                (r"/add",  AddPlayer),
                (r'/static/(.*)', tornado.web.StaticFileHandler, 
                {'path': os.path.dirname(__file__)+"styles/static/"}),]
        settings = {}
        super(Application, self).__init__(handlers, **settings)

def main():
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(8000)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
