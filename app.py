#!/usr/bin/python
# -*- coding: utf-8 -*-

from todo import ToDoBot
from flask import Flask, request
from flask import json


import os
import logging
from logging.handlers import RotatingFileHandler

class Flasky(ToDoBot):
    ''' UGH, buffer is not thread safe!!'''
    def lingrbot(self):
        if request.method == 'POST':
            text = request.data
            array = json.loads(text)
            for event in array['events']:
                s = self.handle(event) 
                for t in s.render_for_lingr(500):
                    self.post(s.room, t)
            return ''
        else:
            return 'hello! ' #self.handle_about(None, None, None, None, None)

app = Flask(__name__)

formatter = logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s '
        '[in %(pathname)s:%(lineno)d]'
        )

debug_log = os.path.join(app.root_path, 'logs/debug.log')
debug_file_handler = RotatingFileHandler(
            debug_log, maxBytes=100000, backupCount=10
            )
debug_file_handler.setLevel(logging.INFO)
debug_file_handler.setFormatter(formatter)
app.logger.addHandler(debug_file_handler)

error_log = os.path.join(app.root_path, 'logs/error.log')
error_file_handler = RotatingFileHandler(
            error_log, maxBytes=100000, backupCount=10
            )    
error_file_handler.setLevel(logging.ERROR)
error_file_handler.setFormatter(formatter)
app.logger.addHandler(error_file_handler)


if __name__ == '__main__':
    import sys
    from sqlalchemy import create_engine
    from sqlalchemy.pool import QueuePool
    # maybe poolclass=SingletonThreadPool

    if len(sys.argv) > 1 and sys.argv[1] == 'debug':
        app.debug = True
    else:
        app.logger.setLevel(logging.INFO)

    engine = create_engine('sqlite:///./todo.sqlite', poolclass=QueuePool)

    if app.debug:
        bot = Flasky(b'todo2', bot_secret=None, engine=engine)
    else:
        bot = Flasky(b'todo2', bot_secret=open('todo.txt', mode='rb').read().rstrip(), engine=engine)

    app.route('/lingrbot', methods=['GET', 'POST'])(bot.lingrbot)
    app.run(host='0.0.0.0', port=11001)

