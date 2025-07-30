"""
命令行接口模块

提供：
- 主程序入口
- 命令行参数解析
- 交互式界面
"""

from .main import main, run_cli

__all__ = [
    "main",
    "run_cli",
]
