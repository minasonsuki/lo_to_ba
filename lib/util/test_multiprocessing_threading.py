#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import io
import sys
import unittest

from itertools import repeat
from time import sleep
from concurrent.futures._base import Future
import socket

workspace_path = os.path.dirname(os.path.abspath(__file__))
os.chdir(workspace_path)

sys.path.append(f"{os.path.dirname(os.path.abspath(__file__))}/../../lib/util")
from conf import Conf
from log import Log, with_standard_log
from observer import Observer

from multiprocessing_threading import execute_by_multiprocessing, multi_test

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


class multiprocessing_test(unittest.TestCase):
    """
    multiprocessing_threading.pyのテスト

    Attributes
    ----------
    log : Log
        logger

    ob : Observer
        処理時間などを観測するクラス。

    max_workers : int
        並列処理時に同時に実行可能なタスクの最大数。

    chunksize : int
        ProcessPoolExecutorを使用する際の引数。
        When using ProcessPoolExecutor, this method chops iterables into a number of chunks which it submits to the pool as separate tasks. The (approximate) size of these chunks can be specified by setting chunksize to a positive integer. For very long iterables, using a large value for chunksize can significantly improve performance compared to the default size of 1. With ThreadPoolExecutor, chunksize has no effect.
        https://docs.python.org/ja/3/library/concurrent.futures.html#concurrent.futures.ProcessPoolExecutor
    """
    @classmethod
    def setUpClass(cls):
        with open("../../log/log", "w"):
            pass
        cls.log = Log.getLogger()
        cls.ob = Observer
        host = socket.gethostname()
        if host in ["aries-acr", "libra-acr"]:
            cls.max_workers = 128
        elif host in ["workingtower"]:
            cls.max_workers = 32
        else:
            cls.max_workers = 32
        cls.log.info(f"\n\n{__class__.__name__}.{sys._getframe().f_code.co_name} finished.\n---------- start ---------")

    def setUp(self):
        pass

    # @with_standard_log
    # def test_branch_by_computer_name(self):
    #     """
    #     コンピュータ名によってmax_workersを決める機能のテスト

    #     """
    #     try:
    #         print(f"self.max_workers: {self.max_workers}")
    #     except(Exception) as e:
    #         self.log.error(f"ERROR: caught exception at {__class__.__name__}.{sys._getframe().f_code.co_name}")
    #         self.log.exception("[[" + e.__class__.__name__ + " EXCEPTION OCCURED]]: %s", e)
    #         self.log.error("traceback:\n", stack_info=True, exc_info=True)
    #         raise e

    # @with_standard_log
    # def test_ThreadPoolExecutor_submit_sleep(self):
    #     max_task_number = 128
    #     mode = "ThreadPoolExecutor_submit"
    #     arg1_list = [f"msg: test_execute_by_multiprocessing[{task_number}]" for task_number in range(max_task_number)]
    #     arg2 = f"from {sys._getframe().f_code.co_name}"
    #     args = [(task_number, log, arg1, arg2) for task_number, log, arg1, arg2 in zip(range(max_task_number), repeat(self.log), arg1_list, repeat(arg2))]
    #     with Observer(stdout=True, message=f"{__class__.__name__}.{sys._getframe().f_code.co_name}", log=self.log):
    #         results = execute_by_multiprocessing(multi_test_method_sleep, args, max_workers=self.max_workers, mode="ThreadPoolExecutor_submit")
    #     if mode == "ThreadPoolExecutor_submit":
    #         for result in results:
    #             pass
    #             # print(result.result())
    #             # print(type(result))
    #     elif mode == "ThreadPoolExecutor_map":
    #         for result in results:
    #             pass
    #             # print(results)
    #     print(f"len(results): {len(results)}")

    # @with_standard_log
    # def test_ThreadPoolExecutor_map_sleep(self):
    #     max_task_number = 128
    #     mode = "ThreadPoolExecutor_map"
    #     arg1_list = [f"msg: test_execute_by_multiprocessing[{task_number}]" for task_number in range(max_task_number)]
    #     arg2 = f"from {sys._getframe().f_code.co_name}"
    #     args = [(task_number, log, arg1, arg2) for task_number, log, arg1, arg2 in zip(range(max_task_number), repeat(self.log), arg1_list, repeat(arg2))]
    #     with Observer(stdout=True, message=f"{__class__.__name__}.{sys._getframe().f_code.co_name}", log=self.log):
    #         results = execute_by_multiprocessing(multi_test_method_sleep, args, max_workers=self.max_workers, mode="ThreadPoolExecutor_submit")
    #     if mode == "ThreadPoolExecutor_submit":
    #         for result in results:
    #             pass
    #             # print(result.result())
    #             # print(type(result))
    #     elif mode == "ThreadPoolExecutor_map":
    #         for result in results:
    #             pass
    #             # print(results)
    #     print(f"len(results): {len(results)}")

    @with_standard_log
    def test_ThreadPoolExecutor_submit_sum10000(self):
        max_number = 10000
        max_task_number = 128
        mode = "ThreadPoolExecutor_submit"
        arg1_list = [f"msg: test_execute_by_multiprocessing[{task_number}]" for task_number in range(max_task_number)]
        arg2 = max_number
        args = [(task_number, log, arg1, arg2) for task_number, log, arg1, arg2 in zip(range(max_task_number), repeat(self.log), arg1_list, repeat(arg2))]
        with Observer(stdout=True, message=f"{__class__.__name__}.{sys._getframe().f_code.co_name}", log=self.log):
            results = execute_by_multiprocessing(multi_test_method_sum, args, max_workers=self.max_workers, mode=mode)
        print(f"type(results): {type(results)}, mode={mode}")
        print(f"type(results[0]): {type(results[0])}, mode={mode}")
        print(f"len(results): {len(results)}")
        if mode == "ThreadPoolExecutor_submit" or mode == "ProcessPoolExecutor_submit":
            for result in results:
                # print(result.result())
                pass
        elif mode == "ThreadPoolExecutor_map" or mode == "ProcessPoolExecutor_map":
            for result in results:
                # print(results)
                pass
        # for result in results:
        #     if isinstance(result, Future):
        #         from concurrent.futures._base import Future
        #         print(f"result: {result.result()}")
        #     else:
        #         print(f"result: {result}")

    @with_standard_log
    def test_ThreadPoolExecutor_map_sum10000(self):
        max_number = 10000
        max_task_number = 128
        mode = "ThreadPoolExecutor_map"
        arg1_list = [f"msg: test_execute_by_multiprocessing[{task_number}]" for task_number in range(max_task_number)]
        arg2 = max_number
        args = [(task_number, log, arg1, arg2) for task_number, log, arg1, arg2 in zip(range(max_task_number), repeat(self.log), arg1_list, repeat(arg2))]
        with Observer(stdout=True, message=f"{__class__.__name__}.{sys._getframe().f_code.co_name}", log=self.log):
            results = execute_by_multiprocessing(multi_test_method_sum, args, max_workers=self.max_workers, mode=mode)
        print(f"type(results): {type(results)}, mode={mode}")
        print(f"type(results[0]): {type(results[0])}, mode={mode}")
        if mode == "ThreadPoolExecutor_submit" or mode == "ProcessPoolExecutor_submit":
            for result in results:
                # print(result.result())
                pass
        elif mode == "ThreadPoolExecutor_map" or mode == "ProcessPoolExecutor_map":
            for result in results:
                # print(results)
                pass
        # for result in results:
        #     if isinstance(result, Future):
        #         from concurrent.futures._base import Future
        #         print(f"result: {result.result()}")
        #     else:
        #         print(f"result: {result}")

    @with_standard_log
    def test_ProcessPoolExecutor_submit_sum10000(self):
        max_number = 10000
        max_task_number = 128
        mode = "ProcessPoolExecutor_submit"
        arg1_list = [f"msg: test_execute_by_multiprocessing[{task_number}]" for task_number in range(max_task_number)]
        arg2 = max_number
        args = [(task_number, log, arg1, arg2) for task_number, log, arg1, arg2 in zip(range(max_task_number), repeat(self.log), arg1_list, repeat(arg2))]
        with Observer(stdout=True, message=f"{__class__.__name__}.{sys._getframe().f_code.co_name}", log=self.log):
            results = execute_by_multiprocessing(multi_test_method_sum, args, max_workers=self.max_workers, mode=mode)
        print(f"type(results): {type(results)}, mode={mode}")
        print(f"type(results[0]): {type(results[0])}, mode={mode}")
        print(f"len(results): {len(results)}")
        if mode == "ThreadPoolExecutor_submit" or mode == "ProcessPoolExecutor_submit":
            for result in results:
                # print(result.result())
                pass
        elif mode == "ThreadPoolExecutor_map" or mode == "ProcessPoolExecutor_map":
            for result in results:
                # print(results)
                pass
        # for result in results:
        #     if isinstance(result, Future):
        #         from concurrent.futures._base import Future
        #         print(f"result: {result.result()}")
        #     else:
        #         print(f"result: {result}")

    @with_standard_log
    def test_ProcessPoolExecutor_map_sum10000_chunksize1(self):
        max_number = 10000
        max_task_number = 128
        chunksize = 1
        mode = "ProcessPoolExecutor_map"
        arg1_list = [f"msg: test_execute_by_multiprocessing[{task_number}]" for task_number in range(max_task_number)]
        arg2 = max_number
        args = [(task_number, log, arg1, arg2) for task_number, log, arg1, arg2 in zip(range(max_task_number), repeat(self.log), arg1_list, repeat(arg2))]
        with Observer(stdout=True, message=f"{__class__.__name__}.{sys._getframe().f_code.co_name}", log=self.log):
            results = execute_by_multiprocessing(multi_test_method_sum, args, max_workers=self.max_workers, chunksize=chunksize, mode=mode)
        print(f"type(results): {type(results)}, mode={mode}")
        print(f"type(results[0]): {type(results[0])}, mode={mode}")
        if mode == "ThreadPoolExecutor_submit" or mode == "ProcessPoolExecutor_submit":
            for result in results:
                # print(result.result())
                pass
        elif mode == "ThreadPoolExecutor_map" or mode == "ProcessPoolExecutor_map":
            for result in results:
                # print(results)
                pass
        # for result in results:
        #     if isinstance(result, Future):
        #         from concurrent.futures._base import Future
        #         print(f"result: {result.result()}")
        #     else:
        #         print(f"result: {result}")

    # 以下インスタンスメソッド
    @with_standard_log
    def multi_test_instance_method_sleep(self, args):
        try:
            task_number = args[0]
            message1 = args[1]
            message2 = args[2]
            self.log.debug(f"task_number[{task_number}], message1[{message1}], message2[{message2}]")
            self.log.debug(f"task_number[{task_number}], sleep(3)")
            sleep(3)
            return f"done. message1[{message1}], message2[{message2}]"
        except Exception as e:
            self.log.error('[[EXCEPTION OCCURRED]]: %s', e)
            raise e


