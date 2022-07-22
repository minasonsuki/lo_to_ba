#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from itertools import repeat
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

from time import sleep

sys.path.append(f"{os.path.dirname(os.path.abspath(__file__))}/../../lib/utils")
from conf import Conf
from log import Log, with_standard_log


def execute_by_multiprocessing(method, args, mode="ThreadPoolExecutor_submit", max_workers=32, chunksize=1):
    """
    ThreadPoolExecutorにより並列処理を行う関数。
    特性：
        ThreadPoolExecutor_submit：
        ThreadPoolExecutor_map：
        ProcessPoolExecutor_submit：
        ProcessPoolExecutor_map：

    Examples
    ----------

    Parameters
    ----------
    method : function
        並列処理を行う関数。
        引数は必ず1つのtuple。
        method内で引数argsを展開する。

    args : list or tuple
        methodの引数

    mode : str
        ThreadPoolExecutor_submit
        ThreadPoolExecutor_map
        ProcessPoolExecutor_submit
        ProcessPoolExecutor_map

    max_workers : int
        並列処理時に同時に実行可能なタスクの最大数。

    chunksize : int
        ProcessPoolExecutorのmapを使用する際の引数。
        When using ProcessPoolExecutor, this method chops iterables into a number of chunks which it submits to the pool as separate tasks. The (approximate) size of these chunks can be specified by setting chunksize to a positive integer. For very long iterables, using a large value for chunksize can significantly improve performance compared to the default size of 1. With ThreadPoolExecutor, chunksize has no effect.
        https://docs.python.org/ja/3/library/concurrent.futures.html#concurrent.futures.ProcessPoolExecutor

    Returns
    ----------
    results : list
        並列実行結果を格納したlist
        if mode == "ThreadPoolExecutor_submit":
            [<Future at 0x... state=finished returned NoneType>]
        elif mode == "ThreadPoolExecutor_map":
            [<generator object Executor.map.<locals>.result_iterator at 0x...>]

    Reference
    ----------
    Futureオブジェクトの詳細は下記
    https://docs.python.org/ja/3/library/concurrent.futures.html#concurrent.futures.Future

    ThreadPoolExecutorのsubmitとmapの違いは下記
    https://qiita.com/tag1216/items/db5adcf1ddcb67cfefc8
    ### submit
    １つのタスクを実行キューに追加します。
    実行中のタスクがmax_workers未満であれば追加されたタスクは即実行が開始されます。
    戻り値のFutureオブジェクトでタスクのキャンセルや実行結果の取得を行います。
    ### map
    実行タスクをiteratorで渡します。
    戻り値はタスクの実行結果を取得するためのgeneratorです。

    Example
    ----------
    mode = "ThreadPoolExecutor_map"
    results = this_class.multi_test("secai from jupyter", max_workers=128, mode=mode)
    if mode == "ThreadPoolExecutor_submit":
        for result in results:
            print(result.result())
            print(type(result))
    elif mode == "ThreadPoolExecutor_map":
    for result in results:
            print(results)

    """
    if mode == "ThreadPoolExecutor_submit":
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            results = [executor.submit(method, arg) for arg in args]
    elif mode == "ThreadPoolExecutor_map":
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            results = list(executor.map(method, args))
    elif mode == "ProcessPoolExecutor_submit":
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            results = [executor.submit(method, arg) for arg in args]
    elif mode == "ProcessPoolExecutor_map":
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            results = list(executor.map(method, args, chunksize=chunksize))
    else:
        sys.exit(1)
    return results


def multi_test(arg2=None, max_workers=32, mode="ThreadPoolExecutor_submit", task_kind="sleep"):
    """
    execute_by_multiprocessingの実行サンプル。

    Parameters
    ----------
    message : str
        if task_kind == "sleep":
            logに出力する文字列
        elif task_kind == "sum":
            0～N-1まで足す時のN

    max_workers : int
        ThreadPoolExecutorのmax_workers

    mode : str
        ThreadPoolExecutor_submit
        ThreadPoolExecutor_map

    task_kind : str
        sleep: logにメッセージを出力して3秒sleepする。

    Returns
    ----------
    results : list
        list of <class 'concurrent.futures._base.Future'>
        list of <generator object Executor.map.<locals>.result_iterator at 0x...>
        Futureオブジェクトの詳細は下記
        https://docs.python.org/ja/3/library/concurrent.futures.html#concurrent.futures.Future

    Example
    ----------
    mode = "ThreadPoolExecutor_map"
    results = this_class.multi_test("secai from jupyter", max_workers=128, mode=mode)
    if mode == "ThreadPoolExecutor_submit":
        for result in results:
            print(result.result())
            print(type(result))
    elif mode == "ThreadPoolExecutor_map":
    for result in results:
            print(results)
    """
    def this_method_sleep(args):
        try:
            task_number = args[0]
            message1 = args[1]
            message2 = args[2]
            self.log.debug(f"task_number[{task_number}], message1[{message1}], message2[{message2}]")
            self.log.debug("sleep(3)")
            sleep(3)
            return f"done. message1[{message1}], message2[{message2}]"
        except Exception as e:
            self.log.error('[[EXCEPTION OCCURRED]]: %s', e)
            raise e

    def this_method_sum(args):
        try:
            message = args[0]
            max_number = args[1]
            if max_number is None:
                max_number = 10
            result_message = f"message[{message}], max_number[{max_number}]"
            self.log.debug(result_message)

            result = 0
            for i in range(max_number):
                result += 1

            self.log.debug(f"dene. result[{result}], {result_message}")
            return result
        except Exception as e:
            self.log.error('[[EXCEPTION OCCURRED]]: %s', e)
            raise e

    results = []
    if mode == "ThreadPoolExecutor_submit":
        if task_kind == "sleep":
            arg1_list = [f"msg: test_execute_by_multiprocessing[{task_number}]" for task_number in range(100)]
            args = [(arg1, arg2) for arg1, arg2 in zip(arg1_list, repeat(arg1), repeat(arg2))]
            # for arg in args:
            #     print(arg)
            results = self.execute_by_multiprocessing(method_sleep, max_workers=max_workers, mode=mode, args=args)
        elif task_kind == "sum10":
            arg1_list = [f"msg: test_execute_by_multiprocessing[{task_number}]" for task_number in range(10)]
            args = [(arg1, arg2) for arg1, arg2 in zip(arg1_list, repeat(arg2))]
            results = self.execute_by_multiprocessing(method_sum, max_workers=max_workers, mode=mode, args=args)
        elif task_kind == "sum1000":
            arg1_list = [f"msg: test_execute_by_multiprocessing[{task_number}]" for task_number in range(1000)]
            args = [(arg1, arg2) for arg1, arg2 in zip(arg1_list, repeat(arg2))]
            results = self.execute_by_multiprocessing(method_sum, max_workers=max_workers, mode=mode, args=args)
    elif mode == "ThreadPoolExecutor_map":
        if task_kind == "sleep":
            results = self.execute_by_multiprocessing(method_sleep, max_workers=max_workers, mode=mode, args=args)

    # print(f"results:\n{results}")
    # print(f"type(results):\n{type(results)}")
    return results
