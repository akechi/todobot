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
import sqlite3

import gitsha1



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



class ToDoBot(object):
    nohelp = "*** No help on %s"
    help_postfix = """\r\nこのボットはあるふぁばんです\r\n何があっても知りません"""
    prefix = 'handle_'
    adminnicks = set(['aoisensi'])

    buffering_size = 500 #byte

    def __init__(self, bot_id, bot_secret, dbpath):
        self.bot_id = bot_id
        if bot_secret:
            self.verifier = hashlib.sha1(bot_id + bot_secret).hexdigest()
        else:
            self.verifier = None
        self.con = sqlite3.connect(dbpath, isolation_level=None)
        self.con.text_factory = str
        self.buffers = {}

    def post(self, room, text):
        '''
            FIXME: return values, timeoout

        '''
        if self.verifier:
            req = {'room':room, 'bot':self.bot_id, 'text':text, 'bot_verifier':self.verifier}
            params = urllib.parse.urlencode(req)
            r = urllib.request.urlopen('http://lingr.com/api/room/say?' + params)
        else:
            print(text, file=sys.stdout)

    def buffered_post(self, room, text):
        buf = self.buffers.get(room, None)
        if buf and sum([len(line) + 1 for line in buf]) + len(text) > self.buffering_size:
            self.flush_buf(room)
        buf = self.buffers.get(room, None)
        if buf is None:
            buf = []
        buf.append(text)
        self.buffers[room] = buf

    def flush_buf(self, room):
        buf = self.buffers.get(room, None)
        if buf:
            self.post(room, '\n'.join(buf))
            self.buffers[room] = None

    def handle(self, event):
        args = event['message']['text'].split()
        room = event['message']['room']
        if args[0]  != '#todo':
            return
        if len(args) == 1:
            self.post(room, 'Please "#todo help"')
            return
        
        command = self.make_handler_name(args[1])
        if '.' in command:
            self.post(room, 'NO "." in command, please!')
            return

        method = getattr(self, command, None)

        if method is None:
            self.post(room, 'No such command, %s. Please #todo help"'%(args[1],))
            return 


        cur = self.con.cursor()
        whom = event['message']['speaker_id']
        
        try:
            r = method(cur, room, whom, event, args)
        except Exception as e:
            print(str(type(e)))
            print(str(e.args))
            print(e.message)
                    
        finally:
            self.con.commit()

    def is_admin(self, nickname):
        return nickname in self.adminnick

    def make_handler_name(self, s):
        return self.prefix + s.replace('-', '_') #FIXME unsafe!!

    def get_handle_XXX(self):
        for k in self.__class__.__dict__:
            if k.startswith(self.prefix):
                yield k, getattr(self, k)

    def handle_help(self, cur, room, whom, event, args):
        """#todo help [command] ... if no command supplied, list all commands."""
        d = dict([(k, getattr(m, "__doc__", self.nohelp%(k,))) for k, m in self.get_handle_XXX()])

        if len(args) == 3 and self.make_handler_name(args[2]) in d:
            sys.stdout.write(d[self.make_handler_name(args[2])] + self.help_postfix)
        else:
            sys.stdout.write('\n'.join(list(d.values())) + self.help_postfix)

    def handle_add(self, cur, room, whom , event, args):
        """#todo add [description]"""
        text = ' '.join(args[2:])
        cur.execute("insert into TODO (username, description, created_at, status) values (?, ?, datetime('now', 'localtime'), 0);", (whom, str(text)))
        id = cur.lastrowid
        cur.execute("select * from TODO where id = ?", (id,))
        row = cur.fetchone()
        self.post(room, prnformat(row))

    def handle_addto(self, cur, room, whom, event, args):
        """#todo addto [nickname] [description]"""
        nickname = args[2] #target
        text = ' '.join(args[3:])
        text += ' (by %s) ' % whom #event['message']['speaker_id']
        cur.execute("insert into TODO (username, description, created_at, status) values (?, ?, datetime('now', 'localtime'), 0);", (nickname, str(text)))
        id = cur.lastrowid
        cur.execute("select * from TODO where id = ?", (id,))
        row = cur.fetchone()
        self.post(room, prnformat(row))

    def handle_list_all(self, cur, room, whom, event, args):
        """#todo list-all"""
        cur.execute("select * from TODO where username = ?", (whom,))
        for row in cur:
            self.buffered_post(room, prnformat(row))
        self.flush_buf(room)

    def handle_list_done(self, cur, room, whom, event, args):
        """#todo list-done"""
        cur.execute("select * from TODO where username = ? AND status = 1", (whom,))
        for row in cur:
            self.buffered_post(room, prnformat(row))
        self.flush_buf(room)

    def handle_list(self, cur, room, whom, event, args):
        """#todo list"""
        cur.execute("select * from TODO where username = ? AND status = 0", (whom,))
        i = None
        for i, row in enumerate(cur):
            self.buffered_post(room, prnformat(row))
        if i is None:
            self.buffered_post(room, 'nothing found for %s'%(whom,))
        self.flush_buf(room)

    def handle_listof_all(self, cur, room, whom, event, args):
        """#todo listof-all [nickname]"""
        whose = args[2]
        cur.execute("select * from TODO where username = ?", (whose,))
        for row in cur:
            self.buffered_post(room, prnformat(row))
        self.flush_buf(room)

    def handle_listof_done(self, cur, room, whom, event, args):
        """#todo listof-done [nickname]"""
        whose = args[2]
        cur.execute("select * from TODO where username = ? AND status = 1", (whose,))
        for row in cur:
            self.buffered_post(room, prnformat(row))
        self.flush_buf(room)

    def handle_listof(self, cur, room, whom, event, args):
        """#todo listof [nickname]"""
        whose = args[2]
        cur.execute("select * from TODO where username = ? AND status = 0", (whose,))
        for row in cur:
            self.buffered_post(room, prnformat(row))
        self.flush_buf(room)
    
    def handle_list_everything(self, cur, room, whom, event, args):
        """#todo list-everything"""
        cur.execute("select * from TODO")
        for row in cur:
            self.buffered_post(room, prnformat(row))
        self.flush_buf(room)

    def handle_done(self, cur, room, whom, event, args):
        """#todo done [id]"""
        if(args[2].isdigit()):
            id = int(args[2])
            cur.execute("select (username) from TODO where id = ?", (id,))
            usernames = cur.fetchone()
            if(usernames == None):
                self.post(room, "そんな予定はない")
            elif(usernames[0][0] == '@' or usernames[0] == whom):
                cur.execute("update TODO set status =1 WHERE id = ?;", (args[2],))
                cur.execute("select * from TODO where id = ?", (id,))
                row = cur.fetchone()
                self.post(room, prnformat(row))
            else:
                self.post(room, "それはお前の予定じゃない")
        else:
            self.post(room, "そもそも予定じゃない")

    def handle_del(self, cur, room, whom, event, args):
        """#todo del [id]"""
        if(args[2].isdigit()):
            id = int(args[2])
            cur.execute("select (username) from TODO where id = ?", (id,))
            usernames = cur.fetchone()
            if(usernames == None):
                self.post(room, "そんな予定はない")
            elif(usernames[0] == '@' or usernames[0] == whom):
                cur.execute("delete from TODO WHERE id = ?;", (args[2],))
                self.post(room, '削除したよ')
            else:
                self.post(room, "それはお前の予定じゃない")
        else:
            self.post(room, "そもそも予定じゃない")

    def handle_show(self, cur, room, whom, event, args):
        """#todo show [id]"""
        if(args[2].isdigit()):
            id = int(args[2])
            cur.execute("select * from TODO where id = ?", (id,))
            row = cur.fetchone()
            if(row == None):
                self.post(room, "そんな予定はない")
            else:
                self.post(room, prnformat(row))
        else:
            self.post(room, "そもそも予定じゃない")

    def handle_sudodel(self, cur, room, whom, event, args):
        """#todo sudodel [id]"""
        if(args[2].isdigit()):
            if self.is_admin(whom):
                id = int(args[2])
                cur.execute("select (username) from TODO where id = ?", (id,))
                usernames = cur.fetchone()
                if(usernames == None):
                    self.post(room, "そんな予定はない")
                else:
                    cur.execute("delete from TODO WHERE id = ?;", (args[2],))
                    self.post(room, '削除したよ')
            else:
                self.post(room, 'sudoersに入ってないよ')
        else:
            self.post(room, "そもそも予定じゃない")

    def handle_debug(self, cur, room, whom, event, args):
        """#todo debug [id]"""
        if self.is_admin(whom):
            if(args[2].isdigit()):
                cur.execute("select (username) from TODO where id = ?", (int(args[2]),))
                print(str(cur.fetchone()))

    def handle_about(self, cur, room, whom, event, args):
        """#todo about"""
        self.buffered_post(room, "To Do Bot ")
        self.buffered_post(room, gitsha1.Id + ' on ' + sys.version)
        self.buffered_post(room, "It provides task management feature to lingr room.")
        self.buffered_post(room, "see https://github.com/akechi/todobot")
        self.flush_buf(room)


    def serve_as_cgi(self, content_length):
        print('Content-type: text/html\n')
        query = sys.stdin.read(content_length)
        array = json.loads(query)
        events = array['events']
        for event in events:
            self.handle(event)
                
        
if __name__ == '__main__':
    bot = ToDoBot(b'lion', bot_secret=open('todo.txt', mode='rb').read(), dbpath='todo.sqlite')
    bot.serve_as_cgi(int(os.environ['CONTENT_LENGTH']))


