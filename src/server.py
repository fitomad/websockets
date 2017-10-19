import os
import sys
import tornado.ioloop
import tornado.web

from static import AppStaticFileHandler    
from chat import ChatWebSocketHandler

def make_app():
    root = os.path.dirname(__file__)

    return tornado.web.Application([
        (r"/talking", ChatWebSocketHandler), # WebSocket
        (r"/(.*)", AppStaticFileHandler, {"path": root, "default_filename": "web/login.html"})
    ],
    debug = False
    )

if __name__ == "__main__":
    app = make_app()
    
    server = tornado.httpserver.HTTPServer(app)
    server.bind(9090)

    if sys.platform == "win32":
        # Windows no tiene soporte para Fork
        server.start(1)
    else:
        # Fork process
        server.start(0)
     
    tornado.ioloop.IOLoop.current().start()