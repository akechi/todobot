#!/usr/bin/python
# -*- coding: utf-8 -*-

from todo.lingrbot import ToDoBot, Lingrman, Spool 
from flask import Flask, request
from flask import json


import os
import logging
from logging.handlers import RotatingFileHandler




class Flasky(ToDoBot):
    def lingrbot(self):
        if request.method == 'POST':
            array = json.loads(request.data)
            return ''.join([self.postman.deliver(self.on_json(event)) for event in array['events']])
        else:
            return 'hello! ' #self.handle_about(None, None, None, None, None)

    def one_arg(self, cmd, username):
        spool = Spool(None)
        got = self.handle(cmd, spool, username)

        return "<br/>".join([r.prnformat() for r in got.rows])


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
    from sqlalchemy.orm import sessionmaker

    if len(sys.argv) > 1 and sys.argv[1] == 'debug':
        app.debug = True
    else:
        app.logger.setLevel(logging.INFO)

    engine = create_engine('sqlite:///./todo.sqlite', poolclass=QueuePool)
    lingr = Lingrman(b'todo2', bot_secret=open('todo.txt', mode='rb').read().rstrip())

    bot = Flasky(lingr, sessionmaker(bind=engine))

    app.route('/lingrbot', methods=['GET', 'POST'])(bot.lingrbot)
    app.route('/<cmd>/<username>', methods=['GET'])(bot.one_arg)
    if app.debug:
        app.run()
    else:
        app.run(host='0.0.0.0', port=11001)
    

