#!/usr/bin/env python
# coding: utf-8
import os

import tornado.web
import tornado.httpserver
import tornado.ioloop
from  tornado.options import define, parse_command_line, options


define(name="port", default=8000, type=int)
define(name="debug", default=False, type=bool)

from handlers import ApiHandler, HomeHandler, DownloadHandler, InjectHandler, StreamHandler


urls = [
    (r'/', HomeHandler),
    (r'/api', ApiHandler),
    (r'/download/(.*)', DownloadHandler),
    (r'/s', StreamHandler),
    (r'/watch', InjectHandler),
]

settings = {
    'debug': options.debug,
    "static_path": os.path.join(os.path.dirname(__file__), "static"),
    "xsrf_cookies": True,
}

if __name__ == '__main__':
    parse_command_line()

    app = tornado.web.Application(handlers=urls, **settings)

    server = tornado.httpserver.HTTPServer(app)
    server.listen(options.port)

    server.start(num_processes=1)

    tornado.ioloop.IOLoop.current().start()
