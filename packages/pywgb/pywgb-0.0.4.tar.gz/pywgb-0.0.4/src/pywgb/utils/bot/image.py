#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Image type message sender

- Author: Rex Zhou <879582094@qq.com>
- Created Time: 2025/5/29 14:05
- Copyright: Copyright © 2025 Rex Zhou. All rights reserved.
"""
from base64 import b64encode
from hashlib import md5
from pathlib import Path

from . import AbstractWeComGroupBot, FilePathLike


class ImageWeComGroupBot(AbstractWeComGroupBot):
    """Image type message Wecom Group Bot"""

    @property
    def _doc_key(self) -> str:
        return "图片类型"

    def prepare_data(
            self,
            msg: str = None,  # pylint:disable=unused-argument
            /,
            file_path: FilePathLike = None,
            **kwargs) -> dict:
        """
        Convert the message to Image format.
        :param msg: Message to convert.
        :param file_path: File path.
        :param kwargs: Other keyword arguments.
        :return: Converted message.
        """
        file_path = Path(file_path) if file_path else None
        # Check format, only support: `.jpg` and `.png`
        if file_path.suffix.lower() not in [
                ".jpg", ".png"
        ] or kwargs.get("test") == "wrong_format_image":
            raise TypeError("Just support image type: jpg or png")
        with open(file_path, "rb") as _:
            content = _.read()
        # Check image size, only smaller than `2M`
        max_size = 2 * pow(1024, 2)
        if len(content) > max_size or kwargs.get("test") == "oversize_image":
            raise BufferError("The image is too large, more than 2M")
        result = {
            "msg": {
                "msgtype": "image",
                "image": {
                    "base64": b64encode(content).decode("utf-8"),
                    "md5": md5(content).hexdigest(),
                }
            }
        }
        return result
