#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import time
import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../../lib/utils")
from conf import Conf as conf
from log import Log
from singleton import Singleton


# class Observer(metaclass=Singleton):
class Observer():
    def __init__(self, logfile=None, stdout=True, message=None, log=None):
        if log is None:
            self.log = Log.getLogger()
        else:
            self.log = log
        self.log.debug(__class__.__name__ + "." + sys._getframe().f_code.co_name + " start")
        self.log.debug("logfile: " + str(logfile) + ", stdout: " + str(stdout) + ", message: " + str(message) + ", id: " + str(id(self)))
        self.logfile = logfile
        self.stdout = stdout
        self.message = message
        self.start = None
        self.log.debug(__class__.__name__ + "." + sys._getframe().f_code.co_name + " finished")

    def __enter__(self):
        self.run(message=self.message)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.end()
        pass

    def run(self, message=None):
        self.log.debug(__class__.__name__ + "." + sys._getframe().f_code.co_name + " start")
        if not self.start is None:
            self.log.error("!None")
        self.start = time.time()
        self.message = message
        self.log.debug(__class__.__name__ + "." + sys._getframe().f_code.co_name + " finished")

    def end(self):
        elapsed_time = time.time() - self.start
        self.start = None
        
        if self.message:
            m = str(datetime.datetime.now()) + ":" + self.message + " elapsed_time[sec]:{0}".format(elapsed_time)
        else:
            m =  str(datetime.datetime.now()) + ":elapsed_time[sec]:{0}".format(elapsed_time)
        
        if self.stdout:
            print (m)
        if not self.logfile is None:
            self.log.debug("add message to " + self.logfile)
            with open(self.logfile, mode="a") as f:
                print(m, file=f)
        return m
