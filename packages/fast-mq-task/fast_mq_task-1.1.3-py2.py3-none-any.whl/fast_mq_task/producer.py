# -*- coding: utf-8 -*-
import logging
import time
from aio_pika import Message, DeliveryMode
from aiormq import AMQPConnectionError, ConnectionClosed, ChannelInvalidStateError
from tenacity import retry, retry_if_exception_type, wait_fixed

from .client import RabbitMQClient
from .models import TaskMessage


# --------------------------
# 生产者模块 (producer.py)
# --------------------------
class TaskProducer(RabbitMQClient):

    @retry(
        retry=retry_if_exception_type((AMQPConnectionError, ConnectionClosed, RuntimeError, ChannelInvalidStateError)),
        wait=wait_fixed(5),
    )
    async def publish_task(self, task: TaskMessage):
        # 确保队列定义
        _, exchange = await self.ensure_declare(task_type=task.task_type)

        message = Message(
            body=task.json().encode(),
            content_type="application/json",
            headers={
                "x-task-type": task.task_type,
                "x-created-at": time.time()
            },
            delivery_mode=DeliveryMode.PERSISTENT,  # 添加消息持久化
            priority=task.priority  # 设置消息优先级
        )

        try:
            await exchange.publish(
                message=message,
                routing_key=task.get_routing_key()
            )
            # print(f"Published message {task}")
        except (AMQPConnectionError, ConnectionClosed, ChannelInvalidStateError, RuntimeError) as e:
            logging.error(f"链路异常: {str(e)}")
            raise e
