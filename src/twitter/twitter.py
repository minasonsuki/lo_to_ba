#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import getpass
from time import sleep
from selenium import webdriver
import chromedriver_binary
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

sys.path.append(f"{os.path.dirname(os.path.abspath(__file__))}/../../lib/util")
from conf import Conf
from log import Log, with_standard_log


class Twitter():
    def __init__(self, log=None):
        if log is None:
            self.log = Log.getLogger()
        else:
            self.log = log
        self.log.debug(f"{__class__.__name__}.{sys._getframe().f_code.co_name} started.")
        self.twitter_id = input('twitter id> ')
        self.twitter_passwd = getpass.getpass('twitter passwd(hidden)> ')
        self.log.debug(f"{__class__.__name__}.{sys._getframe().f_code.co_name} finished.")

    @with_standard_log
    def create_driver(self):
        self.options = Options()
        for option in Conf.get("chrome_options"):
            self.log.debug("options += " + str(option))
            self.options.add_argument("--" + option)
        self.driver = webdriver.Chrome(options=self.options)
        return self.driver

    @with_standard_log
    def login_by_driver(self, driver):
        xpath = '//input[@id="username_or_email"]'
        element = driver.find_element(By.XPATH, xpath)
        element.send_keys(self.twitter_id)
        xpath = '//input[@id="password"]'
        element = driver.find_element(By.XPATH, xpath)
        element.send_keys(self.twitter_passwd)
        xpath = '//input[@class="submit button selected"]'
        element = driver.find_element(By.XPATH, xpath)
        element.click()
        sleep(10)

        cookies = {
            cookie['name']: cookie['value']
            for cookie in driver.get_cookies()
        }

        return self.driver, cookies

    """
    @with_standard_log
    def (self):
        import ipdb; ipdb.set_trace()
        try:
            pass
        except(Exception) as e:
            self.log.error(f"ERROR: caught exception at {__class__.__name__}.{sys._getframe().f_code.co_name}")
            self.log.exception("[[" + e.__class__.__name__ + " EXCEPTION OCCURED]]: %s", e)
            self.log.error("traceback:\n", stack_info=True, exc_info=True)
            raise e
    """
