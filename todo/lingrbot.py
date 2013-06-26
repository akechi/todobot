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
        #print(r.read(), sys.stderr)



class ToDoBot(object):
    nohelp = "*** No help on %s"
    help_postfix = """\r\nこのボットはあるふぁばんです\r\n何があっても知りません"""
    prefix = 'handle_'
    adminnicks = set(['aoisensi'])

    def __init__(self, postman):
        self.postman = postman


    def on_json(self, event):
        args = event['message']['text'].split()
        room = event['message']['room']
        spool = Spool(room)
        if args[0]  != '#todo':
            return spool
        if len(args) == 1:
            spool.write('Please "#todo help"')
            return spool
        who = event['message']['speaker_id']

        return self.handle(args[1], spool, who, *(args[2:]))
    

    def handle(self, cmd, spool, who, *args):
        command = self.make_handler_name(cmd)
        if '.' in command:
            spool.write('NO "." in command, please!')
            return spool

        method = getattr(self, command, None)
        if method is None:
            spool.write('No such command, %s.'%(cmd,))
            return spool
        return method(spool, who, *args)


    def is_admin(self, nickname):
        return nickname in self.adminnick

    def make_handler_name(self, s):
        return self.prefix + s.replace('-', '_') #FIXME unsafe!!

    def get_handle_XXX(self):
        for k in self.__class__.__dict__:
            if k.startswith(self.prefix):
                yield k, getattr(self, k)

    def handle_help(self, spool, who, on_what=None):
        """#todo help [command] ... if no command supplied, list all commands."""
        d = dict([(k, getattr(m, "__doc__", self.nohelp%(k,))) for k, m in self.get_handle_XXX()])

        if on_what is not None and self.make_handler_name(on_what) in d:
            spool.write(d[self.make_handler_name(on_what)] + self.help_postfix)
        else:
            spool.write('\n'.join(d.values()) + self.help_postfix)
        return spool

    def handle_add(self, spool, who, *descriptions):
        """#todo add [description]"""
        text = ' '.join(descriptions)
        td = ToDo.add(username=who, description=text, created_at=datetime.now(), status=0)

        spool.add(td)
        return spool

    def handle_addto(self, spool, who, nickname, *descriptions):
        """#todo addto [nickname] [description]"""
        text = ' '.join(descriptions)
        text += ' (by %s) ' % who #event['message']['speaker_id']
        td = ToDo.add(username=nickname, description=text, created_at=datetime.now(), status=0)
        spool.add(td.id)
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

    def handle_list(self, spool, who):
        """#todo list"""
        for td in ToDo.list_whose(who, status=False):
            spool.add(td)
        spool.write('nothing found for %s'%(who,))
        return spool

    def handle_listof_all(self, spool, who, whose):
        """#todo listof-all [nickname]"""
        for td in ToDo.list_whose(whose):
            spool.add(td)
        spool.write('nothing found for %s'%(whose,))
        return spool

    def handle_listof_done(self, spool, who, whose):
        """#todo listof-done [nickname]"""
        for td in ToDo.list_whose(whose, status=True):
            spool.add(td)
        spool.write('nothing found for %s'%(whose,))
        return spool

    def handle_listof(self, spool, who, whose):
        """#todo listof [nickname]"""
        for td in ToDo.list_whose(whose, status=False):
            spool.add(td)
        spool.write('nothing found for %s'%(whose,))
        return spool

    def handle_list_everything(self, spool, who):
        """#todo list-everything"""
        for td in ToDo.list_all():
            spool.add(td)
        spool.write('nothing found for %s'%(who,))
        return spool

    def handle_done(self, spool, who, which):
        """#todo done [id]"""
        if not which.isdigit():
            spool.write("そもそも予定じゃない")
            return spool
        found = ToDo.get(int(which))
        if found is None:
            spool.write("そんな予定はない")
            return spool
        if found.username.startswith('@') or found.username == who:
            found.done()
            spool.write(found.prnformat())
        else:
            spool.write("それはお前の予定じゃない")
        return spool

    def handle_edit(self, spool, who, which, *description):
        """#todo edit [id] [new description]"""
        description = ' '.join(description)
        if not which.isdigit():
            spool.write("そもそも予定じゃない")
            return spool
        found = ToDo.get(int(which))
        if found is None:
            spool.write("そんな予定はない")
            return spool
        if found.username.startswith('@') or found.username == who:
            found.edit(description=description)
            spool.write(found.prnformat())
        else:
            spool.write("それはお前の予定じゃない")
        return spool

    def handle_del(self, spool, who, which):
        """#todo del [id]"""
        if not which.isdigit():
            spool.write("そもそも予定じゃない")
            return spool
        found = ToDo.get(int(which))
        if found is None:
            spool.write("そんな予定はない")
            return spool
        if found.username.startswith('@') or found.username == who:
            found.done()
            spool.write('削除したよ')
        else:
            spool.write("それはお前の予定じゃない")
        return spool

    def handle_show(self, spool, who, which):
        """#todo show [id]"""
        if not which.isdigit():
            spool.write("そもそも予定じゃない")
            return spool
        found = ToDo.get(int(which))
        if found is None:
            spool.write("そんな予定はない")
        else:
            spool.add(found)
        return spool

    def handle_sudodel(self, spool, who, which):
        """#todo sudodel [id]"""
        if not which.isdigit():
            spool.write("そもそも予定じゃない")
            return spool
        if not self.is_admin(who):
            spool.write('sudoersに入ってないよ')
            return spool
        found = ToDo.get(int(which)) #just one.
        if found is None:
            spool.write("そんな予定はない")
        else:
            found.delete()
            spool.write('削除したよ')
        return spool

    def handle_debug(self, spool, who, which):
        """#todo debug [id]"""
        if self.is_admin(who):
            if(which.isdigit()):
                td = ToDo.get(int(which))
                spool.add(td.prnformat())
        return spool

    def handle_about(self, spool, who):
        """#todo about"""
        spool.write("To Do Bot\n")
        spool.write('on ' + sys.version + '\n')
        spool.write("It provides task management feature to lingr room.\n")
        spool.write("see https://github.com/akechi/todobot")
        return spool


