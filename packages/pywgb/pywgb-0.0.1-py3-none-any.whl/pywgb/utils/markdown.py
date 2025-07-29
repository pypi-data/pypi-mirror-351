#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Markdown type message sender


- Author: Rex Zhou <879582094@qq.com>
- Created Time: 2025/5/27 15:12
- Copyright: Copyright © 2025 Rex Zhou. All rights reserved.
"""

from .abstract import AbstractWeComGroupBot


class MarkdownWeComGroupBot(AbstractWeComGroupBot):
    """Markdown type message Wecom Group Bot"""

    @property
    def _doc_key(self) -> str:
        return "markdown类型"

    def convert_msg(self, msg: str, /, **kwargs) -> dict:
        """
        Convert the message to Markdown format.
        :param msg: Message to convert.
        :param kwargs: Other keyword arguments.
        :return: Converted message.
        """
        result = {"msgtype": "markdown", "markdown": {"content": msg.strip()}}
        if kwargs.get("test"):
            result = {"msgtype": "markdown"}
        return result
