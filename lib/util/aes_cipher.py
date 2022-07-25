#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto import Random
import ast
from pathlib import Path

sys.path.append(f"{os.path.dirname(os.path.abspath(__file__))}/../../lib/utils")
from conf import Conf as conf
from log import Log, with_standard_log


class AESCipher():
    def __init__(self, log=None):
        if log is None:
            self.log = Log.getLogger()
        else:
            self.log = log
        self.log.debug(f"{__class__.__name__}.{sys._getframe().f_code.co_name} started.")
        self.log.debug(f"{__class__.__name__}.{sys._getframe().f_code.co_name} finished.")

    @with_standard_log
    def create_aes(self, passwd, initial_vector):
        sha = SHA256.new()
        sha.update(passwd.encode())
        key = sha.digest()
        return AES.new(key, AES.MODE_CFB, initial_vector)

    def encrypt(self, data, passwd):
        default_char_code = conf.get("default_char_code")
        initial_vector = Random.new().read(AES.block_size)
        return initial_vector + self.create_aes(passwd, initial_vector).encrypt(data.encode(default_char_code))

    def decrypt(self, data, passwd):
        initial_vector, cipher = data[:AES.block_size], data[AES.block_size:]
        return self.create_aes(passwd, initial_vector).decrypt(cipher)

    def decrypt_from_file(self, encrypted_filename, encrypt_password, data_format="JSON"):
        default_char_code = conf.get("default_char_code")
        encrypted_file = Path(encrypted_filename)
        if not encrypted_file.exists():
            print(f"encrypt_file[{encrypted_filename}] doesnt exist. return False")
            return False

        if data_format not in ["JSON"]:
            print(f"data format[{data_format}] is unavailable. return False")
            return False

        if data_format == "JSON":
            with open(encrypted_file, "rb") as f:
                data = ast.literal_eval(str(self.decrypt(f.read(), encrypt_password).decode(default_char_code)))
                return data
        return False

    """
    @with_standard_log
    def (self):
        import pdb; pdb.set_trace()

    def (self):
        self.log.debug(f"{__class__.__name__}.{sys._getframe().f_code.co_name} started.")
        self.log.debug(f"{__class__.__name__}.{sys._getframe().f_code.co_name} finished.")
        self.log.error(f"{__class__.__name__}.{sys._getframe().f_code.co_name}")
        try:
            pass
        except(Exception) as e:
            self.log.error(f"ERROR: caught exception at {__class__.__name__}.{sys._getframe().f_code.co_name}")
            self.log.exception("[[" + e.__class__.__name__ + " EXCEPTON OCCURED]]: %s", e)
            self.log.error("traceback:\n", stack_info=True, exc_info=True)
            raise e
    """
