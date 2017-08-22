__author__ = ''
import tornado.web
import tornado.httpserver
import logic

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("upload.html")
    def post(self):
        logic.post_MainHandler(self)

class StatsHandler(tornado.web.RequestHandler):
    def get(self)
        logic.get_StatsHandler(self)
        
 
class GameHandler(tornado.web.RequestHandler):
    def get(self):
        logic.get_GameHandler

class StateHandler(tornado.web.RequestHandler):
    def get(self:)
        logic.get_StateHandler(self)

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [(r"/", MainHandler),
                (r"/game", GameHandler),
                (r"/state", StateHandler), 
                (r"/stats", StatsHandler),
                (r'/static/(.*)', tornado.web.StaticFileHandler, 
                {'path': os.path.dirname(__file__)+"/static/"}),]
        settings = {}
        super(Application, self).__init__(handlers, **settings)

def main():
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(8000)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
