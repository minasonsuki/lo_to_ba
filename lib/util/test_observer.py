#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import io
import sys
import unittest
import time

workspace_path = os.path.dirname(os.path.abspath(__file__))
os.chdir(workspace_path)

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../../lib/utils")
from conf import Conf
from log import Log
from observer import Observer

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


class Observer_test(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.log = Log.getLogger()
        cls.log.info("\n\n" + __class__.__name__ + "." + sys._getframe().f_code.co_name + " finished.\n---------- start ---------")

    def setUp(self):
        self.ob = Observer()

    """
    def test_run_and_end(self):
        self.log.debug(__class__.__name__ + "." + sys._getframe().f_code.co_name + " start")
        self.ob.run()
        time.sleep(1)
        self.ob.end()
        self.log.debug(__class__.__name__ + "." + sys._getframe().f_code.co_name + " finished")

    def test_with(self):
        self.log.debug(__class__.__name__ + "." + sys._getframe().f_code.co_name + " start")
        with Observer() as ob:
            time.sleep(1)
        self.log.debug(__class__.__name__ + "." + sys._getframe().f_code.co_name + " finished")

    def test_message(self):
        self.log.debug(__class__.__name__ + "." + sys._getframe().f_code.co_name + " start")
        self.ob.run(message="test_message")
        time.sleep(1)
        self.ob.end()        
        self.log.debug(__class__.__name__ + "." + sys._getframe().f_code.co_name + " finished")

    def test_message_with(self):
        self.log.debug(__class__.__name__ + "." + sys._getframe().f_code.co_name + " start")
        with Observer(message="test_message_with") as ob:
            time.sleep(1)
        self.log.debug(__class__.__name__ + "." + sys._getframe().f_code.co_name + " finished")
    """
    def test_logfile(self):
        with Observer(logfile="observe_log.txt", message="test_logfile") as ob:
            time.sleep(1)
        


    """
    def test_(self):
        self.log.debug(__class__.__name__ + "." + sys._getframe().f_code.co_name + " start")
        self.log.debug(__class__.__name__ + "." + sys._getframe().f_code.co_name + " finished")
    """


if __name__ == '__main__':
    unittest.main()
