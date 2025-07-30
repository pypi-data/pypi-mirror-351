# coding=utf-8
class ConfigError(Exception):
    """配置操作基础异常"""


class ConfigExistsError(ConfigError):
    """配置已存在异常"""


class ConfigNotFoundError(ConfigError):
    """配置不存在异常"""