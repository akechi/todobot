#!/usr/bin/python
# -*- coding: utf-8 -*-

#id username description created_at status

import re
import os
import sys
import json
import urllib.request, urllib.parse, urllib.error
import urllib.request, urllib.error, urllib.parse
import hashlib
from datetime import datetime

from todo.models import ToDo
from todo import models
from todo.lingrparse import parse



class Spool(object):
    buffering_size = 500 #byte

    def __init__(self, room):
        self.room = room
        self.rows = []
        self.text = ''

    def add(self, row):
        self.rows.append(row)

    def write(self, s):
        self.text += s

    def render_for_lingr(self, size):
        if self.rows:
            self.rows = [r.prnformat() for r in self.rows]
        else:
            self.rows = [line for line in self.text.splitlines()]
        buf = []
        for next in self.rows:
            if buf and sum([len(line) + 1 for line in buf]) + len(next) > size:
                yield '\n'.join(buf)
                buf = []
            buf.append(next)
        yield '\n'.join(buf)


class Postman(object):
    def deliver(self, spool):
        pass

class Lingrman(object):
    def __init__(self, bot_id, bot_secret):
        self.bot_id = bot_id
        self.verifier = hashlib.sha1(bot_id + bot_secret).hexdigest()

    def deliver(self, spool):
        for t in spool.render_for_lingr(500):
            self.post(spool.room, t)
        return ''

    def post(self, room, text):
        '''
            FIXME: return values, timeoout
        '''
        req = {'room':room, 'bot':self.bot_id, 'text':text, 'bot_verifier':self.verifier}
        params = urllib.parse.urlencode(req)
        r = urllib.request.urlopen('http://lingr.com/api/room/say?' + params)


