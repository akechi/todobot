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



TEST = True

class ToDoBot(object):
    def __init__(self, bot_id, bot_secret):
        self.bot_id = bot_id
        if bot_secret:
            self.verifier = hashlib.sha1(bot_id + bot_secret).hexdigest()
        else:
            self.verifier = None

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


if TEST:
    bot = ToDoBot('lion', bot_secret=None)
else:
    bot = ToDoBot('lion', bot_secret=open('todo.txt').read())


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

def main():
    print 'Content-type: text/html\n'
    content_length = int(os.environ['CONTENT_LENGTH'])
    query = sys.stdin.read(content_length)
    array = json.loads(query)
    events = array['events']
    for event in events:
        args = event['message']['text'].split()
        room = event['message']['room']
        if(args[0] == '#todo'):
            try:
                con = sqlite3.connect('todo.sql', isolation_level=None)
                con.text_factory=str
                    
                if(len(args) == 1):
                    bot.post(room, 'Please "#todo help"')
                    
                elif(args[1] == 'help'):
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
                    
                elif(args[1] == 'add'):
                    c = con.cursor()
                    nickname = event['message']['speaker_id']
                    text = ' '.join(args[2:])
                    c.execute(u"insert into TODO (username, description, created_at, status) values (?, ?, datetime('now', 'localtime'), 0);", (nickname, unicode(text)))
                    id = c.lastrowid
                    c.execute(u"select * from TODO where id = ?", (id,))
                    row = c.fetchone()
                    bot.post(room, prnformat(row))
                    
                elif(args[1] == 'addto'):
                    c = con.cursor()
                    nickname = args[2]
                    text = ' '.join(args[3:])
                    text += ' (by %s) ' % event['message']['speaker_id']
                    c.execute(u"insert into TODO (username, description, created_at, status) values (?, ?, datetime('now', 'localtime'), 0);", (nickname, unicode(text)))
                    id = c.lastrowid
                    c.execute(u"select * from TODO where id = ?", (id,))
                    row = c.fetchone()
                    bot.post(room, prnformat(row))
                    
                elif(args[1] == 'list-all'):
                    nickname = event['message']['speaker_id']
                    c = con.cursor()
                    c.execute(u"select * from TODO where username = ?", (nickname,))
                    for row in c:
                        bot.post(room, prnformat(row))
                        
                elif(args[1] == 'list-done'):
                    nickname = event['message']['speaker_id']
                    c = con.cursor()
                    c.execute(u"select * from TODO where username = ? AND status = 1", (nickname,))
                    for row in c:
                        bot.post(room, prnformat(row))
                    
                elif(args[1] == 'list'):
                    nickname = event['message']['speaker_id']
                    c = con.cursor()
                    c.execute(u"select * from TODO where username = ? AND status = 0", (nickname,))
                    for row in c:
                        bot.post(room, prnformat(row))
                    
                elif(args[1] == 'listof-all'):
                    nickname = args[2]
                    c = con.cursor()
                    c.execute(u"select * from TODO where username = ?", (nickname,))
                    for row in c:
                        bot.post(room, prnformat(row))
                    
                elif(args[1] == 'listof-done'):
                    nickname = args[2]
                    c = con.cursor()
                    c.execute(u"select * from TODO where username = ? AND status = 1", (nickname,))
                    for row in c:
                        bot.post(room, prnformat(row))
                    
                elif(args[1] == 'listof'):
                    nickname = args[2]
                    c = con.cursor()
                    c.execute(u"select * from TODO where username = ? AND status = 0", (nickname,))
                    for row in c:
                        bot.post(room, prnformat(row))
                    
                elif(args[1] == 'list-everything'):
                    c = con.cursor()
                    c.execute(u"select * from TODO")
                    for row in c:
                        bot.post(room, prnformat(row))
                    
                elif(args[1] == 'done'):
                    if(args[2].isdigit()):
                        nickname = event['message']['speaker_id']
                        id = int(args[2])
                        c = con.cursor()
                        c.execute(u"select (username) from TODO where id = ?", (id,))
                        usernames = c.fetchone()
                        if(usernames == None):
                            bot.post(room, "そんな予定はない")
                        elif(usernames[0][0] == '@' or usernames[0] == nickname):
                            c.execute(u"update TODO set status =1 WHERE id = ?;", (args[2],))
                            c.execute(u"select * from TODO where id = ?", (id,))
                            row = c.fetchone()
                            bot.post(room, prnformat(row))
                        else:
                            bot.post(room, "それはお前の予定じゃない")
                    else:
                        bot.post(room, "そもそも予定じゃない")
                        
                elif(args[1] == 'del'):
                    if(args[2].isdigit()):
                        nickname = event['message']['speaker_id']
                        id = int(args[2])
                        c = con.cursor()
                        c.execute(u"select (username) from TODO where id = ?", (id,))
                        usernames = c.fetchone()
                        if(usernames == None):
                            bot.post(room, "そんな予定はない")
                        elif(usernames[0] == '@' or usernames[0] == nickname):
                            c.execute(u"delete from TODO WHERE id = ?;", (args[2],))
                            bot.post(room, '削除したよ')
                        else:
                            bot.post(room, "それはお前の予定じゃない")
                    else:
                        bot.post(room, "そもそも予定じゃない")
                        
                elif(args[1] == 'show'):
                    if(args[2].isdigit()):
                        nickname = event['message']['speaker_id']
                        id = int(args[2])
                        c = con.cursor()
                        c.execute(u"select * from TODO where id = ?", (id,))
                        row = c.fetchone()
                        if(row == None):
                            bot.post(room, "そんな予定はない")
                        else:
                            bot.post(room, prnformat(row))
                    else:
                        bot.post(room, "そもそも予定じゃない")
                        
                elif(args[1] == 'sudodel'):
                    if(args[2].isdigit()):
                        nickname = event['message']['speaker_id']
                        if(nickname == 'aoisensi'):
                            id = int(args[2])
                            c = con.cursor()
                            c.execute(u"select (username) from TODO where id = ?", (id,))
                            usernames = c.fetchone()
                            if(usernames == None):
                                bot.post(room, "そんな予定はない")
                            else:
                                c.execute(u"delete from TODO WHERE id = ?;", (args[2],))
                                bot.post(room, '削除したよ')
                        else:
                            bot.post(room, 'sudoersに入ってないよ')
                    else:
                        bot.post(room, "そもそも予定じゃない")
                        
                elif(args[1] == 'debug' and 'aoisensi' == event['message']['speaker_id'] ):
                    if(args[2].isdigit()):
                        nickname = event['message']['speaker_id']
                        c = con.cursor()
                        c.execute(u"select (username) from TODO where id = ?", (int(args[2]),))
                        print str(c.fetchone())
                
            except Exception as e:
                print str(type(e))
                print str(e.args)
                print e.message
                    
            finally:
                con.close()
        
if __name__ == '__main__':
    main()

