"""
Tavily Tools - Tavily搜索结果格式化工具包

提供Tavily搜索API的高级封装和多格式输出功能。

主要功能：
- 搜索结果格式化和美化输出
- JSON/HTML报告生成
- 搜索质量分析
- 批量搜索处理
- 配置管理

使用示例：
    from tavily_tools import TavilyFormatter, SearchClient

    client = SearchClient()
    response = client.search("Python编程")

    formatter = TavilyFormatter(response)
    formatter.print_full()
    formatter.save_json()
"""

# 版本信息
__version__ = "0.1.0"
__author__ = "morty"
__email__ = "silenceboychen@gmail.com"

from .config.settings import Config, get_config, get_tavily_client

# 主要导出类和函数
from .core.formatter import TavilyFormatter, quick_format
from .core.search import SearchClient, batch_search, interactive_search

__all__ = [
    "TavilyFormatter",
    "SearchClient",
    "quick_format",
    "interactive_search",
    "batch_search",
    "Config",
    "get_config",
    "get_tavily_client",
    "__version__",
]
