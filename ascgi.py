#!/usr/bin/python
# -*- coding: utf-8 -*-

from wsgiref.handlers import CGIHandler
from app import app

if __name__ == '__main__':
    CGIHandler().run(app)

