#!/usr/bin/env python
# coding: utf-8
import os

import tornado.web
import tornado.httpserver
import tornado.ioloop
import tornado.gen
import json
import tornado.util

from urllib.parse import urlparse, parse_qs
import youtube_dl
import tornado.httpclient
from tornado.web import HTTPError

class MyLogger(object):
    def debug(self, msg):
        print(msg)

    def warning(self, msg):
        print(msg)

    def error(self, msg):
        print(msg)


def my_hook(d):
    if d['status'] == 'finished':
        print('Done downloading, now converting ...')


ydl_opts = {
    # 'format': 'bestaudio/best',
    # 'postprocessors': [{
    #     'key': 'FFmpegExtractAudio',
    #     'preferredcodec': 'mp3',
    #     'preferredquality': '192',
    # }],
    'logger': MyLogger(),
    'progress_hooks': [my_hook],
    "noplaylist": True,
    "id": True,
    "outtmpl": '%(id)s_%(width)sx%(height)s.%(ext)s',
    "dump_single_json": True,
    "simulate": True,
}


def youtubeUrlParser(url):
    parsed_url = urlparse(url)
    qs = parse_qs(qs=parsed_url.query)
    _id = qs.get('v', [None])[0]
    return _id


class HomeHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        self.render('index.html')


class ApiHandler(tornado.web.RequestHandler):
    def post(self, *args, **kwargs):
        data = json.loads(str(self.request.body.decode('utf-8')))
        url = data['url']
        _id = youtubeUrlParser(url)

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([_id])

        self.write(_id)


class StreamHandler(tornado.web.RequestHandler):
    _id = None

    @tornado.gen.coroutine
    def get(self):

        url = self.get_argument('url')
        self.write(url)

        self._id = youtubeUrlParser(url)

        self.flush()

        ydl_opts = {
            'logger': MyLogger(),
            'progress_hooks': [self._hook],
            "noplaylist": True,
            "outtmpl": '%(id)s.%(ext)s',
            "simulate": False,
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([self._id])

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
    (r'/home', HomeHandler),
    (r'/api', ApiHandler),
    (r'/', StreamHandler),
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