# 以下通常メソッド
def multi_test_method_sleep(args):
    try:
        task_number = args[0]
        log = args[1]
        message1 = args[2]
        message2 = args[3]
        log.debug(f"task_number[{task_number}], message1[{message1}], message2[{message2}]")
        log.debug(f"task_number[{task_number}], sleep(3)")
        sleep(3)
        return f"done. message1[{message1}], message2[{message2}]"
    except Exception as e:
        log.error('[[EXCEPTION OCCURRED]]: %s', e)
        raise e


def multi_test_method_sum(args):
    try:
        task_number = args[0]
        log = args[1]
        message = args[2]
        max_number = args[3]
        if max_number is None:
            max_number = 10
        result_message = f"task_number[{task_number}], message[{message}], max_number[{max_number}]"
        log.debug(result_message)

        result = 0
        for i in range(max_number):
            result += i

        log.debug(f"dene. result[{result}], {result_message}")
        return result
    except Exception as e:
        log.error('[[EXCEPTION OCCURRED]]: %s', e)
        raise e

    # @with_standard_log
    # def test_ThreadPoolExecutor_map_sleep(self):
    #     mode = "ThreadPoolExecutor_submit"
    #     # mode = "ThreadPoolExecutor_map"
    #     # task_kind = "sleep"
    #     # task_kind = "sum10"
    #     # arg2 = 1000000
    #     # results = visualizer.multi_test(arg2=arg2, max_workers=128, mode=mode, task_kind=task_kind)
    #     task_kind = "sum1000"
    #     arg2 = 1000000
    #     results = multi_test(arg2=arg2, max_workers=128, mode=mode, task_kind=task_kind)
    #     if mode == "ThreadPoolExecutor_submit":
    #         for result in results:
    #             pass
    #             # print(result.result())
    #             # print(type(result))
    #     elif mode == "ThreadPoolExecutor_map":
    #         for result in results:
    #             pass
    #             # print(results)
    #     print(len(results))

    # @with_standard_log
    # def test_ThreadPoolExecutor_submit_sum1000(self):
    #     mode = "ThreadPoolExecutor_submit"
    #     # mode = "ThreadPoolExecutor_map"
    #     # task_kind = "sleep"
    #     # task_kind = "sum10"
    #     # arg2 = 1000000
    #     # results = visualizer.multi_test(arg2=arg2, max_workers=128, mode=mode, task_kind=task_kind)
    #     task_kind = "sum1000"
    #     arg2 = 1000000
    #     results = multi_test(arg2=arg2, max_workers=128, mode=mode, task_kind=task_kind)
    #     if mode == "ThreadPoolExecutor_submit":
    #         for result in results:
    #             pass
    #             # print(result.result())
    #             # print(type(result))
    #     elif mode == "ThreadPoolExecutor_map":
    #         for result in results:
    #             pass
    #             # print(results)
    #     print(len(results))

    # @with_standard_log
    # def test_ThreadPoolExecutor_map_sum1000(self):
    #     mode = "ThreadPoolExecutor_submit"
    #     # mode = "ThreadPoolExecutor_map"
    #     # task_kind = "sleep"
    #     # task_kind = "sum10"
    #     # arg2 = 1000000
    #     # results = visualizer.multi_test(arg2=arg2, max_workers=128, mode=mode, task_kind=task_kind)
    #     task_kind = "sum1000"
    #     arg2 = 1000000
    #     results = multi_test(arg2=arg2, max_workers=128, mode=mode, task_kind=task_kind)
    #     if mode == "ThreadPoolExecutor_submit":
    #         for result in results:
    #             pass
    #             # print(result.result())
    #             # print(type(result))
    #     elif mode == "ThreadPoolExecutor_map":
    #         for result in results:
    #             pass
    #             # print(results)
    #     print(len(results))

    """
    @with_standard_log
    def (self):
        "*3
        関数の説明

        Parameters
        ----------
        パラメータ名 : 型
            パラメータの説明

        Returns
        ----------
        戻り値名 : 型
            戻り値の説明

        Reference
        ----------
        参考記事など

        Example
        ----------
        例

        "*3
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
