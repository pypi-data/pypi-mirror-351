#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test module

- Author: Rex Zhou <879582094@qq.com>
- Created Time: 2025/5/27 14:58
- Copyright: Copyright © 2025 Rex Zhou. All rights reserved.
"""
from os import getenv
from pathlib import Path
from random import randint
from urllib.parse import urlparse, unquote

from dotenv import load_dotenv

# pylint: disable=import-error
from src.pywgb.utils import TextWeComGroupBot
from src.pywgb.utils import MarkdownWeComGroupBot
from src.pywgb.utils import ImageWeComGroupBot

env_file = Path(__file__).parent.with_name(".env")
load_dotenv(env_file, override=True)
VALID_KEY = getenv("VALID_KEY")


def test_text_initial() -> None:
    """
    Test TextWeComGroupBot initialisation.
    :return:
    """
    valid_url = getenv("VALID_URL")
    print()
    print("Check valid key:", VALID_KEY)
    print("Check valid url:", valid_url)
    # Verify valid key and url
    bot = TextWeComGroupBot(VALID_KEY)
    assert urlparse(unquote(bot.doc)).fragment == bot._doc_key  # pylint: disable=protected-access
    assert VALID_KEY == bot.key
    assert f"TextWeComGroupBot({VALID_KEY})" == str(bot)
    assert valid_url.split("=")[-1] == TextWeComGroupBot(valid_url).key
    # Verify invalid key and url
    invalids = [getenv("INVALID_KEY"), getenv("INVALID_URL"), None]
    for invalid in invalids:
        try:
            TextWeComGroupBot(invalid)
        except ValueError:
            ...


def test_markdown_initial() -> None:
    """
    Test MarkdownWeComGroupBot initialisation.
    :return:
    """
    # Verify valid key and url
    bot = MarkdownWeComGroupBot(VALID_KEY)
    assert urlparse(unquote(bot.doc)).fragment == bot._doc_key  # pylint: disable=protected-access
    assert VALID_KEY == bot.key


def test_image_initial() -> None:
    """
    Test ImageWeComGroupBot initialisation.
    :return:
    """
    # Verify valid key and url
    bot = ImageWeComGroupBot(VALID_KEY)
    assert urlparse(unquote(bot.doc)).fragment == bot._doc_key  # pylint: disable=protected-access
    assert VALID_KEY == bot.key


def test_successful_send() -> None:
    """
    Test send message function
    :return:
    """
    bot = TextWeComGroupBot(getenv("VALID_KEY"))
    print(bot)
    result = bot.send(f"This is a test TEXT message: {randint(1, 100)}")
    print(result)
    assert result["errcode"] == 0
    bot = MarkdownWeComGroupBot(getenv("VALID_KEY"))
    print(bot)
    result = bot.send(f"## This is a test Markdown message: {randint(1, 100)}")
    print(result)
    assert result["errcode"] == 0
    bot = ImageWeComGroupBot(getenv("VALID_KEY"))
    print(bot)
    result = bot.send(file_path=Path(__file__).with_name("test.png"))
    print(result)
    assert result["errcode"] == 0


def test_overheat() -> None:
    """
    Test overheat function
    :return:
    """
    bot = TextWeComGroupBot(getenv("VALID_KEY"))
    bot.send("This message was delayed by overheat", test="overheat")


def test_oversize_image() -> None:
    """
    Test oversize image send
    :return:
    """
    bot = ImageWeComGroupBot(getenv("VALID_KEY"))
    file = Path(__file__).with_name("test.png")
    try:
        bot.send(file_path=file, test="wrong_format_image")
    except TypeError:
        ...
    try:
        bot.send(file_path=file, test="oversize_image")
    except BufferError:
        ...


def test_request_exception() -> None:
    """
    Test request exception
    :return:
    """
    bot = TextWeComGroupBot(getenv("VALID_KEY"))
    try:
        bot.send("This message WON'T be sent, cause by API error",
                 test="api_error")
    except IOError:
        ...
    try:
        bot.send("This message WON'T be sent, cause by request error",
                 test="request_error")
    except ConnectionRefusedError:
        ...
