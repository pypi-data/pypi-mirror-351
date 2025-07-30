# coding=utf-8
import logging

import redis
import json
import time
from rediscluster import RedisCluster
from rediscluster.connection import ClusterConnectionPool
from .exceptions import ConfigExistsError, ConfigNotFoundError, ConfigValueNotStringError

log = logging.getLogger(__name__)

class DynamicConfigManager:
    def __init__(self,
                 cluster_nodes,  # 节点列表（如["host1:port1", "host2:port2"]）
                 password=None,
                 socket_timeout=10,  # 执行超时时间
                 socket_connect_timeout=30,  # 连接超时时间
                 ):
        self.conn_pool = ClusterConnectionPool(
            startup_nodes=cluster_nodes,
            password=password,
            max_connections=5,  # 每个节点的最大连接数
            max_connections_per_node=True,
            socket_timeout=socket_timeout,
            socket_connect_timeout=socket_connect_timeout,
            skip_full_coverage_check=True,
        )
        self.redis = RedisCluster(connection_pool=self.conn_pool)


    def create_config(self, key, value, channel=None):
        """
        创建新的配置项

        :param key: 配置键名
        :type key: str
        :param value: 配置值
        :type value: str
        :param channel: 变更通知频道，可选
        :type channel: str|None
        :return: 操作是否成功
        :rtype: bool
        :raises ConfigExistsError: 当配置键已存在时抛出
        """
        if not isinstance(key, basestring) or not isinstance(value, basestring):
            raise ConfigValueNotStringError("key或value必须为字符串类型")
        result = self.redis.setnx(key, value)
        if not result:
            raise ConfigExistsError("配置键 '%s' 已存在" % key)
        self._publish_change(key, value, channel)
        return True

    def update_config(self, key, value, channel=None):
        """
        更新现有配置项

        :param key: 要更新的配置键名
        :type key: str
        :param value: 新的配置值
        :type value: str
        :param channel: 变更通知频道，可选
        :type channel: str|None
        :return: 操作是否成功
        :rtype: bool
        :raises ConfigNotFoundError: 当配置键不存在时抛出
        """
        if not isinstance(key, basestring) or not isinstance(value, basestring):
            raise ConfigValueNotStringError("key或value必须为字符串类型")

        if not self.redis.exists(key):
            raise ConfigNotFoundError("配置键 '%s' 不存在" % key)

        # 更新配置
        result = self.redis.set(key, value)

        # 发布变更通知
        self._publish_change(key, value, channel)
        return result

    def get_config(self, key, default=None):
        """
        获取配置项的值

        :param key: 要获取的配置键名
        :type key: str
        :param default: 当键不存在时返回的默认值，可选
        :type default: str|None
        :return: 配置值或默认值
        :rtype: str|None
        """
        try:
            value = self.redis.get(key)
            return value.decode('utf-8') if value else default
        except Exception as e:
            log.error("获取配置失败: %s" % str(e))
            return default

    def _publish_change(self, key, value, channel):
        try:
            if not channel:
                return
            channel = "dynamic_config_changes:"+channel
            message = json.dumps({
                'key': key,
                'value': value,
            })
            self.redis.publish(channel, message)
            log.info("已发布配置变更通知到频道 '%s': %s" % (channel, key))
        except Exception as e:
            log.error("发布变更通知失败: %s" % str(e))

    def delete_config(self, key, channel=None):
        """
        删除配置项

        :param key: 要删除的配置键名
        :type key: str
        :param channel: 变更通知频道，可选
        :type channel: str|None
        :return: 删除键数量
        :rtype: int
        :raises ConfigNotFoundError: 当配置键不存在时抛出
        """
        if not self.redis.exists(key):
            raise ConfigNotFoundError("配置键 '%s' 不存在" % key)

        result = self.redis.delete(key)
        if channel:
            self._publish_change(key, None, channel)  # 发布删除通知
        return result

    def list_configs(self, pattern='*'):
        """
        列出匹配模式的配置键

        :param pattern: 键名匹配模式，默认为'*'
        :type pattern: str
        :return: 匹配的键名列表
        :rtype: list[str]
        """
        try:
            keys = self.redis.keys(pattern)
            return [key.decode('utf-8') for key in keys]
        except Exception as e:
            log.error("列出配置失败: %s" % str(e))
            return []

