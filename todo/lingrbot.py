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
import functools

from lib.reast import findbind, bindable
from todo.models import ToDo
from todo import models
from todo.lingrparse import rx, ast, cap



class Spool(object):
    buffering_size = 500 #byte

    def __init__(self, room):
        self.room = room
        self.rows = []
        self._pre = ''
        self._post = ''
        self._error = ''

    def add(self, row):
        self.rows.append(row)

    def error(self, s):
        self._error += s

    def pre(self, s):
        self._pre += s

    def post(self, s):
        self._post += s

    def render_for_lingr(self, size):
        rows = []
        if self.rows:
            t = datetime.now()
            rows += [line for line in self._pre.splitlines()]
            rows += [r.prnformat(t) for r in self.rows]
            rows += [line for line in self._post.splitlines()]
        else:
            rows = [line for line in self._error.splitlines()]
        buf = []
        for next in rows:
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
    nohelp = "*** No help on {}"
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
        m = rx.match(text)
        if m is None:
            return spool
        d = dict([(k, v) for k, v in m.groupdict().items() if v is not None])
        if len(d) == 1:
            spool.error('何をしたいのかわからない。"#todo help" してみて.')
            return spool

        method, name = self.find_method(d)

        if method is None:
            spool.error('そのcommand実装されてない. "{0}"'.format(text))
            return spool

        method = functools.partial(method, who=who, spool=spool)

        assoc = cap.associate(d)

        to_bind = bindable(assoc, d, ('hashtodo', name[1:]))
        missing, toomany = findbind(method, to_bind)

        if missing:
            spool.error('引数がたりない {0}'.format(missing))
            return spool
        if toomany:
            spool.error('引数が多すぎる. {0}'.format(toomany))
            return spool

        return method(**to_bind) 

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
        return dict([(k, getattr(m, "__doc__", self.nohelp.format(k))) for k, m in self.get_handle_XXX()])

    def make_handler_name(self, s):
        return self.prefix + s.replace('-', '_')

    def handle_help(self, spool, who, command=None):
        """#todo help [command] ... if no command supplied, list all commands."""
        d = self.make_help_map()

        if command is not None and self.make_handler_name(command) in d:
            spool.error(d[self.make_handler_name(command)] + self.help_postfix)
        else:
            spool.error('\n'.join(d.values()) + self.help_postfix)
        return spool

    def handle_add(self, spool, who, description):
        """#todo add [description]"""
        td = ToDo.add(username=who, description=description, created_at=datetime.now(), status=0)
        spool.add(td)
        return spool

    def handle_addto(self, spool, who, nickname, description, nicknames=None):
        """#todo addto [nickname] [description]"""
        '''
            u1_nickname=None, ...
            too_many_nickname=None
        '''

        description += ' (by {})'.format(who) #event['message']['speaker_id']
        t = datetime.now()
        td = ToDo.add(username=nickname, description=description, created_at=t, status=0)
        spool.add(td)
        for n in nicknames or []:
            td = ToDo.add(username=n, description=description, created_at=t, status=0)
            spool.add(td)
        return spool

    def handle_list_all(self, spool, who):
        """#todo list-all"""
        for td in ToDo.list_whose(who):
            spool.add(td)
        spool.error('nothing found for {}'.format(who))
        return spool

    def handle_list_done(self, spool, who):
        """#todo list-done"""
        for td in ToDo.list_whose(who, status=True):
            spool.add(td)
        spool.error('nothing found for {}'.format(who))
        return spool

    def handle_list(self, spool, who, start=None, end=None, 
            keyword=None, quoted=None):
        """#todo list [start-end] [keyword or quoted]"""
        '''
        start = kw.get('range_start',
                kw.get('range_both_start', 0))
        end = kw.get('range_end',
                kw.get('range_both_end', None))
        '''
        if start is None:
            start = 0
        if end is None:
            limit = 3
        else:
            limit = int(end) - int(start)

        like = keyword if keyword else (quoted if quoted else None)
        #FIXME danger!

        q = ToDo.list_whose(who, status=False)
        if like is not None:
            q = q.filter(ToDo.description.like('%{}%'.format(like)))

        n = q.count()
        if n == 0:
            spool.error('nothing found for {}'.format(who))
            return spool
        
        q = q.order_by(ToDo.created_at.desc()).\
            offset(start).limit(limit)
        found = q.count()

        spool.pre('showing {} of {}'.format(found, n))
        for td in q:
            spool.add(td)
        return spool

    def handle_listof_all(self, spool, who, nickname=None):
        """#todo listof-all [nickname]"""
        if nickname is None:
            return self.handle_help(spool, who, 'listof_all')

        for td in ToDo.list_whose(nickname).order_by(ToDo.created_at.desc()):
            spool.add(td)
        spool.error('nothing found for {}'.format(nickname))
        return spool

    def handle_listof_done(self, spool, who, nickname):
        """#todo listof-done [nickname]"""
        for td in ToDo.list_whose(nickname, status=True).order_by(ToDo.created_at.desc()):
            spool.add(td)
        spool.error('nothing found for {}'.format(nickname))
        return spool

    def handle_listof(self, spool, who, nickname, start=None, end=None, keyword=None, quoted=None):
        """#todo listof [nickname] [start-end] [keyword or quoted]"""
        return self.handle_list(spool, nickname, start, end, keyword, quoted)

    def handle_list_everything(self, spool, who):
        """#todo list-everything"""
        for td in ToDo.list_all():
            spool.add(td)
        spool.error('nothing found for {}'.format(who))
        return spool

    def handle_moveto(self, spool, who, nickname, task_id):
        """#todo moveto [nickname] [task_id]"""
        if task_id is None:
            spool.error("そもそも予定じゃない")
            return spool
        found = ToDo.get(int(task_id))
        if found is None:
            spool.error("そんな予定はない")
        else:
            old = found.description
            new = old + " ( moved from " + who + ") "
            found.edit(username=nickname, description=new)
            spool.add(found)
        return spool

    def handle_done(self, spool, who, task_ids):
        """#todo done [id] [id] [id] [id] [id]"""
        for task_id in task_ids:
            if task_id is None:
                spool.error("そもそも予定じゃない")
                continue
            found = ToDo.get(int(task_id))
            if found is None:
                spool.error("そんな予定はない '{}\n'".format(task_id))
                continue
            if found.username.startswith('@') or found.username == who:
                found.done()
                t = datetime.now()
                spool.error(found.prnformat(t))
            else:
                spool.error("{}はお前の予定じゃない\n".format(found))
        return spool

    def handle_edit(self, spool, who, task_id, description):
        """#todo edit [id] [new description]"""
        if task_id is None:
            spool.error("そもそも予定じゃない")
            return spool
        found = ToDo.get(int(task_id))
        if found is None:
            spool.error("そんな予定はない '{}'".format(task_id))
            return spool
        if found.username.startswith('@') or found.username == who:
            found.edit(description=description)
            t = datetime.now()
            spool.error(found.prnformat(t))
        else:
            spool.error("それはお前の予定じゃない")
        return spool

    def handle_del(self, spool, who, task_ids):
        """#todo del [id] [id] [id] [id] [id]"""
        for task_id in task_ids:
            if task_id is None:
                spool.error("そもそも予定じゃない")
                continue
            found = ToDo.get(int(task_id))
            if found is None:
                spool.error("そんな予定はない '{}'\n".format(task_id))
                continue
            if found.username.startswith('@') or found.username == who:
                found.delete()
                spool.error('{}を削除したよ\n'.format(task_id))
            else:
                spool.error("{}はお前の予定じゃない\n".format(task_id))
        return spool

    def handle_show(self, spool, who, task_id=None):
        """#todo show [id]"""
        if task_id is None:
            spool.error("そもそも予定じゃない")
            return spool
        found = ToDo.get(int(task_id))
        if found is None:
            spool.error("そんな予定はない '{}'\n".format(task_id))
        else:
            spool.add(found)
        return spool

    def handle_sudodel(self, spool, who, task_id):
        """#todo sudodel [id]"""
        if task_id is None:
            spool.error("そもそも予定じゃない")
            return spool
        if not self.is_admin(who):
            spool.error('sudoersに入ってないよ')
            return spool
        found = ToDo.get(int(task_id)) #just one.
        if found is None:
            spool.error("そんな予定はない '{}'\n".format(task_id))
        else:
            found.delete()
            spool.error('{}を削除したよ\n'.format(task_id))
        return spool

    def handle_debug(self, spool, who, task_id):
        """#todo debug [id]"""
        if self.is_admin(who):
            if task_id is not None:
                td = ToDo.get(int(task_id))
                t = datetime.now()
                spool.add(td.prnformat(t))
        return spool

    def handle_about(self, spool, who):
        """#todo about"""
        spool.error("To Do Bot\n")
        spool.error('on ' + sys.version + '\n')
        spool.error("It provides task management feature to lingr room.\n")
        spool.error("see https://github.com/akechi/todobot")
        return spool


