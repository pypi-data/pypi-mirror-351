
# -*- coding: utf-8 -*-
# @Author  : ydf
# @Time    : 2022/7/9 0008 12:12

import threading
import time
from typing import Optional

from fastboost.funboost_config_deafult import BrokerConnConfig
from fastboost.publishers.base_publisher import AbstractPublisher
from logging import getLogger

logger = getLogger(__name__)


class AliyunRocketmqPublisher(AbstractPublisher):
    _group_id__rocketmq_producer = {}
    _lock_for_create_producer = threading.Lock()

    def custom_init(self):
        try:
            from rocketmq.client import Producer
        except BaseException as e:
            raise ImportError(f'rocketmq包只支持linux和mac: {str(e)}') from e

        group_id = f'GID-{self._queue_name}'  # 阿里云要求 GID- 开头
        with self._lock_for_create_producer:
            if group_id not in self.__class__._group_id__rocketmq_producer:
                producer = Producer(group_id)

                # 设置阿里云认证信息
                producer.set_session_credentials(
                    BrokerConnConfig.ALIYUN_ROCKETMQ_ACCESS_KEY,
                    BrokerConnConfig.ALIYUN_ROCKETMQ_SECRET_KEY,
                    ''
                )

                # 设置阿里云 Name Server 地址
                producer.set_namesrv_addr(BrokerConnConfig.ALIYUN_ROCKETMQ_NAMESRV_ADDR)

                # 设置实例 ID（如果有）
                if getattr(BrokerConnConfig, 'ALIYUN_ROCKETMQ_INSTANCE_ID', None):
                    producer.set_instance_name(BrokerConnConfig.ALIYUN_ROCKETMQ_INSTANCE_ID)

                producer.start()
                self.__class__._group_id__rocketmq_producer[group_id] = producer
            else:
                producer = self.__class__._group_id__rocketmq_producer[group_id]
            self._producer = producer

    def concrete_realization_of_publish(self, msg: str):
        try:
            from rocketmq.client import Message
        except BaseException as e:
            raise ImportError(f'rocketmq包只支持linux和mac: {str(e)}') from e

        rocket_msg = Message(self._queue_name)
        rocket_msg.set_body(msg)

        # 可选设置 TAG
        if getattr(self, '_tag', None):
            rocket_msg.put_user_property('TAGS', self._tag)

        result = self._producer.send_sync(rocket_msg)
        if result.status != 'SEND_OK':
            logger.error(f"消息发送失败: {result.status}, 内容: {msg}")
        else:
            logger.info(f"消息发送成功: {result.msg_id}")

    def clear(self):
        logger.warning('清除队列暂不支持，python版的rocket包无相关API。')

    def get_message_count(self):
        if time.time() - getattr(self, '_last_warning_count', 0) > 300:
            setattr(self, '_last_warning_count', time.time())
            logger.warning('获取消息数量，python版的rocket包暂不支持。')
        return -1

    def close(self):
        if self._producer:
            self._producer.shutdown()
            logger.info("RocketMQ Producer 已关闭")

    def __del__(self):
        self.close()