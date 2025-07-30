# coding=utf-8
import logging

import redis
import json
import time
from rediscluster import RedisCluster
from rediscluster.connection import ClusterConnectionPool
from exceptions import ConfigExistsError, ConfigNotFoundError

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
        result = self.redis.setnx(key, value)
        if not result:
            raise ConfigExistsError("配置键 '%s' 已存在" % key)
        self._publish_change(key, value, channel)
        return True

    def update_config(self, key, value, channel=None):
        # 检查键是否存在
        if not self.redis.exists(key):
            raise ConfigNotFoundError("配置键 '%s' 不存在" % key)

        # 更新配置
        self.redis.set(key, value)

        # 发布变更通知
        self._publish_change(key, value, channel)
        return True

    def get_config(self, key, default=None):
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
        if not self.redis.exists(key):
            raise ConfigNotFoundError("配置键 '%s' 不存在" % key)

        self.redis.delete(key)
        if channel:
            self._publish_change(key, None, channel)  # 发布删除通知
        return True

    def list_configs(self, pattern='*'):
        try:
            keys = self.redis.keys(pattern)
            return [key.decode('utf-8') for key in keys]
        except Exception as e:
            log.error("列出配置失败: %s" % str(e))
            return []

