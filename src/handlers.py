#!/usr/bin/env python
# coding: utf-8
import json
import os

import tornado.gen
import tornado.web
import youtube_dl
from tornado.web import HTTPError

from loggers import MyLogger
from helpers import youtubeUrlParser
import sys
import shutil

class BaseHandler(tornado.web.RequestHandler):
    ydl_opts = {}
    _id = None

    def __init__(self, application, request, *args, **kwargs):
        super().__init__(application, request, **kwargs)

        self.check_downloads_folder()

        self.ydl_opts = {
            'format': 'best[ext=mp4][filesize<20M]',
            "keepvideo": True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'logger': MyLogger(),
            'progress_hooks': [self._hook],
            "noplaylist": True,
            "outtmpl": 'downloads/%(id)s.%(ext)s',
            "simulate": False,
        }

    def check_downloads_folder(self):
        DOWNLOADS = os.path.abspath("downloads")

        if not os.path.exists(DOWNLOADS):
            os.mkdir(DOWNLOADS)

    def _hook(self, d):
        if d['status'] == 'finished':
            print(d)
            self.write('Done downloading, now converting ...')
            self.flush()
        else:
            self.write(d['_percent_str'])
            self.write('<br>')
            self.flush()

    def get_video_name(self):
        return  self._id + ".mp4"

    def get_audio_name(self):
        return self._id + ".mp3"

    def get_video_link(self):
        return '/download/{file}'.format(file=self._id + ".mp4")

    def get_audio_link(self):
        return '/download/{file}'.format(file=self._id + ".mp3")


class ApiHandler(BaseHandler):
    _id = None

    def post(self, *args, **kwargs):
        data = json.loads(str(self.request.body.decode('utf-8')))
        url = data['url']
        self._id = youtubeUrlParser(url)

        # self.ydl_opts["progress_hooks"] = [self.]

        with youtube_dl.YoutubeDL(self.ydl_opts) as ydl:
            ydl.download([url])


        self.check_downloads_folder()
        response = {
            "video": self.get_video_link(),
            "audio": self.get_audio_link(),
            "id": self._id
        }

        self.write(response)

    def _hook(self, d):
        if d['status'] == 'finished':
            pass

        else:
            pass

class HomeHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        self.render('index.html')


class StreamHandler(BaseHandler):
    _id = None

    @tornado.gen.coroutine
    def get(self):

        url = self.get_argument('url')
        self.write(url)
        self.write('<br>')

        self._id = youtubeUrlParser(url)

        self.flush()

        with youtube_dl.YoutubeDL(self.ydl_opts) as ydl:
            ydl.download([self._id])

        self.write('<br>')
        self.write('<a href="/download/{file}">{file}</a>'.format(file=self._id + ".mp3"))
        self.write('<br>')
        self.write('<a href="/download/{file}">{file}</a>'.format(file=self._id + ".mp4"))

        self.finish()

    def on_chunk(self, chunk):
        self.write('some chunk')
        self.flush()


class InjectHandler(BaseHandler):
    _id = None

    @tornado.gen.coroutine
    def get(self):

        self._id = self.get_argument('v')
        self.write(self._id)
        self.write("<br>")

        self.flush()

        with youtube_dl.YoutubeDL(self.ydl_opts) as ydl:
            ydl.download([self._id])

        self.write('<br>')
        self.write('<a href="/download/{file}">{file}</a>'.format(file=self._id + ".mp3"))
        self.write('<br>')
        self.write('<a href="/download/{file}">{file}</a>'.format(file=self._id + ".mp4"))

        self.finish()

    def on_chunk(self, chunk):
        self.write('some chunk')
        self.flush()


class DownloadHandler(tornado.web.RequestHandler):
    def get(self, file_name):
        _file_dir = os.path.abspath("downloads")
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