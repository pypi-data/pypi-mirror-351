#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ConsoleLogger

author: shadow shell
"""

from shadowshell.logging.logger import Logger
from shadowshell.logging.logging_constants import LoggingConstants

class ConsoleLogger(Logger):

    def debug(self, content):
        if LoggingConstants.LEVEL_DEBUG is True:
            self.__log(content)     
    def info(self, content):
        if LoggingConstants.LEVEL_INFO is True:
            self.__log(content)

    def warn(self, content):
        self.__log(content)
    
    def error(self, content):
        self.__log(content)

    def __log(self, content):
        print("%s" % (content))
