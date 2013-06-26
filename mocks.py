#!/usr/bin/python
# -*- coding: utf-8 -*-



class LingrUser(object):
    def __init__(self, username):
        self.username = username

    def say(self, text):
        req = """{"events":[{"message":{"text":"%s","speaker_id":"%s","room":"computer_science"}}]}"""

        return req%(text, self.username)



