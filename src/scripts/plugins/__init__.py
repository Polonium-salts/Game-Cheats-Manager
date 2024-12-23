from .base_plugin import BasePlugin
from .antivirus_plugin import AntiVirusPlugin

# 注册所有可用的插件
available_plugins = [
    AntiVirusPlugin
] 