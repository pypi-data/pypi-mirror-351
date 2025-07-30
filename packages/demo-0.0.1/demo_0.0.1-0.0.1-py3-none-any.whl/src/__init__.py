"""
lqxnjk lqxnjk@qq.com
"""
__name__ = "demo"
__version__ = "0.0.1"

# 明确公开的API
__all__ = []

# 自动添加包内数据文件路径
import os, sys

_DATA_PATH = os.path.join(os.path.dirname(__file__), "data")

# 处理不同Python版本的兼容性
if sys.version_info < (3, 8):
    pass
    # from typing_extensions import Final
else:
    pass
    # from typing import Final


# 为包提供版本信息
def version():
    return __version__


# 延迟加载重型依赖（如 TensorFlow/PyTorch）
def __getattr__(name):
    if name == "HeavyClass":
        # from .heavy_module import HeavyClass
        # return HeavyClass
        pass
    raise AttributeError(f"No attribute {name}")


# 为包提供类型提示（PEP 561）
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass
