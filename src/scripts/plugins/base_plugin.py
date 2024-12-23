from abc import ABC, abstractmethod

class BasePlugin(ABC):
    """插件基类"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """插件名称"""
        pass
        
    @property
    @abstractmethod
    def description(self) -> str:
        """插件描述"""
        pass
        
    @property
    @abstractmethod
    def version(self) -> str:
        """插件版本"""
        pass
        
    @property
    @abstractmethod
    def author(self) -> str:
        """插件作者"""
        pass
        
    @abstractmethod
    def initialize(self, app):
        """初始化插件"""
        pass
        
    @abstractmethod
    def cleanup(self):
        """清理插件"""
        pass 