#!/usr/bin/python
# -*- coding: utf-8 -*-


from todo import ToDoBot
from flask import Flask, request
from flask import json



app = Flask(__name__)

app.debug = True

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
    from sqlalchemy import create_engine
    from sqlalchemy.pool import QueuePool
    # maybe poolclass=SingletonThreadPool

    engine = create_engine('sqlite:///./todo.sqlite', poolclass=QueuePool)
    #bot = Flasky(b'lion', bot_secret=open('todo.txt', mode='rb').read(), engine=engine)
    bot = Flasky(b'lion', bot_secret=None, engine=engine)
    app.route('/lingrbot', methods=['GET', 'POST'])(bot.lingrbot)
    app.run()

