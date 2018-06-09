#!/usr/bin/env python
# coding: utf-8
import json

import tornado.web
import youtube_dl

from main import ydl_opts
from helpers import youtubeUrlParser


class ApiHandler(tornado.web.RequestHandler):
    def post(self, *args, **kwargs):
        data = json.loads(str(self.request.body.decode('utf-8')))
        url = data['url']
        _id = youtubeUrlParser(url)

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([_id])

        self.write(_id)


class HomeHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        self.render('index.html')