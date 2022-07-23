#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import io
import sys
import argparse
from datetime import datetime, timedelta, timezone

workspace_path = f"{os.path.dirname(os.path.abspath(__file__))}/../../test/workspace"
os.chdir(workspace_path)

sys.path.append(f"{os.path.dirname(os.path.abspath(__file__))}/../../lib/util")
from conf import Conf
from log import Log
from observer import Observer

sys.path.append(f"{os.path.dirname(os.path.abspath(__file__))}/../../src/lobi")
from lobi import Lobi

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def main(timestamp, args):
    try:
        login_by = args.login_by
        with open("../../log/log", "w"):
            pass
        log = Log.getLogger(exec_env="normal")
        log.info("FILE[" + __file__ + "] start")
        print("FILE[" + __file__ + "] start", flush=True)
        # ob = Observer(stdout=False, log=log)

        if not os.path.exists(Conf.get("dir_output")):
            os.makedirs(Conf.get("dir_output"), exist_ok=True)

        message = "lobiへのログイン"
        log.info(message)
        print(message, flush=True)
        with Observer(stdout=True, message=message, log=log):
            lobi = Lobi(log=log)
            lobi.login(by=login_by)
        message = f"{message} 完了"
        log.info(message)
        print(message, flush=True)

        message = "ログインチェック"
        log.info(message)
        print(message, flush=True)
        with Observer(stdout=True, message=message, log=log):
            lobi.login_check()
        message = f"{message} 完了"
        log.info(message)
        print(message, flush=True)

        message = "プライベートグループのリスト読み込み"
        log.info(message)
        print(message, flush=True)
        with Observer(stdout=True, message=message, log=log):
            private_group_list = lobi.read_private_group_list()
            private_group_dict = lobi.load_private_group_json()
        message = f"{message} 完了"
        log.info(message)
        print(message, flush=True)

        message = "プライベートグループのループ開始"
        log.info(message)
        print(message, flush=True)
        for private_group in private_group_list:
            group_name, total_users, group_uid = lobi.parse_private_group_list(private_group)

            message = f"[{group_name}]フォルダの作成"
            log.info(message)
            print(message, flush=True)
            with Observer(stdout=True, message=message, log=log):
                lobi.create_empty_output_dir(group_name)
            message = f"{message} 完了"
            log.info(message)
            print(message, flush=True)

            message = f"meta_{group_name}.jsonの作成"
            log.info(message)
            print(message, flush=True)
            with Observer(stdout=True, message=message, log=log):
                lobi.create_meta_group_json(group_name, group_uid, private_group_dict)
            message = f"{message} 完了"
            log.info(message)
            print(message, flush=True)

            message = f"chat_{group_name}.jsonの作成"
            log.info(message)
            print(message, flush=True)
            with Observer(stdout=True, message=message, log=log):
                lobi.get_all_chat_of_target_group(group_name, group_uid)
            message = f"{message} 完了"
            log.info(message)
            print(message, flush=True)

        message = "全て完了"
        log.info(message)
        print(message, flush=True)

    except Exception as e:
        raise e

    return 0


if __name__ == '__main__':
    timestamp = datetime.now(timezone(timedelta(hours=+9), 'JST'))
    parser = argparse.ArgumentParser()
    parser.add_argument("-b", "--login_by", help="ログインタイプ", required=True, type=str, choices=["lobi", "twitter", "lobi_unhidden"])

    args = parser.parse_args()
    main(timestamp, args)
