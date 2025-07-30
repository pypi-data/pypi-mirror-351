#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Decorators module

- Author: Rex Zhou <879582094@qq.com>
- Created Time: 2025/5/29 14:48
- Copyright: Copyright © 2025 Rex Zhou. All rights reserved.
"""
from functools import wraps
from logging import getLogger
from time import sleep

from requests import RequestException

logger = getLogger(__name__)


def verify_and_convert_data(function):
    """
    Verify the data and convert the message to standard format.
    :param function: Callable object.
    :return: Result dict.
    """

    @wraps(function)
    def wrapper(self, *args, **kwargs) -> dict:
        """
        Verify the data and convert the message to standard format.
        :param self: Object instance.
        :param args: Positional arguments.
        :param kwargs: Other keyword arguments.
        :return: Result dict.
        """
        logger.debug("---- %s ----", verify_and_convert_data.__name__)
        logger.debug("Positional arguments: %s", args)
        logger.debug("Other kwargs: %s", kwargs)
        data = self.prepare_data(*args, **kwargs)
        msg = None if "msg" not in data else data.pop("msg")
        file_path = None if "file_path" not in data else data.pop("file_path")
        logger.debug("Converted message: %s", msg)
        logger.debug("Converted file path: %s", file_path)
        logger.debug("Converted other kwargs: %s", data)
        logger.debug("---- %s ----", verify_and_convert_data.__name__)
        return function(self, msg, file_path=file_path, **data)

    return wrapper


def detect_overheat(function):
    """
    Detect overheat.
    :param function: Callable object.
    :return: Result dict.
    """
    overheat_threshold: int = 60
    overheat_error_code: int = 45009

    @wraps(function)
    def wrapper(self, *args, **kwargs) -> dict:
        """
        Detect overheat.
        :param self: Object instance.
        :param args: Positional arguments.
        :param kwargs: Keyword arguments.
        :return: Result dict.
        """
        logger.debug("==== %s ====", detect_overheat.__name__)
        logger.debug("Positional arguments: %s", args)
        logger.debug("Other kwargs: %s", kwargs)
        if self.OVERHEAT >= 0:
            logger.warning("Overheat detected.")
            while self.OVERHEAT >= 0:
                print(f"\rCooling down: {self.OVERHEAT:02d}s",
                      end='',
                      flush=True)
                sleep(1)
                self.OVERHEAT -= 1
            print()
        result = function(self, *args, **kwargs)
        threshold = overheat_threshold
        if kwargs.get("test") == "overheat":
            threshold = 1
            kwargs.pop("test")
            result["errcode"] = overheat_error_code
        if result.get("errcode") == overheat_error_code:
            self.OVERHEAT = threshold
            result = wrapper(self, *args, **kwargs)
        logger.debug("==== %s ====", detect_overheat.__name__)
        return result

    return wrapper


def handle_request_exception(function):
    """
    Handle request exception.
    :param function: Callable object.
    :return:
    """

    @wraps(function)
    def wrapper(self, *args, **kwargs):
        """
        Handle request exception.
        :param self: Object instance.
        :param args: Positional arguments.
        :param kwargs: Keyword arguments.
        :return: Result dict.
        """
        logger.debug("#### %s ####", handle_request_exception.__name__)
        logger.debug("Positional arguments: %s", args)
        logger.debug("Other kwargs: %s", kwargs)
        try:
            if (test := kwargs.get("test")) == "request_error":
                raise RequestException
            if test == "api_error":
                result = {"errcode": -1}
            else:
                result = function(self, *args, **kwargs)
            if result.get("errcode") != 0:
                msg = f"Request failed, please refer to the official manual: {self.doc}"
                logger.error(msg)
                logger.error("Error message: %s", result)
                raise IOError(msg)
        except RequestException as error:
            msg = f"Unable to initiate API request correctly: {error}"
            logger.error(msg)
            raise ConnectionRefusedError(msg) from error
        logger.debug("#### %s ####", handle_request_exception.__name__)
        return result

    return wrapper
