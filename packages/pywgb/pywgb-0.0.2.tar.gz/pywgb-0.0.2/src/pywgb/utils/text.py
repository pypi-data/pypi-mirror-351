#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Text type message sender

- Author: Rex Zhou <879582094@qq.com>
- Created Time: 2025/5/27 14:53
- Copyright: Copyright © 2025 Rex Zhou. All rights reserved.
"""

from .abstract import AbstractWeComGroupBot, FilePathLike


class TextWeComGroupBot(AbstractWeComGroupBot):
    """Text type message Wecom Group Bot"""

    @property
    def _doc_key(self) -> str:
        return "文本类型"

    def prepare_data(
            self,
            msg: str = None,
            /,
            file_path: FilePathLike = None,  # pylint: disable=unused-argument
            **kwargs) -> dict:
        """
        Convert the message to text format data.
        :param msg: Message to convert.
        :param file_path: File path.
        :param kwargs: Other keyword arguments.
        :return: Converted data.
        """
        mentioned_list: list = kwargs.get("mentioned_list", [])
        mentioned_mobile_list: list = kwargs.get("mentioned_mobile_list", [])
        result = {
            "msg": {
                "msgtype": "text",
                "text": {
                    "content": msg.strip(),
                    "mentioned_list": mentioned_list,
                    "mentioned_mobile_list": mentioned_mobile_list
                }
            }
        }
        return result
