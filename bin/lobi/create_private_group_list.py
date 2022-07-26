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

        message = "プライベートグループのリスト作成"
        log.info(message)
        print(message, flush=True)
        with Observer(stdout=True, message=message, log=log):
            lobi.create_private_group_list()
        message = f"{message} 完了"
        log.info(message)
        print(message, flush=True)

        message = "全て完了"
        log.info(message)
        print(message, flush=True)

    except Exception as e:
        log.error("ERROR: caught exception at main")
        log.exception("[[" + e.__class__.__name__ + " EXCEPTION OCCURED]]: %s", e)
        log.error("traceback:\n", stack_info=True, exc_info=True)
        raise e

    return 0


if __name__ == '__main__':
    timestamp = datetime.now(timezone(timedelta(hours=+9), 'JST'))
    parser = argparse.ArgumentParser()
    parser.add_argument("-b", "--login_by", help="ログインタイプ", required=True, type=str, choices=["lobi", "twitter", "lobi_unhidden"])

    args = parser.parse_args()
    main(timestamp, args)
