# -*- coding: utf-8 -*-
class DropMessageException(Exception):
    """
    丢弃消息
    """

    def __init__(self, msg=None):
        self.msg = msg


class RequeueMessageException(Exception):
    """
    重新入队再次处理
    """

    def __init__(self, msg=None):
        self.msg = msg
