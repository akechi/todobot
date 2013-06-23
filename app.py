#!/usr/bin/python
# -*- coding: utf-8 -*-

from todo import ToDoBot
from flask import Flask, request
from flask import json


class Flasky(ToDoBot):
    ''' UGH, buffer is not thread safe!!'''
    def lingrbot(self):
        if request.method == 'POST':
            text = request.data
            array = json.loads(text)
            for event in array['events']:
                s = self.handle(event) 
                for t in s.render_as_text(500):
                    self.post(s.room, t)
            return ''
        else:
            return 'hello! ' #self.handle_about(None, None, None, None, None)


if __name__ == '__main__':
    import sys
    from sqlalchemy import create_engine
    from sqlalchemy.pool import QueuePool
    # maybe poolclass=SingletonThreadPool

    app = Flask(__name__)
    if len(sys.argv) > 1 and sys.argv[1] == 'debug':
        app.debug = True
    engine = create_engine('sqlite:///./todo.sqlite', poolclass=QueuePool)
    if app.debug:
        bot = Flasky(b'lion', bot_secret=None, engine=engine)
    else:
        bot = Flasky(b'lion', bot_secret=open('todo.txt', mode='rb').read(), engine=engine)
    app.route('/lingrbot', methods=['GET', 'POST'])(bot.lingrbot)
    app.run()

