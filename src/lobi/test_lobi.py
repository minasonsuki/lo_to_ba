#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import io
import sys
import unittest
import requests

workspace_path = f"{os.path.dirname(os.path.abspath(__file__))}/../../test/workspace"
os.chdir(workspace_path)

sys.path.append(f"{os.path.dirname(os.path.abspath(__file__))}/../../lib/util")
from conf import Conf
from log import Log, with_standard_log

sys.path.append(f"{os.path.dirname(os.path.abspath(__file__))}/../../src/lobi")
from lobi import Lobi

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


class TemplateTest(unittest.TestCase):

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
        self.lobi = Lobi(log=self.log)

    # @with_standard_log
    # def test_login_by_twitter(self):
    #     cookies = self.lobi.login(by="twitter")
    #     response = requests.get("https://web.lobi.co/api/groups?count=1000&page=1", cookies=cookies)
    #     print(response.text)

    # @with_standard_log
    # def test_replace_groupname_string(self):
    #     print(self.lobi.replace_groupname_string("あああ"))
    #     print(self.lobi.replace_groupname_string("a, b"))
    #     print("a\nb")
    #     print(self.lobi.replace_groupname_string("a, b"))
    #     print(self.lobi.replace_groupname_string("back\slash"))

    @with_standard_log
    def test_replace_dirname_string(self):
        string = "\\-/-:-*-\"-<->-|-.-?"
        print(f"before: {string}")
        print(f"after: {self.lobi.replace_dirname_string(string)}")

    # @with_standard_log
    # def test_save_lobi_user_icon(self):
    #     url = "https://assets.nakamap.com/img/user/0dd17e7db69a0db26e1415e1e49df0c45751f78f_72.png"
    #     user_id = "997083246946791424"
    #     group_name = "トムソンギルド会議3"
    #     save_path = f"{Conf.get('dir_output')}/{group_name}/img/icon/{user_id}{os.path.splitext(url)[1]}"

    #     # result = self.nakamap.save_lobi_image(url, save_path=save_path, mode="user", user_id=user_id)
    #     result = self.nakamap.save_lobi_image(url, save_path=save_path)
    #     print(f"result: {result}")

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
