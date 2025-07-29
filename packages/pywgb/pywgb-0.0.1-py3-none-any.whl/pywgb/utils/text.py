#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Text type message sender

- Author: Rex Zhou <879582094@qq.com>
- Created Time: 2025/5/27 14:53
- Copyright: Copyright © 2025 Rex Zhou. All rights reserved.
"""

from .abstract import AbstractWeComGroupBot


class TextWeComGroupBot(AbstractWeComGroupBot):
    """Text type message Wecom Group Bot"""

    @property
    def _doc_key(self) -> str:
        return "文本类型"

    def convert_msg(self, msg: str, /, **kwargs) -> dict:
        """
        Convert the message to text format.
        :param msg: Message to convert.
        :param kwargs: Other keyword arguments.
        :return: Converted message.
        """
        mentioned_list: list = kwargs.get("mentioned_list", [])
        mentioned_mobile_list: list = kwargs.get("mentioned_mobile_list", [])
        result = {
            "msgtype": "text",
            "text": {
                "content": msg.strip(),
                "mentioned_list": mentioned_list,
                "mentioned_mobile_list": mentioned_mobile_list
            }
        }
        if kwargs.get("test"):
            result = {"msgtype": "text"}
        return result
