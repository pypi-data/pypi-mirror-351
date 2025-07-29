# 版本信息
__version__ = '0.0.2'

# 导出utils模块
from .utils import *

# 定义 __all__ 控制 from fvgtools import * 的行为
__all__ = ['utils']

# 可选：包级别初始化（如日志、全局配置）
print("Initializing fvgtools...")