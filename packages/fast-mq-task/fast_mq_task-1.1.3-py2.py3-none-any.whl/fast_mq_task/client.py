# -*- coding: utf-8 -*-
import logging
import os

import aio_pika
from typing import Dict, Union
from aio_pika import Exchange, ExchangeType, Channel, Queue
from aio_pika.abc import AbstractExchange, AbstractQueue
from aiormq import ConnectionClosed, ChannelClosed, AMQPConnectionError
from tenacity import retry, retry_if_exception_type, wait_fixed

from .keys import get_default_exchange_name, get_default_routing_key, get_default_queue_name

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# --------------------------
# 客户端基础模块 (client.py)
# --------------------------
class RabbitMQClient:
    def __init__(self, amqp_url: str, message_ttl: int = None):
        self.amqp_url = amqp_url
        self.message_ttl = message_ttl or os.getenv('RABBIT_DEFAULT_MESSAGE_TTL') or 432000000
        self.connection = None
        self.channels: Dict[str, Channel] = {}
        self.exchanges: Dict[str, Union[Exchange, AbstractExchange]] = {}
        self.queues: Dict[str, Union[Queue, AbstractQueue]] = {}

    @retry(
        retry=retry_if_exception_type((
                ConnectionClosed,
                ConnectionError,
                ChannelClosed,
                AMQPConnectionError
        )),
        wait=wait_fixed(5)
    )
    async def connect(self):
        """支持多种异常类型的指数退避重连机制"""
        if self.connection and not self.connection.is_closed:
            return self

        self.connection = await aio_pika.connect_robust(self.amqp_url, timeout=10)
        logging.info("链接建立成功")
        return self

    async def close(self):
        """带异常处理的关闭方法"""
        try:
            for channel in list(self.channels.values()):
                await channel.close()
            if self.connection:
                await self.connection.close()
        except Exception as e:
            logging.error(f"关闭链接时发生异常: {str(e)}")
        finally:
            # 清理缓存资源
            self.exchanges.clear()
            self.queues.clear()
            self.channels.clear()

    async def get_channel(self, task_type: str, prefetch: int = 4) -> Channel:
        if not self.connection or self.connection.is_closed:
            await self.connect()

        task_type = task_type or 'default'
        if task_type not in self.channels:
            channel = await self.connection.channel()
            await channel.set_qos(
                prefetch_count=prefetch
            )
            logging.info(f"信道定义: task_type={task_type}, prefetch={prefetch}")
            self.channels[task_type] = channel

        return self.channels[task_type]

    async def get_exchange(self, channel: Channel, exchange_name: str = None, exchange_type: str = "topic") -> Exchange:
        # 统一交换器类型为小写
        exchange_type = exchange_type.lower()

        # 添加交换器类型校验
        if exchange_type not in ["direct", "topic", "fanout", "headers"]:
            raise ValueError(f"Invalid exchange type: {exchange_type}")
        if not exchange_name:
            exchange_name = get_default_exchange_name()

        if exchange_name not in self.exchanges:
            self.exchanges[exchange_name] = await channel.declare_exchange(
                name=exchange_name,
                type=exchange_type,
                durable=True,  # 持久化交换器
                auto_delete=False,
                arguments={
                    "x-queue-type": "quorum"  # 使用高可用队列类型
                }
            )
            logging.info(f"交换机定义: exchange={exchange_name}, type={exchange_type}")

        return self.exchanges[exchange_name]

    async def ensure_declare(self, task_type: str, prefetch: int = 10):
        # 创建专属channel避免相互影响
        channel = await self.get_channel(task_type, prefetch)

        exchange_key = get_default_exchange_name()
        exchange_type = ExchangeType.TOPIC
        routing_key = get_default_routing_key(task_type)
        queue_key = get_default_queue_name(task_type)

        # 声明交换器和队列
        exchange = await self.get_exchange(channel=channel, exchange_name=exchange_key, exchange_type=exchange_type)
        if queue_key not in self.queues:
            queue = await channel.declare_queue(
                name=queue_key,
                durable=True,
                arguments={
                    'x-max-priority': 10,  # 支持优先级队列
                    'x-message-ttl': self.message_ttl  # 24小时过期（单位：毫秒）
                }
            )
            await queue.bind(exchange, routing_key)
            self.queues[queue_key] = queue

        return self.queues[queue_key], exchange
