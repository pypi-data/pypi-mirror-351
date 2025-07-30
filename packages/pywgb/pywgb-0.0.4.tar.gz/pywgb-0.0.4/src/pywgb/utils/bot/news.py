#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
News type message sender

- Author: Rex Zhou <879582094@qq.com>
- Created Time: 2025/5/30 10:31
- Copyright: Copyright © 2025 Rex Zhou. All rights reserved.
"""

from typing import List, Dict

from . import AbstractWeComGroupBot, FilePathLike


class NewsWeComGroupBot(AbstractWeComGroupBot):
    """News type message Wecom Group Bot"""

    @property
    def _doc_key(self) -> str:
        return "图文类型"

    @staticmethod
    def _check_articles(articles: List[Dict[str, str]],
                        test: str = None) -> None:
        """
        Check all articles are standard format.
        :param articles: A list of articles.
        :param test: The test value.
        :return:
        """
        for index, article in enumerate(articles):
            if not isinstance(article, dict) or test == "article_data_error":
                msg_ = f"The No.{index + 1} article data is not a dict"
                raise ValueError(msg_)
            for param in ["title", "url"]:
                if param not in article or not article[
                        param] or test == "article_parameter_error":
                    msg_ = f"The No.{index + 1} article lack required parameter: {param}"
                    raise ValueError(msg_)

    # pylint:disable=unused-argument
    def prepare_data(self,
                     msg: str = None,
                     /,
                     file_path: FilePathLike = None,
                     **kwargs) -> dict:
        """
        Convert the message to News format.
        :param msg: Message to convert.
        :param file_path: File path.
        :param kwargs: Other keyword arguments.
        :return: Converted message.
        """
        articles = kwargs.get('articles', [])
        if not articles:
            raise ValueError("No articles found")
        if len(articles) > 8:
            raise ValueError("Too many articles. The maximum limit is 8")
        # Check the article's required parameters
        self._check_articles(articles, test=kwargs.get("test"))
        result = {"msg": {"msgtype": "news", "news": {"articles": articles}}}
        return result
