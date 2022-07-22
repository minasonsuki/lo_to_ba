#!/usr/bin/env python
# -*- coding: utf-8 -*-

import yaml
import codecs
from pathlib import Path, PurePosixPath


class Conf:
    @classmethod
    def get(cls, conf, conffile=None):
        if conffile is None:
            conffile = "../../config.yml"
        with codecs.open(conffile, "r", encoding="utf-8") as f:
            confs = yaml.load(f, Loader=yaml.SafeLoader)
        return cls._format(confs[conf], conffile)

    @classmethod
    def _format(cls, conf_result, conffile):
        if isinstance(conf_result, list):
            return [cls._format(conf, conffile) for conf in conf_result]
        elif isinstance(conf_result, str) and "${CONF_ABSPATH}" in conf_result:
            conf_abspath = str((PurePosixPath(Path(conffile).parent.resolve())))
            return f"{PurePosixPath(Path(conf_result.replace('${CONF_ABSPATH}', conf_abspath)))}"
        else:
            return conf_result
