#!/usr/bin/env python
# coding: utf-8
import os

import tornado.gen
import tornado.httpclient
import tornado.httpserver
import tornado.ioloop
import tornado.util
import tornado.web
import youtube_dl
from tornado.web import HTTPError

# from handlers import ApiHandler, HomeHandler
from helpers import youtubeUrlParser
# from hooks import my_hook
from loggers import MyLogger

class StreamHandler(tornado.web.RequestHandler):
    _id = None

    @tornado.gen.coroutine
    def get(self):

        url = self.get_argument('url')
        self.write(url)
        self.write('<br>')

        self._id = youtubeUrlParser(url)

        self.flush()

        ydl_opts = {
            'format': 'best[ext=mp4][filesize<10M]', # 'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best', #
            "keepvideo": True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'logger': MyLogger(),
            'progress_hooks': [self._hook],
            "noplaylist": True,
            "outtmpl": '%(id)s.%(ext)s',
            "simulate": False,
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([self._id])

        self.write('<br>')
        self.write('<a href="/download/{file}">{file}</a>'.format(file=self._id + ".mp3"))
        self.write('<br>')
        self.write('<a href="/download/{file}">{file}</a>'.format(file=self._id + ".mp4"))

        self.finish()

    def on_chunk(self, chunk):
        self.write('some chunk')
        self.flush()

    def _hook(self, d):
        if d['status'] == 'finished':
            self.write('Done downloading, now converting ...')
            self.flush()
        else:
            self.write(d['_percent_str'])
            self.write('<br>')
            self.flush()

class InjectHandler(tornado.web.RequestHandler):
    _id = None

    @tornado.gen.coroutine
    def get(self):

        self._id = self.get_argument('v')
        self.write(self._id)
        self.write("<br>")

        self.flush()

        ydl_opts = {
            'format': 'bestaudio/best',
            "keepvideo": True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'logger': MyLogger(),
            'progress_hooks': [self._hook],
            "noplaylist": True,
            "outtmpl": '%(id)s.%(ext)s',
            "simulate": False,
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([self._id])

        self.write('<br>')
        self.write('<a href="/download/{file}">{file}</a>'.format(file=self._id + ".mp3"))

        self.finish()

    def on_chunk(self, chunk):
        self.write('some chunk')
        self.flush()

    def _hook(self, d):
        if d['status'] == 'finished':
            self.write('Done downloading, now converting ...')
            self.flush()
        else:
            self.write(d['_percent_str'])
            self.write('<br>')
            self.flush()


class DownloadHandler(tornado.web.RequestHandler):
    def get(self, file_name):
        _file_dir = os.path.abspath("") #+ "/home/ahmed/workspace/repos/bitbucket.org/yout.guneysu.xyz/src"
        _file_path = "%s/%s" % (_file_dir, file_name)
        if not file_name or not os.path.exists(_file_path):
            raise HTTPError(404)
        self.set_header('Content-Type', 'application/force-download')
        self.set_header('Content-Disposition', 'attachment; filename=%s' % file_name)
        with open(_file_path, "rb") as f:
            try:
                while True:
                    _buffer = f.read(4096)
                    if _buffer:
                        self.write(_buffer)
                    else:
                        f.close()
                        self.finish()
                        return
            except:
                raise HTTPError(404)
        raise HTTPError(500)

urls = [
    # (r'/home', HomeHandler),
    # (r'/api', ApiHandler),
    (r'/', StreamHandler),
    # (r'/watch', InjectHandler),
    (r'/download/(.*)', DownloadHandler),
]

settings = {
    'debug': True,
    "static_path": os.path.join(os.path.dirname(__file__), "static"),
    "xsrf_cookies": True,
}

if __name__ == '__main__':
    app = tornado.web.Application(handlers=urls, **settings)

    server = tornado.httpserver.HTTPServer(app)
    server.listen(8000)

    server.start(num_processes=1)

    tornado.ioloop.IOLoop.current().start()
