# coding=utf-8
import logging

from gevent.monkey import patch_all, is_module_patched

if not is_module_patched('socket'):
    patch_all()  # 确保socket被补丁（协程非阻塞）

import gevent
import redis
from rediscluster import RedisCluster
from rediscluster.connection import ClusterConnectionPool


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
        动态配置类
        :param cluster_nodes:
        :param password:
        :param cache_capacity:
        :param cache_expire:
        :param socket_timeout:
        :param socket_connect_timeout:
        :param reconnection_interval:
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
        self.subscription_channel = channel + ":config_changes"

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
        """启动订阅协程，并监控其异常，异常时自动重启"""

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
        """更新缓存（处理LRU和过期时间）"""
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
        """读取配置（优先本地缓存，未命中/过期则拉取Redis）"""
        try:
            current_time = time.time()
            # 检查缓存是否存在且未过期
            if key in self.cache:
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
        """修改配置（同步到Redis Cluster并广播变更）"""
        try:
            self.redis.set(key, value)
            self.redis.publish(self.subscription_channel, json.dumps({'key': key, 'value': value}))
            self._update_cache(key, value)  # 更新本地缓存
        except Exception as e:
            log.error("配置同步失败: %s", str(e))
            raise

    def delete(self, key):
        """删除配置（同步到Redis Cluster并广播变更）"""
        try:
            self.redis.delete(key)
            self.redis.publish(self.subscription_channel, json.dumps({'key': key, 'value': None}))
            if key in self.cache:
                del self.cache[key]  # 删除本地缓存
        except Exception as e:
            log.error("配置删除失败: %s", str(e))
            raise


    def close(self):
        """关闭资源"""
        if self.enable_subscribe:
            self.redis.pubsub().unsubscribe(self.subscription_channel)
            self.subscription_greenlet.kill()
        self.redis.close()

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


def test_expire():
    con_list = [
        {'host': 'paas.dc.node1.dzqd.cn', 'port': 6301, 'name': 'paas.dc.node1.dzqd.cn:6301'},
        {'host': 'paas.dc.node2.dzqd.cn', 'port': 6301, 'name': 'paas.dc.node2.dzqd.cn:6301'},
        {'host': 'paas.dc.node3.dzqd.cn', 'port': 6301, 'name': 'paas.dc.node3.dzqd.cn:6301'}
    ]

    client = DynamicConfigClient(cluster_nodes=con_list, password='qDQkj2%zc8da*AP.2$afQZO', cache_capacity=1,
                                 cache_expire=10, channel="Y122010101")

    client.set("config1", "value1")
    client.set("config2", "value2")

    gevent.sleep(1.5)
    print(client.get("config1"))  # 应该返回 "value1"
    print(client.get("config2"))  # 应该返回 "value2"

    client.set("config1", "value1_new")
    print(client.get("config1"))  # 应该返回 "value1_new"

    client.refresh()
    print(client.get("config1"))  # 应该返回 "value1_new"



if __name__ == "__main__":
    # -------------------- 使用示例 --------------------
    # Redis Cluster 节点列表（示例用本地伪集群）
    con_list = [
        {'host': 'paas.dc.node1.dzqd.cn', 'port': 6301, 'name': 'paas.dc.node1.dzqd.cn:6301'},
        {'host': 'paas.dc.node2.dzqd.cn', 'port': 6301, 'name': 'paas.dc.node2.dzqd.cn:6301'},
        {'host': 'paas.dc.node3.dzqd.cn', 'port': 6301, 'name': 'paas.dc.node3.dzqd.cn:6301'}
    ]

    client = DynamicConfigClient(cluster_nodes=con_list, password='qDQkj2%zc8da*AP.2$afQZO', cache_capacity=500,
                                 cache_expire=1, enable_subscription=True, channel="Y122010101")

    # 读取配置（首次拉取Redis，后续走缓存）
    print("当前feature_switch值:", client.get('feature_switch', default='off'))

    # 修改配置（自动同步到集群并广播）
    client.set('feature_switch', 'on')

    # client.delete('feature_switch')
    gevent.sleep(10)  # 等待订阅协程处理消息

    print(client.get('feature_switch', default='1'))

    print(client.get('test_key3'))
    client.close()
