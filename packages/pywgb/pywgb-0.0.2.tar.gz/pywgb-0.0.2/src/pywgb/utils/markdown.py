#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Markdown type message sender


- Author: Rex Zhou <879582094@qq.com>
- Created Time: 2025/5/27 15:12
- Copyright: Copyright © 2025 Rex Zhou. All rights reserved.
"""

from .abstract import AbstractWeComGroupBot, FilePathLike


class MarkdownWeComGroupBot(AbstractWeComGroupBot):
    """Markdown type message Wecom Group Bot"""

    @property
    def _doc_key(self) -> str:
        return "markdown类型"

    def prepare_data(
            self,
            msg: str = None,
            /,
            file_path: FilePathLike = None,  # pylint: disable=unused-argument
            **kwargs) -> dict:
        """
        Convert the message to Markdown format data.
        :param msg: Message to convert.
        :param file_path: File path.
        :param kwargs: Other keyword arguments.
        :return: Converted data.
        """
        result = {
            "msg": {
                "msgtype": "markdown",
                "markdown": {
                    "content": msg.strip()
                }
            }
        }
        return result
