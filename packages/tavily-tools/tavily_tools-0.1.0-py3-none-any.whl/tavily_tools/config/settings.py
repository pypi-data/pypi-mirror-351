"""
配置管理模块

用于安全地加载和管理环境变量配置，提供：
- 环境变量加载和验证
- API客户端初始化
- 配置项管理
- 目录结构确保
"""

import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional

from dotenv import load_dotenv

from ..utils.helpers import ensure_directory


class Config:
    """
    配置管理类

    统一管理应用程序的所有配置项
    """

    def __init__(self, env_file: Optional[str] = None):
        """
        初始化配置，自动加载.env文件

        Args:
            env_file: 环境变量文件路径，默认为项目根目录的.env
        """
        self._env_file = env_file
        self._load_environment()
        self._validate_config()
        self._ensure_directories()

    def _load_environment(self):
        """加载环境变量"""
        # 查找.env文件的路径
        if self._env_file:
            env_path = Path(self._env_file)
        else:
            # 从当前模块向上查找项目根目录
            current_dir = Path(__file__).parent
            env_path = None

            # 向上查找.env文件，最多查找5级
            for _ in range(5):
                test_path = current_dir / ".env"
                if test_path.exists():
                    env_path = test_path
                    break
                current_dir = current_dir.parent
                if current_dir == current_dir.parent:  # 到达根目录
                    break

            # 如果没找到，使用默认路径
            if not env_path:
                env_path = Path.cwd() / ".env"

        # 如果.env文件存在，则加载它
        if env_path.exists():
            load_dotenv(env_path)
            print(f"✅ 已加载环境变量文件: {env_path}")
        else:
            print(f"⚠️  未找到.env文件: {env_path}")
            print("请根据.env.template创建.env文件并配置API密钥")

    def _validate_config(self):
        """验证必要的配置项"""
        if not self.tavily_api_key:
            print("❌ 错误: 未找到TAVILY_API_KEY环境变量")
            print("📝 请按以下步骤配置:")
            print("1. 复制 .env.template 为 .env")
            print("2. 编辑 .env 文件，填入您的Tavily API密钥")
            print("3. 重新运行程序")
            sys.exit(1)
        elif self.tavily_api_key == "your_tavily_api_key_here":
            print("❌ 错误: 请在.env文件中设置真实的API密钥")
            print("当前API密钥仍为模板默认值")
            sys.exit(1)

        # 验证API密钥格式
        if len(self.tavily_api_key) < 20:
            print("⚠️  警告: API密钥长度似乎不正确，请检查配置")

    def _ensure_directories(self):
        """确保必要的目录存在"""
        ensure_directory(self.results_save_path)

        # 确保日志目录存在（如果配置了）
        if hasattr(self, "log_path") and self.log_path:
            ensure_directory(Path(self.log_path).parent)

    @property
    def tavily_api_key(self) -> str:
        """获取Tavily API密钥"""
        return os.getenv("TAVILY_API_KEY", "")

    @property
    def default_search_query(self) -> str:
        """获取默认搜索查询"""
        return os.getenv("DEFAULT_SEARCH_QUERY", "deepseek")

    @property
    def results_save_path(self) -> str:
        """获取结果保存路径"""
        return os.getenv("RESULTS_SAVE_PATH", "./results/")

    @property
    def log_level(self) -> str:
        """获取日志级别"""
        return os.getenv("LOG_LEVEL", "INFO")

    @property
    def log_path(self) -> str:
        """获取日志文件路径"""
        return os.getenv("LOG_PATH", "./logs/tavily_tools.log")

    @property
    def max_search_results(self) -> int:
        """获取最大搜索结果数量"""
        try:
            return int(os.getenv("MAX_SEARCH_RESULTS", "10"))
        except ValueError:
            return 10

    @property
    def search_timeout(self) -> int:
        """获取搜索超时时间（秒）"""
        try:
            return int(os.getenv("SEARCH_TIMEOUT", "30"))
        except ValueError:
            return 30

    @property
    def enable_html_reports(self) -> bool:
        """是否启用HTML报告生成"""
        return os.getenv("ENABLE_HTML_REPORTS", "true").lower() in ("true", "1", "yes", "on")

    def show_config(self, show_sensitive: bool = False):
        """
        显示当前配置（隐藏敏感信息）

        Args:
            show_sensitive: 是否显示敏感信息（如完整API密钥）
        """
        print("📋 当前配置:")

        # API密钥显示
        if show_sensitive:
            api_key_display = self.tavily_api_key
        else:
            api_key_display = f"{'*' * 8}...{self.tavily_api_key[-4:] if len(self.tavily_api_key) > 4 else '****'}"

        print(f"   🔑 API密钥: {api_key_display}")
        print(f"   🔍 默认搜索: {self.default_search_query}")
        print(f"   📁 保存路径: {Path(self.results_save_path).absolute()}")
        print(f"   📊 最大结果数: {self.max_search_results}")
        print(f"   ⏱️  搜索超时: {self.search_timeout}秒")
        print(f"   📄 HTML报告: {'启用' if self.enable_html_reports else '禁用'}")
        print(f"   📝 日志级别: {self.log_level}")

    def to_dict(self) -> Dict[str, Any]:
        """
        将配置转换为字典

        Returns:
            配置字典（不包含敏感信息）
        """
        return {
            "default_search_query": self.default_search_query,
            "results_save_path": self.results_save_path,
            "max_search_results": self.max_search_results,
            "search_timeout": self.search_timeout,
            "enable_html_reports": self.enable_html_reports,
            "log_level": self.log_level,
            "api_key_configured": bool(self.tavily_api_key),
        }

    def update_config(self, **kwargs):
        """
        更新配置项（仅在当前会话中有效）

        Args:
            **kwargs: 要更新的配置项
        """
        for key, value in kwargs.items():
            env_key = key.upper()
            os.environ[env_key] = str(value)
            print(f"✅ 已更新配置: {key} = {value}")


