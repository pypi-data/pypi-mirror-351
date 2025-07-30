# coding=utf-8
import logging

from gevent.monkey import patch_all, is_module_patched

if not is_module_patched('socket'):
    patch_all()  # 确保socket被补丁（协程非阻塞）

import gevent
import redis
from rediscluster import RedisCluster
from rediscluster.connection import ClusterConnectionPool
from .exceptions import ConfigValueNotStringError

import json
import time
from collections import OrderedDict  # LRU实现


log = logging.getLogger(__name__)


def _ensure_str(s, encoding='utf-8'):
    """将unicode转换为str，其他类型保持不变"""
    if isinstance(s, unicode):
        return s.encode(encoding)
    return s


class DynamicConfigClient:
    def __init__(self,
                 cluster_nodes,  # 节点列表（如["host1:port1", "host2:port2"]）
                 password=None,
                 cache_capacity=1000,  # LRU最大容量
                 cache_expire=300,  # 缓存过期时间（秒）
                 socket_timeout=10, # 执行超时时间
                 socket_connect_timeout=30, # 连接超时时间
                 subscription_reconnection_interval=5, # 重连间隔时间，订阅模式连接断开重连时间间隔
                 enable_subscription=False, # 是否开启订阅模式 默认不开启
                 channel="global",
                 ):
        """
        初始化动态配置客户端

        :param cluster_nodes: Redis集群节点列表，格式[{"host":"host1","port":port1}]
        :type cluster_nodes: list[dict|str]
        :param password: Redis访问密码
        :type password: str
        :param cache_capacity: 本地LRU缓存容量
        :type cache_capacity: int
        :param cache_expire: 缓存过期时间(秒)
        :type cache_expire: int
        :param socket_timeout: 操作超时时间(秒)
        :type socket_timeout: int
        :param socket_connect_timeout: 连接超时时间(秒)
        :type socket_connect_timeout: int
        :param subscription_reconnection_interval: 订阅重连间隔(秒)
        :type subscription_reconnection_interval: int
        :param enable_subscription: 是否启用订阅模式
        :type enable_subscription: bool
        :param channel: 订阅频道名称
        :type channel: str
        """
        # -------------------- Redis Cluster 初始化 --------------------
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
        self.subscription_channel = "dynamic_config_changes:"+channel

        # -------------------- 本地缓存配置 --------------------
        self.cache = OrderedDict()  # LRU缓存（键: {value, expire_time}）
        self.cache_capacity = cache_capacity  # LRU最大容量
        self.cache_expire = cache_expire  # 缓存过期时间（秒）

        # -------------------- 配置变更监听 --------------------
        self.enable_subscribe = enable_subscription
        self.subscription_reconnection_interval = subscription_reconnection_interval
        if self.enable_subscribe:
            self._start_subscription()  # 启动订阅协程（带异常监控）

    def _start_subscription(self):
        """启动订阅协程，并监控其异常，异常时自动重启
        """

        def restart_on_failure(greenlet):
            log.error("订阅协程异常终止，尝试重启...")
            self._start_subscription()  # 递归重启

        self.subscription_greenlet = gevent.spawn(self._subscribe_loop)
        self.subscription_greenlet.link(restart_on_failure)  # 绑定异常回调

    def _subscribe_loop(self):
        while True:  # 无限循环确保连接断开后重新订阅
            pubsub = None
            try:
                # 初始化 Pub/Sub 并订阅
                pubsub = self.redis.pubsub()
                pubsub.subscribe(self.subscription_channel)

                # 监听消息（带超时检测）
                for message in pubsub.listen():
                    if message['type'] == 'message':
                        log.info("收到配置变更广播: %v", message['data'])
                        # 处理消息（转换类型、更新缓存等）
                        data = json.loads(message['data'].decode('utf-8'))
                        key = _ensure_str(data['key'])
                        new_value = _ensure_str(['value'])
                        self._update_cache(key, new_value)

            except (redis.exceptions.ConnectionError, redis.exceptions.TimeoutError) as e:
                log.info("Pub/Sub 连接超时: %s，%d秒后尝试重连...", str(e), self.subscription_reconnection_interval)
                gevent.sleep(self.subscription_reconnection_interval)  # 等待重连间隔
            except Exception as e:
                log.error("Pub/Sub 未知异常: %s，%d秒后尝试重连...",str(e), self.subscription_reconnection_interval)
                gevent.sleep(self.subscription_reconnection_interval)
            finally:
                # 确保关闭旧连接，释放资源
                if pubsub:
                    try:
                        pubsub.close()  # 显式关闭 Pub/Sub 连接
                    except Exception as e:
                        log.error("关闭旧 Pub/Sub 连接失败: %s", str(e))


    def _update_cache(self, key, value):
        """更新缓存（处理LRU和过期时间）
        """
        if self.cache_capacity <= 0:
            return
        # 若键存在，先删除（避免重复）
        if key in self.cache:
            del self.cache[key]

        if value is None:
            return
        # 添加新条目（移至末尾表示最近使用）
        self.cache[key] = {
            'value': value,
            'expire_time': time.time() + self.cache_expire
        }
        # 若超过容量，移除最久未使用的条目（OrderedDict最前的键）
        while len(self.cache) > self.cache_capacity:
            self.cache.popitem(last=False)  # last=False: 移除最前（最久未使用）

    def get(self, key, default=None):
        """读取配置（优先本地缓存，未命中/过期则拉取Redis）

        :param key: 配置键名
        :type key: str
        :param default: 当键不存在时返回的默认值
        :type default: str|None
        :return: 配置值或默认值
        :rtype: str|None
        :raises Exception: 当Redis操作失败时抛出
        """
        try:
            current_time = time.time()
            # 检查缓存是否存在且未过期
            if self.cache_capacity > 0 and key in self.cache:
                cache_entry = self.cache[key]
                if cache_entry['expire_time'] > current_time:
                    # 命中缓存，将条目移至末尾（标记为最近使用）
                    self.cache.pop(key)
                    self.cache[key] = cache_entry
                    return cache_entry['value']
                else:
                    # 缓存过期，删除旧条目
                    del self.cache[key]

            # 缓存未命中/过期，从Redis拉取
            value = self.redis.get(key)
            if value is not None:
                self._update_cache(key, value)  # 更新缓存
                return value
            return default
        except Exception as e:
            log.error("配置读取失败: %s", str(e))
            raise


    def set(self, key, value):
        """修改配置（同步到Redis Cluster并广播变更）

        :param key: 配置键名
        :type key: str
        :param value: 配置值
        :type value: str
        :return: bool
        :rtype: None
        :raises Exception: 当Redis操作失败时抛出
        """
        if not isinstance(key, basestring) or not isinstance(value, basestring):
            raise ConfigValueNotStringError("key或value必须为字符串类型")
        try:
            result = self.redis.set(key, value)
            self.redis.publish(self.subscription_channel, json.dumps({'key': key, 'value': value}))
            self._update_cache(key, value)  # 更新本地缓存
        except Exception as e:
            log.error("配置同步失败: %s", str(e))
            raise
        return result

    def delete(self, key):
        """删除配置（同步到Redis Cluster并广播变更）

        :param key: 配置键名
        :type key: str
        :return: 删除键数量
        :rtype: int
        :raises Exception: 当Redis操作失败时抛出
        """
        try:
            result = self.redis.delete(key)
            self.redis.publish(self.subscription_channel, json.dumps({'key': key, 'value': None}))
            if key in self.cache:
                del self.cache[key]  # 删除本地缓存
        except Exception as e:
            log.error("配置删除失败: %s", str(e))
            raise
        return result

    def refresh(self, *keys):
        refreshed_keys = []
        try:
            if not keys:
                keys = list(self.cache.keys())
            # 刷新指定键列表
            for k in keys:
                value = self.get(k)
                if value is not None:
                    self._update_cache(k, value)
                    refreshed_keys.append(k)
                else:
                    # 键不存在，从缓存中删除
                    if k in self.cache:
                        del self.cache[k]
            log.info("刷新完成，成功%d个，失败%d个" ,len(refreshed_keys), len(keys) - len(refreshed_keys))
            return refreshed_keys
        except Exception as e:
            log.error("刷新键 %v 失败: %s", keys, str(e))
            raise