class ToDoBot(object):
    nohelp = "*** No help on %s"
    help_postfix = """\r\nこのボットはあるふぁばんです\r\n何があっても知りません"""
    prefix = 'handle_'
    adminnicks = set(['aoisensi'])

    def __init__(self, postman):
        self.postman = postman

    def on_json(self, event):
        text = event['message']['text']
        room = event['message']['room']
        who = event['message']['speaker_id']

        spool = Spool(room)
        d = parse(text)
        if d is None:
            return spool
        if len(d) == 1:
            spool.write('Please "#todo help"')
            return spool
        del(d['_hashtodo'])

        method, name = self.find_method(d)

        if method is None:
            spool.write('No such command.')
            return spool

        return method(spool, who, **self.strip(d, name))

    def strip(self, d, name):
        return dict([(k[len(name)+1:], v) for k, v in d.items()
            if k.startswith(name) and len(k) > len(name) + 1])

    def find_method(self, d):
        for k, m in self.get_handle_XXX():
           n = k[len("handle"):] 
           if n in d:
              return m, n
        return None, None

    def is_admin(self, nickname):
        return nickname in self.adminnick

    def get_handle_XXX(self):
        for c in self.__class__.__mro__:
            for k in c.__dict__:
                if k.startswith(self.prefix):
                    yield k, getattr(self, k)

    def make_help_map(self):
        return dict([(k, getattr(m, "__doc__", self.nohelp%(k,))) for k, m in self.get_handle_XXX()])

    def make_handler_name(self, s):
        return self.prefix + s.replace('-', '_')

    def handle_help(self, spool, who, command=None):
        """#todo help [command] ... if no command supplied, list all commands."""
        d = self.make_help_map()

        if command is not None and self.make_handler_name(command) in d:
            spool.write(d[self.make_handler_name(command)] + self.help_postfix)
        else:
            spool.write('\n'.join(d.values()) + self.help_postfix)
        return spool

    def handle_add(self, spool, who, description):
        """#todo add [description]"""
        td = ToDo.add(username=who, description=description, created_at=datetime.now(), status=0)
        spool.add(td)
        return spool

    def handle_addto(self, spool, who, nickname, description, **kw):
        """#todo addto [nickname] [description]"""
        '''
            u1_nickname=None, ...
            too_many_nickname=None
        '''
        if "too_many_nickname" in kw:
            spool.write("Too many nicknames!")
            return spool
        description += ' (by %s) ' % who #event['message']['speaker_id']
        t = datetime.now()
        td = ToDo.add(username=nickname, description=description, created_at=t, status=0)
        spool.add(td)
        for k, n in kw.items():
            if k[:-1].endswith('nicknames'):
                td = ToDo.add(username=n, description=description, created_at=t, status=0)
                spool.add(td)
        return spool

    def handle_list_all(self, spool, who):
        """#todo list-all"""
        for td in ToDo.list_whose(who):
            spool.add(td)
        spool.write('nothing found for %s'%(who,))
        return spool

    def handle_list_done(self, spool, who):
        """#todo list-done"""
        for td in ToDo.list_whose(who, status=True):
            spool.add(td)
        spool.write('nothing found for %s'%(who,))
        return spool

    def handle_list(self, spool, who, **kw):
        """#todo list"""
        start = kw.get('range_start',
                kw.get('range_both_start', 0))
        end = kw.get('range_end',
                kw.get('range_both_end', None))
        if end is None:
           limit = -1
        else:
           limit = int(end) - int(start)
        keyword = kw.get('keyword', None)

        if keyword is not None:
            #FIXME danger!
            for td in ToDo.list_whose(who, status=False).\
                filter(ToDo.description.like('%%%s%%'%(keyword, ))).\
                offset(start).limit(limit):
                spool.add(td)
        else:
            for td in ToDo.list_whose(who, status=False).\
                offset(start).limit(limit):
                spool.add(td)
        spool.write('nothing found for %s'%(who,))
        return spool

    def handle_listof_all(self, spool, who, nickname=None):
        """#todo listof-all [nickname]"""
        if nickname is None:
            return self.handle_help(spool, who, 'listof_all')

        for td in ToDo.list_whose(nickname):
            spool.add(td)
        spool.write('nothing found for %s'%(nickname,))
        return spool

    def handle_listof_done(self, spool, who, nickname):
        """#todo listof-done [nickname]"""
        for td in ToDo.list_whose(nickname, status=True):
            spool.add(td)
        spool.write('nothing found for %s'%(nickname,))
        return spool

    def handle_listof(self, spool, who, nickname):
        """#todo listof [nickname]"""
        for td in ToDo.list_whose(nickname, status=False):
            spool.add(td)
        spool.write('nothing found for %s'%(nickname,))
        return spool

    def handle_list_everything(self, spool, who):
        """#todo list-everything"""
        for td in ToDo.list_all():
            spool.add(td)
        spool.write('nothing found for %s'%(who,))
        return spool

    def handle_moveto(self, spool, who, nickname, task_id):
        """#todo moveto [nickname] [task_id]"""
        if task_id is None:
            spool.write("そもそも予定じゃない")
            return spool
        found = ToDo.get(int(task_id))
        if found is None:
            spool.write("そんな予定はない")
        else:
            found.set_nickname(nickname)
            spool.add(found)
        return spool

    def handle_done(self, spool, who, task_id=None):
        """#todo done [id]"""
        if task_id is None:
            spool.write("そもそも予定じゃない")
            return spool
        found = ToDo.get(int(task_id))
        if found is None:
            spool.write("そんな予定はない")
            return spool
        if found.username.startswith('@') or found.username == who:
            found.done()
            spool.write(found.prnformat())
        else:
            spool.write("それはお前の予定じゃない")
        return spool

    def handle_edit(self, spool, who, task_id, description):
        """#todo edit [id] [new description]"""
        if task_id is None:
            spool.write("そもそも予定じゃない")
            return spool
        found = ToDo.get(int(task_id))
        if found is None:
            spool.write("そんな予定はない")
            return spool
        if found.username.startswith('@') or found.username == who:
            found.edit(description=description)
            spool.write(found.prnformat())
        else:
            spool.write("それはお前の予定じゃない")
        return spool

    def handle_del(self, spool, who, task_id):
        """#todo del [id]"""
        if task_id is None:
            spool.write("そもそも予定じゃない")
            return spool
        found = ToDo.get(int(task_id))
        if found is None:
            spool.write("そんな予定はない")
            return spool
        if found.username.startswith('@') or found.username == who:
            found.done()
            spool.write('削除したよ')
        else:
            spool.write("それはお前の予定じゃない")
        return spool

    def handle_show(self, spool, who, task_id=None):
        """#todo show [id]"""
        if task_id is None:
            spool.write("そもそも予定じゃない")
            return spool
        found = ToDo.get(int(task_id))
        if found is None:
            spool.write("そんな予定はない")
        else:
            spool.add(found)
        return spool

    def handle_sudodel(self, spool, who, task_id):
        """#todo sudodel [id]"""
        if task_id is None:
            spool.write("そもそも予定じゃない")
            return spool
        if not self.is_admin(who):
            spool.write('sudoersに入ってないよ')
            return spool
        found = ToDo.get(int(task_id)) #just one.
        if found is None:
            spool.write("そんな予定はない")
        else:
            found.delete()
            spool.write('削除したよ')
        return spool

    def handle_debug(self, spool, who, task_id):
        """#todo debug [id]"""
        if self.is_admin(who):
            if task_id is not None:
                td = ToDo.get(int(task_id))
                spool.add(td.prnformat())
        return spool

    def handle_about(self, spool, who):
        """#todo about"""
        spool.write("To Do Bot\n")
        spool.write('on ' + sys.version + '\n')
        spool.write("It provides task management feature to lingr room.\n")
        spool.write("see https://github.com/akechi/todobot")
        return spool


