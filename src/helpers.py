#!/usr/bin/env python
# coding: utf-8
from urllib.parse import urlparse, parse_qs


def youtubeUrlParser(url):
    parsed_url = urlparse(url)
    qs = parse_qs(qs=parsed_url.query)

    if parsed_url.netloc ==  'youtu.be':
        return parsed_url.path.strip('/')

    _id = qs.get('v', [None])[0]
    return _id