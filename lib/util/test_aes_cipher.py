#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import unittest
import codecs
import ast
import getpass
from pathlib import Path
sys.path.append(f"{os.path.dirname(os.path.abspath(__file__))}/../../lib/utils")
from conf import Conf
from log import Log, with_standard_log
from aes_cipher import AESCipher

workspace_path = f"{os.path.dirname(os.path.abspath(__file__))}/../../test/workspace"
os.chdir(workspace_path)
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


class AESCipherTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls, log=None):
        with open("../../log/log", "w"):
            pass
        if log is None:
            cls.log = Log.getLogger()
        else:
            cls.log = log
        cls.log.info(f"\n\n{__class__.__name__}.{sys._getframe().f_code.co_name} finished.\n---------- start ---------")

    def setUp(self):
        self.cipher = AESCipher(log=self.log)

    @with_standard_log
    def test_encrypt_and_create_file(self):
        print("create encrypted file")
        encrypted_file = Path(f"{Conf.get('dir_certification')}/{Conf.get('twitter_key_file')}")
        if encrypted_file.parent.is_dir() is False:
            os.makedirs(encrypted_file.parent, exist_ok=True)

        encrypt_password = getpass.getpass('encrypt password(hidden)> ')
        confirm_password = getpass.getpass('confirm(hidden)> ')
        if encrypt_password != confirm_password:
            print("Passwords dont match. exit(0)")
            sys.exit(0)
        uid = getpass.getpass('twitter id(hidden)> ')
        passwd = getpass.getpass('twitter passwd(hidden)> ')
        data = {"uid": uid, "passwd": passwd}
        encrypted_data = self.cipher.encrypt(str(data), encrypt_password)

        with open(encrypted_file, "wb") as f:
            f.write(encrypted_data)

        return True

    @with_standard_log
    def test_decrypt_from_file(self):
        encrypted_file = Path(f"{Conf.get('dir_certification')}/{Conf.get('twitter_key_file')}")
        if not encrypted_file.parent.is_dir():
            print(f"password directory[{encrypted_file.parent.resolve()}] doesnt exist. mkdir or check config.yml. exit 0")
            sys.exit(0)

        encrypt_password = getpass.getpass('encrypt password(hidden)> ')
        confirm_password = getpass.getpass('confirm(hidden)> ')
        if encrypt_password != confirm_password:
            print("Passwords dont match. exit(0)")
            sys.exit(0)

        with open(encrypted_file, "rb") as f:
            twitter_key = ast.literal_eval(str(self.cipher.decrypt(f.read(), encrypt_password)))
        print(f"twitter_key: {twitter_key}")

    # @with_standard_log
    # def test_decrypt_from_file(self):
    #     result = self.cipher.decrypt_from_file(f"{Conf.get('dir_certification')}/{Conf.get('twitter_key_file')}", "F", data_format="JSON")
    #     print(f"result:{result}")

    """
    @with_standard_log
    def test_(self):
        print(f"result:{result}")

        import pdb; pdb.set_trace()
        self.log.error(f"{__class__.__name__}.{sys._getframe().f_code.co_name}")
    """


if __name__ == '__main__':
    unittest.main()
