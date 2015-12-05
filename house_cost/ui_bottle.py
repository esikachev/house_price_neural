#!/usr/bin/env python
# -- coding: utf-8 --

__author__ = 'michael'

from bottle import route, run, template, view

@route('/')
@view('house_cost/views/app')
def index():
    return

run(host='localhost', port=8080)