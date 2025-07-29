# -*- coding: utf-8 -*-
import time
import uuid
from typing import Any, Dict, Callable, Optional
from aio_pika import ExchangeType
from pydantic import BaseModel, Field

from . import keys


# --------------------------
# 模型类模块 (models.py)
# --------------------------
class RabbitMeta(BaseModel):
    """
    消息发布元数据
    """
    # 交换机键
    task_type: str = None
    # 交换机键
    exchange_key: str = None
    # 交换机类型
    exchange_type: str = None
    # 绑定关系（路由）键
    routing_key: str = None
    # 队列名称
    queue_key: str = None
    # 队列名称
    prefetch: int = None
    # 队列名称
    max_workers: int = None

    # 处理函数
    handler_func: Callable = None

    def __init__(self, task_type: str = None, prefetch: int = None, max_workers: int = None, handler_func: Callable = None, **data: Any):
        super().__init__(**data)
        self.task_type = task_type

        self.prefetch = prefetch
        self.max_workers = max_workers
        self.handler_func = handler_func

        self.exchange_key = keys.get_default_exchange_name()
        self.exchange_type = ExchangeType.TOPIC
        self.routing_key = keys.get_default_routing_key(task_type)
        self.queue_key = keys.get_default_queue_name(task_type)


class TaskMessage(BaseModel):
    task_type: str
    data: Dict[str, Any] = Field(default_factory=dict)
    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: int = Field(default_factory=lambda: int(time.time()))
    priority: Optional[int] = Field(default=0, description="任务优先级，0-10，数字越大优先级越高")

    def get_routing_key(self):
        return keys.get_default_routing_key(self.task_type)
