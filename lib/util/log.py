#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import logging
import logging.handlers

import time
import multiprocessing
import threading
import traceback

from conf import Conf as conf
from singleton import Singleton


def with_standard_log(func):
    def stdlog(self, *args, **kwargs):
        if self.log is not None:
            self.log.debug(self.__class__.__name__ + "." + func.__name__ + " started.")
        result = func(self, *args, **kwargs)
        if self.log is not None:
            self.log.debug(self.__class__.__name__ + "." + func.__name__ + " finished.")
        return result
    return stdlog


def clear_log(logger):
    return True
    fh = logger.handlers
    print(fh)


class Log(logging.Handler, metaclass=Singleton):
    """
    Attributes
    ----------
    loglevel : str
        CRITICAL, ERROR, WARNING, INFO, DEBUG, NOTSET
        logger.setLevel(loglevel)で使われる。このloggerの閾値をloglevelに設定し、loglevelよりも深刻でないログメッセージは無視されます。

    Reference
    ----------
    https://docs.python.org/ja/3/library/logging.html
    """
    log = None  # for singleton

    @classmethod
    def getLogger(cls, name=None, exec_env=None, logfile=None, conffile=None):
        try:
            if exec_env is None:
                exec_env = conf.get("exec_env")
            if logfile is None:
                logfile = f"{conf.get('logdir', conffile=conffile)}/{conf.get('logfile', conffile=conffile)}"

            cls._name = name
            cls.exec_env = exec_env
            cls.logfile = logfile
            cls.conffile = conffile

            if exec_env == "singleton":
                return cls.getSingletonLogger(name=name, logfile=logfile, conffile=conffile)
            elif exec_env == "normal":
                return cls.getNormalLogger(name=name, logfile=logfile, conffile=conffile)
            elif exec_env == "multi":
                _log = Log(name=cls._name, exec_env=cls.exec_env, logfile=cls.logfile, conffile=cls.conffile)
                return _log.getMultiLogger(name=cls._name, logfile=cls.logfile, conffile=cls.conffile)
            elif exec_env == "spark":
                return cls.getSparkLogger(name=name, logfile=logfile, conffile=conffile)
            else:
                sys.exit("getLogger Type Error[" + str(exec_env) + "]")
        except(Exception) as e:
            # print(f"ERROR: caught exception at {__class__.__name__}.{sys._getframe().f_code.co_name}", flush=True)
            # print("[[" + e.__class__.__name__ + " EXCEPTON OCCURED]]: %s", e, flush=True)
            # print("traceback:\n", "".join(traceback.format_stack()), flush=True)
            raise e

    def __init__(self, name=None, exec_env=None, logfile=None, conffile=None):
        # print(f"{__class__.__name__}.{sys._getframe().f_code.co_name} started. logfile:{logfile}", flush=True)
        logging.Handler.__init__(self)
        self.queue = multiprocessing.Queue(-1)
        t = threading.Thread(target=self.receive)
        t.daemon = True
        t.start()

    @classmethod
    def common_logger_setup(cls, logger, logfile=None, conffile=None):
        # print(f"{__class__.__name__}.{sys._getframe().f_code.co_name} started. logfile:{logfile}", flush=True)
        # clear logger's handlers
        logger.handlers.clear()

        loglevel = conf.get("loglevel", conffile=conffile)
        logging.Formatter.converter = time.localtime

        if os.name == "nt":
            fh = logging.FileHandler(logfile, encoding=conf.get("default_char_code"))
        else:
            rotate_log_size = conf.get("rotate_log_size")
            fh = logging.handlers.RotatingFileHandler(
                filename=logfile,
                maxBytes=rotate_log_size,
                backupCount=conf.get("backup_log_count")
            )

        # formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        formatter = logging.Formatter('%(asctime)s-%(levelname)s(%(name)s):%(filename)s.%(funcName)s::%(message)s')
        fh.setFormatter(formatter)
        logger.addHandler(fh)

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        stream_handler.setLevel(conf.get("loglevel_to_stdout", conffile=conffile))
        logger.addHandler(stream_handler)

        cls._handler = logger.handlers

        id_ = id(logger)
        logger.setLevel(eval("logging." + loglevel))
        logger.debug("return logger as below:\n logfile:[{logfile}]\n id:[{id_}]\n fh:[{logger.handlers}]".format(**locals()))

    @classmethod
    def getSingletonLogger(cls, name=None, logfile=None, conffile=None):
        # print(f"{__class__.__name__}.{sys._getframe().f_code.co_name} started.", flush=True)
        if cls.log is not None:  # called before and already created.
            # cls.log.debug(f"testreturn logger previously created. (logging.handlers):{logging.handlers}")
            return cls.log
        logger = logging.getLogger(str(name))
        cls.common_logger_setup(logger, logfile=logfile, conffile=conffile)
        cls.log = logger
        # logger.debug(f"testreturn new singleton logger. (logging.handlers):{logging.handlers}")
        return logger

    @classmethod
    def getNormalLogger(cls, name=None, logfile=None, conffile=None):
        # print(f"{__class__.__name__}.{sys._getframe().f_code.co_name} started.", flush=True)
        # print(f"{__class__.__name__}.{sys._getframe().f_code.co_name} started.")
        logger = logging.getLogger(str(name))
        # [logger.removeHandler(h) for h in logger.handlers]
        cls.common_logger_setup(logger, logfile=logfile, conffile=conffile)
        cls.log = logger
        # logger.debug(f"testreturn new normal logger. (logging.handlers):{logging.handlers}")
        return logger

    def getMultiLogger(self, name=None, logfile=None, conffile=None):
        self._name = name
        self.logfile = logfile
        self.conffile = conffile
        # print(f"{__class__.__name__}.{sys._getframe().f_code.co_name} started. _name:{self._name}, logfile:{self.logfile}", flush=True)

        logger = logging.getLogger(str(self._name)).getChild(str(self._name))
        # print(f"logger.handlers: {logger.handlers}", flush=True)
        # import pdb; pdb.set_trace()

        # for handler in logger.handlers:
        #     handler.close()
        #     logger.removeHandler(handler)

        # print(f"logger.handlers: {logger.handlers}", flush=True)
        # import pdb; pdb.set_trace()

        self.common_logger_setup(logger, logfile=self.logfile, conffile=self.conffile)
        # if os.name == "nt":
        #     self._handler = logging.FileHandler(logfile, encoding=conf.get("default_char_code"))
        # else:
        #     rotate_log_size = conf.get("rotate_log_size")
        #     self._handler = logging.handlers.RotatingFileHandler(
        #         filename=self.logfile,
        #         maxBytes=rotate_log_size,
        #         backupCount=conf.get("backup_log_count")
        #     )
        # logging.Handler.__init__(self)
        # logging.Handler.__init__(self)

        # logger = logging.getLogger(str(name))
        # [logger.removeHandler(h) for h in logger.handlers]
        # import pdb; pdb.set_trace()
        # fh = logging.FileHandler(filename=self.logfile)
        # logger.addHandler(fh)
        # cls.common_logger_setup(logger, logfile=self.logfile, conffile=self.conffile)
        # cls.log = logger
        # logger.debug(f"testreturn new multi logger. (logging.handlers):{logging.handlers}")
        return logger

    @classmethod
    def getSparkLogger(cls, name=None, logfile=None, conffile=None):
        from pyspark import SparkContext
        # sc = SparkContext.getOrCreate()
        # log4j = sc._jvm.org.apache.log4j
        # logger = log4j.LogManager.getLogger("myLogger")
        # logger = log4j.LogManager.getLogger(__name__)
        # logger = log4j.LogManager.getRootLogger()
        # logger.appender.FILE.File="../../var/log/log"
        # logger.setLevel(log4jLogger.Level.DEBUG)
        # logger.info("aaaa")
        # return logger

        if 'LOG_DIRS' not in os.environ:
            sys.stderr.write('Missing LOG_DIRS environment variable, pyspark logging disabled')
            return

        file = os.environ['LOG_DIRS'].split(',')[0] + '/log'
        logging.basicConfig(filename=file, level=logging.INFO, format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s')
        logger = logging.getLogger()
        return logger

    def setFormatter(self, fmt):
        logging.Handler.setFormatter(self, fmt)
        self._handler.setFormatter(fmt)

    def receive(self):
        while True:
            try:
                record = self.queue.get()
                self._handler.emit(record)
            except (KeyboardInterrupt, SystemExit):
                raise
            except EOFError:
                break
            except:
                traceback.print_exc(file=sys.stderr)

    def send(self, s):
        self.queue.put_nowait(s)

    def _format_record(self, record):
        # ensure that exc_info and args
        # have been stringified.  Removes any chance of
        # unpickleable things inside and possibly reduces
        # message size sent over the pipe
        if record.args:
            record.msg = record.msg % record.args
            record.args = None
        if record.exc_info:
            dummy = self.format(record)
            record.exc_info = None

        return record

    def emit(self, record):
        try:
            s = self._format_record(record)
            self.send(s)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)

    def close(self):
        if isinstance(self._handler, list):
            [handler.close() for handler in self._handler]
        else:
            self._handler.close()
        logging.Handler.close(self)

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
            self.log.error(f"caught exception at {sys._getframe().f_code.co_name}")
            self.log.exception("[[" + e.__class__.__name__ + " EXCEPTON OCCURED]]: %s", e)
            return False
    """
