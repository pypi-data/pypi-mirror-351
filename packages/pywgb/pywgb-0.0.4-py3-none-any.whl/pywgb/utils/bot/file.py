#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File type message sender

- Author: Rex Zhou <879582094@qq.com>
- Created Time: 2025/5/30 14:40
- Copyright: Copyright © 2025 Rex Zhou. All rights reserved.
"""

from . import AbstractWeComGroupBot, FilePathLike, MediaUploader


class FileWeComGroupBot(AbstractWeComGroupBot):
    """File type message Wecom Group Bot"""

    @property
    def _doc_key(self) -> str:
        return "文件类型"

    # pylint:disable=unused-argument
    def prepare_data(self,
                     msg: str = None,
                     /,
                     file_path: FilePathLike = None,
                     **kwargs) -> dict:
        """
        Convert the message to File format.
        :param msg: Message to convert.
        :param file_path: File path.
        :param kwargs: Other keyword arguments.
        :return: Converted message.
        """
        response = MediaUploader(self.key).upload(file_path, **kwargs)
        result = {
            "msg": {
                "msgtype": "file",
                "file": {
                    "media_id": response["media_id"],
                }
            }
        }
        return result
