#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
import re
import _sre

from lib.remod import *


class RemodTestCase(unittest.TestCase):
    def setUp(self):
        self.text = 'abc'
        self.x = named('a', 'a')
        
    def test_compile(self): 
        self.assertEqual("(?P<_a>a(?:))",self.x.make(''))

        got = self.x.compile()
        self.assertIsNotNone(got.rx)# _sre.SRE_Pattern


    def test_foo(self):
        r = self.x.compile()
        m = r.match(self.text)
        self.assertIsNotNone(m.mo)


if __name__ == '__main__':
    unittest.main()
