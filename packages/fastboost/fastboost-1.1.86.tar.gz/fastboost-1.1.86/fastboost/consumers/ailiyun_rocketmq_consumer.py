# -*- coding: utf-8 -*-
# @Author  : ydf
# @Time    : 2022/7/8 0008 13:27

import json
import time
from typing import Optional
from fastboost.constant import BrokerEnum
from fastboost.consumers.base_consumer import AbstractConsumer
from fastboost.funboost_config_deafult import BrokerConnConfig
from fastboost.publishers.rocketmq_publisher import RocketmqPublisher
from fastboost.core.func_params_model import PublisherParams

logger = __import__('logging').getLogger(__name__)


class AliyunRocketmqConsumer(AbstractConsumer):
    """
    支持阿里云 RocketMQ 的消费者类。
    """

    # 从全局配置中读取阿里云相关参数
    ALIYUN_ROCKETMQ_ACCESS_KEY = getattr(BrokerConnConfig, 'ALIYUN_ROCKETMQ_ACCESS_KEY', None)
    ALIYUN_ROCKETMQ_SECRET_KEY = getattr(BrokerConnConfig, 'ALIYUN_ROCKETMQ_SECRET_KEY', None)
    ALIYUN_ROCKETMQ_NAMESRV_ADDR = getattr(BrokerConnConfig, 'ALIYUN_ROCKETMQ_NAMESRV_ADDR', None)
    ALIYUN_ROCKETMQ_INSTANCE_ID = getattr(BrokerConnConfig, 'ALIYUN_ROCKETMQ_INSTANCE_ID', None)

    GROUP_ID_PREFIX = 'GID-'  # 阿里云要求 Group ID 以 GID- 开头

    def _shedual_task(self):
        try:
            from rocketmq.client import PushConsumer
        except BaseException as e:
            raise ImportError(f'rocketmq包只支持linux和mac: {e}') from e

        group_id = f'{self.GROUP_ID_PREFIX}{self._queue_name}'
        consumer = PushConsumer(group_id)

        if not self.ALIYUN_ROCKETMQ_NAMESRV_ADDR:
            raise ValueError("未配置 ALIYUN_ROCKETMQ_NAMESRV_ADDR")

        consumer.set_namesrv_addr(self.ALIYUN_ROCKETMQ_NAMESRV_ADDR)
        consumer.set_thread_count(1)
        consumer.set_message_batch_max_size(self.consumer_params.concurrent_num)

        # 设置阿里云认证信息
        if self.ALIYUN_ROCKETMQ_ACCESS_KEY and self.ALIYUN_ROCKETMQ_SECRET_KEY:
            consumer.set_session_credentials(
                self.ALIYUN_ROCKETMQ_ACCESS_KEY,
                self.ALIYUN_ROCKETMQ_SECRET_KEY,
                ''
            )

        if self.ALIYUN_ROCKETMQ_INSTANCE_ID:
            consumer.set_instance_name(self.ALIYUN_ROCKETMQ_INSTANCE_ID)

        # 初始化消息重发 publisher
        self._publisher = RocketmqPublisher(publisher_params=PublisherParams(queue_name=self._queue_name))

        def callback(rocketmq_msg):
            self.logger.debug(f'从阿里云 RocketMQ 的 [{self._queue_name}] 主题中取出消息: {rocketmq_msg.body}')
            kw = {'body': rocketmq_msg.body, 'rocketmq_msg': rocketmq_msg}
            self._submit_task(kw)

        consumer.subscribe(self._queue_name, callback)
        consumer.start()

        self.logger.info(f"阿里云 RocketMQ 消费者已启动，监听主题 [{self._queue_name}]")
        while True:
            time.sleep(3600)  # 长时间运行

    def _confirm_consume(self, kw):
        """
        消息确认消费成功。RocketMQ 自动提交 offset。
        """
        pass  # 阿里云 RocketMQ 默认自动提交 offset

    def _requeue(self, kw):
        """
        消息重新入队（失败后重试）
        """
        self._publisher.publish(kw['body'])
