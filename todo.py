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
            buf = []
            for next in self.rows:
                next = prnformat(next)
                if buf and sum([len(line) + 1 for line in buf]) + len(next) > size:
                    yield '\n'.join(buf)
                    buf = []
                buf.append(next)
            yield '\n'.join(buf)
        else:
            yield self.text


class Postman(object):
    def deliver(self, spool):
        pass

class Lingrman(object):
    def __init__(self, bot_id, bot_secret):
        self.bot_id = bot_id
        self.verifier = hashlib.sha1(bot_id + bot_secret).hexdigest()

    def deliver(self, room, spool):
        for t in s.render_for_lingr(500):
            self.post(s.room, t)
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

    def __init__(self, postman, engine):
        self.engine = engine 
        self.postman = postman

    def handle(self, event):
        args = event['message']['text'].split()
        room = event['message']['room']
        spool = Spool(room)

        if args[0]  != '#todo':
            return spool

        if len(args) == 1:
            spool.write('Please "#todo help"')
            return spool
        
        command = self.make_handler_name(args[1])
        if '.' in command:
            spool.write('NO "." in command, please!')
            return spool

        method = getattr(self, command, None)

        if method is None:
            spool.write('No such command, %s. Please #todo help"'%(args[1],))
            return spool

        whom = event['message']['speaker_id']
        
        with self.engine.connect() as conn:
            return method(spool, conn, room, whom, event, args)


    def is_admin(self, nickname):
        return nickname in self.adminnick

    def make_handler_name(self, s):
        return self.prefix + s.replace('-', '_') #FIXME unsafe!!

    def get_handle_XXX(self):
        for k in self.__class__.__dict__:
            if k.startswith(self.prefix):
                yield k, getattr(self, k)

    def handle_help(self, spool, conn, room, whom, event, args):
        """#todo help [command] ... if no command supplied, list all commands."""
        d = dict([(k, getattr(m, "__doc__", self.nohelp%(k,))) for k, m in self.get_handle_XXX()])

        if len(args) == 3 and self.make_handler_name(args[2]) in d:
            spool.write(d[self.make_handler_name(args[2])] + self.help_postfix)
        else:
            spool.write('\n'.join(list(d.values())) + self.help_postfix)
        return spool

    def handle_add(self, spool, conn, room, whom , event, args):
        """#todo add [description]"""
        text = ' '.join(args[2:])
        result = conn.execute("insert into TODO (username, description, created_at, status) values (?, ?, datetime('now', 'localtime'), 0);", (whom, str(text)))
        id = result.lastrowid
        result = conn.execute("select * from TODO where id = ?", (id,))
        row = result.fetchone()
        spool.add(row)
        return spool

    def handle_addto(self, spool, conn, room, whom, event, args):
        """#todo addto [nickname] [description]"""
        nickname = args[2] #target
        text = ' '.join(args[3:])
        text += ' (by %s) ' % whom #event['message']['speaker_id']
        result = conn.execute("insert into TODO (username, description, created_at, status) values (?, ?, datetime('now', 'localtime'), 0);", (nickname, str(text)))
        id = result.lastrowid
        result = conn.execute("select * from TODO where id = ?", (id,))
        spool.add(result.fetchone())
        return spool

    def handle_list_all(self, spool, conn, room, whom, event, args):
        """#todo list-all"""
        for row in conn.execute("select * from TODO where username = ?", (whom,)):
            spool.add(row)
        return spool

    def handle_list_done(self, spool, conn, room, whom, event, args):
        """#todo list-done"""
        for row in conn.execute("select * from TODO where username = ? AND status = 1", (whom,)):
            spool.add(row)
        return spool

    def handle_list(self, spool, conn, room, whom, event, args):
        """#todo list"""
        result = conn.execute("select * from TODO where username = ? AND status = 0", (whom,))
        i = None
        for i, row in enumerate(result):
            spool.add(row)
        if i is None:
            spool.write('nothing found for %s'%(whom,))
        return spool

    def handle_listof_all(self, spool, conn, room, whom, event, args):
        """#todo listof-all [nickname]"""
        whose = args[2]
        for row in conn.execute("select * from TODO where username = ?", (whose,)):
            spool.add(row)
        return spool

    def handle_listof_done(self, spool, conn, room, whom, event, args):
        """#todo listof-done [nickname]"""
        whose = args[2]
        for row in conn.execute("select * from TODO where username = ? AND status = 1", (whose,)):
            spool.add(row)
        return spool

    def handle_listof(self, spool, conn, room, whom, event, args):
        """#todo listof [nickname]"""
        whose = args[2]
        for row in conn.execute("select * from TODO where username = ? AND status = 0", (whose,)):
            spool.add(row)
        return spool
    
    def handle_list_everything(self, spool, conn, room, whom, event, args):
        """#todo list-everything"""
        for row in conn.execute("select * from TODO"):
            spool.add(row)
        return spool

    def handle_done(self, spool, conn, room, whom, event, args):
        """#todo done [id]"""
        if(args[2].isdigit()):
            id = int(args[2])
            result = conn.execute("select (username) from TODO where id = ?", (id,))
            usernames = result.fetchone()
            if(usernames == None):
                spool.write("そんな予定はない")
            elif(usernames[0][0] == '@' or usernames[0] == whom):
                conn.execute("update TODO set status =1 WHERE id = ?;", (args[2],))
                result = conn.execute("select * from TODO where id = ?", (id,))
                spool.add(result.fetchone())
            else:
                spool.write("それはお前の予定じゃない")
        else:
            spool.write("そもそも予定じゃない")
        return spool

    def handle_del(self, spool, conn, room, whom, event, args):
        """#todo del [id]"""
        if(args[2].isdigit()):
            id = int(args[2])
            result = conn.execute("select (username) from TODO where id = ?", (id,))
            usernames = result.fetchone()
            if(usernames == None):
                spool.write("そんな予定はない")
            elif(usernames[0] == '@' or usernames[0] == whom):
                conn.execute("delete from TODO WHERE id = ?;", (args[2],))
                spool.write('削除したよ')
            else:
                spool.write("それはお前の予定じゃない")
        else:
            spool.write("そもそも予定じゃない")
        return spool

    def handle_show(self, spool, conn, room, whom, event, args):
        """#todo show [id]"""
        if(args[2].isdigit()):
            id = int(args[2])
            result = conn.execute("select * from TODO where id = ?", (id,))
            row = result.fetchone()
            if(row == None):
                spool.write("そんな予定はない")
            else:
                spool.add(row)
        else:
            spool.write("そもそも予定じゃない")
        return spool

    def handle_sudodel(self, spool, conn, room, whom, event, args):
        """#todo sudodel [id]"""
        if(args[2].isdigit()):
            if self.is_admin(whom):
                id = int(args[2])
                result = conn.execute("select (username) from TODO where id = ?", (id,))
                usernames = result.fetchone()
                if(usernames == None):
                    spool.write(room, "そんな予定はない")
                else:
                    conn.execute("delete from TODO WHERE id = ?;", (args[2],))
                    spool.write('削除したよ')
            else:
                spool.write('sudoersに入ってないよ')
        else:
            spool.write("そもそも予定じゃない")
        return spool

    def handle_debug(self, spool, conn, room, whom, event, args):
        """#todo debug [id]"""
        if self.is_admin(whom):
            if(args[2].isdigit()):
                result = conn.execute("select (username) from TODO where id = ?", (int(args[2]),))
                spool.write(str(result.fetchone()))
        return spool

    def handle_about(self, spool, conn, room, whom, event, args):
        """#todo about"""
        spool.write("To Do Bot\n")
        spool.write('on ' + sys.version + '\n')
        spool.write("It provides task management feature to lingr room.\n")
        spool.write("see https://github.com/akechi/todobot")
        return spool

