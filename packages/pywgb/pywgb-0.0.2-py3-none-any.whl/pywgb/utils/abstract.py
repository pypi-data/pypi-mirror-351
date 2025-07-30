#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Abstract classes

- Author: Rex Zhou <879582094@qq.com>
- Created Time: 2025/5/27 13:54
- Copyright: Copyright © 2025 Rex Zhou. All rights reserved.
"""
__all__ = ["AbstractWeComGroupBot", "FilePathLike"]

from abc import ABC, abstractmethod
from logging import getLogger
from os import PathLike
from typing import Union
from urllib.parse import quote, urlparse, parse_qs
from uuid import UUID

from requests import Session, session

from .deco import verify_and_convert_data, detect_overheat, handle_request_exception

logger = getLogger(__name__)
FilePathLike = Union[str, PathLike]


class AbstractWeComGroupBot(ABC):
    """Abstract class of Wecom group bot."""

    # The base path of the document
    _DOC_URL: str = "https://developer.work.weixin.qq.com/document/path/91770"
    # API Endpoint
    _API_END_POINT: str = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send'
    # Default requests headers
    _HEADERS: dict = {"Content-Type": "application/json"}
    # Class level variable for detect overheat
    OVERHEAT: int = -1

    def __init__(self, key: str) -> None:
        """
        Initialize the class.
        :param key: The key of group bot webhook url.
        """
        if key is None:
            raise ValueError("Key is required")
        self.key = self._verify_uuid(key.strip())
        self.session: Session = session()
        self.session.headers = self._HEADERS

    @staticmethod
    def _parse_webhook_url(url: str) -> str:
        """
        Parse webhook url into key string.
        :param url: Webhook url.
        :return: Key string.
        """
        # If the key passed by url, split and parse it.
        try:
            query = urlparse(url).query
            params = parse_qs(query)
            if "key" not in params or not params["key"]:
                raise ValueError("Missing 'key' parameter in URL")
            return params["key"][0]
        except Exception as error:
            msg = f"Invalid webhook URL {url}."
            logger.critical(msg)
            raise ValueError(msg) from error

    def _verify_uuid(self, key: Union[str, UUID], max_attempts: int = 2) -> str:
        """
        Verify the key weather is UUID format.
        :param key: Key string
        :param max_attempts: Max number of attempts.
        :return: Result bool
        """
        if max_attempts <= 0:  # pragma: no cover
            raise ValueError("Maximum verification attempts exceeded")
        # The standard key format is UUID format.
        if isinstance(key, UUID):  # pragma: no cover
            return str(key)
        try:
            UUID(key)
            return key
        except (ValueError, TypeError, AttributeError) as error:
            try:
                key = self._parse_webhook_url(key)
                return self._verify_uuid(key, max_attempts - 1)
            except ValueError:
                ...
            raise ValueError(f"Invalid key format: {key}") from error

    def __repr__(self) -> str:
        """
        Return the class name.
        :return: Class name.
        """
        return f"{self.__class__.__name__}({self.key})"

    @property
    @abstractmethod
    def _doc_key(self) -> str:
        """
        The key of the document description.
        :return: key of the document description
        """

    @property
    def api_end_point(self) -> str:
        """
        Returns the address of the spliced endpoint url.
        :return: Endpoint url
        """
        end_point = f"{self._API_END_POINT}?key={self.key}"
        return end_point

    @property
    def doc(self) -> str:
        """
        API URL of the document description
        :return: URL of the document
        """
        url = f"{self._DOC_URL}#{quote(self._doc_key)}"
        return url

    # pylint:disable=unused-argument
    @handle_request_exception
    @detect_overheat
    @verify_and_convert_data
    def send(self,
             msg: str = None,
             /,
             file_path: FilePathLike = None,
             **kwargs) -> dict:
        """
        Method of sending a message. `Refer`_

        .. _`Refer`: https://developer.work.weixin.qq.com/document/path/91770

        :param msg: Message body.
        :param file_path: File path. Used for send image/voice/file.
        :return: Result dict.
        """
        logger.debug("~~~~ %s ~~~~", self.send.__name__)
        logger.debug("Message: %s", msg)
        logger.debug("File path: %s", file_path)
        logger.debug("Other kwargs: %s", kwargs)
        response = self.session.post(self.api_end_point, json=msg)
        result = response.json()
        logger.debug("~~~~ %s ~~~~", self.send.__name__)
        logger.info("Message has been sent: %s", result)
        return result

    @abstractmethod
    def prepare_data(self,
                     msg: str = None,
                     /,
                     file_path: FilePathLike = None,
                     **kwargs) -> dict:
        """
        Prepare data methods, subclasses must complete specific implementations
        :param msg: Message body.
        :param file_path: File path.
        :param kwargs: Other keyword arguments.
        :return: Result dict.
        """