def get_tavily_client():
    """
    获取配置好的Tavily客户端

    Returns:
        TavilyClient: 已配置API密钥的客户端实例

    Raises:
        SystemExit: 如果配置无效或客户端初始化失败
    """
    try:
        from tavily import TavilyClient

        config = Config()
        client = TavilyClient(
            api_key=config.tavily_api_key,
            # 可以在这里添加其他客户端配置
        )

        print(f"🔑 Tavily客户端初始化成功")
        return client

    except ImportError as e:
        print(f"❌ 无法导入Tavily库: {e}")
        print("请安装tavily-python: pip install tavily-python")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Tavily客户端初始化失败: {e}")
        print("请检查您的API密钥配置和网络连接")
        sys.exit(1)


def get_config() -> Config:
    """
    获取配置实例

    Returns:
        Config: 配置实例
    """
    return Config()


# 全局配置实例（延迟初始化）
_config: Optional[Config] = None


def init_config(env_file: Optional[str] = None, force_reload: bool = False) -> Config:
    """
    初始化全局配置

    Args:
        env_file: 环境变量文件路径
        force_reload: 是否强制重新加载

    Returns:
        Config: 配置实例
    """
    global _config

    if _config is None or force_reload:
        _config = Config(env_file)

    return _config


def get_global_config() -> Optional[Config]:
    """
    获取全局配置实例（如果已初始化）

    Returns:
        Config实例或None
    """
    return _config


# 配置验证函数
def validate_environment() -> bool:
    """
    验证环境配置是否正确

    Returns:
        bool: 配置是否有效
    """
    try:
        config = Config()
        return bool(config.tavily_api_key and config.tavily_api_key != "your_tavily_api_key_here")
    except SystemExit:
        return False
    except Exception:
        return False
