#!/usr/bin/env python
# coding: utf-8
def my_hook(d):
    if d['status'] == 'finished':
        print('Done downloading, now converting ...')