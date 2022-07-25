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
from pathlib import Path

sys.path.append(f"{os.path.dirname(os.path.abspath(__file__))}/../../lib/util")
from conf import Conf
from log import Log, with_standard_log
from aes_cipher import AESCipher


class Twitter():
    def __init__(self, log=None):
        if log is None:
            self.log = Log.getLogger()
        else:
            self.log = log
        self.log.debug(f"{__class__.__name__}.{sys._getframe().f_code.co_name} started.")
        self.cipher = AESCipher(log=self.log)
        encrypted_file = Path(f"{Conf.get('dir_certification')}/{Conf.get('twitter_key_file')}")
        if not encrypted_file.parent.is_dir():
            os.makedirs(encrypted_file.parent, exist_ok=True)
        encrypt_password = getpass.getpass('twitterログイン情報の暗号化用パスワード(hidden)> ')
        confirm_password = getpass.getpass('確認(hidden)> ')
        if encrypt_password != confirm_password:
            print("パスワードが一致していません。プログラム終了")
            sys.exit(0)
        if not encrypted_file.exists():
            self.twitter_id = input('twitter id> ')
            self.twitter_passwd = getpass.getpass('twitter passwd(hidden)> ')
            data = {"twitter id": self.twitter_id, "twitter_passwd": self.twitter_passwd}
            encrypted_data = self.cipher.encrypt(str(data), encrypt_password)
            with open(encrypted_file, "wb") as f:
                f.write(encrypted_data)
        else:
            with open(encrypted_file, "rb") as f:
                decrypted_data = self.cipher.decrypt_from_file(encrypted_file, encrypt_password, data_format="JSON")
            self.twitter_id = decrypted_data["twitter id"]
            self.twitter_passwd = decrypted_data["twitter_passwd"]

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
