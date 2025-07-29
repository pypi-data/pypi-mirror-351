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
    Test TextWeComGroupBot initialisation.
    :return:
    """
    # Verify valid key and url
    bot = MarkdownWeComGroupBot(VALID_KEY)
    assert urlparse(unquote(bot.doc)).fragment == bot._doc_key  # pylint: disable=protected-access
    assert VALID_KEY == bot.key


def test_send() -> None:
    """
    Test send message function
    :return:
    """
    bot = TextWeComGroupBot(getenv("VALID_KEY"))
    print(bot)
    result = bot.send(f"This is a test TEXT message: {randint(1, 100)}")
    print(result)
    assert result["errcode"] == 0
    try:
        bot.send("This message WON'T be sent", test=1)
    except IOError:
        ...
    bot = MarkdownWeComGroupBot(getenv("VALID_KEY"))
    print(bot)
    result = bot.send(f"## This is a test Markdown message: {randint(1, 100)}")
    print(result)
    assert result["errcode"] == 0
    try:
        bot.send("This message WON'T be sent", test=1)
    except IOError:
        ...
