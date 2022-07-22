#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import io
import sys
import unittest
import codecs
import requests

workspace_path = f"{os.path.dirname(os.path.abspath(__file__))}/../../test/workspace"
os.chdir(workspace_path)

sys.path.append(f"{os.path.dirname(os.path.abspath(__file__))}/../../lib/util")
from conf import Conf
from log import Log, with_standard_log

sys.path.append(f"{os.path.dirname(os.path.abspath(__file__))}/../../src/twitter")
from twitter import Twitter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


class TwitterTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls, log=None):
        with open(f"{os.path.dirname(os.path.abspath(__file__))}/../../log/log", "w"):
            pass
        if log is None:
            cls.log = Log.getLogger()
        else:
            cls.log = log
        cls.log.info(f"\n\n{__class__.__name__}.{sys._getframe().f_code.co_name} finished.\n---------- start ---------")

    def setUp(self):
        self.twitter = Twitter(log=self.log)
        self.driver = self.twitter.create_driver()
        self.driver.get("https://lobi.co/signup/twitter")

    @with_standard_log
    def test_login_by_driver(self):
        driver, cookies = self.twitter.login_by_driver(self.driver)
        response = requests.get(
            "https://web.lobi.co/api/groups?count=20&page=1",
            cookies=cookies)
        groups = response.text
        # groups = self.session.get("https://web.lobi.co/api/groups?count=20&page=1")
        with codecs.open("groups.txt", mode="w", encoding="utf-8") as f:
            f.write(groups)

    """
    @with_standard_log
    def test_(self):
        result = 
        print(f"result:{result}")
        self.assertEqual("_test", result)
        self.assertNotEqual("_test", result)
        self.assertTrue(result)
        self.aasertFalse(result)
        import ipdb; ipdb.set_trace()
        try:
            pass
        except(Exception) as e:
            self.log.error(f"ERROR: caught exception at {__class__.__name__}.{sys._getframe().f_code.co_name}")
            self.log.exception("[[" + e.__class__.__name__ + " EXCEPTION OCCURED]]: %s", e)
            self.log.error("traceback:\n", stack_info=True, exc_info=True)
            raise e
    """


if __name__ == '__main__':
    unittest.main()
