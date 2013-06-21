#!/usr/bin/python
# -*- coding: utf-8 -*-

#id username description created_at status

import re
import os
import sys
import json
import urllib
import urllib2
import hashlib
import sqlite3




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
    def __init__(self, bot_id, bot_secret):
        self.bot_id = bot_id
        if bot_secret:
            self.verifier = hashlib.sha1(bot_id + bot_secret).hexdigest()
        else:
            self.verifier = None
        self.con = sqlite3.connect('todo.sql', isolation_level=None)
        self.con.text_factory = str

    def post(self, room, text):
        '''
            FIXME: return values, timeoout

        '''
        if self.verifier:
            req = {'room':room, 'bot':self.bot_id, 'text':text, 'bot_verifier':self.bot_verifier}
            params = urllib.urlencode(req)
            r = urllib2.urlopen('http://lingr.com/api/room/say?' + params)
        else:
            print >> sys.stderr, room, ":", text

    def handle(self, event):
        args = event['message']['text'].split()
        room = event['message']['room']
        if args[0]  != '#todo':
            return
        if len(args) == 1:
            self.post(room, 'Please "#todo help"')
            return
        
        command = 'handle_' + args[1].replace('-', '_') #FIXME unsafe!!
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
            r = method(cur, whom, event, args)
        except Exception as e:
            print str(type(e))
            print str(e.args)
            print e.message
                    
        finally:
            self.con.commit()


    def handle_help(self, event, args):
        sys.stdout.write("""#todo add [description]
#todo list
#todo done [id]
#todo del [id]
#todo addto [nickname] [description]
#todo listof [nickname]
#todo listof-all [nickname]
#todo listof-done [nickname]
#todo show [id]

このボットはあるふぁばんです
何があっても知りません""")

    def handle_add(self, cur, whom , event, args):
        text = ' '.join(args[2:])
        cur.execute(u"insert into TODO (username, description, created_at, status) values (?, ?, datetime('now', 'localtime'), 0);", (whom, unicode(text)))
        id = c.lastrowid
        cur.execute(u"select * from TODO where id = ?", (id,))
        row = c.fetchone()
        self.post(room, prnformat(row))

    def handle_addto(self, cur, whom, event, args):
        nickname = args[2] #target
        text = ' '.join(args[3:])
        text += ' (by %s) ' % whom #event['message']['speaker_id']
        cur.execute(u"insert into TODO (username, description, created_at, status) values (?, ?, datetime('now', 'localtime'), 0);", (nickname, unicode(text)))
        id = c.lastrowid
        cur.execute(u"select * from TODO where id = ?", (id,))
        row = c.fetchone()
        self.post(room, prnformat(row))

    def handle_list_all(self, cur, whom, event, args):
        cur.execute(u"select * from TODO where username = ?", (whom,))
        for row in c:
            self.post(room, prnformat(row))

    def handle_list_done(self, cur, whom, event, args):
        cur.execute(u"select * from TODO where username = ? AND status = 1", (whom,))
        for row in c:
            self.post(room, prnformat(row))

    def handle_list(self, cur, whom, event, args):
        """elif(args[1] == 'list'):"""
        cur.execute(u"select * from TODO where username = ? AND status = 0", (whom,))
        for row in c:
            self.post(room, prnformat(row))

    def handle_listof_all(self, cur, whom, event, args):
        """elif(args[1] == 'listof-all'):"""
        whose = args[2]
        cur.execute(u"select * from TODO where username = ?", (whose,))
        for row in c:
            self.post(room, prnformat(row))

    def handle_listof_done(self, cur, whom, event, args):
        """elif(args[1] == 'listof-done'):"""
        whose = args[2]
        cur.execute(u"select * from TODO where username = ? AND status = 1", (whose,))
        for row in c:
            self.post(room, prnformat(row))

    def handle_listof(self, cur, whom, event, args):
        """elif(args[1] == 'listof'):"""
        whose = args[2]
        cur.execute(u"select * from TODO where username = ? AND status = 0", (whose,))
        for row in c:
            self.post(room, prnformat(row))
    
    def handle_list_everything(self, cur, whom, event, args):
        """elif(args[1] == 'list-everything'):"""
        cur.execute(u"select * from TODO")
        for row in c:
            self.post(room, prnformat(row))

    def handle_done(self, cur, whom, event, args):
        """elif(args[1] == 'done'):"""
        if(args[2].isdigit()):
            id = int(args[2])
            cur.execute(u"select (username) from TODO where id = ?", (id,))
            usernames = c.fetchone()
            if(usernames == None):
                self.post(room, "そんな予定はない")
            elif(usernames[0][0] == '@' or usernames[0] == whom):
                cur.execute(u"update TODO set status =1 WHERE id = ?;", (args[2],))
                cur.execute(u"select * from TODO where id = ?", (id,))
                row = c.fetchone()
                self.post(room, prnformat(row))
            else:
                self.post(room, "それはお前の予定じゃない")
        else:
            self.post(room, "そもそも予定じゃない")

    def handle_del(self, cur, whom, event, args):
        """elif(args[1] == 'del'):"""
        if(args[2].isdigit()):
            id = int(args[2])
            cur.execute(u"select (username) from TODO where id = ?", (id,))
            usernames = c.fetchone()
            if(usernames == None):
                self.post(room, "そんな予定はない")
            elif(usernames[0] == '@' or usernames[0] == whom):
                cur.execute(u"delete from TODO WHERE id = ?;", (args[2],))
                self.post(room, '削除したよ')
            else:
                self.post(room, "それはお前の予定じゃない")
        else:
            self.post(room, "そもそも予定じゃない")

    def handle_show(self, cur, whom, event, args):
        """elif(args[1] == 'show'):"""
        if(args[2].isdigit()):
            id = int(args[2])
            cur.execute(u"select * from TODO where id = ?", (id,))
            row = c.fetchone()
            if(row == None):
                self.post(room, "そんな予定はない")
            else:
                self.post(room, prnformat(row))
        else:
            self.post(room, "そもそも予定じゃない")

    def handle_sudodel(self, cur, whom, event, args):
        """elif(args[1] == 'sudodel'):"""
        if(args[2].isdigit()):
            if(whom == 'aoisensi'):
                id = int(args[2])
                cur.execute(u"select (username) from TODO where id = ?", (id,))
                usernames = c.fetchone()
                if(usernames == None):
                    self.post(room, "そんな予定はない")
                else:
                    cur.execute(u"delete from TODO WHERE id = ?;", (args[2],))
                    self.post(room, '削除したよ')
            else:
                self.post(room, 'sudoersに入ってないよ')
        else:
            self.post(room, "そもそも予定じゃない")

    def handle_debug(self, cur, whom, event, args):
        """elif(args[1] == 'debug' """
        if 'aoisensi' == event['message']['speaker_id']:
            if(args[2].isdigit()):
                cur.execute(u"select (username) from TODO where id = ?", (int(args[2]),))
                print str(c.fetchone())


TEST = True

if TEST:
    bot = ToDoBot('lion', bot_secret=None)
else:
    bot = ToDoBot('lion', bot_secret=open('todo.txt').read())


def serve_as_cgi(content_length):
    print 'Content-type: text/html\n'
    query = sys.stdin.read(content_length)
    array = json.loads(query)
    events = array['events']
    for event in events:
        bot.handle(event)
                
        
if __name__ == '__main__':
    if TEST:
        import sys
        with open(sys.argv[2], 'w') as fout:
            with open(sys.argv[1], 'r') as fin:
                fin.seek(0, os.SEEK_END)
                count = fin.tell()
                fin.seek(0, os.SEEK_SET)
                sys.stdin = fin
                sys.stdout = fout
                serve_as_cgi(count)
    else:
        serve_as_cgi(int(os.environ['CONTENT_LENGTH']))



