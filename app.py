#!/usr/bin/python
# -*- coding: utf-8 -*-

from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine('sqlite:///./todo.sqlite', poolclass=QueuePool)
# maybe poolclass=SingletonThreadPool

from flask import Flask, request

app = Flask(__name__)

app.debug = True

def prnformat(row):
    s = []
    if(row[4] != 0):
        s.append('[X]')
    else:
        s.append('[_]')
    s.append("%04d" % row[0])
    s.append(row[1])
    s.append(row[2])
    s.append(row[3])
    return ' '.join(s)


@app.route('/lingrbot', methods=['GET', 'POST'])
def hello_world():
    """#todo listof-all [nickname]"""
    with engine.connect() as conn:
        result = ''
        cur = conn.execute("select * from TODO where username = ?", ('raa0121',))
        result = '\n'.join(list([prnformat(row) for row in cur]))
    return result

"""
    request.method == 'POST'
        '''array = json.loads(request.data)'''
        '''or'''
        '''array = request.json'''
        return "do action"
"""

if __name__ == '__main__':
    app.run()

