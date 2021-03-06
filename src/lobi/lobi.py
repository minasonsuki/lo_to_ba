#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from time import sleep
import requests
from bs4 import BeautifulSoup
import urllib
import re
import codecs
import csv
import json
from json.decoder import WHITESPACE
from datetime import datetime, timedelta, timezone
import getpass
import shutil
from pathlib import Path
from requests.exceptions import ConnectionError

sys.path.append(f"{os.path.dirname(os.path.abspath(__file__))}/../../lib/util")
from conf import Conf
from log import Log, with_standard_log
from observer import Observer
from aes_cipher import AESCipher

sys.path.append(f"{os.path.dirname(os.path.abspath(__file__))}/../../src/twitter")
from twitter import Twitter


class Lobi():
    def __init__(self, log=None):
        if log is None:
            self.log = Log.getLogger()
        else:
            self.log = log
        self.log.debug(f"{__class__.__name__}.{sys._getframe().f_code.co_name} started.")
        # self.user_img_dict = {}
        self.re_groupname = re.compile(r"\n|,|\\| |\?")
        self.re_dirname = re.compile(r"/|\*|\||\\|:|\"|\<|\>|\.|\?")
        self.log.debug(f"{__class__.__name__}.{sys._getframe().f_code.co_name} finished.")

    @with_standard_log
    def login(self, by="twitter"):
        """_summary_

        Parameters
        ----------
        by : str, optional
            lobi or twitter
        """
        if by == "lobi" or by == "lobi_unhidden":
            self.cipher = AESCipher(log=self.log)
            encrypted_file = Path(f"{Conf.get('dir_certification')}/{Conf.get('lobi_key_file')}")
            if not encrypted_file.parent.is_dir():
                os.makedirs(encrypted_file.parent, exist_ok=True)
            encrypt_password = getpass.getpass('lobiログイン情報の暗号化用パスワード(hidden)> ')
            confirm_password = getpass.getpass('確認(hidden)> ')
            if encrypt_password != confirm_password:
                print("パスワードが一致していません。プログラム終了")
                sys.exit(0)
            if not encrypted_file.exists():
                lobi_email = input('lobi e-mail addres> ')
                if by == "lobi":
                    lobi_passwd = getpass.getpass('lobi passwd(hidden)> ')
                elif by == "lobi_unhidden":
                    lobi_passwd = input('lobi passwd> ')
                else:
                    self.log.error("login_by not lobi nor lobi_unhidden")
                    sys.exit(1)
                data = {"lobi_e-mail_addres": lobi_email, "lobi_passwd": lobi_passwd}
                encrypted_data = self.cipher.encrypt(str(data), encrypt_password)
                with open(encrypted_file, "wb") as f:
                    f.write(encrypted_data)
            else:
                with open(encrypted_file, "rb") as f:
                    decrypted_data = self.cipher.decrypt_from_file(encrypted_file, encrypt_password, data_format="JSON")
                lobi_email = decrypted_data["lobi_e-mail_addres"]
                lobi_passwd = decrypted_data["lobi_passwd"]

            session = requests.Session()
            lobi_login_url = "https://lobi.co/signin"
            res = session.get(lobi_login_url)
            soup = BeautifulSoup(res.text, features="html.parser")
            csrf_token = soup.find(attrs={'name': 'csrf_token'}).get('value')
            login_info = {
                "csrf_token": csrf_token,
                "email": lobi_email,
                "password": lobi_passwd
            }
            session.post(lobi_login_url, data=login_info)
            self.cookies = session.cookies
            return self.cookies
        elif by == "twitter":
            twitter = Twitter(log=self.log)
            driver = twitter.create_driver()
            driver.get("https://lobi.co/signup/twitter")
            driver, self.cookies = twitter.login_by_driver(driver)
            return self.cookies
        return None

    @with_standard_log
    def login_check(self, cookies=None):
        if cookies is None:
            cookies = self.cookies
        res = requests.get("https://web.lobi.co/api/groups?count=10000&page=1", cookies=cookies)
        if res.status_code != 200:
            self.log.error(f"login失敗。status_code[{res.status_code}]")
            sys.exit(1)
        return res

    @with_standard_log
    def create_private_group_list(self, filename="joining_private_groups", cookies=None):
        if cookies is None:
            cookies = self.cookies
        url = "https://web.lobi.co/api/groups?count=10000&page=1"
        self.log.debug(f"requests.get({url}, cookies=cookies)")
        groups = requests.get(url, cookies=cookies)
        response_status_code = groups.status_code
        self.log.debug(f"response status_code[{response_status_code}]")
        if response_status_code > Conf.get("response_status_code_error_threshold"):
            self.log.error(f"response status_code[{response_status_code}]")
            self.log.error(f"url[{url}]")

        with codecs.open(f"{Conf.get('dir_output')}/{filename}.json", "w", encoding=Conf.get("default_char_code"), errors="replace") as f:
            json.dump(groups.json(), f, indent=4, ensure_ascii=False)

        with codecs.open(f"{Conf.get('dir_output')}/{filename}.csv", "w", encoding=Conf.get("csv_char_code"), errors="ignore") as f:
            csv_writer = csv.writer(f)
            csv_writer.writerow(["name", "total_users", "uid"])
            for group in groups.json()[0]["items"]:
                csv_writer.writerow([self.replace_groupname_string(group["name"]), group["total_users"], group["uid"]])
        shutil.copyfile(f"{Conf.get('dir_output')}/{filename}.csv", f"{Conf.get('dir_output')}/original_{filename}.csv")

    @with_standard_log
    def load_private_group_json(self, filename="joining_private_groups"):
        with codecs.open(f"{Conf.get('dir_output')}/{filename}.json", "r", encoding=Conf.get("default_char_code"), errors="replace") as f:
            private_group_json = json.load(f)
        return {private_group["uid"]: private_group for private_group in private_group_json[0]["items"]}

    def replace_groupname_string(self, string):
        return self.re_groupname.sub("_", string)

    def replace_dirname_string(self, string):
        return self.re_dirname.sub("_", string)

    @with_standard_log
    def read_private_group_list(self, filename="joining_private_groups"):
        with codecs.open(f"{Conf.get('dir_output')}/{filename}.csv", "r", encoding=Conf.get("csv_char_code"), errors="replace") as f:
            reader = csv.reader(f)
            self.private_group_list = [row for row in reader][1:]
        return self.private_group_list

    @with_standard_log
    def parse_private_group_list(self, private_group_list):
        """_summary_
        return group_name, total_users, group_uid

        Parameters
        ----------
        private_group_list : _type_
            _description_

        Returns
        -------
        _type_
            return group_name, total_users, group_uid
        """
        group_name = private_group_list[0]
        total_users = private_group_list[1]
        group_uid = private_group_list[2]
        return group_name, total_users, group_uid

    @with_standard_log
    def create_empty_output_dir(self, group_name):
        group_name_for_path = self.replace_dirname_string(group_name)
        base_output_dir = f"{Conf.get('dir_output')}/{group_name_for_path}"
        for sub_dir_name in ["img/group", "img/user/icon", "img/user/cover", "img/chat"]:
            sub_dir = f"{base_output_dir}/{sub_dir_name}"
            if not os.path.exists(sub_dir):
                os.makedirs(sub_dir, exist_ok=True)
        return base_output_dir, group_name_for_path

    @with_standard_log
    def create_meta_group_json(self, group_name, group_uid, private_group_dict):
        group_name_for_path = self.replace_dirname_string(group_name)
        group_dict = private_group_dict[group_uid]
        if "icon" in group_dict:
            url = group_dict["icon"]
            group_dict["icon_path"] = self.save_lobi_image(url, f"{Conf.get('dir_output')}/{group_name_for_path}", "img/group/icon")

        if "wallpaper" in group_dict:
            url = group_dict["wallpaper"]
            group_dict["wallpaper_path"] = self.save_lobi_image(url, f"{Conf.get('dir_output')}/{group_name_for_path}", "img/group/wallpaper")

        with codecs.open(f"{Conf.get('dir_output')}/{group_name_for_path}/meta_{group_name_for_path}.json", "w", encoding=Conf.get("default_char_code"), errors="replace") as f:
            json.dump(group_dict, f, indent=4, ensure_ascii=False)

    @with_standard_log
    def loads_chat_json(self, string):
        size = len(string)
        decoder = json.JSONDecoder()

        end = 0
        while True:
            index = WHITESPACE.match(string[end:]).end()
            i = end + index
            if i >= size:
                break
            ob, end = decoder.raw_decode(string, i)
            yield ob

    @with_standard_log
    def load_target_private_group_chat_json(self, group_name, group_uid, cookies=None, url=None, requests_wait_time="from_conf"):
        try:
            if cookies is None:
                cookies = self.cookies
            if requests_wait_time == "from_conf":
                requests_wait_time = Conf.get("requests_wait_time")

            group_name_for_path = self.replace_dirname_string(group_name)
            chat_json_save_path = f"{Conf.get('dir_output')}/{group_name_for_path}/chat_{group_name_for_path}.json"

            if not os.path.exists(chat_json_save_path):
                return False

            message = f"{chat_json_save_path} の読み込み(時間かかる)"
            self.log.info(message)
            print(message, flush=True)
            with Observer(stdout=True, message=message, log=self.log):
                with codecs.open(chat_json_save_path, "r", encoding=Conf.get("default_char_code"), errors="ignore") as f:
                    print()
                    chats = list(self.loads_chat_json(f.read()))
                if len(chats) <= 1:
                    if url is None:
                        url = f"https://web.lobi.co/api/group/{group_uid}/chats?count=30"
                else:
                    last_id = chats[-2]["id"]
                    if url is None:
                        url = f"https://web.lobi.co/api/group/{group_uid}/chats?count=30&older_than={last_id}"
            message = f"{message} 完了"
            self.log.info(message)
            print(message, flush=True)

            self.log.debug(f"requests.get({url}, cookies=cookies)")
            chats = requests.get(url, cookies=cookies)
            response_status_code = chats.status_code
            self.log.debug(f"response status_code[{response_status_code}]")
            if response_status_code > Conf.get("response_status_code_error_threshold"):
                self.log.error(f"response status_code[{response_status_code}]")
                self.log.error(f"url[{url}]")

            self.log.debug(f"sleep({Conf.get('requests_wait_time')})")
            sleep(Conf.get('requests_wait_time'))
            return chats.json()
        except ConnectionError as e:
            self.log.info(f"ERROR: caught exception at {__class__.__name__}.{sys._getframe().f_code.co_name}")
            self.log.info("[[" + e.__class__.__name__ + " EXCEPTION OCCURED]]: %s", e)
            self.log.info("traceback:\n", stack_info=True, exc_info=True)
            self.log.info(f"requests_wait_time[{requests_wait_time}], url[{url}]")
            requests_wait_time = requests_wait_time * 2
            self.log.info(f"next requests_wait_time is {requests_wait_time}")
            if requests_wait_time > Conf.get("max_requests_wait_time"):
                self.log.error(f"next requests_wait_time[{requests_wait_time}] > Conf.get('max_requests_wait_time')[{Conf.get('max_requests_wait_time')}]")
                self.log.exception("[[" + e.__class__.__name__ + " EXCEPTION OCCURED]]: %s", e)
                self.log.error("traceback:\n", stack_info=True, exc_info=True)
                raise e
            requests.Session()
            message = f"再接続のため{requests_wait_time}秒待機"
            sleep(requests_wait_time)
            self.load_target_private_group_chat_json(group_name, group_uid, cookies=cookies, url=url, requests_wait_time=requests_wait_time)

    @with_standard_log
    def get_all_chat_of_target_group(self, group_name, group_uid, cookies=None, url1=None, url2=None, url3=None, requests_wait_time="from_conf"):
        try:
            group_name_for_path = self.replace_dirname_string(group_name)
            if cookies is None:
                cookies = self.cookies
            if requests_wait_time == "from_conf":
                requests_wait_time = Conf.get("requests_wait_time")

            chat_json_save_path = f"{Conf.get('dir_output')}/{group_name_for_path}/chat_{group_name_for_path}.json"

            chats_json_list = self.load_target_private_group_chat_json(group_name, group_uid, cookies=cookies)

            if chats_json_list is False:  # 新規作成
                with codecs.open(chat_json_save_path, "w", encoding=Conf.get("default_char_code"), errors="ignore") as f:
                    pass

                if url1 is None:
                    url1 = f"https://web.lobi.co/api/group/{group_uid}/chats?count=30"
                self.log.debug(f"requests.get({url1}, cookies=cookies)")
                chat_response = requests.get(url1, cookies=cookies)
                response_status_code = chat_response.status_code
                self.log.debug(f"response status_code[{response_status_code}]")
                if response_status_code > Conf.get("response_status_code_error_threshold"):
                    self.log.error(f"response status_code[{response_status_code}]")
                    self.log.error(f"url1[{url1}]")

                self.log.debug(f"sleep({Conf.get('requests_wait_time')})")
                sleep(Conf.get('requests_wait_time'))

                chats_json_list = chat_response.json()

            index = 0
            while len(chats_json_list) > 0:
                chat = chats_json_list[0]
                if "user" in chat:
                    if "icon" in chat["user"]:
                        image_url = chat["user"]["icon"]
                        user_uid = chat["user"]["uid"]
                        chat["user"]["icon_path"] = self.save_lobi_image(image_url, f"{Conf.get('dir_output')}/{group_name_for_path}", f"img/user/icon/{user_uid}")
                    if "cover" in chat["user"]:
                        image_url = chat["user"]["cover"]
                        user_uid = chat["user"]["uid"]
                        chat["user"]["cover_path"] = self.save_lobi_image(image_url, f"{Conf.get('dir_output')}/{group_name_for_path}", f"img/user/cover/{user_uid}")
                if "assets" in chat:
                    for asset_dict in chat["assets"]:
                        image_url = asset_dict["raw_url"]
                        id = asset_dict["id"]
                        asset_dict["saved_path"] = self.save_lobi_image(image_url, f"{Conf.get('dir_output')}/{group_name_for_path}", f"img/chat/{id}")

                created_date = int(chat["created_date"])
                created_date_jp = datetime.fromtimestamp(created_date, timezone(timedelta(hours=+9), 'JST')).strftime('%Y/%m/%d %H:%M:%S')
                chat["created_date_jp"] = created_date_jp

                if url2 is None:
                    url2 = f"https://web.lobi.co/api/group/{group_uid}/chats/replies?to={chat['id']})"
                self.log.debug(f"requests.get({url2}, cookies=cookies)")
                full_replies = requests.get(url2, cookies=cookies)
                response_status_code = full_replies.status_code
                self.log.debug(f"response status_code[{response_status_code}]")
                if response_status_code > Conf.get("response_status_code_error_threshold"):
                    self.log.error(f"response status_code[{response_status_code}]")
                    self.log.error(f"url2[{url2}]")
                url2 = None

                self.log.debug(f"sleep({Conf.get('get_full_replies_wait_time')})")
                sleep(Conf.get('get_full_replies_wait_time'))
                self.log.debug(f"full_replies: {full_replies}")
                if full_replies.status_code != 400:
                    chat["full_replies"] = full_replies.json()["chats"][::-1]
                    for full_reply_dict in chat["full_replies"]:
                        if "user" in full_reply_dict:
                            if "icon" in full_reply_dict["user"]:
                                image_url = full_reply_dict["user"]["icon"]
                                user_uid = full_reply_dict["user"]["uid"]
                                full_reply_dict["user"]["icon_path"] = self.save_lobi_image(image_url, f"{Conf.get('dir_output')}/{group_name_for_path}", f"img/user/icon/{user_uid}")
                            if "cover" in full_reply_dict["user"]:
                                image_url = full_reply_dict["user"]["cover"]
                                user_uid = full_reply_dict["user"]["uid"]
                                chat["user"]["cover_path"] = self.save_lobi_image(image_url, f"{Conf.get('dir_output')}/{group_name_for_path}", f"img/user/cover/{user_uid}")
                        if "assets" in full_reply_dict:
                            for asset_dict in full_reply_dict["assets"]:
                                image_url = asset_dict["raw_url"]
                                id = asset_dict["id"]
                                asset_dict["saved_path"] = self.save_lobi_image(image_url, f"{Conf.get('dir_output')}/{group_name_for_path}", f"img/chat/{id}")
                        created_date = int(full_reply_dict["created_date"])
                        created_date_jp = datetime.fromtimestamp(created_date, timezone(timedelta(hours=+9), 'JST')).strftime('%Y/%m/%d %H:%M:%S')
                        full_reply_dict["created_date_jp"] = created_date_jp

                with codecs.open(chat_json_save_path, "a", encoding=Conf.get("default_char_code"), errors="ignore") as f:
                    json.dump(chat, f, indent=4, ensure_ascii=False)

                last_id = chat["id"]
                index += 1

                message = f"グループ[{group_name}]のチャット{index}件目({created_date_jp}投稿)取得完了。キュー残り{len(chats_json_list)}"
                print(message, flush=True)
                self.log.debug(message)

                chats_json_list.pop(0)
                if len(chats_json_list) == 0:
                    print("次の30件をロードしてキューに追加", flush=True)
                    if url3 is None:
                        url3 = f"https://web.lobi.co/api/group/{group_uid}/chats?count=30&older_than={last_id}"
                    self.log.debug(f"requests.get({url3}, cookies=cookies)")
                    chats = requests.get(url3, cookies=cookies)
                    response_status_code = chats.status_code
                    self.log.debug(f"response status_code[{response_status_code}]")
                    if response_status_code > Conf.get("response_status_code_error_threshold"):
                        self.log.error(f"response status_code[{response_status_code}]")
                        self.log.error(f"url[{url3}]")
                    url3 = None

                    self.log.debug(f"sleep({Conf.get('requests_wait_time')})")
                    sleep(Conf.get('requests_wait_time'))
                    chats_json_list = chats.json()
            print(f"{group_name} 取得完了", flush=True)

        except ConnectionError as e:
            self.log.info(f"ERROR: caught exception at {__class__.__name__}.{sys._getframe().f_code.co_name}")
            self.log.info("[[" + e.__class__.__name__ + " EXCEPTION OCCURED]]: %s", e)
            self.log.info("traceback:\n", stack_info=True, exc_info=True)
            self.log.info(f"requests_wait_time[{requests_wait_time}], url1[{url1}], url2[{url2}], url3[{url3}]")
            requests_wait_time = requests_wait_time * 2
            self.log.info(f"next requests_wait_time is {requests_wait_time}")
            if requests_wait_time > Conf.get("max_requests_wait_time"):
                self.log.error(f"next requests_wait_time[{requests_wait_time}] > Conf.get('max_requests_wait_time')[{Conf.get('max_requests_wait_time')}]")
                self.log.exception("[[" + e.__class__.__name__ + " EXCEPTION OCCURED]]: %s", e)
                self.log.error("traceback:\n", stack_info=True, exc_info=True)
                raise e
            requests.Session()
            message = f"再接続のため{requests_wait_time}秒待機"
            sleep(requests_wait_time)
            self.get_all_chat_of_target_group(group_name, group_uid, cookies=cookies, url1=url1, url2=url2, url3=url3,  requests_wait_time=requests_wait_time)

    @with_standard_log
    def download_file(self, url, dst_path):
        try:
            message = f"download[{dst_path}]"
            print(message, flush=True)
            self.log.debug(message)
            self.log.debug(f"urllib.request.urlopen({url}")
            with urllib.request.urlopen(url) as web_file, open(dst_path, 'wb') as local_file:
                local_file.write(web_file.read())
                self.log.debug(f"sleep({Conf.get('download_file_wait_time')})")
                sleep(Conf.get('download_file_wait_time'))
        except urllib.error.URLError as e:
            print(e, flush=True)
            self.log.error(f"ERROR: caught exception at {__class__.__name__}.{sys._getframe().f_code.co_name}")
            self.log.exception("[[" + e.__class__.__name__ + " EXCEPTION OCCURED]]: %s", e)
            self.log.error("traceback:\n", stack_info=True, exc_info=True)
            # raise e
        except Exception as e:
            print(e, flush=True)
            self.log.error(f"ERROR: caught exception at {__class__.__name__}.{sys._getframe().f_code.co_name}")
            self.log.exception("[[" + e.__class__.__name__ + " EXCEPTION OCCURED]]: %s", e)
            self.log.error("traceback:\n", stack_info=True, exc_info=True)

    @with_standard_log
    def save_lobi_image(self, url, base_dir, relative_path):
        _, extension = os.path.splitext(url)
        save_path = f"{base_dir}/{relative_path}{extension}"
        dir_save_path = os.path.basename(save_path)
        self.log.debug(f"save_path: {save_path}")
        if os.path.exists(save_path):
            self.log.debug(f"save_path[{save_path}] exists. skip.")
            return f"{relative_path}{extension}"

        self.log.debug(f"save_path[{save_path}] doesnt exist. download.")
        if not os.path.exists(dir_save_path):
            os.makedirs(dir_save_path, exist_ok=True)
        self.download_file(url, save_path)
        return f"{relative_path}{extension}"

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
